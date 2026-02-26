from datetime import datetime

from pydantic import BaseModel, Field


class InvoiceCreateRequest(BaseModel):
    workspace_id: int
    actor_email: str
    customer: str
    business_no: str = ""
    supply_amount: float = Field(gt=0)
    vat_rate: float = 0.1
    metadata: dict = Field(default_factory=dict)


class InvoiceIssueRequest(BaseModel):
    workspace_id: int
    actor_email: str
    approver: str
    approval_request_id: int = 0


class InvoiceResponse(BaseModel):
    id: int
    customer: str
    business_no: str
    amount: float
    tax_amount: float
    status: str
    metadata: dict
    created_at: datetime
    updated_at: datetime
