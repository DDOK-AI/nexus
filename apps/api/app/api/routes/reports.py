from fastapi import APIRouter
from typing import Optional

from app.schemas.reports import ReportGenerateRequest
from app.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/daily")
def generate_daily(payload: ReportGenerateRequest) -> dict:
    return report_service.generate_report(
        report_type="daily",
        period_start=payload.period_start,
        period_end=payload.period_end,
    )


@router.post("/weekly")
def generate_weekly(payload: ReportGenerateRequest) -> dict:
    return report_service.generate_report(
        report_type="weekly",
        period_start=payload.period_start,
        period_end=payload.period_end,
    )


@router.get("")
def list_reports(report_type: Optional[str] = None, limit: int = 100) -> dict:
    return {"reports": report_service.list_reports(report_type=report_type, limit=limit)}
