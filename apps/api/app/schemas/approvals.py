from pydantic import BaseModel


class ApprovalCreateRequest(BaseModel):
    workspace_id: int
    actor_email: str
    request_type: str
    reason: str
    payload: dict


class ApprovalDecisionRequest(BaseModel):
    workspace_id: int
    actor_email: str
    note: str = ""
