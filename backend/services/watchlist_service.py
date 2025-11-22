from datetime import datetime, timezone
from pathlib import Path

from backend.repositories.watchlist_repo import WatchlistRepository

# Path to the JSON data file
WATCHLIST_FILE = Path(__file__).resolve().parents[1] / "data" / "watchlist.json"

# Create repository instance
repo = WatchlistRepository(str(WATCHLIST_FILE))


def _now_utc_iso() -> str:
    """Return the current UTC timestamp in ISO8601 format."""
    return datetime.now(timezone.utc).isoformat()


def get_user_watchlist(user_id: str):
    """Return the watchlist list for a user, or empty list if not exists."""
    data = repo.load()

    for user in data.get("users", []):
        if user["userId"] == user_id:
            return user["watchlist"]

    return []


def add_to_watchlist(user_id: str, movie_title: str):
    """Add a movie to a user's watchlist."""
    data = repo.load()

    # Check if user exists
    for user in data["users"]:
        if user["userId"] == user_id:
            # Check duplicate
            if any(m["movieTitle"] == movie_title for m in user["watchlist"]):
                return {"message": "Movie already in watchlist"}

            # Add new movie
            user["watchlist"].append({
                "movieTitle": movie_title,
                "addedAt": _now_utc_iso(),
            })

            repo.save(data)
            return {"message": "Movie added"}

    # User not found → create new user
    data["users"].append({
        "userId": user_id,
        "watchlist": [{
            "movieTitle": movie_title,
            "addedAt": _now_utc_iso(),
        }],
    })

    repo.save(data)
    return {"message": "New user added with first movie"}


def remove_from_watchlist(user_id: str, movie_title: str):
    """Remove a movie from a user's watchlist."""
    data = repo.load()

    for user in data["users"]:
        if user["userId"] == user_id:
            before = len(user["watchlist"])
            user["watchlist"] = [
                m for m in user["watchlist"]
                if m["movieTitle"] != movie_title
            ]

            repo.save(data)

            if len(user["watchlist"]) < before:
                return {"message": "Movie removed"}
            else:
                return {"message": "Movie not found"}

    return {"message": "User not found"}
