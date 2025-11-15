from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.search import router as search_router
from backend.routers.flags_router import router as flags_router
from backend.routers.penalties_router import router as penalties_router
from backend.routers.watchlist_router import router as watchlist_router

app = FastAPI(title="COSC310 API (dev)")

# allow local frontend (Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(watchlist_router)
app.include_router(search_router)
app.include_router(flags_router)
app.include_router(penalties_router)
