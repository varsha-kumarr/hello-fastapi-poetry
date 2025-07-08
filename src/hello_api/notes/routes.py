from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, or_, func
from uuid import UUID
from hello_api.db import get_session
from hello_api.notes import models, schema

router = APIRouter()


@router.put("/notes", response_model=schema.NoteResponse)
async def upsert_note(
    note: schema.NoteCreateUpdate,
    session: AsyncSession = Depends(get_session)
):
    if note.id:
        # Update flow
        result = await session.execute(select(models.notes).where(models.notes.c.id == note.id))
        existing_note = result.fetchone()
        if not existing_note:
            raise HTTPException(status_code=404, detail="Note not found")

        await session.execute(
            update(models.notes)
            .where(models.notes.c.id == note.id)
            .values(title=note.title, body=note.body)
        )
        await session.commit()

        result = await session.execute(select(models.notes).where(models.notes.c.id == note.id))
        row = result.fetchone()
        return schema.NoteResponse(**row._mapping)

    else:
        # Create flow
        result = await session.execute(
            insert(models.notes)
            .values(title=note.title, body=note.body)
            .returning(models.notes)
        )
        await session.commit()
        row = result.fetchone()
        return schema.NoteResponse(**row._mapping)


@router.get("/notes/{note_id}", response_model=schema.NoteResponse)
async def get_note(note_id: UUID, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(models.notes).where(models.notes.c.id == note_id))
    note = result.fetchone()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return schema.NoteResponse(**note._mapping)


@router.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: UUID, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(models.notes).where(models.notes.c.id == note_id))
    note = result.fetchone()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    await session.execute(delete(models.notes).where(models.notes.c.id == note_id))
    await session.commit()
    return


@router.get("/notes", response_model=schema.NoteListResponse)
async def list_notes(
    search: str = Query("", alias="search"),
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session)
):
    filters = []
    if search:
        filters.append(
            or_(
                models.notes.c.title.ilike(f"%{search}%"),
                models.notes.c.body.ilike(f"%{search}%")
            )
        )

    total_query = select(func.count()).select_from(models.notes).where(*filters)
    total_result = await session.execute(total_query)
    total = total_result.scalar()

    query = (
        select(models.notes)
        .where(*filters)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    items = [schema.NoteResponse(**row._mapping) for row in result.fetchall()]

    return schema.NoteListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )
