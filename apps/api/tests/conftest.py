import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("ALLOW_MOCK_AUTH", "true")
os.environ.setdefault("GITHUB_APP_SLUG", "gws-deepagent")
os.environ.setdefault("APP_SECRET", "test-secret")
os.environ.setdefault("DB_PATH", "apps/api/data/test.db")

from app.db.database import db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def cleanup_db() -> None:
    db.clear_all()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def create_workspace(client: TestClient, owner_email: str = "owner@example.com") -> int:
    resp = client.post("/workspaces", json={"actor_email": owner_email, "name": "BaeumAI"})
    assert resp.status_code == 200
    return resp.json()["id"]


def connect_google(client: TestClient, workspace_id: int, user_email: str = "owner@example.com") -> None:
    connect = client.post(
        "/oauth/google/connect",
        json={"workspace_id": workspace_id, "user_email": user_email},
    )
    assert connect.status_code == 200
    state = connect.json()["state"]
    callback = client.post(
        "/oauth/google/callback",
        json={"code": "demo-auth-code", "state": state},
    )
    assert callback.status_code == 200
