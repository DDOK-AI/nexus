from __future__ import annotations

import base64
import json
import secrets
import time
from typing import Optional
from urllib.parse import urlencode

import httpx

from app.core.security import sign_state, verify_state
from app.core.settings import settings
from app.db.database import db
from app.services.workspace_service import workspace_service


class GithubIntegrationService:
    @staticmethod
    def _b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

    def _load_private_key_pem(self) -> str:
        raw = settings.github_app_private_key.strip()
        if not raw:
            raise ValueError("GITHUB_APP_PRIVATE_KEY 설정이 필요합니다.")

        if "\\n" in raw:
            raw = raw.replace("\\n", "\n")
        return raw

    def _create_app_jwt(self) -> str:
        if not settings.github_app_id:
            raise ValueError("GITHUB_APP_ID 설정이 필요합니다.")

        private_key_pem = self._load_private_key_pem()

        # Lazy import: only needed for real GitHub App JWT flow.
        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding
        except Exception as exc:  # pragma: no cover
            raise ValueError("cryptography 패키지가 필요합니다. `pip install cryptography` 후 재시도하세요.") from exc

        now = int(time.time())
        header = {"alg": "RS256", "typ": "JWT"}
        payload = {
            "iat": now - 60,
            "exp": now + 540,
            "iss": settings.github_app_id,
        }

        signing_input = f"{self._b64url(json.dumps(header, separators=(',', ':')).encode())}.{self._b64url(json.dumps(payload, separators=(',', ':')).encode())}"

        private_key = serialization.load_pem_private_key(private_key_pem.encode("utf-8"), password=None)
        signature = private_key.sign(signing_input.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
        return f"{signing_input}.{self._b64url(signature)}"

    def _get_installation_token(self, installation_id: int) -> str:
        app_jwt = self._create_app_jwt()
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(
                f"{settings.github_api_url}/app/installations/{installation_id}/access_tokens",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {app_jwt}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                json={"repositories": []},
            )
        if resp.status_code >= 400:
            raise ValueError(f"GitHub installation token 발급 실패: {resp.status_code} {resp.text}")
        return resp.json().get("token", "")

    def _get_repo_query_token(self, installation_id: int) -> Optional[str]:
        if settings.github_app_token:
            return settings.github_app_token

        if settings.github_app_id and settings.github_app_private_key:
            token = self._get_installation_token(installation_id)
            if not token:
                raise ValueError("GitHub installation token을 발급하지 못했습니다.")
            return token

        return None

    def install_url(self, *, workspace_id: int, actor_email: str) -> dict:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="github.link",
        )
        if not settings.github_app_slug and not settings.github_app_install_url:
            raise ValueError("GITHUB_APP_SLUG 또는 GITHUB_APP_INSTALL_URL 설정이 필요합니다.")

        state = sign_state(
            {
                "workspace_id": workspace_id,
                "actor_email": actor_email,
                "provider": "github_app",
                "nonce": secrets.token_urlsafe(12),
            },
            expires_in_sec=900,
        )

        if settings.github_app_install_url:
            base = settings.github_app_install_url
        else:
            base = f"https://github.com/apps/{settings.github_app_slug}/installations/new"

        return {
            "workspace_id": workspace_id,
            "state": state,
            "install_url": f"{base}?{urlencode({'state': state})}",
        }

    def callback(self, *, state: str, installation_id: int, account_login: str) -> dict:
        payload = verify_state(state)
        if not payload:
            raise ValueError("유효하지 않은 state 입니다.")
        if payload.get("provider") != "github_app":
            raise ValueError("GitHub App state가 아닙니다.")

        workspace_id = int(payload["workspace_id"])
        actor_email = str(payload["actor_email"])
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="github.link",
        )

        now = db.now_iso()
        db.execute(
            """
            INSERT INTO github_installations(workspace_id, installation_id, account_login, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(workspace_id, installation_id) DO UPDATE SET
                account_login=excluded.account_login,
                updated_at=excluded.updated_at
            """,
            (workspace_id, installation_id, account_login, now, now),
        )

        row = db.fetchone(
            "SELECT * FROM github_installations WHERE workspace_id=? AND installation_id=?",
            (workspace_id, installation_id),
        )
        assert row is not None
        return row

    def list_installations(self, *, workspace_id: int, actor_email: str) -> list[dict]:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="workspace.read",
        )
        return db.fetchall(
            "SELECT * FROM github_installations WHERE workspace_id=? ORDER BY id DESC",
            (workspace_id,),
        )

    def list_installation_repos(self, *, workspace_id: int, actor_email: str, installation_id: int) -> dict:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="github.link",
        )

        token = self._get_repo_query_token(installation_id)
        if not token:
            return {
                "mode": "no-github-token",
                "repositories": [],
                "note": "GITHUB_APP_TOKEN 또는 GITHUB_APP_ID+GITHUB_APP_PRIVATE_KEY를 설정하면 실제 조회됩니다.",
            }

        with httpx.Client(timeout=20.0) as client:
            resp = client.get(
                f"{settings.github_api_url}/installation/repositories",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {token}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
        if resp.status_code >= 400:
            raise ValueError(f"GitHub 설치 리포 조회 실패: {resp.status_code} {resp.text}")

        data = resp.json()
        return {
            "mode": "real-github-api",
            "total_count": data.get("total_count", 0),
            "repositories": data.get("repositories", []),
        }

    def link_repo(
        self,
        *,
        workspace_id: int,
        actor_email: str,
        installation_id: int,
        repo_full_name: str,
    ) -> dict:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="github.link",
        )

        repo_id = None
        default_branch = None
        is_private = 0
        mode = "no-github-token"

        token = self._get_repo_query_token(installation_id)
        if token:
            with httpx.Client(timeout=20.0) as client:
                resp = client.get(
                    f"{settings.github_api_url}/repos/{repo_full_name}",
                    headers={
                        "Accept": "application/vnd.github+json",
                        "Authorization": f"Bearer {token}",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                )
            if resp.status_code >= 400:
                raise ValueError(f"GitHub repo 조회 실패: {resp.status_code} {resp.text}")
            repo = resp.json()
            repo_id = repo.get("id")
            default_branch = repo.get("default_branch")
            is_private = 1 if repo.get("private") else 0
            mode = "real-github-api"

        now = db.now_iso()
        db.execute(
            """
            INSERT INTO github_repos(workspace_id, installation_id, repo_id, full_name, default_branch, is_private, linked_by, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (workspace_id, installation_id, repo_id, repo_full_name, default_branch, is_private, actor_email, now, now),
        )

        row = db.fetchone("SELECT * FROM github_repos ORDER BY id DESC LIMIT 1")
        assert row is not None
        return {
            **row,
            "mode": mode,
            "note": None
            if token
            else "GITHUB_APP_TOKEN 또는 GITHUB_APP_ID+GITHUB_APP_PRIVATE_KEY를 설정하면 실제 repo 메타데이터를 저장합니다.",
        }

    def list_linked_repos(self, *, workspace_id: int, actor_email: str) -> list[dict]:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="workspace.read",
        )
        return db.fetchall(
            "SELECT * FROM github_repos WHERE workspace_id=? ORDER BY id DESC",
            (workspace_id,),
        )

    def resolve_workspace_from_installation(self, installation_id: int) -> Optional[int]:
        row = db.fetchone(
            "SELECT workspace_id FROM github_installations WHERE installation_id=? ORDER BY id DESC LIMIT 1",
            (installation_id,),
        )
        return int(row["workspace_id"]) if row else None


github_integration_service = GithubIntegrationService()
