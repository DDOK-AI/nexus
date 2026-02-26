from fastapi import FastAPI

from app.api.routes.agent import router as agent_router
from app.api.routes.approvals import router as approvals_router
from app.api.routes.auth import router as auth_router
from app.api.routes.billing import router as billing_router
from app.api.routes.chat import router as chat_router
from app.api.routes.docs import router as docs_router
from app.api.routes.github import router as github_router
from app.api.routes.health import router as health_router
from app.api.routes.reports import router as reports_router
from app.api.routes.roadmap import router as roadmap_router
from app.api.routes.workspace import router as workspace_router
from app.core.settings import settings

app = FastAPI(title=settings.app_name)

app.include_router(health_router)
app.include_router(roadmap_router)
app.include_router(workspace_router)
app.include_router(auth_router)
app.include_router(github_router)
app.include_router(reports_router)
app.include_router(docs_router)
app.include_router(chat_router)
app.include_router(billing_router)
app.include_router(approvals_router)
app.include_router(agent_router)


@app.get("/")
def root() -> dict:
    return {
        "service": settings.app_name,
        "message": "GWS DeepAgent Workspace API (P0)",
        "docs": "/docs",
    }
