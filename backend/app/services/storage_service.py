from typing import Annotated
from urllib.parse import quote

import httpx
from fastapi import Depends

from app.core.config import Settings, get_settings
from app.core.exceptions import ConfigurationError, NotFoundError, UpstreamServiceError


class DocumentStorageService:
    def __init__(self, settings: Settings) -> None:
        if not settings.supabase_secret_key:
            raise ConfigurationError("SUPABASE_SECRET_KEY is required for storage access")

        self._supabase_url = settings.supabase_url.rstrip("/")
        self._service_key = settings.supabase_secret_key

    def download_text(self, bucket: str, path: str) -> str:
        response = httpx.get(
            self._object_url(bucket, path),
            headers=self._headers(),
            timeout=10,
        )

        if response.status_code == 404:
            raise NotFoundError("Document content not found")

        response.raise_for_status()
        return response.text

    def upload_text(self, bucket: str, path: str, content: str) -> None:
        response = httpx.put(
            self._object_url(bucket, path),
            content=content.encode("utf-8"),
            headers={
                **self._headers(),
                "Content-Type": "text/plain",
                "x-upsert": "true",
            },
            timeout=10,
        )

        if response.is_error:
            raise UpstreamServiceError("Failed to upload document content")

    def _headers(self) -> dict[str, str]:
        return {
            "apikey": self._service_key,
            "Authorization": f"Bearer {self._service_key}",
        }

    def _object_url(self, bucket: str, path: str) -> str:
        encoded_path = quote(path, safe="/")
        return f"{self._supabase_url}/storage/v1/object/{bucket}/{encoded_path}"


def get_document_storage_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> DocumentStorageService:
    return DocumentStorageService(settings=settings)
