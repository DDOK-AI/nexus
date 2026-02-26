from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Query, Request

from app.schemas.github import GithubInstallCallbackRequest, GithubInstallUrlRequest, GithubRepoLinkRequest
from app.services.github_integration_service import github_integration_service
from app.services.github_service import github_service
from app.services.workspace_service import workspace_service

router = APIRouter(prefix="/github", tags=["github"])


@router.post("/app/install-url")
def app_install_url(payload: GithubInstallUrlRequest) -> dict:
    try:
        return github_integration_service.install_url(workspace_id=payload.workspace_id, actor_email=payload.actor_email)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/app/callback")
def app_callback(payload: GithubInstallCallbackRequest) -> dict:
    try:
        return github_integration_service.callback(
            state=payload.state,
            installation_id=payload.installation_id,
            account_login=payload.account_login,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/app/callback")
def app_callback_from_redirect(
    state: str = Query(default=""),
    installation_id: int = Query(default=0),
    setup_action: str = Query(default=""),
) -> dict:
    if not state or not installation_id:
        raise HTTPException(status_code=400, detail="state, installation_id가 필요합니다.")

    try:
        result = github_integration_service.callback(
            state=state,
            installation_id=installation_id,
            account_login="",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "ok": True,
        "setup_action": setup_action,
        "installation": result,
    }


@router.get("/app/installations")
def list_installations(workspace_id: int, actor_email: str) -> dict:
    try:
        data = github_integration_service.list_installations(workspace_id=workspace_id, actor_email=actor_email)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"installations": data}


@router.get("/app/installations/{installation_id}/repos")
def list_installation_repos(workspace_id: int, actor_email: str, installation_id: int) -> dict:
    try:
        data = github_integration_service.list_installation_repos(
            workspace_id=workspace_id,
            actor_email=actor_email,
            installation_id=installation_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return data


@router.post("/repos/link")
def link_repo(payload: GithubRepoLinkRequest) -> dict:
    try:
        return github_integration_service.link_repo(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            installation_id=payload.installation_id,
            repo_full_name=payload.repo_full_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/repos")
def list_linked_repos(workspace_id: int, actor_email: str) -> dict:
    try:
        repos = github_integration_service.list_linked_repos(workspace_id=workspace_id, actor_email=actor_email)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"repos": repos}


@router.post("/webhook")
async def webhook(
    request: Request,
    x_github_event: str = Header(default="unknown"),
    x_hub_signature_256: Optional[str] = Header(default=None),
) -> dict:
    body = await request.body()

    if not github_service.verify_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid GitHub signature")

    payload = json.loads(body.decode("utf-8") or "{}")
    return github_service.ingest_event(event_type=x_github_event, payload=payload)


@router.get("/events")
def list_events(workspace_id: int, actor_email: str, limit: int = 100) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="workspace.read",
        )
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return {"events": github_service.list_events(workspace_id=workspace_id, limit=limit)}
