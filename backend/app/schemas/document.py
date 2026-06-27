from datetime import datetime

from pydantic import BaseModel


class DocumentSummary(BaseModel):
    id: str
    title: str
    owner_id: str
    updated_at: datetime
