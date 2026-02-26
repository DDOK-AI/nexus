from __future__ import annotations

from typing import Optional

from app.db.database import db


class ApprovalService:
    def create_request(
        self,
        *,
        workspace_id: int,
        request_type: str,
        payload: dict,
        requested_by: str,
        reason: str,
    ) -> dict:
        now = db.now_iso()
        db.execute(
            """
            INSERT INTO approvals(workspace_id, request_type, payload_json, reason, status, requested_by, requested_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (workspace_id, request_type, db.to_json(payload), reason, "pending", requested_by, now),
        )
        row = db.fetchone("SELECT * FROM approvals ORDER BY id DESC LIMIT 1")
        assert row is not None
        return self._deserialize(row)

    def list_requests(self, *, workspace_id: int, status: Optional[str], limit: int = 100) -> list[dict]:
        if status:
            rows = db.fetchall(
                "SELECT * FROM approvals WHERE workspace_id=? AND status=? ORDER BY id DESC LIMIT ?",
                (workspace_id, status, limit),
            )
        else:
            rows = db.fetchall(
                "SELECT * FROM approvals WHERE workspace_id=? ORDER BY id DESC LIMIT ?",
                (workspace_id, limit),
            )
        return [self._deserialize(row) for row in rows]

    def get_request(self, request_id: int) -> Optional[dict]:
        row = db.fetchone("SELECT * FROM approvals WHERE id=?", (request_id,))
        if not row:
            return None
        return self._deserialize(row)

    def approve(self, *, request_id: int, decided_by: str, note: str = "") -> Optional[dict]:
        row = db.fetchone("SELECT * FROM approvals WHERE id=?", (request_id,))
        if not row:
            return None
        if row["status"] != "pending":
            raise ValueError("이미 처리된 승인 요청입니다.")

        now = db.now_iso()
        db.execute(
            "UPDATE approvals SET status=?, decided_by=?, decided_at=?, decision_note=? WHERE id=?",
            ("approved", decided_by, now, note, request_id),
        )
        updated = db.fetchone("SELECT * FROM approvals WHERE id=?", (request_id,))
        return self._deserialize(updated) if updated else None

    def reject(self, *, request_id: int, decided_by: str, note: str = "") -> Optional[dict]:
        row = db.fetchone("SELECT * FROM approvals WHERE id=?", (request_id,))
        if not row:
            return None
        if row["status"] != "pending":
            raise ValueError("이미 처리된 승인 요청입니다.")

        now = db.now_iso()
        db.execute(
            "UPDATE approvals SET status=?, decided_by=?, decided_at=?, decision_note=? WHERE id=?",
            ("rejected", decided_by, now, note, request_id),
        )
        updated = db.fetchone("SELECT * FROM approvals WHERE id=?", (request_id,))
        return self._deserialize(updated) if updated else None

    def ensure_approved(
        self,
        *,
        request_id: Optional[int],
        workspace_id: int,
        request_type: str,
    ) -> dict:
        if request_id is None:
            raise ValueError("approval_request_id가 필요합니다.")

        req = self.get_request(request_id)
        if not req:
            raise ValueError("승인 요청을 찾을 수 없습니다.")
        if req["workspace_id"] != workspace_id:
            raise ValueError("다른 workspace의 승인 요청입니다.")
        if req["request_type"] != request_type:
            raise ValueError("승인 요청 타입이 일치하지 않습니다.")
        if req["status"] != "approved":
            raise ValueError("승인되지 않은 요청입니다.")
        return req

    @staticmethod
    def _deserialize(row: dict) -> dict:
        return {
            "id": row["id"],
            "workspace_id": row["workspace_id"],
            "request_type": row["request_type"],
            "payload": db.from_json(row["payload_json"]),
            "reason": row["reason"],
            "status": row["status"],
            "requested_by": row["requested_by"],
            "requested_at": row["requested_at"],
            "decided_by": row["decided_by"],
            "decided_at": row["decided_at"],
            "decision_note": row["decision_note"],
        }


approval_service = ApprovalService()
