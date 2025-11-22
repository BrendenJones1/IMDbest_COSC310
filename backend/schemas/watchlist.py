
# backend/schemas/watchlist_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MovieItem(BaseModel):
    movieTitle: str = Field(..., example="Inception")
    addedAt: datetime = Field(..., example="2025-10-30T12:34:56+00:00")


class UserWatchlist(BaseModel):
    userId: str = Field(..., example="u1")
    watchlist: List[MovieItem] = []


class AddMovieRequest(BaseModel):
    movieTitle: str = Field(..., example="Interstellar")


class WatchlistResponse(BaseModel):
    message: str
