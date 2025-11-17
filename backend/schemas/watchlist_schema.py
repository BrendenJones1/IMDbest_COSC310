from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, ConfigDict


class MovieItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    movie_title: str = Field(..., alias="movieTitle")
    added_at: datetime = Field(..., alias="addedAt")


class WatchlistResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., alias="userId")
    watchlist: List[MovieItem] = []


class WatchlistAddRequest(BaseModel):
    movie_title: str = Field(..., alias="movieTitle")


class WatchlistMessage(BaseModel):
    message: str


# Backwards compatibility with earlier names used in codebase/tests
AddMovieRequest = WatchlistAddRequest
UserWatchlist = WatchlistResponse
MovieItemResponse = MovieItem
