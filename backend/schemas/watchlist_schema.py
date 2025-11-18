from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class MovieItem(BaseModel):
    movie_title: str = Field(..., alias="movieTitle")
    added_at: datetime = Field(..., alias="addedAt")

    class Config:
        populate_by_name = True


class WatchlistResponse(BaseModel):
    user_id: str = Field(..., alias="userId")
    watchlist: List[MovieItem] = []

    class Config:
        populate_by_name = True


class WatchlistAddRequest(BaseModel):
    movie_title: str = Field(..., alias="movieTitle")


class WatchlistMessage(BaseModel):
    message: str
