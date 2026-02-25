from fastapi import APIRouter

from app.services.deepagents_runtime import runtime_status

router = APIRouter(prefix="/platform", tags=["platform"])


@router.get("/status")
def platform_status() -> dict:
    return runtime_status()


@router.get("/modules")
def modules() -> dict:
    return {
        "modules": [
            "oauth-google",
            "workspace-connectors",
            "github-webhook-journal",
            "reporting-engine",
            "docs-base",
            "team-chat",
            "billing-barobill-adapter",
            "deepagent-orchestrator",
        ]
    }
