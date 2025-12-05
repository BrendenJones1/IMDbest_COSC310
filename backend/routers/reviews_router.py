from fastapi import APIRouter, Query, Path, HTTPException, Response, status
from typing import Literal, Optional
from pydantic import BaseModel

from backend.services.review_service import ReviewService
from backend.schemas.review import ReviewCreate, ReviewOut

router = APIRouter(prefix="/reviews", tags=["reviews"])
service = ReviewService()


class UpvotePayload(BaseModel):
    voter_id: str


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


@router.get("/{movie_id}/{user_id}", response_model=ReviewOut)
def get_user_review(
    movie_id: str = Path(..., description="Slug id of the movie (e.g., 'the-dark-knight')"),
    user_id: str = Path(..., description="User id who authored the review"),
):
    """
    Return a single user's review for the given movie, or 404 if missing.
    """
    item = service.get_user_review(user_id, movie_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="review not found")
    return item


@router.post("/{movie_id}/{user_id}", response_model=ReviewOut)
def upsert_review(
    movie_id: str = Path(..., description="Slug id of the movie (e.g., 'the-dark-knight')"),
    user_id: str = Path(..., description="User id who authored the review"),
    payload: ReviewCreate = ...,
    response: Response = None,
):
    """
    Create or update a review for a movie by a given user.
    Returns 201 Created if a new review is created, 200 OK if updated.
    """
    existed_before: Optional[ReviewOut] = service.get_user_review(user_id, movie_id)
    item = service.upsert_review(user_id, movie_id, payload)
    if existed_before is None and response is not None:
        response.status_code = status.HTTP_201_CREATED
    return item


@router.delete("/{movie_id}/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    movie_id: str = Path(..., description="Slug id of the movie (e.g., 'the-dark-knight')"),
    user_id: str = Path(..., description="User id who authored the review"),
):
    """
    Delete a user's review for a movie. Returns 204 even if the review did not exist.
    """
    service.delete_user_review(user_id, movie_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{movie_id}/{user_id}/upvote", response_model=ReviewOut)
def upvote_review(
    movie_id: str = Path(..., description="Slug id of the movie (e.g., 'the-dark-knight')"),
    user_id: str = Path(..., description="User id who authored the review"),
    payload: UpvotePayload = ...,
):
    """
    Upvote a review by user_id for the given movie. voter_id cannot match user_id.
    """
    return service.upvote_review(movie_id, user_id, payload.voter_id)


@router.post("/{movie_id}/{user_id}/downvote", response_model=ReviewOut)
def downvote_review(
    movie_id: str = Path(..., description="Slug id of the movie (e.g., 'the-dark-knight')"),
    user_id: str = Path(..., description="User id who authored the review"),
    payload: UpvotePayload = ...,
):
    """
    Downvote a review by user_id for the given movie. voter_id cannot match user_id.
    """
    return service.downvote_review(movie_id, user_id, payload.voter_id)
