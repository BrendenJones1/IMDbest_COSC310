from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.routers.search import router as search_router
from backend.routers.auth_router import router as auth_router
from backend.routers.watchlist_router import router as watchlist_router
from backend.routers.flags_router import router as flags_router
from backend.routers.penalties_router import router as penalties_router
from backend.routers.users_router import router as users_router
from backend.routers.admin_router import router as admin_router
from backend.routers.reviews_router import router as reviews_router

app = FastAPI(title="COSC310 API (dev)")

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

app.include_router(auth_router)
app.include_router(search_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(flags_router)
app.include_router(penalties_router)
app.include_router(watchlist_router)
app.include_router(reviews_router)
