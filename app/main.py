from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import user, friendships, websocket, upload

from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

from .database import create_db_and_tables
from fastapi.responses import HTMLResponse

app = FastAPI()

app.include_router(user.router)
app.include_router(friendships.router)
app.include_router(websocket.router)
app.include_router(upload.router)

ROOT_PATH = Path(__file__).parent
def create_dirs():
    os.makedirs(os.path.join(ROOT_PATH, "uploads"), exist_ok=True)

create_dirs()

app.mount("/uploads", StaticFiles(directory=os.path.join(ROOT_PATH, "uploads")), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
def startup_events():
    create_db_and_tables()