# app/schemas/document.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentBase(BaseModel):
    title: str
    content: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    file_path: str
    summary: Optional[str] = None
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True