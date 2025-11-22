from fastapi import APIRouter, HTTPException, status

from backend.schemas.watchlist import (
    UserWatchlist,
    AddMovieRequest,
    WatchlistResponse,
)
from backend.services import watchlist_service as wl

router = APIRouter(
    prefix="/watchlists",
    tags=["Watchlists"],
)

def _add_movie_impl(user_id: str, movie_title: str) -> WatchlistResponse:
    """
    Shared implementation for adding a movie to a user's watchlist.
    Preserves existing behavior:
      - 201 when movie added or first movie for a new user
      - 409 when movie already exists
    """
    result = wl.add_to_watchlist(user_id, movie_title)
    message = result.get("message", "")
    if message == "Movie already in watchlist":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )
    return WatchlistResponse(message=message)

def _remove_movie_impl(user_id: str, movie_title: str, not_found_as_404: bool) -> WatchlistResponse:
    """
    Shared implementation for removing a movie from a user's watchlist.
    Preserves existing behavior differences:
      - Primary DELETE returns 200 "Movie not found" for missing movie
      - Compatibility DELETE returns 404 "Movie not found"
      - Both return 404 "User not found" when user does not exist
    """
    result = wl.remove_from_watchlist(user_id, movie_title)
    message = result.get("message", "")
    if message == "User not found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )
    if not_found_as_404 and message == "Movie not found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )
    return WatchlistResponse(message=message)


# GET user watchlist
@router.get("/{user_id}", response_model=UserWatchlist)
def get_user_watchlist(user_id: str):
    """
    Return the watchlist for the given user.
    If the user does not exist in the JSON file, return an empty list.
    """
    watchlist_raw = wl.get_user_watchlist(user_id)
    return {
        "userId": user_id,
        "watchlist": watchlist_raw,
    }


# ---------------------------------------------------------------------------
# Primary POST endpoint used by your integration tests:
#   POST /watchlists/{user_id}/movies
# ---------------------------------------------------------------------------
@router.post(
    "/{user_id}/movies",
    response_model=WatchlistResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_movie_to_watchlist(user_id: str, body: AddMovieRequest):
    """
    Add a movie to the user's watchlist.
    Returns:
      - 201 when the movie is added or first movie for a new user
      - 409 when the movie is already in the watchlist
    """
    return _add_movie_impl(user_id, body.movieTitle)


# ---------------------------------------------------------------------------
# Compatibility POST endpoint used by existing router tests:
#   POST /watchlists/{user_id}
# Same behavior as POST /watchlists/{user_id}/movies
# ---------------------------------------------------------------------------
@router.post(
    "/{user_id}",
    response_model=WatchlistResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_movie_to_watchlist_short(user_id: str, body: AddMovieRequest):
    """
    Compatibility endpoint for tests that call POST /watchlists/{user_id}.
    Uses the same service logic as the primary POST endpoint.
    """
    return _add_movie_impl(user_id, body.movieTitle)


# ---------------------------------------------------------------------------
# Primary DELETE endpoint used by your integration tests:
#   DELETE /watchlists/{user_id}/movies/{movie_title}
# ---------------------------------------------------------------------------
@router.delete(
    "/{user_id}/movies/{movie_title}",
    response_model=WatchlistResponse,
)
def remove_movie_from_watchlist(user_id: str, movie_title: str):
    """
    Remove a movie from the user's watchlist.
    Returns:
      - 200 with message "Movie removed" if it was there
      - 200 with message "Movie not found" if it was not in the list
      - 404 with message "User not found" if no such user
    """
    return _remove_movie_impl(user_id, movie_title, not_found_as_404=False)


# ---------------------------------------------------------------------------
# Compatibility DELETE endpoint used by existing router tests:
#   DELETE /watchlists/{user_id}/{movie_title}
# Same behavior as DELETE /watchlists/{user_id}/movies/{movie_title}
# ---------------------------------------------------------------------------
@router.delete(
    "/{user_id}/{movie_title}",
    response_model=WatchlistResponse,
)
def remove_movie_from_watchlist_short(user_id: str, movie_title: str):
    """
    Compatibility endpoint for tests that call DELETE /watchlists/{user_id}/{movie_title}.
    Uses the same service logic as the primary DELETE endpoint.
    """
    return _remove_movie_impl(user_id, movie_title, not_found_as_404=True)
