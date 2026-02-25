from pydantic import BaseModel, Field


class AgentCommandRequest(BaseModel):
    user_email: str
    instruction: str
    context: dict = Field(default_factory=dict)


class AgentCommandResponse(BaseModel):
    summary: str
    steps: list[dict]
    outputs: dict
