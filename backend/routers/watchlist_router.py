from fastapi import APIRouter, HTTPException, status

from backend.schemas.watchlist_schema import (
    WatchlistAddRequest,
    WatchlistMessage,
    WatchlistResponse,
)
from backend.services import watchlist_service

router = APIRouter(prefix="/watchlists", tags=["watchlists"])


@router.get("/{user_id}", response_model=WatchlistResponse)
def get_watchlist(user_id: str) -> WatchlistResponse:
    """Return the watchlist for a given user. Empty list if user not found."""
    items = watchlist_service.get_user_watchlist(user_id)
    return WatchlistResponse(user_id=user_id, watchlist=items)


@router.post(
    "/{user_id}",
    response_model=WatchlistMessage,
    status_code=status.HTTP_201_CREATED,
)
def add_movie(user_id: str, payload: WatchlistAddRequest) -> WatchlistMessage:
    """Add a movie to the user's watchlist."""
    result = watchlist_service.add_to_watchlist(user_id, payload.movie_title)
    message = result.get("message", "")
    if message == "Movie already in watchlist":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)
    return WatchlistMessage(**result)


@router.delete(
    "/{user_id}/{movie_title}",
    response_model=WatchlistMessage,
)
def remove_movie(user_id: str, movie_title: str) -> WatchlistMessage:
    """Remove a movie from the user's watchlist."""
    result = watchlist_service.remove_from_watchlist(user_id, movie_title)
    message = result.get("message", "")
    if message == "User not found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    if message == "Movie not found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    return WatchlistMessage(**result)
