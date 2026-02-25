from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request

from app.services.github_service import github_service

router = APIRouter(prefix="/github", tags=["github"])


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
def list_events(limit: int = 100) -> dict:
    return {"events": github_service.list_events(limit=limit)}
