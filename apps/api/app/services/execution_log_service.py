from __future__ import annotations

from typing import Optional

from app.db.database import db


class ExecutionLogService:
    def create_pending(self, *, workspace_id: int, user_email: str, instruction: str, context: dict) -> int:
        now = db.now_iso()
        db.execute(
            """
            INSERT INTO agent_execution_logs(
                workspace_id, user_email, instruction, context_json, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (workspace_id, user_email, instruction, db.to_json(context), "pending", now, now),
        )
        row = db.fetchone("SELECT id FROM agent_execution_logs ORDER BY id DESC LIMIT 1")
        assert row is not None
        return int(row["id"])

    def complete(self, *, log_id: int, steps: list[dict], outputs: dict) -> None:
        now = db.now_iso()
        db.execute(
            "UPDATE agent_execution_logs SET status=?, steps_json=?, outputs_json=?, updated_at=? WHERE id=?",
            ("completed", db.to_json(steps), db.to_json(outputs), now, log_id),
        )

    def fail(self, *, log_id: int, error_message: str) -> None:
        now = db.now_iso()
        db.execute(
            "UPDATE agent_execution_logs SET status=?, error_message=?, updated_at=? WHERE id=?",
            ("failed", error_message, now, log_id),
        )

    def list_logs(self, *, workspace_id: int, limit: int = 100) -> list[dict]:
        rows = db.fetchall(
            "SELECT * FROM agent_execution_logs WHERE workspace_id=? ORDER BY id DESC LIMIT ?",
            (workspace_id, limit),
        )
        return [self._deserialize(row) for row in rows]

    def get_log(self, log_id: int) -> Optional[dict]:
        row = db.fetchone("SELECT * FROM agent_execution_logs WHERE id=?", (log_id,))
        if not row:
            return None
        return self._deserialize(row)

    @staticmethod
    def _deserialize(row: dict) -> dict:
        return {
            "id": row["id"],
            "workspace_id": row["workspace_id"],
            "user_email": row["user_email"],
            "instruction": row["instruction"],
            "context": db.from_json(row["context_json"]),
            "steps": db.from_json(row["steps_json"]) if row.get("steps_json") else [],
            "outputs": db.from_json(row["outputs_json"]) if row.get("outputs_json") else {},
            "status": row["status"],
            "error_message": row.get("error_message"),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }


execution_log_service = ExecutionLogService()
