
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

# ADD movie to watchlist

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
    result = wl.add_to_watchlist(user_id, body.movieTitle)

    message = result.get("message", "")
    if message == "Movie already in watchlist":
    
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )

    
    return WatchlistResponse(message=message)


# REMOVE movie from watchlist

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
    result = wl.remove_from_watchlist(user_id, movie_title)
    message = result.get("message", "")

    if message == "User not found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )

    return WatchlistResponse(message=message)
