from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime

class NoteIn(BaseModel):
    id: Optional[UUID4] = None
    title: str
    body: str

class NoteOut(NoteIn):
    id: UUID4
    created_at: datetime
    updated_at: datetime

class NoteListResponse(BaseModel):
    items: List[NoteOut]
    total: int
    limit: int
    offset: int
