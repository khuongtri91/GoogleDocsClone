from typing import Annotated
from uuid import uuid4

from fastapi import Depends

from app.core.exceptions import BadRequestError, NotFoundError
from app.repositories.document_repository import (
    DocumentRecord,
    DocumentRepository,
    get_document_repository,
)
from app.schemas.document import DocumentCreate, DocumentDetail, DocumentSummary, DocumentUpdate
from app.schemas.user import AuthenticatedUser
from app.services.storage_service import (
    DocumentStorageService,
    get_document_storage_service,
)


class DocumentService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        storage_service: DocumentStorageService,
    ) -> None:
        self._document_repository = document_repository
        self._storage_service = storage_service

    def list_documents(self, user: AuthenticatedUser) -> list[DocumentSummary]:
        return self._document_repository.list_for_user(user.id)

    def create_document(
        self,
        user: AuthenticatedUser,
        payload: DocumentCreate,
    ) -> DocumentDetail:
        title = payload.title.strip()

        if not title:
            raise BadRequestError("Document title is required")

        document_id = str(uuid4())
        storage_path = f"{user.id}/{document_id}.txt"

        try:
            document = self._document_repository.create(
                document_id=document_id,
                owner_id=user.id,
                title=title,
                storage_path=storage_path,
            )
            self._storage_service.upload_text(
                bucket=document.storage_bucket,
                path=document.storage_path,
                content="",
            )
            self._document_repository.commit()
        except Exception:
            self._document_repository.rollback()
            raise

        return self._to_detail(document=document, content="")

    def get_document(self, document_id: str, user: AuthenticatedUser) -> DocumentDetail:
        document = self._document_repository.get_accessible(
            document_id=document_id,
            user_id=user.id,
        )

        if document is None:
            raise NotFoundError("Document not found")

        content = self._storage_service.download_text(
            bucket=document.storage_bucket,
            path=document.storage_path,
        )

        return self._to_detail(document=document, content=content)

    def update_document(
        self,
        document_id: str,
        user: AuthenticatedUser,
        payload: DocumentUpdate,
    ) -> DocumentDetail:
        if payload.title is None and payload.content is None:
            raise BadRequestError("No document changes provided")

        current_document = self._document_repository.get_accessible(
            document_id=document_id,
            user_id=user.id,
        )

        if current_document is None:
            raise NotFoundError("Document not found")

        next_title = payload.title.strip() if payload.title is not None else None

        if next_title == "":
            raise BadRequestError("Document title is required")

        try:
            if payload.content is not None:
                self._storage_service.upload_text(
                    bucket=current_document.storage_bucket,
                    path=current_document.storage_path,
                    content=payload.content,
                )

            updated_document = self._document_repository.update_editable(
                document_id=document_id,
                user_id=user.id,
                title=next_title,
                content_changed=payload.content is not None,
            )

            if updated_document is None:
                raise NotFoundError("Document not found")

            self._document_repository.commit()
        except Exception:
            self._document_repository.rollback()
            raise

        content = (
            payload.content
            if payload.content is not None
            else self._storage_service.download_text(
                bucket=updated_document.storage_bucket,
                path=updated_document.storage_path,
            )
        )

        return self._to_detail(document=updated_document, content=content)

    def delete_document(self, document_id: str, user: AuthenticatedUser) -> None:
        deleted = self._document_repository.soft_delete_owned(
            document_id=document_id,
            owner_id=user.id,
        )

        if not deleted:
            self._document_repository.rollback()
            raise NotFoundError("Document not found")

        self._document_repository.commit()

    def _to_detail(self, document: DocumentRecord, content: str) -> DocumentDetail:
        return DocumentDetail(
            id=document.id,
            title=document.title,
            owner_id=document.owner_id,
            head_revision=document.head_revision,
            updated_at=document.updated_at,
            content=content,
        )


def get_document_service(
    document_repository: Annotated[DocumentRepository, Depends(get_document_repository)],
    storage_service: Annotated[
        DocumentStorageService,
        Depends(get_document_storage_service),
    ],
) -> DocumentService:
    return DocumentService(
        document_repository=document_repository,
        storage_service=storage_service,
    )
