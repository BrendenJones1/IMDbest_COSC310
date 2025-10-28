# backend/tests/test_search.py
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_search_structure():
    r = client.get("/search?q=dark")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data and "total" in data
    assert isinstance(data["items"], list)
    for item in data["items"]:
        assert "id" in item and "title" in item
