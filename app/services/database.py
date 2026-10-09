"""Database collection and index initialization."""

from typing import Any, Dict, List, Tuple

from pymongo.database import Database

COLLECTIONS: Dict[str, List[Tuple[str, Any]]] = {
    "users": [
        ("user_id", 1),
        ("patient_id", 1),
    ],
    "documents": [
        ("user_id", 1),
        ("patient_id", 1),
        ("document_id", 1),
        ("source_document_id", 1),
        ("date", 1),
    ],
    "document_pages": [
        ("document_id", 1),
        ("source_document_id", 1),
        ("page_number", 1),
    ],
    "prescriptions": [
        ("user_id", 1),
        ("source_document_id", 1),
        ("prescription_date", 1),
    ],
    "lab_results": [
        ("user_id", 1),
        ("source_document_id", 1),
        ("test_date", 1),
    ],
    "diagnostic_reports": [
        ("user_id", 1),
        ("source_document_id", 1),
        ("report_date", 1),
    ],
    "discharge_summaries": [
        ("user_id", 1),
        ("source_document_id", 1),
        ("discharge_date", 1),
    ],
    "timeline_events": [
        ("event_id", 1),
        ("user_id", 1),
        ("source_document_id", 1),
        ("date", 1),
    ],
    "wellness_records": [
        ("user_id", 1),
        ("date", 1),
        ("source", 1),
    ],
    "health_summaries": [
        ("summary_id", 1),
        ("user_id", 1),
        ("source_documents", 1),
    ],
}


def ensure_database_structure(database: Database) -> Dict[str, list]:
    """Create expected collections and indexes without inserting medical data."""
    created_indexes: Dict[str, list] = {}

    for collection_name, indexes in COLLECTIONS.items():
        collection = database[collection_name]
        for field, direction in indexes:
            collection.create_index([(field, direction)])
        created_indexes[collection_name] = [field for field, _ in indexes]

    return created_indexes
