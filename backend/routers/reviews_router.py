from fastapi import APIRouter, Query, Path
from typing import Literal

from backend.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])
service = ReviewService()


@router.get("/{movie_id}")
def list_reviews(
    movie_id: str = Path(..., description="Slug id of the movie (e.g., 'the-dark-knight')"),
    sort: Literal["recent", "upvotes"] = Query("upvotes", description="Sort by 'recent' or 'upvotes'"),
    limit: int = Query(3, ge=1, le=100, description="Max reviews to return"),
    offset: int = Query(0, ge=0, description="Number of reviews to skip"),
):
    all_items = service.list_reviews(movie_id, sort=sort)
    total = len(all_items)
    items = all_items[offset:offset + limit]
    return {"items": items, "total": total, "limit": limit, "offset": offset}

