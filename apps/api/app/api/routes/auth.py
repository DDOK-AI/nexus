from fastapi import APIRouter, HTTPException

from app.schemas.auth import GoogleCallbackRequest, GoogleConnectRequest, GoogleConnectResponse, OAuthAccount
from app.services.oauth_service import oauth_service
from app.services.workspace_service import workspace_service

router = APIRouter(prefix="/oauth/google", tags=["oauth"])


@router.post("/connect", response_model=GoogleConnectResponse)
def connect_google(payload: GoogleConnectRequest) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=payload.workspace_id,
            actor_email=payload.user_email,
            permission="workspace.read",
        )
        return oauth_service.connect_url(workspace_id=payload.workspace_id, user_email=payload.user_email)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/callback", response_model=OAuthAccount)
def callback_google(payload: GoogleCallbackRequest) -> dict:
    try:
        return oauth_service.callback(code=payload.code, state=payload.state)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/account/{user_email}", response_model=OAuthAccount)
def account(user_email: str) -> dict:
    try:
        result = oauth_service.account(user_email)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not result:
        return {
            "provider": "google",
            "user_email": user_email,
            "scope": "",
            "connected": False,
            "token_type": "",
            "expires_at": "",
        }
    return result
