from fastapi import APIRouter, Query, Path
from typing import Literal

from backend.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])
service = ReviewService()


@router.get("/{movie_id}")
def list_reviews(
    movie_id: str = Path(..., description="Slug id of the movie (e.g., 'the-dark-knight')"),
    sort: Literal["recent", "upvotes"] = Query("recent", description="Sort by 'recent' or 'upvotes'"),
):
    items = service.list_reviews(movie_id, sort=sort)
    # pydantic models are jsonable; FastAPI will handle serialization
    return {"items": items, "total": len(items)}

