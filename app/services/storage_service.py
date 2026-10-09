"""Reusable Cloudinary storage service for health documents."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import cloudinary
from cloudinary import api, uploader

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


class CloudinaryStorageService:
    """Upload and manage files in Cloudinary without exposing credentials."""

    def __init__(self) -> None:
        self.cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME", "").strip()
        self.api_key = os.getenv("CLOUDINARY_API_KEY", "").strip()
        self.api_secret = os.getenv("CLOUDINARY_API_SECRET", "").strip()

        if not all((self.cloud_name, self.api_key, self.api_secret)):
            raise RuntimeError("Cloudinary configuration is incomplete")

        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    def upload_file(
        self,
        file_data: bytes,
        original_filename: str,
        content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a supported file and return safe metadata only."""
        extension = Path(original_filename).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError(
                "Unsupported file type. Allowed formats are PDF, JPG, JPEG, and PNG."
            )

        resource_type = "raw" if extension == ".pdf" else "image"
        file_format = extension.lstrip(".").lower()
        if file_format == "jpeg":
            file_format = "jpg"

        uploaded = uploader.upload(
            file_data,
            resource_type=resource_type,
            filename=Path(original_filename).name,
            use_filename=True,
            unique_filename=True,
            overwrite=False,
        )

        return {
            "public_id": uploaded.get("public_id"),
            "secure_url": uploaded.get("secure_url"),
            "resource_type": uploaded.get("resource_type", resource_type),
            "format": uploaded.get("format", file_format),
        }

    def delete_file(self, public_id: str) -> None:
        """Delete a Cloudinary resource by public ID."""
        api.delete_resources([public_id])

    def get_file_reference(self, public_id: str) -> Dict[str, Any]:
        """Return a safe reference for an existing Cloudinary resource."""
        resource = api.resource(public_id)
        return {
            "public_id": resource.get("public_id"),
            "secure_url": resource.get("secure_url"),
            "resource_type": resource.get("resource_type"),
        }


def upload_file(
    file_data: bytes,
    original_filename: str,
    content_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Upload a file using the service defaults."""
    return CloudinaryStorageService().upload_file(
        file_data,
        original_filename,
        content_type,
    )


def delete_file(public_id: str) -> None:
    """Delete a Cloudinary resource using the service defaults."""
    CloudinaryStorageService().delete_file(public_id)


def get_file_reference(public_id: str) -> Dict[str, Any]:
    """Retrieve a safe Cloudinary reference using the service defaults."""
    return CloudinaryStorageService().get_file_reference(public_id)
