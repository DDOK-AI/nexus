from pydantic import BaseModel, Field


class AgentCommandRequest(BaseModel):
    workspace_id: int
    actor_email: str
    user_email: str
    instruction: str
    context: dict = Field(default_factory=dict)
    approval_request_id: int = 0


class AgentCommandResponse(BaseModel):
    summary: str
    steps: list[dict]
    outputs: dict
    execution_log_id: int = 0


class AgentStreamRequest(BaseModel):
    workspace_id: int
    actor_email: str
    user_email: str
    instruction: str
    context: dict = Field(default_factory=dict)
    approval_request_id: int = 0
