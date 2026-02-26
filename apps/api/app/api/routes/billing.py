from fastapi import APIRouter, HTTPException

from app.schemas.billing import InvoiceCreateRequest, InvoiceIssueRequest
from app.services.approval_service import approval_service
from app.services.billing_service import billing_service
from app.services.workspace_service import workspace_service

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/invoices")
def create_invoice(payload: InvoiceCreateRequest) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            permission="invoice.create",
        )
        return billing_service.create_invoice(
            workspace_id=payload.workspace_id,
            created_by=payload.actor_email,
            customer=payload.customer,
            business_no=payload.business_no,
            supply_amount=payload.supply_amount,
            vat_rate=payload.vat_rate,
            metadata=payload.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/invoices/{invoice_id}/issue")
def issue_invoice(invoice_id: int, payload: InvoiceIssueRequest) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            permission="invoice.issue",
        )
        invoice = billing_service.get_invoice(payload.workspace_id, invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="세금계산서 초안을 찾을 수 없습니다.")

        request_type = "invoice_issue"
        if payload.approval_request_id <= 0:
            approval = approval_service.create_request(
                workspace_id=payload.workspace_id,
                request_type=request_type,
                payload={"invoice_id": invoice_id, "approver": payload.approver},
                requested_by=payload.actor_email,
                reason="세금계산서 발행은 승인 후 실행됩니다.",
            )
            return {
                "approval_required": True,
                "approval_request": approval,
                "next": f"POST /billing/invoices/{invoice_id}/issue with approval_request_id",
            }

        approval = approval_service.ensure_approved(
            request_id=payload.approval_request_id,
            workspace_id=payload.workspace_id,
            request_type=request_type,
        )

        approved_payload = approval.get("payload", {})
        if int(approved_payload.get("invoice_id", -1)) != invoice_id:
            raise ValueError("승인 요청의 invoice_id가 현재 요청과 다릅니다.")

        issued = billing_service.issue_invoice(
            workspace_id=payload.workspace_id,
            invoice_id=invoice_id,
            approver=payload.approver,
        )
        if not issued:
            raise HTTPException(status_code=404, detail="세금계산서 초안을 찾을 수 없습니다.")
        return issued
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/invoices")
def list_invoices(workspace_id: int, actor_email: str, limit: int = 100) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="workspace.read",
        )
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return {"invoices": billing_service.list_invoices(workspace_id=workspace_id, limit=limit)}
