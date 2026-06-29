import httpx

from app.core.config import Settings
from app.services.storage_service import DocumentStorageService


def build_settings() -> Settings:
    return Settings(
        frontend_origins=["http://localhost:5173"],
        supabase_url="https://example.supabase.co",
        supabase_publishable_key="publishable-key",
        supabase_secret_key="service-key",
        database_url="postgresql://user:pass@localhost/db",
    )


def test_upload_text_uses_plain_text_mime_type(
    monkeypatch,
) -> None:
    captured_headers: dict[str, str] = {}

    def fake_put(
        url: str,
        content: bytes,
        headers: dict[str, str],
        timeout: int,
    ) -> httpx.Response:
        captured_headers.update(headers)
        return httpx.Response(status_code=200)

    monkeypatch.setattr(httpx, "put", fake_put)

    service = DocumentStorageService(settings=build_settings())
    service.upload_text("document-snapshots", "user/document.txt", "Hello")

    assert captured_headers["Content-Type"] == "text/plain"
    assert captured_headers["x-upsert"] == "true"
