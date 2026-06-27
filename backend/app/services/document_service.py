from app.repositories.document_repository import (
    DocumentRepository,
    get_document_repository,
)
from app.schemas.document import DocumentSummary
from app.schemas.user import AuthenticatedUser


class DocumentService:
    def __init__(self, document_repository: DocumentRepository) -> None:
        self._document_repository = document_repository

    def list_documents(self, user: AuthenticatedUser) -> list[DocumentSummary]:
        return self._document_repository.list_for_user(user.id)


def get_document_service() -> DocumentService:
    return DocumentService(document_repository=get_document_repository())
