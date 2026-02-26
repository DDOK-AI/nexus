from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DocCreateRequest(BaseModel):
    workspace_id: int
    actor_email: str
    space: str = "general"
    title: str
    content: str
    tags: list[str] = Field(default_factory=list)


class DocUpdateRequest(BaseModel):
    workspace_id: int
    actor_email: str
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list[str]] = None


class DocResponse(BaseModel):
    id: int
    workspace_id: int
    space: str
    title: str
    content: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime
