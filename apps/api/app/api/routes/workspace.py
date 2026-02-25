from fastapi import APIRouter, HTTPException

from app.schemas.workspace import WorkspaceActionRequest, WorkspaceActionResult
from app.services.workspace_service import workspace_service

router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.get("/services")
def services() -> dict:
    return {"services": workspace_service.supported_services}


@router.post("/execute", response_model=WorkspaceActionResult)
def execute_action(payload: WorkspaceActionRequest) -> dict:
    try:
        result = workspace_service.execute(
            user_email=payload.user_email,
            service=payload.service,
            action=payload.action,
            payload=payload.payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "ok": True,
        "service": payload.service,
        "action": payload.action,
        "result": result,
    }
