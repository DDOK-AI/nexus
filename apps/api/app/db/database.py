from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Iterable, Optional

from app.core.settings import settings


class AppDatabase:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._lock = Lock()
        self._ensure_parent()
        self._init_schema()

    def _ensure_parent(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _connect(self) -> Iterable[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS oauth_accounts (
                        provider TEXT NOT NULL,
                        user_email TEXT NOT NULL,
                        access_token TEXT,
                        refresh_token TEXT,
                        scope TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        PRIMARY KEY (provider, user_email)
                    );

                    CREATE TABLE IF NOT EXISTS github_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_type TEXT NOT NULL,
                        repo TEXT,
                        actor TEXT,
                        payload_json TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS docs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        space TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        tags_json TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS chat_channels (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        description TEXT,
                        created_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS chat_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        channel_id INTEGER NOT NULL,
                        sender TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY(channel_id) REFERENCES chat_channels(id)
                    );

                    CREATE TABLE IF NOT EXISTS reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        report_type TEXT NOT NULL,
                        period_start TEXT NOT NULL,
                        period_end TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS billing_invoices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer TEXT NOT NULL,
                        business_no TEXT,
                        amount REAL NOT NULL,
                        tax_amount REAL NOT NULL,
                        status TEXT NOT NULL,
                        metadata_json TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );
                    """
                )

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def to_json(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False)

    @staticmethod
    def from_json(value: str) -> Any:
        return json.loads(value)

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(query, params)

    def executemany(self, query: str, params: list[tuple[Any, ...]]) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.executemany(query, params)

    def fetchone(self, query: str, params: tuple[Any, ...] = ()) -> Optional[dict[str, Any]]:
        with self._lock:
            with self._connect() as conn:
                row = conn.execute(query, params).fetchone()
        return dict(row) if row else None

    def fetchall(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self._lock:
            with self._connect() as conn:
                rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def clear_all(self) -> None:
        tables = [
            "oauth_accounts",
            "github_events",
            "docs",
            "chat_messages",
            "chat_channels",
            "reports",
            "billing_invoices",
        ]
        with self._lock:
            with self._connect() as conn:
                for table in tables:
                    conn.execute(f"DELETE FROM {table}")


db = AppDatabase(settings.db_path)
