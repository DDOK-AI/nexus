from __future__ import annotations

from typing import Optional

from app.db.database import db


class DocsService:
    def create(self, *, space: str, title: str, content: str, tags: list[str]) -> dict:
        now = db.now_iso()
        db.execute(
            "INSERT INTO docs(space, title, content, tags_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (space, title, content, db.to_json(tags), now, now),
        )

        row = db.fetchone("SELECT * FROM docs ORDER BY id DESC LIMIT 1")
        assert row is not None
        return self._deserialize(row)

    def list(self, *, space: Optional[str] = None, limit: int = 100) -> list[dict]:
        if space:
            rows = db.fetchall(
                "SELECT * FROM docs WHERE space=? ORDER BY updated_at DESC LIMIT ?",
                (space, limit),
            )
        else:
            rows = db.fetchall("SELECT * FROM docs ORDER BY updated_at DESC LIMIT ?", (limit,))

        return [self._deserialize(row) for row in rows]

    def get(self, doc_id: int) -> Optional[dict]:
        row = db.fetchone("SELECT * FROM docs WHERE id=?", (doc_id,))
        if not row:
            return None
        return self._deserialize(row)

    def update(
        self,
        doc_id: int,
        *,
        title: Optional[str],
        content: Optional[str],
        tags: Optional[list[str]],
    ) -> Optional[dict]:
        current = db.fetchone("SELECT * FROM docs WHERE id=?", (doc_id,))
        if not current:
            return None

        next_title = title if title is not None else current["title"]
        next_content = content if content is not None else current["content"]
        next_tags = tags if tags is not None else db.from_json(current["tags_json"])
        updated_at = db.now_iso()

        db.execute(
            "UPDATE docs SET title=?, content=?, tags_json=?, updated_at=? WHERE id=?",
            (next_title, next_content, db.to_json(next_tags), updated_at, doc_id),
        )

        updated = db.fetchone("SELECT * FROM docs WHERE id=?", (doc_id,))
        return self._deserialize(updated) if updated else None

    def delete(self, doc_id: int) -> bool:
        existing = db.fetchone("SELECT id FROM docs WHERE id=?", (doc_id,))
        if not existing:
            return False

        db.execute("DELETE FROM docs WHERE id=?", (doc_id,))
        return True

    def search(self, query: str, limit: int = 50) -> list[dict]:
        pattern = f"%{query}%"
        rows = db.fetchall(
            "SELECT * FROM docs WHERE title LIKE ? OR content LIKE ? ORDER BY updated_at DESC LIMIT ?",
            (pattern, pattern, limit),
        )
        return [self._deserialize(row) for row in rows]

    @staticmethod
    def _deserialize(row: dict) -> dict:
        return {
            "id": row["id"],
            "space": row["space"],
            "title": row["title"],
            "content": row["content"],
            "tags": db.from_json(row["tags_json"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }


docs_service = DocsService()
