import os, sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Allow importing shared/ from project root when running directly
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from .database import init_db  # noqa: E402
from .routers import auth as auth_router  # noqa: E402
from .routers import admin as admin_router  # noqa: E402

load_dotenv()

app = FastAPI(title="Users & Auth API")

# CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

# Mount routers
app.include_router(auth_router.router)
app.include_router(admin_router.router)
