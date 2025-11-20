import json
from datetime import datetime, timezone
from pathlib import Path

WATCHLIST_FILE = Path(__file__).resolve().parents[1] / "data" / "watchlist.json"


def _now_utc_iso() -> str:
    """
    Return the current time as a timezone-aware ISO 8601 string in UTC.
    """
    return datetime.now(timezone.utc).isoformat()


def load_watchlists():
    """
    Load all user watchlists from the backing JSON file, or return an empty structure.
    """
    if not WATCHLIST_FILE.exists():
        return {"users": []}
    with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_watchlists(data):
    """
    Persist the provided watchlist data to the backing JSON file.
    """
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_user_watchlist(user_id: str):
    """
    Return the watchlist for a given user_id, or an empty list if the user has none.
    """
    data = load_watchlists()
    for user in data["users"]:
        if user["userId"] == user_id:
            return user["watchlist"]
    return []


def add_to_watchlist(user_id: str, movie_title: str):
    """
    Add a movie to a user's watchlist, creating the user entry if necessary.
    """
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

    # No existing user; create a new watchlist for this user
    data["users"].append({
        "userId": user_id,
        "watchlist": [{"movieTitle": movie_title, "addedAt": _now_utc_iso()}],
    })
    save_watchlists(data)
    return {"message": "New user added with first movie"}


def remove_from_watchlist(user_id: str, movie_title: str):
    """
    Remove a movie from a user's watchlist and report whether it was found.
    """
    data = load_watchlists()
    for user in data["users"]:
        if user["userId"] == user_id:
            before = len(user["watchlist"])
            user["watchlist"] = [
                m for m in user["watchlist"] if m["movieTitle"] != movie_title
            ]
            save_watchlists(data)
            # Indicate if the movie was actually removed or not present
            return {
                "message": "Movie removed"
                if len(user["watchlist"]) < before
                else "Movie not found"
            }
    return {"message": "User not found"}
