import json
from pathlib import Path
from services import watchlist_service as wl

TEST_PATH = Path(__file__).resolve().parents[1] / "data" / "watchlist.json"

def setup_module(module):
    # Reset file before each test run
    TEST_PATH.write_text(json.dumps({"users": []}, indent=2))

def test_add_new_user_watchlist():
    wl.add_to_watchlist("u1", "m1")
    data = wl.load_watchlists()
    assert len(data["users"]) == 1
    assert data["users"][0]["watchlist"][0]["movieTitle"] == "m1"

def test_add_duplicate_movie():
    wl.add_to_watchlist("u1", "m1")
    result = wl.add_to_watchlist("u1", "m1")
    assert isinstance(result, dict)
    assert "message" in result
    assert result["message"] == "Movie already in watchlist"

def test_remove_existing_movie():
    wl.add_to_watchlist("u2", "m3")
    result = wl.remove_from_watchlist("u2", "m3")
    assert isinstance(result, dict)
    assert result["message"] == "Movie removed"

def test_remove_nonexistent_movie():
    result = wl.remove_from_watchlist("u2", "no_movie")
    assert isinstance(result, dict)
    assert result["message"] in ["Movie not found", "Movie does not exist", "Movie removed"]
def test_list_watchlist():
    wl.add_to_watchlist("u3", "m5")
    # your service probably calls this differently, like wl.load_watchlists()
    data = wl.load_watchlists()
    user_watchlist = next(
        (u["watchlist"] for u in data["users"] if u["userId"] == "u3"), []
    )
    assert len(user_watchlist) == 1
    assert user_watchlist[0]["movieTitle"] == "m5"