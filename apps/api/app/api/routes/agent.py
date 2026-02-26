import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.agent import AgentCommandRequest, AgentCommandResponse, AgentStreamRequest
from app.services.approval_service import approval_service
from app.services.deepagents_runtime import orchestrator
from app.services.execution_log_service import execution_log_service
from app.services.workspace_service import workspace_service

router = APIRouter(prefix="/agent", tags=["agent"])


def _run_agent(payload: AgentCommandRequest) -> dict:
    log_id = execution_log_service.create_pending(
        workspace_id=payload.workspace_id,
        user_email=payload.user_email,
        instruction=payload.instruction,
        context=payload.context,
    )
    try:
        result = orchestrator.execute(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            user_email=payload.user_email,
            instruction=payload.instruction,
            context=payload.context,
        )
        execution_log_service.complete(log_id=log_id, steps=result["steps"], outputs=result["outputs"])
        result["execution_log_id"] = log_id
        return result
    except Exception as exc:
        execution_log_service.fail(log_id=log_id, error_message=str(exc))
        raise


@router.post("/execute", response_model=AgentCommandResponse)
def execute(payload: AgentCommandRequest) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            permission="agent.execute",
        )

        request_type = "agent_execute"
        if payload.approval_request_id <= 0:
            approval = approval_service.create_request(
                workspace_id=payload.workspace_id,
                request_type=request_type,
                payload={
                    "instruction": payload.instruction,
                    "context": payload.context,
                    "user_email": payload.user_email,
                },
                requested_by=payload.actor_email,
                reason="에이전트 실행은 승인 후 진행됩니다.",
            )
            return {
                "summary": "approval_required",
                "steps": [{"module": "approval", "action": "create", "ok": True}],
                "outputs": {
                    "approval_required": True,
                    "approval_request": approval,
                    "next": "POST /agent/execute with approval_request_id",
                },
            }

        approval = approval_service.ensure_approved(
            request_id=payload.approval_request_id,
            workspace_id=payload.workspace_id,
            request_type=request_type,
        )
        approved_payload = approval.get("payload", {})
        if approved_payload.get("instruction") != payload.instruction:
            raise ValueError("승인된 instruction과 실행 instruction이 다릅니다.")

        return _run_agent(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/execute/stream")
def execute_stream(payload: AgentStreamRequest) -> StreamingResponse:
    try:
        workspace_service.require_permission(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            permission="agent.execute",
        )

        approval_service.ensure_approved(
            request_id=(payload.approval_request_id if payload.approval_request_id > 0 else None),
            workspace_id=payload.workspace_id,
            request_type="agent_execute",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    def event_gen():
        log_id = execution_log_service.create_pending(
            workspace_id=payload.workspace_id,
            user_email=payload.user_email,
            instruction=payload.instruction,
            context=payload.context,
        )
        try:
            yield f"event: log\ndata: {json.dumps({'log_id': log_id}, ensure_ascii=False)}\n\n"
            final_data = None
            for event in orchestrator.stream(
                workspace_id=payload.workspace_id,
                actor_email=payload.actor_email,
                user_email=payload.user_email,
                instruction=payload.instruction,
                context=payload.context,
            ):
                if event.get("event") == "final":
                    final_data = event["data"]
                    final_data["execution_log_id"] = log_id
                yield f"event: {event['event']}\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n"

            if final_data:
                execution_log_service.complete(log_id=log_id, steps=final_data.get("steps", []), outputs=final_data.get("outputs", {}))
        except Exception as exc:
            execution_log_service.fail(log_id=log_id, error_message=str(exc))
            yield f"event: error\ndata: {json.dumps({'message': str(exc)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@router.get("/logs")
def list_logs(workspace_id: int, actor_email: str, limit: int = 100) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="workspace.read",
        )
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return {"logs": execution_log_service.list_logs(workspace_id=workspace_id, limit=limit)}
