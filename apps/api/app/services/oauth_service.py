from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlencode

import httpx

from app.core.security import sign_state, verify_state
from app.core.settings import settings
from app.db.database import db


class OAuthService:
    provider = "google"

    def connect_url(self, *, workspace_id: int, user_email: str) -> dict:
        state = sign_state(
            {
                "provider": self.provider,
                "workspace_id": workspace_id,
                "user_email": user_email,
                "nonce": secrets.token_urlsafe(12),
            },
            expires_in_sec=900,
        )

        query = {
            "client_id": settings.google_client_id or "set-google-client-id",
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/tasks",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        return {
            "provider": self.provider,
            "state": state,
            "auth_url": f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(query)}",
        }

    def _exchange_code(self, code: str) -> dict:
        if not settings.google_client_id or not settings.google_client_secret:
            if settings.allow_mock_auth:
                now = datetime.now(timezone.utc)
                return {
                    "access_token": f"mock_access_{code[:12]}",
                    "refresh_token": f"mock_refresh_{code[:12]}",
                    "scope": "calendar tasks drive docs sheets slides meet",
                    "token_type": "Bearer",
                    "expires_at": (now + timedelta(hours=1)).isoformat(),
                    "mock": True,
                }
            raise ValueError("GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET 설정이 필요합니다.")

        with httpx.Client(timeout=15.0) as client:
            response = client.post(
                settings.google_token_url,
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.google_redirect_uri,
                },
                headers={"Accept": "application/json"},
            )

        if response.status_code >= 400:
            raise ValueError(f"Google 토큰 교환 실패: {response.status_code} {response.text}")

        data = response.json()
        expires_in = int(data.get("expires_in", 3600))
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        return {
            "access_token": data.get("access_token", ""),
            "refresh_token": data.get("refresh_token", ""),
            "scope": data.get("scope", ""),
            "token_type": data.get("token_type", "Bearer"),
            "expires_at": expires_at.isoformat(),
            "id_token": data.get("id_token", ""),
            "mock": False,
        }

    def _fetch_google_email(self, access_token: str, token_type: str = "Bearer") -> Optional[str]:
        if access_token.startswith("mock_"):
            return None
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                settings.google_userinfo_url,
                headers={"Authorization": f"{token_type} {access_token}", "Accept": "application/json"},
            )

        if response.status_code >= 400:
            raise ValueError(f"Google userinfo 조회 실패: {response.status_code} {response.text}")

        data = response.json()
        email = data.get("email")
        return str(email) if email else None

    def callback(self, *, code: str, state: str) -> dict:
        payload = verify_state(state)
        if not payload:
            raise ValueError("유효하지 않거나 만료된 state 입니다.")
        if payload.get("provider") != self.provider:
            raise ValueError("OAuth provider state가 일치하지 않습니다.")

        workspace_id = int(payload["workspace_id"])
        user_email = str(payload["user_email"])

        token_data = self._exchange_code(code)

        google_email = self._fetch_google_email(
            token_data.get("access_token", ""),
            token_data.get("token_type", "Bearer"),
        )
        if google_email and google_email.lower() != user_email.lower():
            raise ValueError(
                f"Google 계정 이메일({google_email})과 요청 사용자({user_email})가 일치하지 않습니다."
            )

        now = db.now_iso()

        db.execute(
            """
            INSERT INTO oauth_accounts(provider, user_email, access_token, refresh_token, scope, token_type, expires_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(provider, user_email) DO UPDATE SET
              access_token=excluded.access_token,
              refresh_token=CASE WHEN excluded.refresh_token='' THEN oauth_accounts.refresh_token ELSE excluded.refresh_token END,
              scope=excluded.scope,
              token_type=excluded.token_type,
              expires_at=excluded.expires_at,
              updated_at=excluded.updated_at
            """,
            (
                self.provider,
                user_email,
                token_data["access_token"],
                token_data.get("refresh_token", ""),
                token_data.get("scope", ""),
                token_data.get("token_type", "Bearer"),
                token_data.get("expires_at"),
                now,
                now,
            ),
        )

        return {
            "provider": self.provider,
            "workspace_id": workspace_id,
            "user_email": user_email,
            "scope": token_data.get("scope", ""),
            "connected": True,
            "token_type": token_data.get("token_type", "Bearer"),
            "expires_at": token_data.get("expires_at"),
            "mock": token_data.get("mock", False),
        }

    def disconnect(self, user_email: str) -> bool:
        existing = db.fetchone(
            "SELECT provider, user_email FROM oauth_accounts WHERE provider=? AND user_email=?",
            (self.provider, user_email),
        )
        if not existing:
            return False
        db.execute(
            "DELETE FROM oauth_accounts WHERE provider=? AND user_email=?",
            (self.provider, user_email),
        )
        return True

    def _refresh_token(self, row: dict) -> dict:
        refresh_token = row.get("refresh_token") or ""
        if not refresh_token:
            raise ValueError("refresh_token이 없어 갱신할 수 없습니다.")

        if not settings.google_client_id or not settings.google_client_secret:
            if settings.allow_mock_auth:
                expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
                return {
                    "access_token": f"mock_refreshed_{secrets.token_hex(8)}",
                    "token_type": "Bearer",
                    "expires_at": expires_at.isoformat(),
                    "scope": row.get("scope", ""),
                    "mock": True,
                }
            raise ValueError("Google refresh를 위해 클라이언트 자격 증명이 필요합니다.")

        with httpx.Client(timeout=15.0) as client:
            response = client.post(
                settings.google_token_url,
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
                headers={"Accept": "application/json"},
            )

        if response.status_code >= 400:
            raise ValueError(f"Google 토큰 갱신 실패: {response.status_code} {response.text}")

        data = response.json()
        expires_in = int(data.get("expires_in", 3600))
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        return {
            "access_token": data.get("access_token", ""),
            "token_type": data.get("token_type", row.get("token_type", "Bearer")),
            "expires_at": expires_at.isoformat(),
            "scope": data.get("scope", row.get("scope", "")),
            "mock": False,
        }

    def ensure_valid_access_token(self, user_email: str) -> dict:
        row = db.fetchone(
            "SELECT * FROM oauth_accounts WHERE provider=? AND user_email=?",
            (self.provider, user_email),
        )
        if not row:
            return {"connected": False}

        expires_at_text = row.get("expires_at")
        should_refresh = False
        if expires_at_text:
            try:
                expires_at = datetime.fromisoformat(expires_at_text)
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                should_refresh = expires_at <= (datetime.now(timezone.utc) + timedelta(minutes=2))
            except ValueError:
                should_refresh = True

        if should_refresh:
            refreshed = self._refresh_token(row)
            now = db.now_iso()
            db.execute(
                "UPDATE oauth_accounts SET access_token=?, token_type=?, scope=?, expires_at=?, updated_at=? WHERE provider=? AND user_email=?",
                (
                    refreshed["access_token"],
                    refreshed.get("token_type", "Bearer"),
                    refreshed.get("scope", row.get("scope", "")),
                    refreshed.get("expires_at"),
                    now,
                    self.provider,
                    user_email,
                ),
            )
            row = db.fetchone(
                "SELECT * FROM oauth_accounts WHERE provider=? AND user_email=?",
                (self.provider, user_email),
            )
            assert row is not None

        return {
            "connected": True,
            "provider": row["provider"],
            "user_email": row["user_email"],
            "scope": row.get("scope", ""),
            "token_type": row.get("token_type", "Bearer"),
            "access_token": row.get("access_token", ""),
            "expires_at": row.get("expires_at"),
        }

    def account(self, user_email: str) -> Optional[dict]:
        token = self.ensure_valid_access_token(user_email)
        if not token["connected"]:
            return None
        return {
            "provider": token["provider"],
            "user_email": token["user_email"],
            "scope": token.get("scope", ""),
            "connected": True,
            "token_type": token.get("token_type", "Bearer"),
            "expires_at": token.get("expires_at"),
        }


oauth_service = OAuthService()
