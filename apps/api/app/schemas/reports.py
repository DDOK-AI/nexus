from datetime import date, datetime

from pydantic import BaseModel


class ReportGenerateRequest(BaseModel):
    workspace_id: int
    actor_email: str
    period_start: date
    period_end: date


class ReportResponse(BaseModel):
    id: int
    report_type: str
    period_start: date
    period_end: date
    title: str
    content: str
    created_at: datetime
