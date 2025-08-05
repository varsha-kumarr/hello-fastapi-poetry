import asyncio
from sqlalchemy import text
from .db import engine
from .notes.models import metadata

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