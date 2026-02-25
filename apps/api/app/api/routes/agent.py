from fastapi import APIRouter, HTTPException

from app.schemas.agent import AgentCommandRequest, AgentCommandResponse
from app.services.deepagents_runtime import orchestrator

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/execute", response_model=AgentCommandResponse)
def execute(payload: AgentCommandRequest) -> dict:
    try:
        return orchestrator.execute(
            user_email=payload.user_email,
            instruction=payload.instruction,
            context=payload.context,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
