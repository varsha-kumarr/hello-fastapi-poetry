import uuid
from datetime import datetime

from sqlalchemy import Table, Column, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import MetaData

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
