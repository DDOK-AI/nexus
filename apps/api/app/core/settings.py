from __future__ import annotations

import os
from dataclasses import dataclass


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    app_env: str
    app_name: str
    app_port: int
    app_secret: str
    db_path: str

    deepagent_model: str

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    google_token_url: str
    google_userinfo_url: str
    allow_mock_auth: bool

    github_webhook_secret: str
    github_app_id: str
    github_app_slug: str
    github_app_install_url: str
    github_api_url: str
    github_app_private_key: str
    github_app_token: str

    barobill_member_id: str
    barobill_api_key: str


settings = Settings(
    app_env=os.getenv("APP_ENV", "local"),
    app_name=os.getenv("APP_NAME", "GWS DeepAgent Workspace API"),
    app_port=int(os.getenv("APP_PORT", "8090")),
    app_secret=os.getenv("APP_SECRET", "change-me-in-production"),
    db_path=os.getenv("DB_PATH", "apps/api/data/app.db"),
    deepagent_model=os.getenv("DEEPAGENT_MODEL", "openai:gpt-4.1"),
    google_client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
    google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
    google_redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8090/oauth/google/callback"),
    google_token_url=os.getenv("GOOGLE_TOKEN_URL", "https://oauth2.googleapis.com/token"),
    google_userinfo_url=os.getenv("GOOGLE_USERINFO_URL", "https://openidconnect.googleapis.com/v1/userinfo"),
    allow_mock_auth=_as_bool(os.getenv("ALLOW_MOCK_AUTH", "true"), default=True),
    github_webhook_secret=os.getenv("GITHUB_WEBHOOK_SECRET", ""),
    github_app_id=os.getenv("GITHUB_APP_ID", ""),
    github_app_slug=os.getenv("GITHUB_APP_SLUG", ""),
    github_app_install_url=os.getenv("GITHUB_APP_INSTALL_URL", ""),
    github_api_url=os.getenv("GITHUB_API_URL", "https://api.github.com"),
    github_app_private_key=os.getenv("GITHUB_APP_PRIVATE_KEY", ""),
    github_app_token=os.getenv("GITHUB_APP_TOKEN", ""),
    barobill_member_id=os.getenv("BAROBILL_MEMBER_ID", ""),
    barobill_api_key=os.getenv("BAROBILL_API_KEY", ""),
)
