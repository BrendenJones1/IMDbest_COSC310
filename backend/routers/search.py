# backend/routers/search.py

from fastapi import APIRouter, Query
from backend.services.search_service import search 

router = APIRouter(prefix="/search", tags=["search"])

@router.get("")
def do_search(q: str = Query(""), limit: int = 20):
    items = search(q, limit)
    return {"items": items, "total": len(items)}
