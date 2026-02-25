from __future__ import annotations

from app.services.oauth_service import oauth_service


class WorkspaceService:
    supported_services = ["calendar", "tasks", "drive", "docs", "sheets", "slides", "meet"]

    def execute(self, *, user_email: str, service: str, action: str, payload: dict) -> dict:
        account = oauth_service.account(user_email)
        if not account:
            raise ValueError("Google Workspace 계정이 연결되지 않았습니다. /oauth/google/connect 후 진행하세요.")

        normalized_service = service.lower().strip()
        if normalized_service not in self.supported_services:
            raise ValueError(f"지원하지 않는 서비스입니다: {service}")

        normalized_action = action.lower().strip()
        result = {
            "user_email": user_email,
            "service": normalized_service,
            "action": normalized_action,
            "payload": payload,
            "mode": "simulated-mvp",
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
