from fastapi import APIRouter, HTTPException

from app.schemas.workspace import (
    MemberAddRequest,
    MemberRoleUpdateRequest,
    WorkspaceActionRequest,
    WorkspaceActionResult,
    WorkspaceCreateRequest,
)
from app.services.workspace_service import workspace_service

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("")
def create_workspace(payload: WorkspaceCreateRequest) -> dict:
    try:
        return workspace_service.create_workspace(actor_email=payload.actor_email, name=payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("")
def list_workspaces(user_email: str) -> dict:
    return {"workspaces": workspace_service.list_workspaces(user_email)}


@router.get("/{workspace_id}")
def get_workspace(workspace_id: int, actor_email: str) -> dict:
    try:
        ws = workspace_service.get_workspace(workspace_id, actor_email)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    if not ws:
        raise HTTPException(status_code=404, detail="workspace를 찾을 수 없습니다.")
    return ws


@router.get("/{workspace_id}/members")
def list_members(workspace_id: int, actor_email: str) -> dict:
    try:
        return {"members": workspace_service.list_members(workspace_id=workspace_id, actor_email=actor_email)}
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post("/{workspace_id}/members")
def add_member(workspace_id: int, payload: MemberAddRequest) -> dict:
    try:
        return workspace_service.add_member(
            workspace_id=workspace_id,
            actor_email=payload.actor_email,
            target_email=payload.target_email,
            role=payload.role,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/{workspace_id}/members/{target_email}")
def update_member(workspace_id: int, target_email: str, payload: MemberRoleUpdateRequest) -> dict:
    try:
        member = workspace_service.update_member_role(
            workspace_id=workspace_id,
            actor_email=payload.actor_email,
            target_email=target_email,
            role=payload.role,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not member:
        raise HTTPException(status_code=404, detail="멤버를 찾을 수 없습니다.")
    return member


@router.delete("/{workspace_id}/members/{target_email}")
def remove_member(workspace_id: int, target_email: str, actor_email: str) -> dict:
    try:
        deleted = workspace_service.remove_member(
            workspace_id=workspace_id,
            actor_email=actor_email,
            target_email=target_email,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not deleted:
        raise HTTPException(status_code=404, detail="멤버를 찾을 수 없습니다.")
    return {"deleted": True}


@router.get("/{workspace_id}/permissions/me")
def permissions_me(workspace_id: int, user_email: str) -> dict:
    return workspace_service.permissions_me(workspace_id=workspace_id, user_email=user_email)


@router.get("/{workspace_id}/services")
def services(workspace_id: int, actor_email: str) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="workspace.read",
        )
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"services": workspace_service.supported_services}


@router.post("/{workspace_id}/execute", response_model=WorkspaceActionResult)
def execute_action(workspace_id: int, payload: WorkspaceActionRequest) -> dict:
    if workspace_id != payload.workspace_id:
        raise HTTPException(status_code=400, detail="path workspace_id와 body workspace_id가 다릅니다.")

    try:
        result = workspace_service.execute(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            user_email=payload.user_email or payload.actor_email,
            service=payload.service,
            action=payload.action,
            payload=payload.payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "ok": True,
        "service": payload.service,
        "action": payload.action,
        "result": result,
    }
