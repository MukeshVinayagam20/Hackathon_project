"""Reusable PyMongo repository operations."""

from typing import Any, Dict, List, Optional

from pymongo import ReturnDocument
from pymongo.collection import Collection


class MongoRepository:
    """Small repository facade for future CRUD operations."""

    def __init__(self, collection: Collection) -> None:
        self.collection = collection

    def create(self, document: Dict[str, Any]) -> Any:
        """Insert one document and return the inserted document."""
        return self.collection.insert_one(document).inserted_id

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one document by a query."""
        return self.collection.find_one(query)

    def find_many(
        self,
        query: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, Any]] = None,
        sort: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Find multiple documents in insertion order by default."""
        return list(
            self.collection.find(
                query or {},
                projection=projection,
                sort=sort or {},
            )
        )

    def update_one(
        self,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> Any:
        """Update one document."""
        return self.collection.update_one(query, update, upsert=upsert)

    def update_one_and_return(
        self,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Update one document and return the updated document."""
        return self.collection.find_one_and_update(
            query,
            update,
            upsert=upsert,
            return_document=ReturnDocument.AFTER,
        )

    def delete_one(self, query: Dict[str, Any]) -> Any:
        """Delete one document."""
        return self.collection.delete_one(query)

    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching a query."""
        return self.collection.count_documents(query or {})
