from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_reviews_invalid_sort_returns_422():
    r = client.get("/reviews/some-movie?sort=invalid")
    assert r.status_code == 422
    data = r.json()
    assert data["detail"][0]["type"] in ("enum", "enum_member") or data["detail"][0]["type"].endswith("literal_error")


def test_reviews_limit_below_min_returns_422():
    r = client.get("/reviews/some-movie?limit=0")
    assert r.status_code == 422


def test_reviews_offset_negative_returns_422():
    r = client.get("/reviews/some-movie?offset=-1")
    assert r.status_code == 422


