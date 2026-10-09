"""Regression tests for document uploads."""

import json
import os
import unittest
from io import BytesIO
from unittest.mock import Mock, patch

from fastapi import HTTPException, UploadFile

from app.routes.storage import get_document, upload_document
from app.services.storage_service import CloudinaryStorageService


class CloudinaryStorageServiceTests(unittest.TestCase):
    @patch("app.services.storage_service.uploader.upload")
    @patch("app.services.storage_service.cloudinary.config")
    def test_upload_returns_only_safe_metadata(self, mock_config, mock_upload):
        mock_upload.return_value = {
            "public_id": "sample/public-id",
            "secure_url": "https://res.cloudinary.com/example/sample/public-id",
            "resource_type": "image",
            "format": "jpg",
        }

        with patch.dict(
            os.environ,
            {
                "CLOUDINARY_CLOUD_NAME": "example",
                "CLOUDINARY_API_KEY": "key",
                "CLOUDINARY_API_SECRET": "secret",
            },
        ):
            service = CloudinaryStorageService()
            result = service.upload_file(
                b"fake-image",
                "document.jpg",
                "image/jpeg",
            )

        self.assertEqual(result["public_id"], "sample/public-id")
        self.assertEqual(result["secure_url"], "https://res.cloudinary.com/example/sample/public-id")
        self.assertEqual(result["resource_type"], "image")
        self.assertEqual(result["format"], "jpg")
        self.assertNotIn("api_key", result)
        self.assertNotIn("api_secret", result)
        self.assertNotIn("cloud_name", result)


class DocumentUploadRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_upload_saves_metadata_and_returns_safe_response(self):
        upload = UploadFile(
            filename="report.pdf",
            file=BytesIO(b"%PDF-1.4"),
            content_type="application/pdf",
        )
        storage_service = Mock()
        storage_service.upload_file.return_value = {
            "public_id": "sample/report",
            "secure_url": "https://res.cloudinary.com/example/sample/report",
            "resource_type": "raw",
            "format": "pdf",
        }
        database = Mock()
        database.__getitem__.return_value.insert_one.return_value = Mock()

        with patch(
            "app.routes.storage.CloudinaryStorageService",
            return_value=storage_service,
        ), patch("app.routes.storage.get_database", return_value=database):
            response = await upload_document(
                file=upload,
                user_id="demo-user",
            )

        payload = json.loads(response.body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(payload["document_id"])
        self.assertEqual(payload["original_filename"], "report.pdf")
        self.assertEqual(payload["content_type"], "application/pdf")
        self.assertEqual(payload["file_size"], len(b"%PDF-1.4"))
        self.assertEqual(
            payload["cloudinary_secure_url"],
            storage_service.upload_file.return_value["secure_url"],
        )
        self.assertNotIn("cloudinary_public_id", payload)
        self.assertNotIn("api_key", str(payload))

    async def test_rejects_unsupported_file_extension(self):
        upload = UploadFile(
            filename="report.docx",
            file=BytesIO(b"unsupported"),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        with self.assertRaises(HTTPException) as context:
            await upload_document(file=upload, user_id="demo-user")

        self.assertEqual(context.exception.status_code, 400)

    async def test_get_document_retrieves_metadata(self):
        document = {
            "document_id": "document-1",
            "user_id": "demo-user",
            "original_filename": "report.pdf",
            "content_type": "application/pdf",
            "file_size": 100,
            "cloudinary_public_id": "sample/report",
            "cloudinary_secure_url": "https://res.cloudinary.com/example/sample/report",
            "storage_provider": "cloudinary",
            "status": "uploaded",
        }
        database = Mock()
        database.__getitem__.return_value.find_one.return_value = document

        with patch("app.routes.storage.get_database", return_value=database):
            response = await get_document(document_id="document-1")

        payload = json.loads(response.body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["document_id"], "document-1")
        self.assertNotIn("cloudinary_public_id", payload)
        self.assertNotIn("cloudinary_secure_url", payload)


if __name__ == "__main__":
    unittest.main()
