# backend/routers/search.py

from fastapi import APIRouter, Query
from backend.services.search_service import search, SortField, SortOrder

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def do_search(
    q: str = Query(""),
    limit: int = Query(20, ge=1, le=50),
    sort_by: SortField = SortField.TITLE,
    sort_order: SortOrder = SortOrder.ASC,
):
    items = search(q, limit=limit, sort_by=sort_by, sort_order=sort_order)
    return {"items": items, "total": len(items)}
