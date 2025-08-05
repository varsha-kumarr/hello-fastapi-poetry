from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional

from ..schemas import NoteIn, NoteOut, NoteListResponse
from ..db import async_session

router = APIRouter()

async def get_db():
    async with async_session() as session:
        yield session

@router.put("", response_model=NoteOut)
async def upsert_note(note: NoteIn, db: AsyncSession = Depends(get_db)):
    if note.id:
        query = text("SELECT * FROM notes WHERE id = :id")
        result = await db.execute(query, {"id": str(note.id)})
        existing = result.fetchone()

        if not existing:
            raise HTTPException(status_code=404, detail="Note not found")

        update_query = text("""
            UPDATE notes
            SET title = :title, body = :body, updated_at = now()
            WHERE id = :id
            RETURNING *
        """)
        values = {"id": str(note.id), "title": note.title, "body": note.body}
        result = await db.execute(update_query, values)
        await db.commit()
        row = result.fetchone()
    else:
        insert_query = text("""
            INSERT INTO notes (title, body)
            VALUES (:title, :body)
            RETURNING *
        """)
        result = await db.execute(insert_query, {"title": note.title, "body": note.body})
        await db.commit()
        row = result.fetchone()

    return NoteOut(**dict(row._mapping))


@router.delete("/{note_id}", status_code=204)
async def delete_note(note_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("DELETE FROM notes WHERE id = :id RETURNING id"),
        {"id": str(note_id)}
    )
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Note not found")


@router.get("/{note_id}", response_model=NoteOut)
async def get_note(note_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM notes WHERE id = :id"),
        {"id": str(note_id)}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteOut(**dict(row._mapping))


@router.get("", response_model=NoteListResponse)
async def list_notes(
    search: Optional[str] = None,
    limit: int = Query(default=20, ge=1),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    base_query = "FROM notes WHERE 1=1"
    params: dict[str, object] = {}

    if search:
        base_query += " AND (title ILIKE :search OR body ILIKE :search)"
        params["search"] = f"%{search}%"

    count_query = text(f"SELECT COUNT(*) {base_query}")
    total = await db.execute(count_query, params)
    total_count = total.scalar()

    list_query = text(f"""
        SELECT * {base_query}
        ORDER BY updated_at DESC
        LIMIT :limit OFFSET :offset
    """)
    params.update({"limit": limit, "offset": offset})
    result = await db.execute(list_query, params)

    items = [NoteOut(**dict(row._mapping)) for row in result.fetchall()]

    return NoteListResponse(
        items=items,
        total=total_count or 0,
        limit=limit,
        offset=offset
    )
