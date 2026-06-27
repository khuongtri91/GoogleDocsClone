from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.document import DocumentSummary
from app.schemas.user import AuthenticatedUser
from app.services.document_service import DocumentService, get_document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
async def get_documents(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> list[DocumentSummary]:
    return document_service.list_documents(current_user)
