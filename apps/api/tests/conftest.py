import pytest
from fastapi.testclient import TestClient

from app.db.database import db
from app.main import app


@pytest.fixture(autouse=True)
def cleanup_db() -> None:
    db.clear_all()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
