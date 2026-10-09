"""FastAPI application entry point."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.database import router as database_router
from app.routes.storage import router as storage_router

app = FastAPI(
    title="AI-Powered Personal Health Copilot API",
    version="0.1.0",
)

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(database_router)
app.include_router(storage_router)


@app.get("/api/health")
def health() -> dict:
    """Return the basic API health response."""
    return {
        "status": "ok",
        "message": "Health Copilot API is running",
    }
