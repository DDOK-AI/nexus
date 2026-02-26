from pydantic import BaseModel, Field


class GithubWebhookEvent(BaseModel):
    event_type: str
    repository: str = ""
    actor: str = ""
    payload: dict = Field(default_factory=dict)


class GithubInstallUrlRequest(BaseModel):
    workspace_id: int
    actor_email: str


class GithubInstallCallbackRequest(BaseModel):
    state: str
    installation_id: int
    account_login: str = ""


class GithubRepoLinkRequest(BaseModel):
    workspace_id: int
    actor_email: str
    installation_id: int
    repo_full_name: str
