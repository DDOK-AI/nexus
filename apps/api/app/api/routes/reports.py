from typing import Optional

from fastapi import APIRouter, HTTPException

from app.schemas.reports import ReportGenerateRequest
from app.services.report_service import report_service
from app.services.workspace_service import workspace_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/daily")
def generate_daily(payload: ReportGenerateRequest) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            permission="workspace.read",
        )
        return report_service.generate_report(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            report_type="daily",
            period_start=payload.period_start,
            period_end=payload.period_end,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/weekly")
def generate_weekly(payload: ReportGenerateRequest) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            permission="workspace.read",
        )
        return report_service.generate_report(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            report_type="weekly",
            period_start=payload.period_start,
            period_end=payload.period_end,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("")
def list_reports(workspace_id: int, actor_email: str, report_type: Optional[str] = None, limit: int = 100) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="workspace.read",
        )
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return {"reports": report_service.list_reports(workspace_id=workspace_id, report_type=report_type, limit=limit)}
