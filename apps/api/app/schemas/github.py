from pydantic import BaseModel, Field


class GithubWebhookEvent(BaseModel):
    event_type: str
    repository: str = ""
    actor: str = ""
    payload: dict = Field(default_factory=dict)
