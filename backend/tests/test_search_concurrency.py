# backend/tests/test_search_concurrency.py
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

import backend.repositories.movie_repo as movie_repo
from backend.repositories.movie_repo import MovieRepository
import backend.services.search_service as search_service
from backend.services.search_service import SortField, SortOrder


@pytest.fixture
def seeded_movies(tmp_path, monkeypatch):
    """
    Setup a temporary movies directory with a few movies and metadata,
    wired into MovieRepository and search_service via MOVIES_DIR.
    """
    movies_dir = tmp_path / "movies"
    movies_dir.mkdir(parents=True, exist_ok=True)

    # Make the repo use our temp dir
    monkeypatch.setattr(movie_repo, "MOVIES_DIR", movies_dir)

    # Patch _metadata_path so it doesn't depend on _resolve_movie_dir behaviour
    def fake_metadata_path(movie_id: str) -> Path:
        movie_dir = movies_dir / movie_id
        movie_dir.mkdir(parents=True, exist_ok=True)
        return movie_dir / "metadata.json"

    monkeypatch.setattr(
        movie_repo.MovieRepository,
        "_metadata_path",
        staticmethod(fake_metadata_path),
    )

    # Now safe to seed via the real repo methods
    MovieRepository.save_movie_metadata(
        "movie-1",
        {
            "movie_id": "movie-1",
            "title": "Alpha",
            "movieIMDbRating": 7.5,
            "userRatingAverage": 3.0,
            "datePublished": "2020-01-01",
        },
    )

    MovieRepository.save_movie_metadata(
        "movie-2",
        {
            "movie_id": "movie-2",
            "title": "Beta",
            "movieIMDbRating": 8.2,
            "userRatingAverage": 4.5,
            "datePublished": "2021-06-15",
        },
    )

    MovieRepository.save_movie_metadata(
        "movie-3",
        {
            "movie_id": "movie-3",
            "title": "Gamma",
            "movieIMDbRating": 6.9,
            "userRatingAverage": 2.0,
            "datePublished": "2019-09-10",
        },
    )

    return movies_dir


def test_concurrent_search_read_only(seeded_movies):
    """
    P1: Many concurrent search() calls, no writers.

    Expect:
      - no exceptions
      - each call returns a consistent, sorted set of results
    """
    # Basic expectations for a single call: no query filter, sorted by title
    single = search_service.search(
        q="",
        sort_by=SortField.TITLE,
        sort_order=SortOrder.ASC,
        limit=10,
    )
    assert len(single) == 3
    single_titles = [m["title"] for m in single]
    assert single_titles == sorted(single_titles, key=lambda t: t.lower())

    def worker():
        # Search by title (no filter)
        res_title = search_service.search(
            q="",
            sort_by=SortField.TITLE,
            sort_order=SortOrder.ASC,
            limit=10,
        )
        assert len(res_title) == 3
        titles = [m["title"] for m in res_title]
        assert titles == sorted(titles, key=lambda t: t.lower())

        # Search by IMDb rating descending
        res_rating = search_service.search(
            q="",
            sort_by=SortField.IMDB_RATING,
            sort_order=SortOrder.DESC,
            limit=3,
        )
        assert 1 <= len(res_rating) <= 3
        ratings = [m["imdbRating"] or 0.0 for m in res_rating]
        assert ratings == sorted(ratings, reverse=True)

    with ThreadPoolExecutor(max_workers=10) as pool:
        list(pool.map(lambda _: worker(), range(30)))


def test_concurrent_search_with_metadata_updates(seeded_movies):
    """
    P2: search() under concurrent metadata writes.

    One thread repeatedly updates movie-1's metadata while multiple threads
    perform search() calls sorted by USER_RATING.

    Expect:
      - no exceptions from search()
      - final metadata is valid and search still returns valid JSON-shaped results
    """
    movie_id = "movie-1"

    # Confirm movie exists
    meta_before = MovieRepository.get_movie_metadata(movie_id)
    assert meta_before["movie_id"] == movie_id

    def writer():
        # Simulate some concurrent updates to userRatingAverage and count
        for i in range(20):
            meta = MovieRepository.get_movie_metadata(movie_id)
            meta["userRatingCount"] += 1
            meta["userRatingTotal"] += (i % 5) + 1
            meta["userRatingAverage"] = round(
                meta["userRatingTotal"] / meta["userRatingCount"], 2
            )
            MovieRepository.save_movie_metadata(movie_id, meta)

    def reader():
        # Repeatedly call search while writer is running
        for _ in range(50):
            results = search_service.search(
                q="",
                sort_by=SortField.USER_RATING,
                sort_order=SortOrder.DESC,
                limit=5,
            )
            assert isinstance(results, list)
            for m in results:
                assert "id" in m
                assert "title" in m
                assert "userRatingAverage" in m  # may be None but key present

    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(writer)]
        for _ in range(5):
            futures.append(pool.submit(reader))
        for f in futures:
            f.result()

    meta_after = MovieRepository.get_movie_metadata(movie_id)
    assert isinstance(meta_after["userRatingCount"], int)
    assert isinstance(meta_after["userRatingTotal"], (int, float))
    assert isinstance(meta_after["userRatingAverage"], (int, float))
