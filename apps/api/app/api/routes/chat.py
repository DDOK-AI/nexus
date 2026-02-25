from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChannelCreateRequest, MessageCreateRequest
from app.services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/channels")
def create_channel(payload: ChannelCreateRequest) -> dict:
    try:
        return chat_service.create_channel(name=payload.name, description=payload.description)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"채널 생성 실패: {exc}") from exc


@router.get("/channels")
def list_channels() -> dict:
    return {"channels": chat_service.list_channels()}


@router.post("/channels/{channel_id}/messages")
def post_message(channel_id: int, payload: MessageCreateRequest) -> dict:
    channel = chat_service.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="채널을 찾을 수 없습니다.")

    return chat_service.post_message(channel_id=channel_id, sender=payload.sender, content=payload.content)


@router.get("/channels/{channel_id}/messages")
def list_messages(channel_id: int, limit: int = 100) -> dict:
    channel = chat_service.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="채널을 찾을 수 없습니다.")

    return {"messages": chat_service.list_messages(channel_id=channel_id, limit=limit)}
