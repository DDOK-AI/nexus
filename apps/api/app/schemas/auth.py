from pydantic import BaseModel


class GoogleConnectResponse(BaseModel):
    provider: str = "google"
    auth_url: str
    state: str


class GoogleCallbackRequest(BaseModel):
    code: str
    state: str
    user_email: str


class OAuthAccount(BaseModel):
    provider: str
    user_email: str
    scope: str
    connected: bool
