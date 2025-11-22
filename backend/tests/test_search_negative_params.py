# backend/tests/test_search_negative_params.py

import json

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.repositories import movie_repo as movie_repo_module

client = TestClient(app)


@pytest.fixture(autouse=True)
def movie_dataset(tmp_path, monkeypatch):
    movies_dir = tmp_path / "movies"
    movies_dir.mkdir()

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

    write_movie("Alpha Movie", 8.0, 4.6, "2022-01-01")
    write_movie("Charlie Tale", 9.1, 4.9, "2015-05-05")
    write_movie("Bravo Story", 6.4, 3.7, "2019-03-03")

    yield


@pytest.mark.parametrize(
    "params",
    [
        {"q": "a", "sort_by": "not_a_field"},        # invalid sort_by
        {"q": "a", "sort_order": "sideways"},        # invalid sort_order
    ],
)
def test_search_invalid_sort_params(params):
    response = client.get("/search", params=params)
    assert response.status_code in (400, 422)


@pytest.mark.parametrize(
    "limit",
    [-1, 0],
)
def test_search_invalid_limit(limit):
    response = client.get("/search", params={"q": "a", "limit": limit})
    assert response.status_code in (400, 422)
