from fastapi import APIRouter, Depends, HTTPException, status

from backend.schemas.review import ReviewCreate, ReviewOut, ReviewUpdate
from backend.services.review_service import ReviewService
from backend.utils.security import decode_access_token

router = APIRouter(prefix="/reviews", tags=["reviews"])
service = ReviewService()


@router.post("/{movie_id}", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def add_or_update_review(
    movie_id: str,
    payload: ReviewCreate,
    current_user: dict = Depends(decode_access_token),
) -> ReviewOut:
    return service.upsert_review(current_user["sub"], movie_id, payload)


@router.get("/{movie_id}", response_model=ReviewOut | None)
def get_my_review(
    movie_id: str, current_user: dict = Depends(decode_access_token)
) -> ReviewOut | None:
    return service.get_user_review(current_user["sub"], movie_id)


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_review(
    movie_id: str, current_user: dict = Depends(decode_access_token)
) -> None:
    service.delete_user_review(current_user["sub"], movie_id)
    return None
