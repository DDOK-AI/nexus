from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    app_env: str
    app_name: str
    app_port: int
    db_path: str

    deepagent_model: str

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

    github_webhook_secret: str

    barobill_member_id: str
    barobill_api_key: str


settings = Settings(
    app_env=os.getenv("APP_ENV", "local"),
    app_name=os.getenv("APP_NAME", "GWS DeepAgent Workspace API"),
    app_port=int(os.getenv("APP_PORT", "8090")),
    db_path=os.getenv("DB_PATH", "apps/api/data/app.db"),
    deepagent_model=os.getenv("DEEPAGENT_MODEL", "openai:gpt-4.1"),
    google_client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
    google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
    google_redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8090/oauth/google/callback"),
    github_webhook_secret=os.getenv("GITHUB_WEBHOOK_SECRET", ""),
    barobill_member_id=os.getenv("BAROBILL_MEMBER_ID", ""),
    barobill_api_key=os.getenv("BAROBILL_API_KEY", ""),
)
