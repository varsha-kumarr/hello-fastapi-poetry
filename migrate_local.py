import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from src.hello_api.notes.models import metadata

# Override environment for local connection
os.environ['DB_HOST'] = 'localhost'

# Create engine for local connection
DATABASE_URL = (
    f"postgresql+asyncpg://postgres:postgres@localhost:5432/notes_db"
)

engine = create_async_engine(DATABASE_URL, echo=True)

async def run_migrations():
    """Run database migrations to set up pgvector and create tables."""
    async with engine.begin() as conn:
        # Enable pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        
        # Create tables
        await conn.run_sync(metadata.create_all)
        
        # Create index for vector similarity search
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS notes_index_embedding_idx 
            ON notes_index 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """))
        
        print("Migrations completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_migrations()) 