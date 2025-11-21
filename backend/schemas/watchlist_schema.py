from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, ConfigDict


class MovieItem(BaseModel):
    movie_title: str = Field(..., alias="movieTitle")
    added_at: datetime = Field(..., alias="addedAt")

    model_config = ConfigDict(populate_by_name=True)


class WatchlistResponse(BaseModel):
    user_id: str = Field(..., alias="userId")
    watchlist: List[MovieItem] = []

    model_config = ConfigDict(populate_by_name=True)


class WatchlistAddRequest(BaseModel):
    movie_title: str = Field(..., alias="movieTitle")


class WatchlistMessage(BaseModel):
    message: str
