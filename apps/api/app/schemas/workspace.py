from pydantic import BaseModel, Field


class WorkspaceActionRequest(BaseModel):
    user_email: str
    service: str = Field(description="calendar|tasks|drive|docs|sheets|slides|meet")
    action: str = Field(description="create|list|update|delete|search")
    payload: dict = Field(default_factory=dict)


class WorkspaceActionResult(BaseModel):
    ok: bool
    service: str
    action: str
    result: dict
