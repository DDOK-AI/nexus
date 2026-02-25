from datetime import datetime

from pydantic import BaseModel, Field


class InvoiceCreateRequest(BaseModel):
    customer: str
    business_no: str = ""
    supply_amount: float = Field(gt=0)
    vat_rate: float = 0.1
    metadata: dict = Field(default_factory=dict)


class InvoiceIssueRequest(BaseModel):
    approver: str


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
