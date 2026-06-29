from datetime import UTC, datetime

import pytest

from app.core.exceptions import BadRequestError, NotFoundError
from app.repositories.document_repository import DocumentRecord
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.schemas.user import AuthenticatedUser
from app.services.document_service import DocumentService


class FakeDocumentRepository:
    def __init__(self) -> None:
        self.documents: dict[str, DocumentRecord] = {}
        self.created_storage_paths: list[str] = []
        self.commits = 0
        self.rollbacks = 0
        self.deleted_document_ids: list[str] = []

    def list_for_user(self, user_id: str) -> list[DocumentRecord]:
        return list(self.documents.values())

    def get_accessible(
        self,
        document_id: str,
        user_id: str,
    ) -> DocumentRecord | None:
        return self.documents.get(document_id)

    def create(
        self,
        document_id: str,
        owner_id: str,
        title: str,
        storage_path: str,
    ) -> DocumentRecord:
        document = build_document_record(
            document_id=document_id,
            owner_id=owner_id,
            title=title,
            storage_path=storage_path,
        )
        self.documents[document_id] = document
        self.created_storage_paths.append(storage_path)
        return document

    def update_editable(
        self,
        document_id: str,
        user_id: str,
        title: str | None,
        content_changed: bool,
    ) -> DocumentRecord | None:
        current_document = self.documents.get(document_id)

        if current_document is None:
            return None

        updated_document = DocumentRecord(
            id=current_document.id,
            title=title or current_document.title,
            owner_id=current_document.owner_id,
            storage_bucket=current_document.storage_bucket,
            storage_path=current_document.storage_path,
            head_revision=(
                current_document.head_revision + 1
                if content_changed
                else current_document.head_revision
            ),
            updated_at=current_document.updated_at,
        )
        self.documents[document_id] = updated_document
        return updated_document

    def soft_delete_owned(self, document_id: str, owner_id: str) -> bool:
        document = self.documents.get(document_id)

        if document is None or document.owner_id != owner_id:
            return False

        self.deleted_document_ids.append(document_id)
        del self.documents[document_id]
        return True

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


class FakeDocumentStorageService:
    def __init__(self) -> None:
        self.content_by_path: dict[str, str] = {}
        self.fail_upload = False

    def download_text(self, bucket: str, path: str) -> str:
        return self.content_by_path[path]

    def upload_text(self, bucket: str, path: str, content: str) -> None:
        if self.fail_upload:
            raise RuntimeError("upload failed")

        self.content_by_path[path] = content


def build_document_record(
    document_id: str = "document-1",
    owner_id: str = "user-1",
    title: str = "Document",
    storage_path: str = "user-1/document-1.txt",
) -> DocumentRecord:
    return DocumentRecord(
        id=document_id,
        title=title,
        owner_id=owner_id,
        storage_bucket="document-snapshots",
        storage_path=storage_path,
        head_revision=0,
        updated_at=datetime(2026, 6, 29, tzinfo=UTC),
    )


@pytest.fixture
def user() -> AuthenticatedUser:
    return AuthenticatedUser(id="user-1", email="tri@example.com")


@pytest.fixture
def repository() -> FakeDocumentRepository:
    return FakeDocumentRepository()


@pytest.fixture
def storage_service() -> FakeDocumentStorageService:
    return FakeDocumentStorageService()


@pytest.fixture
def document_service(
    repository: FakeDocumentRepository,
    storage_service: FakeDocumentStorageService,
) -> DocumentService:
    return DocumentService(
        document_repository=repository,
        storage_service=storage_service,
    )


def test_create_document_trims_title_and_writes_empty_snapshot(
    document_service: DocumentService,
    repository: FakeDocumentRepository,
    storage_service: FakeDocumentStorageService,
    user: AuthenticatedUser,
) -> None:
    document = document_service.create_document(
        user=user,
        payload=DocumentCreate(title="  Design notes  "),
    )

    assert document.title == "Design notes"
    assert document.content == ""
    assert repository.commits == 1
    assert repository.rollbacks == 0
    assert repository.created_storage_paths == [f"{user.id}/{document.id}.txt"]
    assert storage_service.content_by_path[f"{user.id}/{document.id}.txt"] == ""


def test_create_document_rolls_back_when_storage_upload_fails(
    document_service: DocumentService,
    repository: FakeDocumentRepository,
    storage_service: FakeDocumentStorageService,
    user: AuthenticatedUser,
) -> None:
    storage_service.fail_upload = True

    with pytest.raises(RuntimeError, match="upload failed"):
        document_service.create_document(
            user=user,
            payload=DocumentCreate(title="Draft"),
        )

    assert repository.commits == 0
    assert repository.rollbacks == 1


def test_get_document_downloads_content(
    document_service: DocumentService,
    repository: FakeDocumentRepository,
    storage_service: FakeDocumentStorageService,
    user: AuthenticatedUser,
) -> None:
    repository.documents["document-1"] = build_document_record()
    storage_service.content_by_path["user-1/document-1.txt"] = "Hello"

    document = document_service.get_document("document-1", user)

    assert document.id == "document-1"
    assert document.content == "Hello"


def test_get_document_raises_not_found_for_inaccessible_document(
    document_service: DocumentService,
    user: AuthenticatedUser,
) -> None:
    with pytest.raises(NotFoundError):
        document_service.get_document("missing-document", user)


def test_update_document_uploads_content_and_increments_revision(
    document_service: DocumentService,
    repository: FakeDocumentRepository,
    storage_service: FakeDocumentStorageService,
    user: AuthenticatedUser,
) -> None:
    repository.documents["document-1"] = build_document_record()
    storage_service.content_by_path["user-1/document-1.txt"] = "Before"

    document = document_service.update_document(
        document_id="document-1",
        user=user,
        payload=DocumentUpdate(title=" Updated ", content="After"),
    )

    assert document.title == "Updated"
    assert document.content == "After"
    assert document.head_revision == 1
    assert storage_service.content_by_path["user-1/document-1.txt"] == "After"
    assert repository.commits == 1


def test_update_document_rejects_empty_payload(
    document_service: DocumentService,
    user: AuthenticatedUser,
) -> None:
    with pytest.raises(BadRequestError, match="No document changes provided"):
        document_service.update_document(
            document_id="document-1",
            user=user,
            payload=DocumentUpdate(),
        )


def test_update_document_rejects_blank_title(
    document_service: DocumentService,
    repository: FakeDocumentRepository,
    user: AuthenticatedUser,
) -> None:
    repository.documents["document-1"] = build_document_record()

    with pytest.raises(BadRequestError, match="Document title is required"):
        document_service.update_document(
            document_id="document-1",
            user=user,
            payload=DocumentUpdate(title="   "),
        )


def test_delete_document_commits_owner_delete(
    document_service: DocumentService,
    repository: FakeDocumentRepository,
    user: AuthenticatedUser,
) -> None:
    repository.documents["document-1"] = build_document_record()

    document_service.delete_document("document-1", user)

    assert repository.deleted_document_ids == ["document-1"]
    assert repository.commits == 1
    assert repository.rollbacks == 0


def test_delete_document_rolls_back_when_document_is_missing(
    document_service: DocumentService,
    repository: FakeDocumentRepository,
    user: AuthenticatedUser,
) -> None:
    with pytest.raises(NotFoundError):
        document_service.delete_document("missing-document", user)

    assert repository.commits == 0
    assert repository.rollbacks == 1
