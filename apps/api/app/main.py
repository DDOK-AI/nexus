from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.roadmap import router as roadmap_router
from app.core.settings import settings

app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(roadmap_router)


@app.get("/")
def root() -> dict:
    return {
        "service": settings.app_name,
        "message": "GWS DeepAgent Workspace bootstrap API",
    }
