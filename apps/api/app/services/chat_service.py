from __future__ import annotations

from typing import Optional

from app.db.database import db


class ChatService:
    def create_channel(self, *, name: str, description: str) -> dict:
        now = db.now_iso()
        db.execute(
            "INSERT INTO chat_channels(name, description, created_at) VALUES (?, ?, ?)",
            (name, description, now),
        )
        row = db.fetchone("SELECT * FROM chat_channels WHERE name=?", (name,))
        assert row is not None
        return row

    def list_channels(self) -> list[dict]:
        return db.fetchall("SELECT * FROM chat_channels ORDER BY id ASC")

    def get_channel(self, channel_id: int) -> Optional[dict]:
        return db.fetchone("SELECT * FROM chat_channels WHERE id=?", (channel_id,))

    def post_message(self, *, channel_id: int, sender: str, content: str) -> dict:
        now = db.now_iso()
        db.execute(
            "INSERT INTO chat_messages(channel_id, sender, content, created_at) VALUES (?, ?, ?, ?)",
            (channel_id, sender, content, now),
        )
        row = db.fetchone("SELECT * FROM chat_messages ORDER BY id DESC LIMIT 1")
        assert row is not None
        return row

    def list_messages(self, channel_id: int, limit: int = 100) -> list[dict]:
        return db.fetchall(
            "SELECT * FROM chat_messages WHERE channel_id=? ORDER BY id DESC LIMIT ?",
            (channel_id, limit),
        )


chat_service = ChatService()
