import pytest
from typing import List
from backend.services.review_service import ReviewService
from backend.services.users_service import user_service as users_service
from backend.schemas.review import ReviewOut
from contextlib import contextmanager


@pytest.fixture
def mock_repos(monkeypatch):
    """
    Mock MovieRepository and ReviewRepository so reviews can be resolved without disk I/O.
    """
    movies = [
        {"id": "thor-ragnarok", "title": "Thor Ragnarok"},
        {"id": "inception", "title": "Inception"},
    ]

    review_data = {
        "thor-ragnarok": {
            "reviews": {
                "u1": {
                    "user_id": "u1",
                    "rating": 9,
                    "review_text": "Great!",
                    "upvotes": 5,
                    "downvotes": 0,
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00",
                },
                "u2": {
                    "user_id": "u2",
                    "rating": 7,
                    "review_text": "Cool",
                    "upvotes": 3,
                    "downvotes": 1,
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00",
                },
            }
        },
        "inception": {
            "reviews": {
                "u1": {
                    "user_id": "u1",
                    "rating": 10,
                    "review_text": "Masterpiece",
                    "upvotes": 10,
                    "downvotes": 0,
                    "created_at": "2025-01-02T00:00:00",
                    "updated_at": "2025-01-02T00:00:00",
                }
            }
        },
    }

    class FakeMovieRepo:
        @staticmethod
        def list_movies():
            return movies

    class FakeReviewRepo:
        @staticmethod
        def get_review_data(movie_id):
            return review_data.get(movie_id, {"reviews": {}})

    monkeypatch.setattr("backend.services.review_service.MovieRepository", FakeMovieRepo)
    monkeypatch.setattr("backend.services.review_service.ReviewRepository", FakeReviewRepo)

    return {"movies": movies, "review_data": review_data}


def test_get_reviews_by_user_id_returns_only_user_reviews(mock_repos):
    """
    get_reviews_by_user_id should return only the target user's reviews and their movie ids.
    """
    service = ReviewService()
    reviews, movies = service.get_reviews_by_user_id("u1")

    assert isinstance(reviews, list)
    assert len(reviews) == 2  # 2 movies reviewed by u1
    assert len(movies) == 2
    assert all(isinstance(r, ReviewOut) for r in reviews)
    assert movies == ["thor-ragnarok", "inception"]


def test_get_reviews_by_user_id_handles_no_reviews(mock_repos):
    """
    get_reviews_by_user_id should return empty lists when the user has no reviews.
    """
    service = ReviewService()
    reviews, movies = service.get_reviews_by_user_id("nonexistent")
    assert reviews == []
    assert movies == []


def test_users_service_get_user_reviews(monkeypatch, mock_repos):
    """
    users_service.get_user_reviews should delegate to review_service and return its list.
    """
    fake_reviews = [
        ReviewOut(
            user_id="u1",
            rating=5,
            review_text="ok",
            upvotes=0,
            downvotes=0,
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )
    ]

    def fake_get_reviews(user_id: str):
        return fake_reviews, []

    monkeypatch.setattr(
        users_service.review_service,
        "get_reviews_by_user_id",
        fake_get_reviews,
    )

    reviews = users_service.get_user_reviews("u1")
    assert reviews == fake_reviews


def test_sync_user_reviews(monkeypatch):
    """
    sync_user_reviews should overwrite the user's stored reviews with current ReviewService data.
    """
    fake_movies: list[str] = []
    fake_reviews = [
        ReviewOut(
            user_id="u1",
            rating=8,
            review_text="good",
            upvotes=0,
            downvotes=0,
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )
    ]

    def fake_get_reviews(user_id: str):
        return fake_reviews, fake_movies

    users = [
        {"id": "u1", "username": "Bob", "reviews": []},
        {"id": "u2", "username": "Sue", "reviews": []},
    ]

    saved: dict = {}

    def fake_load_users():
        return users.copy()

    def fake_save_users(u):
        saved["data"] = u  # capture the saved snapshot for inspection

    monkeypatch.setattr(
        users_service.review_service,
        "get_reviews_by_user_id",
        fake_get_reviews,
    )
    monkeypatch.setattr(users_service.user_repo, "load_users", fake_load_users)
    monkeypatch.setattr(users_service.user_repo, "save_users", fake_save_users)

    users_service.sync_user_reviews("u1")

    updated = saved["data"][0]
    assert updated["id"] == "u1"
    assert updated["reviews"] == [r.model_dump() for r in fake_reviews]

