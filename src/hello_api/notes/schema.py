from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class NoteCreateUpdate(BaseModel):
    id: Optional[UUID] = None
    title: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1)

class NoteResponse(BaseModel):
    id: UUID
    title: str
    body: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # Required to allow conversion from SQLAlchemy rows

class NoteListResponse(BaseModel):
    items: List[NoteResponse]
    total: int
    limit: int
    offset: int
