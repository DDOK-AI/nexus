from pydantic import BaseModel, Field


class WorkspaceCreateRequest(BaseModel):
    actor_email: str
    name: str


class MemberAddRequest(BaseModel):
    actor_email: str
    target_email: str
    role: str = Field(description="owner|admin|member|viewer")


class MemberRoleUpdateRequest(BaseModel):
    actor_email: str
    role: str = Field(description="owner|admin|member|viewer")


class WorkspaceActionRequest(BaseModel):
    workspace_id: int
    actor_email: str
    user_email: str = ""
    service: str = Field(description="calendar|tasks|drive|docs|sheets|slides|meet")
    action: str = Field(description="create|list|update|delete|search")
    payload: dict = Field(default_factory=dict)


class WorkspaceActionResult(BaseModel):
    ok: bool
    service: str
    action: str
    result: dict
