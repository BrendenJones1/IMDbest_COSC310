import json
import pytest

from backend.repositories import movie_repo as movie_repo_module
from backend.repositories.movie_repo import MovieRepository
from backend.repositories.reviews_repo import ReviewRepository
from backend.schemas.review import ReviewCreate
from backend.services.review_service import ReviewService


@pytest.fixture()
def movies_dir(tmp_path, monkeypatch):
    base = tmp_path / "movies"
    base.mkdir()
    monkeypatch.setattr(movie_repo_module, "MOVIES_DIR", base, raising=False)
    # the classes in movie_repo reference the module-level constant directly
    monkeypatch.setattr("repositories.movie_repo.MOVIES_DIR", base, raising=False)
    # also patch the backend-qualified module in case it's imported elsewhere
    monkeypatch.setattr("backend.repositories.movie_repo.MOVIES_DIR", base, raising=False)
    # sanity: ensure both namespaces (if present) point to same path
    try:
        import repositories.movie_repo as legacy_movie_repo  # type: ignore
        assert getattr(legacy_movie_repo, "MOVIES_DIR", None) == base
    except Exception:
        pass
    return base


def create_movie_directory(movies_dir, title="Sample Movie"):
    movie_dir = movies_dir / title
    movie_dir.mkdir()
    (movie_dir / "metadata.json").write_text(
        json.dumps(
            {
                "title": title,
                # initialize fields expected by the service/tests
                "userRatingCount": 0,
                "userRatingTotal": 0.0,
                "userRatingAverage": 0.0,
            }
        ),
        encoding="utf-8",
    )
    return MovieRepository._slug(title)


def test_upsert_review_tracks_average_and_totals(movies_dir):
    movie_id = create_movie_directory(movies_dir, "Thor Ragnarok")
    service = ReviewService()

    first = service.upsert_review("user-1", movie_id, ReviewCreate(rating=4.5, review_text="Great"))
    assert first.rating == 4.5

    metadata = MovieRepository.get_movie_metadata(movie_id)
    assert metadata["userRatingCount"] == 1
    assert metadata["userRatingTotal"] == pytest.approx(4.5)
    assert metadata["userRatingAverage"] == pytest.approx(4.5)

    service.upsert_review("user-2", movie_id, ReviewCreate(rating=2.0))
    metadata = MovieRepository.get_movie_metadata(movie_id)
    assert metadata["userRatingCount"] == 2
    assert metadata["userRatingTotal"] == pytest.approx(6.5)
    assert metadata["userRatingAverage"] == pytest.approx(3.25)

    service.upsert_review("user-1", movie_id, ReviewCreate(rating=5.0))
    metadata = MovieRepository.get_movie_metadata(movie_id)
    assert metadata["userRatingCount"] == 2
    assert metadata["userRatingTotal"] == pytest.approx(7.0)
    assert metadata["userRatingAverage"] == pytest.approx(3.5)


def test_delete_review_updates_metadata(movies_dir):
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


def test_upsert_same_user_preserves_count(movies_dir):
    movie_id = create_movie_directory(movies_dir, "Pulp Fiction")
    service = ReviewService()

    # first review by user-a increments count
    service.upsert_review("user-a", movie_id, ReviewCreate(rating=4.0))
    metadata = MovieRepository.get_movie_metadata(movie_id)
    assert metadata["userRatingCount"] == 1
    assert metadata["userRatingTotal"] == pytest.approx(4.0)
    assert metadata["userRatingAverage"] == pytest.approx(4.0)

    # update same user should NOT increment count, but adjust totals/average
    service.upsert_review("user-a", movie_id, ReviewCreate(rating=2.0))
    metadata = MovieRepository.get_movie_metadata(movie_id)
    assert metadata["userRatingCount"] == 1
    assert metadata["userRatingTotal"] == pytest.approx(2.0)
    assert metadata["userRatingAverage"] == pytest.approx(2.0)

    # second distinct user increments count
    service.upsert_review("user-b", movie_id, ReviewCreate(rating=3.0))
    metadata = MovieRepository.get_movie_metadata(movie_id)
    assert metadata["userRatingCount"] == 2
    assert metadata["userRatingTotal"] == pytest.approx(5.0)
    assert metadata["userRatingAverage"] == pytest.approx(2.5)
