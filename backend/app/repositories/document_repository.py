from app.schemas.document import DocumentSummary


class DocumentRepository:
    def list_for_user(self, user_id: str) -> list[DocumentSummary]:
        return []


def get_document_repository() -> DocumentRepository:
    return DocumentRepository()
