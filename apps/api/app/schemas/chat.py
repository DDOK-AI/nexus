from datetime import datetime

from pydantic import BaseModel


class ChannelCreateRequest(BaseModel):
    workspace_id: int
    actor_email: str
    name: str
    description: str = ""


class ChannelResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime


class MessageCreateRequest(BaseModel):
    workspace_id: int
    sender: str
    content: str


class MessageResponse(BaseModel):
    id: int
    channel_id: int
    sender: str
    content: str
    created_at: datetime
