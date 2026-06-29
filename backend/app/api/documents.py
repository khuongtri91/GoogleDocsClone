from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.core.security import get_current_user
from app.schemas.document import DocumentCreate, DocumentDetail, DocumentSummary, DocumentUpdate
from app.schemas.user import AuthenticatedUser
from app.services.document_service import DocumentService, get_document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
async def get_documents(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> list[DocumentSummary]:
    return document_service.list_documents(current_user)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_document(
    payload: DocumentCreate,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentDetail:
    return document_service.create_document(current_user, payload)


@router.get("/{document_id}")
def get_document(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentDetail:
    return document_service.get_document(str(document_id), current_user)


@router.patch("/{document_id}")
def update_document(
    document_id: UUID,
    payload: DocumentUpdate,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentDetail:
    return document_service.update_document(str(document_id), current_user, payload)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> Response:
    document_service.delete_document(str(document_id), current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
