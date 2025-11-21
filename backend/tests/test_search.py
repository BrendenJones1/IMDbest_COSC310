import json

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.repositories import movie_repo as movie_repo_module
from contextlib import contextmanager

client = TestClient(app)


@pytest.fixture(autouse=True)
def movie_dataset(tmp_path, monkeypatch):
    """
    Seed an isolated movies directory with a small test dataset for each test.
    """
    movies_dir = tmp_path / "movies"
    movies_dir.mkdir()
    # Ensure both the module and its consumers see the same temporary MOVIES_DIR
    monkeypatch.setattr(movie_repo_module, "MOVIES_DIR", movies_dir, raising=False)
    monkeypatch.setattr("backend.repositories.movie_repo.MOVIES_DIR", movies_dir, raising=False)

    def write_movie(title, imdb_rating, user_rating, date_published):
        """
        Create a single movie folder with a metadata.json entry.
        """
        movie_dir = movies_dir / title
        movie_dir.mkdir()
        metadata = {
            "title": title,
            "movieIMDbRating": imdb_rating,
            "userRatingAverage": user_rating,
            "datePublished": date_published,
        }
        (movie_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

    write_movie("Alpha Movie", 8.0, 4.6, "2022-01-01")
    write_movie("Charlie Tale", 9.1, 4.9, "2015-05-05")
    write_movie("Bravo Story", 6.4, 3.7, "2019-03-03")

    yield


def test_search_structure():
    """
    Search endpoint returns a structured payload with items and total count.
    """
    r = client.get("/search?q=a&limit=5")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3
    assert isinstance(data["items"], list)
    assert data["items"][0]["id"]
    assert data["items"][0]["title"]
    assert "imdbRating" in data["items"][0]
    assert "userRatingAverage" in data["items"][0]


def test_default_sort_is_title_ascending():
    """
    By default, search results should be sorted by title in ascending order.
    """
    r = client.get("/search?q=&limit=3")
    titles = [item["title"] for item in r.json()["items"]]
    assert titles == sorted(titles)


def test_sort_by_imdb_rating_desc():
    """
    Sorting by imdb_rating=desc should place the highest-rated movie first.
    """
    r = client.get("/search?q=&sort_by=imdb_rating&sort_order=desc")
    titles = [item["title"] for item in r.json()["items"]]
    assert titles[0] == "Charlie Tale"
    assert titles[-1] == "Bravo Story"
