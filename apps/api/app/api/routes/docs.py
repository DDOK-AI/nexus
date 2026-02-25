from fastapi import APIRouter, HTTPException
from typing import Optional

from app.schemas.docs import DocCreateRequest, DocUpdateRequest
from app.services.docs_service import docs_service

router = APIRouter(prefix="/docs", tags=["docs"])


@router.post("")
def create_doc(payload: DocCreateRequest) -> dict:
    return docs_service.create(space=payload.space, title=payload.title, content=payload.content, tags=payload.tags)


@router.get("")
def list_docs(space: Optional[str] = None, limit: int = 100) -> dict:
    return {"docs": docs_service.list(space=space, limit=limit)}


@router.get("/search/query")
def search_docs(q: str, limit: int = 50) -> dict:
    return {"docs": docs_service.search(query=q, limit=limit)}


@router.get("/{doc_id}")
def get_doc(doc_id: int) -> dict:
    doc = docs_service.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.patch("/{doc_id}")
def update_doc(doc_id: int, payload: DocUpdateRequest) -> dict:
    doc = docs_service.update(doc_id, title=payload.title, content=payload.content, tags=payload.tags)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{doc_id}")
def delete_doc(doc_id: int) -> dict:
    deleted = docs_service.delete(doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": True}
