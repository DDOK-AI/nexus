from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChannelCreateRequest, MessageCreateRequest
from app.services.chat_service import chat_service
from app.services.workspace_service import workspace_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/channels")
def create_channel(payload: ChannelCreateRequest) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            permission="chat.write",
        )
        return chat_service.create_channel(
            workspace_id=payload.workspace_id,
            created_by=payload.actor_email,
            name=payload.name,
            description=payload.description,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"채널 생성 실패: {exc}") from exc


@router.get("/channels")
def list_channels(workspace_id: int, actor_email: str) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="workspace.read",
        )
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return {"channels": chat_service.list_channels(workspace_id)}


@router.post("/channels/{channel_id}/messages")
def post_message(channel_id: int, payload: MessageCreateRequest) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=payload.workspace_id,
            actor_email=payload.sender,
            permission="chat.write",
        )
        return chat_service.post_message(
            workspace_id=payload.workspace_id,
            channel_id=channel_id,
            sender=payload.sender,
            content=payload.content,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/channels/{channel_id}/messages")
def list_messages(channel_id: int, workspace_id: int, actor_email: str, limit: int = 100) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="workspace.read",
        )
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return {"messages": chat_service.list_messages(workspace_id=workspace_id, channel_id=channel_id, limit=limit)}
