from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.watchlist_router import router as watchlist_router
from backend.routers.search_router import router as search_router
from backend.routers.reviews_router import router as reviews_router
from backend.routers.movies_router import router as movies_router
from backend.routers import users_router, admin_router
from backend.routers.flags_router import router as flags_router
from backend.routers.penalties_router import router as penalties_router
from backend.routers.search_router import router as search_router
from backend.routers.notes_router import router as notes_router


app = FastAPI(title="COSC310 API (dev)")

# allow local frontend (Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(watchlist_router)
app.include_router(search_router)
app.include_router(reviews_router)
app.include_router(movies_router)
app.include_router(users_router.router)
app.include_router(admin_router.router)
app.include_router(flags_router)
app.include_router(penalties_router)
app.include_router(notes_router)
