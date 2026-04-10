from fastapi import FastAPI
from .routers import user

from fastapi.middleware.cors import CORSMiddleware

from .database import create_db_and_tables 

app = FastAPI()

app.include_router(
    user.router
)

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