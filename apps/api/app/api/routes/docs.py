from typing import Optional

from fastapi import APIRouter, HTTPException

from app.schemas.docs import DocCreateRequest, DocUpdateRequest
from app.services.docs_service import docs_service
from app.services.workspace_service import workspace_service

router = APIRouter(prefix="/docs", tags=["docs"])


@router.post("")
def create_doc(payload: DocCreateRequest) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            permission="docs.write",
        )
        return docs_service.create(
            workspace_id=payload.workspace_id,
            created_by=payload.actor_email,
            space=payload.space,
            title=payload.title,
            content=payload.content,
            tags=payload.tags,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("")
def list_docs(workspace_id: int, actor_email: str, space: Optional[str] = None, limit: int = 100) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="workspace.read",
        )
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return {"docs": docs_service.list(workspace_id=workspace_id, space=space, limit=limit)}


@router.get("/search/query")
def search_docs(workspace_id: int, actor_email: str, q: str, limit: int = 50) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="workspace.read",
        )
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return {"docs": docs_service.search(workspace_id=workspace_id, query=q, limit=limit)}


@router.get("/{doc_id}")
def get_doc(doc_id: int, workspace_id: int, actor_email: str) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="workspace.read",
        )
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    doc = docs_service.get(workspace_id, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.patch("/{doc_id}")
def update_doc(doc_id: int, payload: DocUpdateRequest) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=payload.workspace_id,
            actor_email=payload.actor_email,
            permission="docs.write",
        )
        doc = docs_service.update(
            payload.workspace_id,
            doc_id,
            title=payload.title,
            content=payload.content,
            tags=payload.tags,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{doc_id}")
def delete_doc(doc_id: int, workspace_id: int, actor_email: str) -> dict:
    try:
        workspace_service.require_permission(
            workspace_id=workspace_id,
            actor_email=actor_email,
            permission="docs.write",
        )
        deleted = docs_service.delete(workspace_id, doc_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": True}
