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

    @staticmethod
    def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        return any(row[1] == column for row in rows)

    def _add_column_if_missing(self, conn: sqlite3.Connection, table: str, column: str, sql_type: str) -> None:
        if not self._column_exists(conn, table, column):
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}")

    def _init_schema(self) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        email TEXT PRIMARY KEY,
                        display_name TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS workspaces (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        owner_email TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        FOREIGN KEY(owner_email) REFERENCES users(email)
                    );

                    CREATE TABLE IF NOT EXISTS workspace_members (
                        workspace_id INTEGER NOT NULL,
                        user_email TEXT NOT NULL,
                        role TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        PRIMARY KEY(workspace_id, user_email),
                        FOREIGN KEY(workspace_id) REFERENCES workspaces(id),
                        FOREIGN KEY(user_email) REFERENCES users(email)
                    );

                    CREATE TABLE IF NOT EXISTS oauth_accounts (
                        provider TEXT NOT NULL,
                        user_email TEXT NOT NULL,
                        access_token TEXT,
                        refresh_token TEXT,
                        scope TEXT,
                        token_type TEXT,
                        expires_at TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        PRIMARY KEY (provider, user_email)
                    );

                    CREATE TABLE IF NOT EXISTS github_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        workspace_id INTEGER,
                        event_type TEXT NOT NULL,
                        repo TEXT,
                        actor TEXT,
                        payload_json TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS github_installations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        workspace_id INTEGER NOT NULL,
                        installation_id INTEGER NOT NULL,
                        account_login TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        UNIQUE(workspace_id, installation_id)
                    );

                    CREATE TABLE IF NOT EXISTS github_repos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        workspace_id INTEGER NOT NULL,
                        installation_id INTEGER,
                        repo_id INTEGER,
                        full_name TEXT NOT NULL,
                        default_branch TEXT,
                        is_private INTEGER NOT NULL DEFAULT 0,
                        linked_by TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS docs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        workspace_id INTEGER,
                        space TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        tags_json TEXT NOT NULL,
                        created_by TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS chat_channels (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        workspace_id INTEGER,
                        name TEXT NOT NULL,
                        description TEXT,
                        created_by TEXT,
                        created_at TEXT NOT NULL,
                        UNIQUE(workspace_id, name)
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
                        workspace_id INTEGER,
                        report_type TEXT NOT NULL,
                        period_start TEXT NOT NULL,
                        period_end TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_by TEXT,
                        created_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS billing_invoices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        workspace_id INTEGER,
                        customer TEXT NOT NULL,
                        business_no TEXT,
                        amount REAL NOT NULL,
                        tax_amount REAL NOT NULL,
                        status TEXT NOT NULL,
                        metadata_json TEXT NOT NULL,
                        created_by TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS approvals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        workspace_id INTEGER NOT NULL,
                        request_type TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        reason TEXT,
                        status TEXT NOT NULL,
                        requested_by TEXT NOT NULL,
                        requested_at TEXT NOT NULL,
                        decided_by TEXT,
                        decided_at TEXT,
                        decision_note TEXT
                    );

                    CREATE TABLE IF NOT EXISTS agent_execution_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        workspace_id INTEGER NOT NULL,
                        user_email TEXT NOT NULL,
                        instruction TEXT NOT NULL,
                        context_json TEXT NOT NULL,
                        steps_json TEXT,
                        outputs_json TEXT,
                        status TEXT NOT NULL,
                        error_message TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );
                    """
                )

                # Backward-compat migrations for older local DBs
                self._add_column_if_missing(conn, "oauth_accounts", "token_type", "TEXT")
                self._add_column_if_missing(conn, "oauth_accounts", "expires_at", "TEXT")
                self._add_column_if_missing(conn, "docs", "workspace_id", "INTEGER")
                self._add_column_if_missing(conn, "docs", "created_by", "TEXT")
                self._add_column_if_missing(conn, "chat_channels", "workspace_id", "INTEGER")
                self._add_column_if_missing(conn, "chat_channels", "created_by", "TEXT")
                self._add_column_if_missing(conn, "reports", "workspace_id", "INTEGER")
                self._add_column_if_missing(conn, "reports", "created_by", "TEXT")
                self._add_column_if_missing(conn, "billing_invoices", "workspace_id", "INTEGER")
                self._add_column_if_missing(conn, "billing_invoices", "created_by", "TEXT")
                self._add_column_if_missing(conn, "github_events", "workspace_id", "INTEGER")

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
            "agent_execution_logs",
            "approvals",
            "billing_invoices",
            "reports",
            "chat_messages",
            "chat_channels",
            "docs",
            "github_repos",
            "github_installations",
            "github_events",
            "oauth_accounts",
            "workspace_members",
            "workspaces",
            "users",
        ]
        with self._lock:
            with self._connect() as conn:
                for table in tables:
                    conn.execute(f"DELETE FROM {table}")


db = AppDatabase(settings.db_path)
