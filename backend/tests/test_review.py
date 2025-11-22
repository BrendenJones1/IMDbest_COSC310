import json
import pytest

from repositories import movie_repo as movie_repo_module
from repositories.movie_repo import MovieRepository
from repositories.reviews_repo import ReviewRepository
from schemas.review import ReviewCreate
from services.review_service import ReviewService
from contextlib import contextmanager


@pytest.fixture()
def movies_dir(tmp_path, monkeypatch):
    """
    Provide an isolated movies directory and point the repository to it for each test.
    """
    base = tmp_path / "movies"
    base.mkdir()
    monkeypatch.setattr(movie_repo_module, "MOVIES_DIR", base, raising=False)
    # Classes in movie_repo use the module-level MOVIES_DIR constant directly
    monkeypatch.setattr("repositories.movie_repo.MOVIES_DIR", base, raising=False)
    return base


def create_movie_directory(movies_dir, title="Sample Movie"):
    """
    Create a minimal on-disk movie folder with metadata and return its slug id.
    """
    movie_dir = movies_dir / title
    movie_dir.mkdir()
    (movie_dir / "metadata.json").write_text(json.dumps({"title": title}), encoding="utf-8")
    return MovieRepository._slug(title)


def test_upsert_review_tracks_average_and_totals(movies_dir):
    """
    upsert_review should keep rating count, total, and average in sync as reviews change.
    """
    movie_id = create_movie_directory(movies_dir, "Thor Ragnarok")
    service = ReviewService()

    # First review initializes metadata aggregates
    first = service.upsert_review("user-1", movie_id, ReviewCreate(rating=4.5, review_text="Great"))
    assert first.rating == 4.5

    metadata = MovieRepository.get_movie_metadata(movie_id)
    assert metadata["userRatingCount"] == 1
    assert metadata["userRatingTotal"] == pytest.approx(4.5)
    assert metadata["userRatingAverage"] == pytest.approx(4.5)

    # Second distinct user review increases count and adjusts average
    service.upsert_review("user-2", movie_id, ReviewCreate(rating=2.0))
    metadata = MovieRepository.get_movie_metadata(movie_id)
    assert metadata["userRatingCount"] == 2
    assert metadata["userRatingTotal"] == pytest.approx(6.5)
    assert metadata["userRatingAverage"] == pytest.approx(3.25)

    # Updating an existing user's review should not change count, only totals/average
    service.upsert_review("user-1", movie_id, ReviewCreate(rating=5.0))
    metadata = MovieRepository.get_movie_metadata(movie_id)
    assert metadata["userRatingCount"] == 2
    assert metadata["userRatingTotal"] == pytest.approx(7.0)
    assert metadata["userRatingAverage"] == pytest.approx(3.5)


def test_delete_review_updates_metadata(movies_dir):
    """
    Deleting a review should update rating aggregates and remove the review entry.
    """
    movie_id = create_movie_directory(movies_dir, "The Dark Knight")
    service = ReviewService()

    service.upsert_review("user-1", movie_id, ReviewCreate(rating=5.0))
    service.upsert_review("user-2", movie_id, ReviewCreate(rating=3.0))

    service.delete_user_review("user-1", movie_id)

    metadata = MovieRepository.get_movie_metadata(movie_id)
    assert metadata["userRatingCount"] == 1
    assert metadata["userRatingTotal"] == pytest.approx(3.0)
    assert metadata["userRatingAverage"] == pytest.approx(3.0)

    reviews = ReviewRepository.get_review_data(movie_id)["reviews"]
    assert "user-1" not in reviews
    assert reviews["user-2"]["rating"] == 3.0


def test_delete_last_review_recalculates_to_zero(movies_dir):
    movie_id = create_movie_directory(movies_dir, "Boundary Delete Last")
    service = ReviewService()

    # Add the sole review
    service.upsert_review("solo-user", movie_id, ReviewCreate(rating=4.0))
    metadata = MovieRepository.get_movie_metadata(movie_id)
    assert metadata["userRatingCount"] == 1
    assert metadata["userRatingTotal"] == pytest.approx(4.0)
    assert metadata["userRatingAverage"] == pytest.approx(4.0)

    # Delete the sole review; should not divide by zero
    service.delete_user_review("solo-user", movie_id)
    metadata = MovieRepository.get_movie_metadata(movie_id)
    assert metadata["userRatingCount"] == 0
    assert metadata["userRatingTotal"] == pytest.approx(0.0)
    assert metadata["userRatingAverage"] == pytest.approx(0.0)

    # Ensure reviews map is empty
    reviews = ReviewRepository.get_review_data(movie_id)["reviews"]
    assert "solo-user" not in reviews
    assert len(reviews) == 0


def test_get_reviews_by_user_id_skips_faulty_movie(monkeypatch, movies_dir):
    # Set up two movies: one valid, one that will trigger a JSON error via monkeypatch
    good_title = "Good Movie"
    bad_title = "Bad Movie"
    good_movie_id = create_movie_directory(movies_dir, good_title)
    bad_movie_id = create_movie_directory(movies_dir, bad_title)

    # Write a valid review for the good movie
    good_reviews_path = (movies_dir / good_title) / "user_reviews.json"
    good_reviews_path.write_text(
        json.dumps({
            "reviews": {
                "u1": {
                    "user_id": "u1",
                    "rating": 8,
                    "review_text": "solid",
                    "upvotes": 2,
                    "downvotes": 0,
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00",
                }
            }
        }),
        encoding="utf-8"
    )

    # Monkeypatch ReviewRepository.get_review_data to raise for the bad movie only
    original_get = ReviewRepository.get_review_data

    def faulty_get_review_data(movie_id: str):
        if movie_id == bad_movie_id:
            # Raise a JSONDecodeError to simulate a corrupt file
            raise json.JSONDecodeError("mock decode error", "X", 0)
        return original_get(movie_id)

    # Patch both possible module paths to be safe
    monkeypatch.setattr("services.review_service.ReviewRepository", ReviewRepository, raising=False)
    monkeypatch.setattr("services.review_service.ReviewRepository.get_review_data", faulty_get_review_data, raising=False)
    try:
        monkeypatch.setattr("backend.services.review_service.ReviewRepository", ReviewRepository, raising=False)
        monkeypatch.setattr("backend.services.review_service.ReviewRepository.get_review_data", faulty_get_review_data, raising=False)
    except Exception:
        # backend.* may not be imported under some test runs; ignore
        pass

    service = ReviewService()
    reviews, movies = service.get_reviews_by_user_id("u1")

    # Should skip the bad movie and still return the good one
    assert len(reviews) == 1
    assert movies == [good_movie_id]

