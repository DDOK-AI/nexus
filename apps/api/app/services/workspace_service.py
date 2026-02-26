from __future__ import annotations

from typing import Optional

from app.core.rbac import has_permission, normalize_role
from app.db.database import db
from app.services.oauth_service import oauth_service


class WorkspaceService:
    supported_services = ["calendar", "tasks", "drive", "docs", "sheets", "slides", "meet"]

    def upsert_user(self, email: str, display_name: str = "") -> None:
        now = db.now_iso()
        existing = db.fetchone("SELECT email FROM users WHERE email=?", (email,))
        if existing:
            db.execute(
                "UPDATE users SET display_name=?, updated_at=? WHERE email=?",
                (display_name, now, email),
            )
            return
        db.execute(
            "INSERT INTO users(email, display_name, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (email, display_name, now, now),
        )

    def create_workspace(self, *, actor_email: str, name: str) -> dict:
        self.upsert_user(actor_email)
        now = db.now_iso()
        db.execute(
            "INSERT INTO workspaces(name, owner_email, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (name, actor_email, now, now),
        )
        ws = db.fetchone("SELECT * FROM workspaces ORDER BY id DESC LIMIT 1")
        assert ws is not None
        db.execute(
            "INSERT OR REPLACE INTO workspace_members(workspace_id, user_email, role, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (ws["id"], actor_email, "owner", now, now),
        )
        return ws

    def list_workspaces(self, user_email: str) -> list[dict]:
        return db.fetchall(
            """
            SELECT w.*
            FROM workspaces w
            JOIN workspace_members m ON m.workspace_id=w.id
            WHERE m.user_email=?
            ORDER BY w.id ASC
            """,
            (user_email,),
        )

    def get_workspace(self, workspace_id: int, actor_email: str) -> Optional[dict]:
        self.require_permission(workspace_id=workspace_id, actor_email=actor_email, permission="workspace.read")
        return db.fetchone("SELECT * FROM workspaces WHERE id=?", (workspace_id,))

    def membership(self, workspace_id: int, user_email: str) -> Optional[dict]:
        return db.fetchone(
            "SELECT workspace_id, user_email, role, created_at, updated_at FROM workspace_members WHERE workspace_id=? AND user_email=?",
            (workspace_id, user_email),
        )

    def role_of(self, workspace_id: int, user_email: str) -> Optional[str]:
        membership = self.membership(workspace_id, user_email)
        if not membership:
            return None
        return membership["role"]

    def require_permission(self, *, workspace_id: int, actor_email: str, permission: str) -> str:
        role = self.role_of(workspace_id, actor_email)
        if not has_permission(role, permission):
            raise ValueError(f"권한이 없습니다. permission={permission}, actor={actor_email}, role={role}")
        return role

    def add_member(self, *, workspace_id: int, actor_email: str, target_email: str, role: str) -> dict:
        self.require_permission(workspace_id=workspace_id, actor_email=actor_email, permission="workspace.manage_members")
        target_role = normalize_role(role)
        self.upsert_user(target_email)

        now = db.now_iso()
        existing = self.membership(workspace_id, target_email)
        if existing:
            db.execute(
                "UPDATE workspace_members SET role=?, updated_at=? WHERE workspace_id=? AND user_email=?",
                (target_role, now, workspace_id, target_email),
            )
        else:
            db.execute(
                "INSERT INTO workspace_members(workspace_id, user_email, role, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (workspace_id, target_email, target_role, now, now),
            )

        row = self.membership(workspace_id, target_email)
        assert row is not None
        return row

    def update_member_role(self, *, workspace_id: int, actor_email: str, target_email: str, role: str) -> Optional[dict]:
        self.require_permission(workspace_id=workspace_id, actor_email=actor_email, permission="workspace.manage_members")
        target_role = normalize_role(role)
        existing = self.membership(workspace_id, target_email)
        if not existing:
            return None

        now = db.now_iso()
        db.execute(
            "UPDATE workspace_members SET role=?, updated_at=? WHERE workspace_id=? AND user_email=?",
            (target_role, now, workspace_id, target_email),
        )
        return self.membership(workspace_id, target_email)

    def remove_member(self, *, workspace_id: int, actor_email: str, target_email: str) -> bool:
        self.require_permission(workspace_id=workspace_id, actor_email=actor_email, permission="workspace.manage_members")
        ws = db.fetchone("SELECT owner_email FROM workspaces WHERE id=?", (workspace_id,))
        if not ws:
            return False
        if ws["owner_email"] == target_email:
            raise ValueError("owner는 삭제할 수 없습니다.")

        existing = self.membership(workspace_id, target_email)
        if not existing:
            return False

        db.execute(
            "DELETE FROM workspace_members WHERE workspace_id=? AND user_email=?",
            (workspace_id, target_email),
        )
        return True

    def list_members(self, *, workspace_id: int, actor_email: str) -> list[dict]:
        self.require_permission(workspace_id=workspace_id, actor_email=actor_email, permission="workspace.read")
        return db.fetchall(
            "SELECT workspace_id, user_email, role, created_at, updated_at FROM workspace_members WHERE workspace_id=? ORDER BY created_at ASC",
            (workspace_id,),
        )

    def permissions_me(self, *, workspace_id: int, user_email: str) -> dict:
        role = self.role_of(workspace_id, user_email)
        return {
            "workspace_id": workspace_id,
            "user_email": user_email,
            "role": role,
            "permissions": {
                "workspace.read": has_permission(role, "workspace.read"),
                "workspace.manage_members": has_permission(role, "workspace.manage_members"),
                "workspace.execute": has_permission(role, "workspace.execute"),
                "agent.execute": has_permission(role, "agent.execute"),
                "approval.decide": has_permission(role, "approval.decide"),
                "invoice.issue": has_permission(role, "invoice.issue"),
                "invoice.create": has_permission(role, "invoice.create"),
            },
        }

    def execute(
        self,
        *,
        workspace_id: int,
        actor_email: str,
        user_email: Optional[str],
        service: str,
        action: str,
        payload: dict,
    ) -> dict:
        self.require_permission(workspace_id=workspace_id, actor_email=actor_email, permission="workspace.execute")

        resolved_user_email = user_email or actor_email
        if not self.membership(workspace_id, resolved_user_email):
            raise ValueError("지정된 user_email이 workspace 멤버가 아닙니다.")

        token_info = oauth_service.ensure_valid_access_token(resolved_user_email)
        if not token_info["connected"]:
            raise ValueError("Google Workspace 계정이 연결되지 않았습니다. /oauth/google/connect 후 진행하세요.")

        normalized_service = service.lower().strip()
        if normalized_service not in self.supported_services:
            raise ValueError(f"지원하지 않는 서비스입니다: {service}")

        normalized_action = action.lower().strip()
        result = {
            "workspace_id": workspace_id,
            "actor_email": actor_email,
            "user_email": resolved_user_email,
            "service": normalized_service,
            "action": normalized_action,
            "payload": payload,
            "mode": "api-contract-ready",
            "token_type": token_info.get("token_type"),
            "message": f"{normalized_service}.{normalized_action} 실행 준비 완료",
        }

        if normalized_service == "calendar" and normalized_action == "create":
            result["created"] = {
                "event_id": "evt_demo_001",
                "title": payload.get("title", "새 일정"),
                "start": payload.get("start"),
                "end": payload.get("end"),
            }

        if normalized_service == "drive" and normalized_action in {"search", "list"}:
            result["items"] = [
                {"id": "file_demo_001", "name": "R&D 주간보고 초안"},
                {"id": "file_demo_002", "name": "고객 미팅 노트"},
            ]

        return result


workspace_service = WorkspaceService()
