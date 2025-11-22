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


def test_query_substring_filters_subset():
    # 'story' should match only "Bravo Story"
    r = client.get("/search?q=story&limit=10")
    assert r.status_code == 200
    items = r.json()["items"]
    assert [i["title"] for i in items] == ["Bravo Story"]


def test_sort_by_title_desc():
    r = client.get("/search?q=&sort_by=title&sort_order=desc&limit=10")
    assert r.status_code == 200
    titles = [item["title"] for item in r.json()["items"]]
    assert titles == sorted(titles, reverse=True)


def test_sort_by_user_rating_asc_and_desc():
    # asc
    r = client.get("/search?q=&sort_by=user_rating&sort_order=asc&limit=10")
    assert r.status_code == 200
    titles_asc = [item["title"] for item in r.json()["items"]]
    # user ratings in dataset: Alpha 4.6, Charlie 4.9, Bravo 3.7
    assert titles_asc[0] == "Bravo Story"   # 3.7 lowest
    assert titles_asc[-1] == "Charlie Tale" # 4.9 highest
    # desc
    r = client.get("/search?q=&sort_by=user_rating&sort_order=desc&limit=10")
    titles_desc = [item["title"] for item in r.json()["items"]]
    assert titles_desc[0] == "Charlie Tale"
    assert titles_desc[-1] == "Bravo Story"


def test_sort_by_release_date_asc_and_desc():
    # asc: 2015 (Charlie) < 2019 (Bravo) < 2022 (Alpha)
    r = client.get("/search?q=&sort_by=release_date&sort_order=asc&limit=10")
    assert r.status_code == 200
    titles_asc = [item["title"] for item in r.json()["items"]]
    assert titles_asc == ["Charlie Tale", "Bravo Story", "Alpha Movie"]
    # desc
    r = client.get("/search?q=&sort_by=release_date&sort_order=desc&limit=10")
    titles_desc = [item["title"] for item in r.json()["items"]]
    assert titles_desc == ["Alpha Movie", "Bravo Story", "Charlie Tale"]


def test_limit_edges_and_types():
    # limit=1 should return exactly 1 item
    r = client.get("/search?q=&limit=1")
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 1
    # limit=50 should not exceed dataset size (3)
    r = client.get("/search?q=&limit=50")
    data = r.json()
    assert len(data["items"]) == 3
    # types stability
    item = data["items"][0]
    assert isinstance(item["id"], str)
    assert isinstance(item["title"], str)
    # imdbRating/userRatingAverage may be float or None if missing
    assert (item["imdbRating"] is None) or isinstance(item["imdbRating"], (int, float))
    assert (item["userRatingAverage"] is None) or isinstance(item["userRatingAverage"], (int, float))
