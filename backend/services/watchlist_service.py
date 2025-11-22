from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.repositories.watchlist_repo import WatchlistRepository

# Path to the JSON data file (tests monkeypatch this)
WATCHLIST_FILE = Path(__file__).resolve().parents[1] / "data" / "watchlist.json"


def _get_repo() -> WatchlistRepository:
    """
    Create a repository using the CURRENT value of WATCHLIST_FILE.

    This is important because tests monkeypatch WATCHLIST_FILE to point to
    a temporary file, and we want the repository to follow that change.
    """
    return WatchlistRepository(str(WATCHLIST_FILE))


def _now_utc_iso() -> str:
    """Return the current UTC timestamp in ISO8601 format."""
    return datetime.now(timezone.utc).isoformat()


# -------- Compatibility wrappers used by tests --------

def load_watchlists() -> Dict[str, List[dict]]:
    """
    Load the full watchlist data structure from disk via the repository.

    Tests call this directly and also monkeypatch WATCHLIST_FILE, so this
    function must respect the current WATCHLIST_FILE each time it is called.
    """
    repo = _get_repo()
    data: Any = repo.load()

    # Backwards compatibility: some older implementations may have stored
    # just a list instead of {"users": [...]}
    if isinstance(data, list):
        data = {"users": data}

    if "users" not in data:
        data["users"] = []

    return data


def save_watchlists(data: Dict[str, Any]) -> None:
    """
    Save the full watchlist data structure to disk via the repository.

    Tests also monkeypatch this (fault injection), so keep it as a separate
    function that add/remove can call.
    """
    repo = _get_repo()
    repo.save(data)


# ----------------- Public service functions -----------------


def get_user_watchlist(user_id: str) -> List[dict]:
    """
    Return the list of watchlist entries for a given user.
    If the user does not exist, return an empty list.
    """
    data = load_watchlists()
    for user in data["users"]:
        if user["userId"] == user_id:
            return user["watchlist"]
    return []


def add_to_watchlist(user_id: str, movie_title: str) -> Dict[str, str]:
    """
    Add a movie to a user's watchlist.

    Returns:
        {"message": "New user added with first movie"}  if user did not exist
        {"message": "Movie added"}                      if user exists and movie is new
        {"message": "Movie already in watchlist"}       if duplicate
    """
    data = load_watchlists()

    # Look for existing user
    for user in data["users"]:
        if user["userId"] == user_id:
            # Duplicate check
            if any(m["movieTitle"] == movie_title for m in user["watchlist"]):
                return {"message": "Movie already in watchlist"}

            # Add new movie
            user["watchlist"].append(
                {
                    "movieTitle": movie_title,
                    "addedAt": _now_utc_iso(),
                }
            )
            save_watchlists(data)
            return {"message": "Movie added"}

    # User not found → create new user with first movie
    data["users"].append(
        {
            "userId": user_id,
            "watchlist": [
                {
                    "movieTitle": movie_title,
                    "addedAt": _now_utc_iso(),
                }
            ],
        }
    )
    save_watchlists(data)
    return {"message": "New user added with first movie"}


def remove_from_watchlist(user_id: str, movie_title: str) -> Dict[str, str]:
    """
    Remove a movie from a user's watchlist.

    Returns:
        {"message": "Movie removed"}      if movie existed and was removed
        {"message": "Movie not found"}    if user exists but movie not in list
        {"message": "User not found"}     if user does not exist
    """
    data = load_watchlists()

    for user in data["users"]:
        if user["userId"] == user_id:
            before = len(user["watchlist"])
            user["watchlist"] = [
                m for m in user["watchlist"] if m["movieTitle"] != movie_title
            ]
            save_watchlists(data)

            if len(user["watchlist"]) < before:
                return {"message": "Movie removed"}
            else:
                return {"message": "Movie not found"}

    return {"message": "User not found"}
