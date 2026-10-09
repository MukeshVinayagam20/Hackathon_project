"""MongoDB-related API routes."""

import os

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.database import get_database
from app.services.database import ensure_database_structure

router = APIRouter()


@router.get("/api/database/health")
def database_health() -> JSONResponse:
    """Check the configured MongoDB Atlas connection with PyMongo."""
    database = get_database()
    if database is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unavailable",
                "message": "MongoDB connection is not configured",
            },
        )

    try:
        database.command("ping")
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unavailable",
                "message": "MongoDB connection failed",
            },
        )

    database_name = os.getenv("DATABASE_NAME", "ai_health_copilot").strip()
    return {
        "status": "connected",
        "database": database_name,
    }


@router.get("/api/database/structure")
def database_structure() -> JSONResponse:
    """Create collection indexes without inserting any medical records."""
    database = get_database()
    if database is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unavailable",
                "message": "MongoDB connection is not configured",
            },
        )

    try:
        indexes = ensure_database_structure(database)
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unavailable",
                "message": "MongoDB structure initialization failed",
            },
        )

    return {
        "status": "initialized",
        "database": os.getenv("DATABASE_NAME", "ai_health_copilot").strip(),
        "collections": indexes,
    }
