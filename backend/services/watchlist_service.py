import json
from datetime import datetime, timezone
from pathlib import Path

WATCHLIST_FILE = Path(__file__).resolve().parents[1] / "data" / "watchlist.json"

def _now_utc_iso() -> str:
    # timezone-aware ISO8601 (e.g., 2025-10-25T07:31:12.345678+00:00)
    return datetime.now(timezone.utc).isoformat()

def load_watchlists():
    if not WATCHLIST_FILE.exists():
        return {"users": []}
    with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_watchlists(data):
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_user_watchlist(user_id: str):
    data = load_watchlists()
    for user in data["users"]:
        if user["userId"] == user_id:
            return user["watchlist"]
    return []

def add_to_watchlist(user_id: str, movie_title: str):
    data = load_watchlists()
    for user in data["users"]:
        if user["userId"] == user_id:
            if any(m["movieTitle"] == movie_title for m in user["watchlist"]):
                return {"message": "Movie already in watchlist"}
            user["watchlist"].append({
                "movieTitle": movie_title,
                "addedAt": _now_utc_iso(),
            })
            save_watchlists(data)
            return {"message": "Movie added"}
    # create new user
    data["users"].append({
        "userId": user_id,
        "watchlist": [{"movieTitle": movie_title, "addedAt": _now_utc_iso()}],
    })
    save_watchlists(data)
    return {"message": "New user added with first movie"}

def remove_from_watchlist(user_id: str, movie_title: str):
    data = load_watchlists()
    for user in data["users"]:
        if user["userId"] == user_id:
            before = len(user["watchlist"])
            user["watchlist"] = [m for m in user["watchlist"] if m["movieTitle"] != movie_title]
            save_watchlists(data)
            # Optional: distinguish not found vs removed
            return {"message": "Movie removed" if len(user["watchlist"]) < before else "Movie not found"}
    return {"message": "User not found"}