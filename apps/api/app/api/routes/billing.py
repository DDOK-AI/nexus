from fastapi import APIRouter, HTTPException

from app.schemas.billing import InvoiceCreateRequest, InvoiceIssueRequest
from app.services.billing_service import billing_service

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/invoices")
def create_invoice(payload: InvoiceCreateRequest) -> dict:
    return billing_service.create_invoice(
        customer=payload.customer,
        business_no=payload.business_no,
        supply_amount=payload.supply_amount,
        vat_rate=payload.vat_rate,
        metadata=payload.metadata,
    )


@router.post("/invoices/{invoice_id}/issue")
def issue_invoice(invoice_id: int, payload: InvoiceIssueRequest) -> dict:
    invoice = billing_service.issue_invoice(invoice_id=invoice_id, approver=payload.approver)
    if not invoice:
        raise HTTPException(status_code=404, detail="세금계산서 초안을 찾을 수 없습니다.")
    return invoice


@router.get("/invoices")
def list_invoices(limit: int = 100) -> dict:
    return {"invoices": billing_service.list_invoices(limit=limit)}
