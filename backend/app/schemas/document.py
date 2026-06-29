from datetime import datetime

from pydantic import BaseModel, Field


class DocumentSummary(BaseModel):
    id: str
    title: str
    owner_id: str
    head_revision: int
    updated_at: datetime


class DocumentDetail(DocumentSummary):
    content: str


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = None
