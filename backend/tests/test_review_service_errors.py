import pytest
from fastapi import HTTPException

from backend.services.review_service import ReviewService
from backend.schemas.review import ReviewCreate


def test_upsert_review_nonexistent_movie_raises_404():
    service = ReviewService()
    with pytest.raises(HTTPException) as exc:
        service.upsert_review(
            user_id="u1",
            movie_id="this-movie-does-not-exist",
            review=ReviewCreate(rating=5, review_text="test"),
        )
    assert exc.value.status_code == 404
    assert exc.value.detail == "movie not found"


def test_delete_review_nonexistent_movie_is_404():
    service = ReviewService()
    with pytest.raises(HTTPException) as exc:
        service.delete_user_review(user_id="u1", movie_id="missing-movie")
    assert exc.value.status_code == 404
    assert exc.value.detail == "movie not found"


def test_get_review_nonexistent_movie_is_404():
    service = ReviewService()
    with pytest.raises(HTTPException) as exc:
        service.get_user_review(user_id="u1", movie_id="another-missing")
    assert exc.value.status_code == 404
    assert exc.value.detail == "movie not found"
