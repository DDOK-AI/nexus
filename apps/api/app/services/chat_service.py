from __future__ import annotations

from typing import Optional

from app.db.database import db


class ChatService:
    def create_channel(self, *, workspace_id: int, created_by: str, name: str, description: str) -> dict:
        now = db.now_iso()
        db.execute(
            "INSERT INTO chat_channels(workspace_id, name, description, created_by, created_at) VALUES (?, ?, ?, ?, ?)",
            (workspace_id, name, description, created_by, now),
        )
        row = db.fetchone("SELECT * FROM chat_channels WHERE workspace_id=? AND name=?", (workspace_id, name))
        assert row is not None
        return row

    def list_channels(self, workspace_id: int) -> list[dict]:
        return db.fetchall("SELECT * FROM chat_channels WHERE workspace_id=? ORDER BY id ASC", (workspace_id,))

    def get_channel(self, workspace_id: int, channel_id: int) -> Optional[dict]:
        return db.fetchone("SELECT * FROM chat_channels WHERE workspace_id=? AND id=?", (workspace_id, channel_id))

    def post_message(self, *, workspace_id: int, channel_id: int, sender: str, content: str) -> dict:
        channel = self.get_channel(workspace_id, channel_id)
        if not channel:
            raise ValueError("채널을 찾을 수 없습니다.")

        now = db.now_iso()
        db.execute(
            "INSERT INTO chat_messages(channel_id, sender, content, created_at) VALUES (?, ?, ?, ?)",
            (channel_id, sender, content, now),
        )
        row = db.fetchone("SELECT * FROM chat_messages ORDER BY id DESC LIMIT 1")
        assert row is not None
        return row

    def list_messages(self, workspace_id: int, channel_id: int, limit: int = 100) -> list[dict]:
        channel = self.get_channel(workspace_id, channel_id)
        if not channel:
            return []
        return db.fetchall(
            "SELECT * FROM chat_messages WHERE channel_id=? ORDER BY id DESC LIMIT ?",
            (channel_id, limit),
        )


chat_service = ChatService()
