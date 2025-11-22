import json

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.repositories import movie_repo as movie_repo_module

client = TestClient(app)


@pytest.fixture(autouse=True)
def movie_dataset(tmp_path, monkeypatch):
    """
    Recreate the same small movie dataset used in test_search.py,
    but isolated in a temporary directory for this module.
    """
    movies_dir = tmp_path / "movies"
    movies_dir.mkdir()

    # Point the movie repo at the temporary directory
    monkeypatch.setattr(movie_repo_module, "MOVIES_DIR", movies_dir, raising=False)
    monkeypatch.setattr(
        "backend.repositories.movie_repo.MOVIES_DIR", movies_dir, raising=False
    )

    def write_movie(title, imdb_rating, user_rating, date_published):
        movie_dir = movies_dir / title
        movie_dir.mkdir()
        metadata = {
            "title": title,
            "movieIMDbRating": imdb_rating,
            "userRatingAverage": user_rating,
            "datePublished": date_published,
        }
        (movie_dir / "metadata.json").write_text(
            json.dumps(metadata), encoding="utf-8"
        )

    # Same three movies as in test_search.py
    write_movie("Alpha Movie", 8.0, 4.6, "2022-01-01")
    write_movie("Charlie Tale", 9.1, 4.9, "2015-05-05")
    write_movie("Bravo Story", 6.4, 3.7, "2019-03-03")

    yield


# ===== 1. Equivalence partitioning for the query parameter =====

@pytest.mark.parametrize(
    "query, expected_total, expected_titles_prefix",
    [
        ("a", 3, None),                        # all three titles contain "a"
        ("Alpha", 1, ["Alpha Movie"]),         # matches a single movie
        ("zzzz-no-such-title", 0, []),         # no matches
        ("", 3, None),                         # empty query = match all
    ],
)
def test_search_query_equivalence_partitions(
    query, expected_total, expected_titles_prefix
):
    response = client.get("/search", params={"q": query, "limit": 10})
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == expected_total

    items = data["items"]

    if expected_total == 0:
        assert items == []

    if expected_titles_prefix is not None:
        titles = [item["title"] for item in items]
        # Only check the prefix of the list so we do not over-constrain ordering
        assert titles[: len(expected_titles_prefix)] == expected_titles_prefix


# ===== 2. Boundary-value analysis for the limit parameter =====

@pytest.mark.parametrize(
    "limit, expected_len",
    [
        (1, 1),   # lower boundary
        (2, 2),   # typical middle value
        (10, 3),  # above total number of movies (3)
    ],
)
def test_search_limit_boundary(limit, expected_len):
    """
    Boundary-value analysis for the `limit` parameter.

    The API currently returns `total` equal to the number of items in this
    page, so we expect:
      - len(items) == expected_len
      - total == expected_len
    """
    response = client.get("/search", params={"q": "", "limit": limit})
    assert response.status_code == 200

    data = response.json()
    items = data["items"]

    assert len(items) == expected_len
    assert data["total"] == expected_len
