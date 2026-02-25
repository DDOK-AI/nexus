from __future__ import annotations

import secrets
from typing import Optional
from urllib.parse import urlencode

from app.core.settings import settings
from app.db.database import db


class OAuthService:
    provider = "google"

    def connect_url(self) -> dict:
        state = secrets.token_urlsafe(16)
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

    def callback(self, *, code: str, user_email: str) -> dict:
        now = db.now_iso()
        access_token = f"access_{code[:12]}"
        refresh_token = f"refresh_{code[:12]}"
        scope = "calendar tasks drive docs sheets slides meet"

        db.execute(
            """
            INSERT INTO oauth_accounts(provider, user_email, access_token, refresh_token, scope, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(provider, user_email) DO UPDATE SET
              access_token=excluded.access_token,
              refresh_token=excluded.refresh_token,
              scope=excluded.scope,
              updated_at=excluded.updated_at
            """,
            (self.provider, user_email, access_token, refresh_token, scope, now, now),
        )

        return {
            "provider": self.provider,
            "user_email": user_email,
            "scope": scope,
            "connected": True,
            "note": "MVP 단계에서는 토큰 교환을 모사합니다. 실제 토큰 교환은 Sprint 1에서 적용",
        }

    def account(self, user_email: str) -> Optional[dict]:
        row = db.fetchone(
            "SELECT provider, user_email, scope FROM oauth_accounts WHERE provider=? AND user_email=?",
            (self.provider, user_email),
        )
        if not row:
            return None

        return {
            "provider": row["provider"],
            "user_email": row["user_email"],
            "scope": row["scope"],
            "connected": True,
        }


oauth_service = OAuthService()
