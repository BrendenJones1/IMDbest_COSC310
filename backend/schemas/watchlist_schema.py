from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class WatchlistItem(BaseModel):
    """Single movie entry in a user's watchlist."""

    model_config = ConfigDict(populate_by_name=True)

    movie_title: str = Field(..., alias="movieTitle", min_length=1)
    added_at: datetime = Field(..., alias="addedAt")


class WatchlistResponse(BaseModel):
    """Watchlist payload returned to clients."""

    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., alias="userId")
    watchlist: List[WatchlistItem]


class WatchlistAddRequest(BaseModel):
    """Incoming payload for adding a movie to a watchlist."""

    model_config = ConfigDict(populate_by_name=True)

    movie_title: str = Field(..., alias="movieTitle", min_length=1)


class WatchlistMessage(BaseModel):
    """Generic response envelope for watchlist operations."""

    message: str
