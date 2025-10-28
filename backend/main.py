from fastapi import FastAPI
from backend.routers import watchlist_router

app = FastAPI()
app.include_router(watchlist_router.router)