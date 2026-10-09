"""Document storage API routes."""

import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.database import get_database
from app.models.schemas import DocumentRecord
from app.services.storage_service import CloudinaryStorageService

router = APIRouter()

ALLOWED_CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}
SUPPORTED_EXTENSIONS = set(ALLOWED_CONTENT_TYPES)
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


def _safe_document_metadata(document: dict) -> dict:
    """Return document metadata without storage credentials."""
    return {
        key: value
        for key, value in document.items()
        if key not in {
            "cloudinary_public_id",
            "cloudinary_secure_url",
        }
    }


@router.post("/api/documents/upload")
async def upload_document(
    file: UploadFile,
    user_id: str = "demo-user",
) -> JSONResponse:
    """Upload one supported file to Cloudinary and persist its metadata."""
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Allowed formats are PDF, JPG, JPEG, and PNG.",
        )

    expected_content_type = ALLOWED_CONTENT_TYPES[extension]
    if file.content_type and file.content_type.lower() != expected_content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The file content type does not match its extension.",
        )

    try:
        file_data = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to read the uploaded file.",
        ) from exc

    if not file_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty.",
        )

    if len(file_data) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="The uploaded file exceeds the 10 MB limit.",
        )

    try:
        storage_service = CloudinaryStorageService()
        storage_result = storage_service.upload_file(
            file_data=file_data,
            original_filename=filename,
            content_type=file.content_type or expected_content_type,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cloudinary storage is not configured.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cloudinary upload failed.",
        ) from exc

    database = get_database()
    if database is None:
        try:
            storage_service.delete_file(storage_result["public_id"])
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB connection is not configured.",
        )

    document_id = str(uuid.uuid4())
    uploaded_at = datetime.utcnow()
    document_metadata = DocumentRecord(
        user_id=user_id,
        document_id=document_id,
        title=filename,
        document_type=file.content_type or expected_content_type,
        date=uploaded_at,
        original_filename=filename,
        content_type=file.content_type or expected_content_type,
        file_size=len(file_data),
        cloudinary_public_id=storage_result["public_id"],
        cloudinary_secure_url=storage_result["secure_url"],
        storage_provider="cloudinary",
        status="uploaded",
        uploaded_at=uploaded_at,
        file_format=storage_result["format"],
        resource_type=storage_result["resource_type"],
    )

    try:
        database["documents"].insert_one(
            document_metadata.model_dump(exclude_none=True)
        )
    except Exception as exc:
        try:
            storage_service.delete_file(storage_result["public_id"])
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to save document metadata.",
        ) from exc

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "document_id": document_id,
            "original_filename": filename,
            "content_type": file.content_type or expected_content_type,
            "file_size": len(file_data),
            "cloudinary_secure_url": storage_result["secure_url"],
            "status": "uploaded",
        },
    )


@router.get("/api/documents/{document_id}")
async def get_document(document_id: str) -> JSONResponse:
    """Retrieve document metadata from MongoDB by document ID."""
    database = get_database()
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB connection is not configured.",
        )

    document = database["documents"].find_one({"document_id": document_id})
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    document.pop("_id", None)
    return JSONResponse(status_code=status.HTTP_200_OK, content=_safe_document_metadata(document))
