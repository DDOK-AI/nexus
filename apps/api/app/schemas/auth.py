from pydantic import BaseModel


class GoogleConnectResponse(BaseModel):
    provider: str = "google"
    auth_url: str
    state: str


class GoogleConnectRequest(BaseModel):
    workspace_id: int
    user_email: str


class GoogleCallbackRequest(BaseModel):
    code: str
    state: str


class OAuthAccount(BaseModel):
    provider: str
    user_email: str
    scope: str
    connected: bool
    token_type: str = "Bearer"
    expires_at: str = ""
