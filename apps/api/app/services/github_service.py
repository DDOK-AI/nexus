from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Optional

from app.core.settings import settings
from app.db.database import db


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
        created_at = db.now_iso()

        db.execute(
            "INSERT INTO github_events(event_type, repo, actor, payload_json, created_at) VALUES(?, ?, ?, ?, ?)",
            (event_type, repo, actor, db.to_json(payload), created_at),
        )

        return {
            "saved": True,
            "event_type": event_type,
            "repo": repo,
            "actor": actor,
            "created_at": created_at,
        }

    def list_events(self, limit: int = 100) -> list[dict]:
        rows = db.fetchall(
            "SELECT id, event_type, repo, actor, payload_json, created_at FROM github_events ORDER BY id DESC LIMIT ?",
            (limit,),
        )

        result: list[dict] = []
        for row in rows:
            result.append(
                {
                    "id": row["id"],
                    "event_type": row["event_type"],
                    "repo": row["repo"],
                    "actor": row["actor"],
                    "payload": db.from_json(row["payload_json"]),
                    "created_at": row["created_at"],
                }
            )
        return result

    def events_between(self, start: datetime, end: datetime) -> list[dict]:
        rows = db.fetchall(
            """
            SELECT id, event_type, repo, actor, payload_json, created_at
            FROM github_events
            WHERE datetime(created_at) >= datetime(?) AND datetime(created_at) <= datetime(?)
            ORDER BY id ASC
            """,
            (start.astimezone(timezone.utc).isoformat(), end.astimezone(timezone.utc).isoformat()),
        )

        events = []
        for row in rows:
            events.append(
                {
                    "id": row["id"],
                    "event_type": row["event_type"],
                    "repo": row["repo"],
                    "actor": row["actor"],
                    "payload": json.loads(row["payload_json"]),
                    "created_at": row["created_at"],
                }
            )
        return events


github_service = GithubService()
