import uuid
from datetime import datetime

from sqlalchemy import Table, Column, String, Text, TIMESTAMP, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import MetaData
from pgvector.sqlalchemy import Vector

metadata = MetaData()

notes = Table(
    "notes",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("title", String(255), nullable=False),
    Column("body", Text, nullable=False),
    Column("created_at", TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
    Column("updated_at", TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
)

notes_index = Table(
    "notes_index",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("note_id", UUID(as_uuid=True), ForeignKey("notes.id"), nullable=False),
    Column("content", Text, nullable=False),
    Column("chunk_index", Integer, nullable=False),
    Column("embedding", Vector(384), nullable=False),  # all-minilm produces 384-dimensional vectors
    Column("created_at", TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
    Column("updated_at", TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
)
