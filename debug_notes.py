import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from src.hello_api.notes.models import notes, notes_index

# Override environment for local connection
os.environ['DB_HOST'] = 'localhost'

# Create engine for local connection
DATABASE_URL = (
    f"postgresql+asyncpg://postgres:postgres@localhost:5432/notes_db"
)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def debug_notes():
    """Debug function to check notes and test vector similarity."""
    async with async_session() as session:
        # Check what notes exist
        stmt = select(notes.c.id, notes.c.title, notes.c.body)
        result = await session.execute(stmt)
        all_notes = result.fetchall()
        
        print(f"Found {len(all_notes)} notes:")
        for note in all_notes:
            print(f"  ID: {note.id}")
            print(f"  Title: {note.title}")
            print(f"  Body preview: {note.body[:100]}...")
            print()
        
        # Check what's in the notes_index
        stmt = select(notes_index.c.note_id, notes_index.c.chunk_index, notes_index.c.content)
        result = await session.execute(stmt)
        all_chunks = result.fetchall()
        
        print(f"Found {len(all_chunks)} chunks in notes_index:")
        for chunk in all_chunks[:5]:  # Show first 5 chunks
            print(f"  Note ID: {chunk.note_id}")
            print(f"  Chunk Index: {chunk.chunk_index}")
            print(f"  Content preview: {chunk.content[:100]}...")
            print()
        
        # Test a simple vector similarity query
        test_query = "What is the periodic table?"
        print(f"Testing similarity for: {test_query}")
        
        # Get a sample embedding from the database
        stmt = select(notes_index.c.embedding).limit(1)
        result = await session.execute(stmt)
        sample_embedding = result.scalar()
        
        if sample_embedding:
            print(f"Sample embedding type: {type(sample_embedding)}")
            print(f"Sample embedding preview: {str(sample_embedding)[:100]}...")
            
            # Test similarity with a higher threshold
            query = text("""
                SELECT note_id, COUNT(*) as chunk_count
                FROM notes_index
                WHERE embedding <=> :embedding < 1.0
                GROUP BY note_id
                ORDER BY chunk_count DESC
                LIMIT 5
            """)
            
            result = await session.execute(query, {"embedding": sample_embedding})
            rows = result.fetchall()
            
            print(f"Found {len(rows)} similar notes with threshold 1.0:")
            for row in rows:
                print(f"  Note ID: {row.note_id}, Chunks: {row.chunk_count}")

if __name__ == "__main__":
    asyncio.run(debug_notes()) 