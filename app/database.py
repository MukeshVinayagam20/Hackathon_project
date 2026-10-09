"""MongoDB Atlas connection utilities."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@lru_cache(maxsize=1)
def get_mongodb_client() -> Optional[MongoClient]:
    """Create and reuse a MongoDB client from the environment."""
    mongodb_uri = os.getenv("MONGODB_URI", "").strip()
    if not mongodb_uri:
        return None

    return MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)


@lru_cache(maxsize=1)
def get_database() -> Optional[Database]:
    """Return the configured MongoDB database."""
    client = get_mongodb_client()
    if client is None:
        return None

    database_name = os.getenv("DATABASE_NAME", "ai_health_copilot").strip()
    return client[database_name]
