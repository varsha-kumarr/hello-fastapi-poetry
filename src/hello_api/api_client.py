import os
from typing import Optional
from uuid import UUID

import httpx
from pydantic import ValidationError
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from hello_api.notes.schema import NoteCreateUpdate, NoteResponse, NoteListResponse


class APIClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:2005")
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def close(self):
        await self.client.aclose()

    # Upsert a note (create or update)
    async def upsert_note(self, note: NoteCreateUpdate) -> NoteResponse:
        try:
            note_dict = note.dict()
        except ValidationError as e:
            raise ValueError(f"Invalid note data: {e}")

        response = await self.client.put("/notes", json=note_dict)
        response.raise_for_status()
        return NoteResponse(**response.json())
    


    async def get_note(self, note_id: UUID) -> NoteResponse:
        response = await self.client.get(f"/notes/{note_id}")
        response.raise_for_status()
        return NoteResponse(**response.json())

    async def delete_note(self, note_id: UUID) -> None:
        response = await self.client.delete(f"/notes/{note_id}")
        response.raise_for_status()
        return

    async def list_notes(self, search: str = "", limit: int = 20, offset: int = 0) -> NoteListResponse:
        params = {"search": search, "limit": limit, "offset": offset}
        response = await self.client.get("/notes", params=params)
        response.raise_for_status()
        return NoteListResponse(**response.json())