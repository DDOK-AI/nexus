from fastapi import APIRouter

from app.schemas.auth import GoogleCallbackRequest, GoogleConnectResponse, OAuthAccount
from app.services.oauth_service import oauth_service

router = APIRouter(prefix="/oauth/google", tags=["oauth"])


@router.get("/connect", response_model=GoogleConnectResponse)
def connect_google() -> dict:
    return oauth_service.connect_url()


@router.post("/callback", response_model=OAuthAccount)
def callback_google(payload: GoogleCallbackRequest) -> dict:
    return oauth_service.callback(code=payload.code, user_email=payload.user_email)


@router.get("/account/{user_email}", response_model=OAuthAccount)
def account(user_email: str) -> dict:
    result = oauth_service.account(user_email)
    if not result:
        return {
            "provider": "google",
            "user_email": user_email,
            "scope": "",
            "connected": False,
        }
    return result
