from typing import Optional

from fastapi import APIRouter, HTTPException

from app.schemas.approvals import ApprovalCreateRequest, ApprovalDecisionRequest
from app.services.approval_service import approval_service
from app.services.workspace_service import workspace_service

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.post("/requests")
def create_request(payload: ApprovalCreateRequest) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            permission="agent.execute",
        )
        return approval_service.create_request(
            workspace_id=payload.workspace_id,
            request_type=payload.request_type,
            payload=payload.payload,
            requested_by=payload.actor_email,
            reason=payload.reason,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/inbox")
def inbox(workspace_id: int, actor_email: str, status: Optional[str] = None, limit: int = 100) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="workspace.read",
        )
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return {"requests": approval_service.list_requests(workspace_id=workspace_id, status=status, limit=limit)}


@router.get("/requests/{request_id}")
def get_request(request_id: int, workspace_id: int, actor_email: str) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="workspace.read",
        )
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    req = approval_service.get_request(request_id)
    if not req or req["workspace_id"] != workspace_id:
        raise HTTPException(status_code=404, detail="승인 요청을 찾을 수 없습니다.")
    return req


@router.post("/requests/{request_id}/approve")
def approve_request(request_id: int, payload: ApprovalDecisionRequest) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            permission="approval.decide",
        )
        req = approval_service.approve(request_id=request_id, decided_by=payload.actor_email, note=payload.note)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not req or req["workspace_id"] != payload.workspace_id:
        raise HTTPException(status_code=404, detail="승인 요청을 찾을 수 없습니다.")
    return req


@router.post("/requests/{request_id}/reject")
def reject_request(request_id: int, payload: ApprovalDecisionRequest) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            permission="approval.decide",
        )
        req = approval_service.reject(request_id=request_id, decided_by=payload.actor_email, note=payload.note)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not req or req["workspace_id"] != payload.workspace_id:
        raise HTTPException(status_code=404, detail="승인 요청을 찾을 수 없습니다.")
    return req
