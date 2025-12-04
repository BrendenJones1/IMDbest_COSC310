# backend/tests/test_reviews_concurrency.py

from concurrent.futures import ThreadPoolExecutor

import pytest

from backend.schemas.review import ReviewCreate
from backend.services.review_service import ReviewService
import repositories.movie_repo as movie_repo
from repositories.movie_repo import MovieRepository, ReviewRepository

@pytest.fixture
def review_service_tmp(tmp_path, monkeypatch):
    """
    Fresh ReviewService backed by a temp movies directory.
    Creates a single movie 'movie-1' that _ensure_movie_exists will find.
    """
    movies_dir = tmp_path / "movies"
    monkeypatch.setattr(movie_repo, "MOVIES_DIR", movies_dir)
    movies_dir.mkdir(parents=True, exist_ok=True)

    # Make a directory for movie-1 so _ensure_movie_exists passes
    movie_dir = movies_dir / "movie-1"
    movie_dir.mkdir(parents=True, exist_ok=True)

    # No metadata / review files yet; they'll be created on first write
    return ReviewService()
def test_concurrent_read_only_reviews(review_service_tmp):
    """
    P1: Multiple readers, no writers.

    Seed a few reviews, then hammer get_user_review and get_reviews_by_user_id
    from multiple threads. Expect:
      - no exceptions
      - consistent data from all readers
    """
    svc = review_service_tmp
    movie_id = "movie-1"

    # Seed reviews sequentially
    user_ids = [f"user{i}" for i in range(5)]
    base_rating = 4
    for uid in user_ids:
        svc.upsert_review(
            user_id=uid,
            movie_id=movie_id,
            review=ReviewCreate(
                rating=base_rating,
                review_text=f"Review from {uid}",
            ),
        )

    # Take a snapshot to compare against
    baseline_review = svc.get_user_review(user_ids[0], movie_id)
    assert baseline_review is not None
    baseline_rating = baseline_review.rating

    def reader():
        # read single review
        r = svc.get_user_review(user_ids[0], movie_id)
        assert r is not None
        assert r.rating == baseline_rating

        # read all reviews by that user
        reviews, movies = svc.get_reviews_by_user_id(user_ids[0])
        # exactly one review for user0, on movie-1
        assert len(reviews) == 1
        assert movies == [movie_id]
        assert reviews[0].rating == baseline_rating

    with ThreadPoolExecutor(max_workers=10) as pool:
        list(pool.map(lambda _: reader(), range(30)))

def test_concurrent_upsert_many_users_same_movie(review_service_tmp):
    """
    P2a: Many concurrent upsert_review calls for different users on the same movie.

    Expect:
      - number of stored reviews == number of users
      - metadata userRatingCount == number of users
      - metadata totals/averages consistent with individual ratings
    """
    svc = review_service_tmp
    movie_id = "movie-1"

    # Define users and their ratings
    user_ids = [f"user{i}" for i in range(20)]
    ratings_by_user = {uid: (i % 5) + 1 for i, uid in enumerate(user_ids)}
    expected_total = sum(ratings_by_user.values())
    expected_count = len(user_ids)

    def worker(uid: str):
        rating = ratings_by_user[uid]
        svc.upsert_review(
            user_id=uid,
            movie_id=movie_id,
            review=ReviewCreate(
                rating=rating,
                review_text=f"Concurrent review from {uid}",
            ),
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(worker, user_ids))

    # Inspect persisted data
    review_data = ReviewRepository.get_review_data(movie_id)
    reviews = review_data["reviews"]
    assert len(reviews) == expected_count
    assert set(reviews.keys()) == set(user_ids)

    metadata = MovieRepository.get_movie_metadata(movie_id)
    assert metadata["userRatingCount"] == expected_count
    assert pytest.approx(metadata["userRatingTotal"]) == expected_total

    # average rounded to 2 decimal places in service
    expected_avg = round(expected_total / expected_count, 2)
    assert metadata["userRatingAverage"] == expected_avg

def test_concurrent_upsert_same_user_updates_consistently(review_service_tmp):
    """
    P2b: Many concurrent updates to the SAME user's review on the same movie.

    Expect:
      - exactly one review stored for that user
      - metadata count == 1
      - metadata total & average consistently match the final stored rating
        (we don't care which rating wins, only that the math is correct).
    """
    svc = review_service_tmp
    movie_id = "movie-1"
    user_id = "user-single"

    # Different ratings that will race; lock should serialize updates.
    ratings = [1, 2, 3, 4, 5]

    def worker(r: int):
        svc.upsert_review(
            user_id=user_id,
            movie_id=movie_id,
            review=ReviewCreate(
                rating=r,
                review_text=f"rating {r}",
            ),
        )

    with ThreadPoolExecutor(max_workers=len(ratings)) as pool:
        list(pool.map(worker, ratings))

    # Exactly one review for this user
    review_data = ReviewRepository.get_review_data(movie_id)
    reviews = review_data["reviews"]
    assert list(reviews.keys()) == [user_id]
    final_review = reviews[user_id]

    final_rating = final_review["rating"]

    metadata = MovieRepository.get_movie_metadata(movie_id)
    assert metadata["userRatingCount"] == 1
    assert pytest.approx(metadata["userRatingTotal"]) == final_rating
    assert metadata["userRatingAverage"] == final_rating
