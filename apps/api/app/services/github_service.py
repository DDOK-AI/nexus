from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Optional

from app.core.settings import settings
from app.db.database import db
from app.services.github_integration_service import github_integration_service


class GithubService:
    def verify_signature(self, body: bytes, signature_header: Optional[str]) -> bool:
        secret = settings.github_webhook_secret
        if not secret:
            return True

        if not signature_header or not signature_header.startswith("sha256="):
            return False

        expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        received = signature_header.split("=", 1)[1]
        return hmac.compare_digest(expected, received)

    def ingest_event(self, event_type: str, payload: dict) -> dict:
        repo = payload.get("repository", {}).get("full_name", "")
        actor = payload.get("sender", {}).get("login", "")
        installation_id = payload.get("installation", {}).get("id")
        workspace_id = None
        if installation_id:
            workspace_id = github_integration_service.resolve_workspace_from_installation(int(installation_id))

        created_at = db.now_iso()

        db.execute(
            "INSERT INTO github_events(workspace_id, event_type, repo, actor, payload_json, created_at) VALUES(?, ?, ?, ?, ?, ?)",
            (workspace_id, event_type, repo, actor, db.to_json(payload), created_at),
        )

        return {
            "saved": True,
            "workspace_id": workspace_id,
            "event_type": event_type,
            "repo": repo,
            "actor": actor,
            "created_at": created_at,
        }

    def list_events(self, workspace_id: Optional[int] = None, limit: int = 100) -> list[dict]:
        if workspace_id is not None:
            rows = db.fetchall(
                "SELECT id, workspace_id, event_type, repo, actor, payload_json, created_at FROM github_events WHERE workspace_id=? ORDER BY id DESC LIMIT ?",
                (workspace_id, limit),
            )
        else:
            rows = db.fetchall(
                "SELECT id, workspace_id, event_type, repo, actor, payload_json, created_at FROM github_events ORDER BY id DESC LIMIT ?",
                (limit,),
            )

        result: list[dict] = []
        for row in rows:
            result.append(
                {
                    "id": row["id"],
                    "workspace_id": row.get("workspace_id"),
                    "event_type": row["event_type"],
                    "repo": row["repo"],
                    "actor": row["actor"],
                    "payload": db.from_json(row["payload_json"]),
                    "created_at": row["created_at"],
                }
            )
        return result

    def events_between(self, workspace_id: int, start: datetime, end: datetime) -> list[dict]:
        rows = db.fetchall(
            """
            SELECT id, workspace_id, event_type, repo, actor, payload_json, created_at
            FROM github_events
            WHERE workspace_id=?
              AND datetime(created_at) >= datetime(?)
              AND datetime(created_at) <= datetime(?)
            ORDER BY id ASC
            """,
            (workspace_id, start.astimezone(timezone.utc).isoformat(), end.astimezone(timezone.utc).isoformat()),
        )

        events = []
        for row in rows:
            events.append(
                {
                    "id": row["id"],
                    "workspace_id": row.get("workspace_id"),
                    "event_type": row["event_type"],
                    "repo": row["repo"],
                    "actor": row["actor"],
                    "payload": json.loads(row["payload_json"]),
                    "created_at": row["created_at"],
                }
            )
        return events


github_service = GithubService()
