import ollama
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
import asyncio
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from .notes.models import notes_index, notes
import uuid

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

async def split_text_into_chunks(text: str) -> List[str]:
    """Split text into chunks using RecursiveCharacterTextSplitter."""
    chunks = text_splitter.split_text(text)
    return chunks

async def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts using all-minilm model."""
    import os
    embeddings = []
    
    # Use custom Ollama host if specified
    ollama_host = os.getenv('OLLAMA_HOST', 'localhost')
    client = ollama.Client(host=f"http://{ollama_host}:11434")
    
    for text in texts:
        response = client.embeddings(
            model="all-minilm",
            prompt=text
        )
        embeddings.append(response['embedding'])
    return embeddings

async def upsert_chunks_with_embeddings(
    session: AsyncSession,
    note_id: uuid.UUID,
    chunks: List[str],
    embeddings: List[List[float]]
) -> None:
    """Upsert chunks and their embeddings into the NotesIndex table."""
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        # Check if chunk already exists for this note and index
        stmt = select(notes_index).where(
            notes_index.c.note_id == note_id,
            notes_index.c.chunk_index == i
        )
        result = await session.execute(stmt)
        existing = result.first()
        
        if existing:
            # Update existing chunk
            await session.execute(
                notes_index.update().where(
                    notes_index.c.note_id == note_id,
                    notes_index.c.chunk_index == i
                ).values(
                    content=chunk,
                    embedding=embedding
                )
            )
        else:
            # Insert new chunk
            await session.execute(
                notes_index.insert().values(
                    id=uuid.uuid4(),
                    note_id=note_id,
                    content=chunk,
                    chunk_index=i,
                    embedding=embedding
                )
            )
    
    await session.commit()

async def process_notes_for_indexing(
    session: AsyncSession,
    note_id: uuid.UUID,
    note_content: str
) -> None:
    """Process a note for indexing: split, embed, and store chunks."""
    # Split text into chunks
    chunks = await split_text_into_chunks(note_content)
    
    # Generate embeddings for chunks
    embeddings = await generate_embeddings(chunks)
    
    # Upsert chunks and embeddings
    await upsert_chunks_with_embeddings(session, note_id, chunks, embeddings)

async def find_most_similar_note(
    session: AsyncSession,
    question: str,
    k: int = 15
) -> uuid.UUID:
    """Find the most similar note to a question using KNN search."""
    # Generate embedding for the question
    question_embedding = await generate_embeddings([question])
    question_vector = question_embedding[0]
    
    # Convert list to string format for pgvector
    vector_str = "[" + ",".join(map(str, question_vector)) + "]"
    
    # Use raw SQL for vector similarity search with better threshold
    from sqlalchemy import text
    query = text(f"""
        SELECT note_id, COUNT(*) as chunk_count, 
               AVG(embedding <=> '{vector_str}'::vector) as avg_distance
        FROM notes_index
        WHERE embedding <=> '{vector_str}'::vector < 0.8
        GROUP BY note_id
        ORDER BY avg_distance ASC, chunk_count DESC
        LIMIT {k}
    """)
    
    result = await session.execute(query)
    rows = result.fetchall()
    
    if not rows:
        # If no results with strict threshold, try with a more lenient one
        query = text(f"""
            SELECT note_id, COUNT(*) as chunk_count, 
                   AVG(embedding <=> '{vector_str}'::vector) as avg_distance
            FROM notes_index
            WHERE embedding <=> '{vector_str}'::vector < 1.0
            GROUP BY note_id
            ORDER BY avg_distance ASC, chunk_count DESC
            LIMIT {k}
        """)
        
        result = await session.execute(query)
        rows = result.fetchall()
        
        if not rows:
            raise ValueError("No similar notes found")
    
    # Return the note_id with the best average distance
    return rows[0].note_id

async def get_note_content(session: AsyncSession, note_id: uuid.UUID) -> str:
    """Get the content of a note by its ID."""
    stmt = select(notes.c.body).where(notes.c.id == note_id)
    result = await session.execute(stmt)
    row = result.first()
    
    if not row:
        raise ValueError(f"Note with ID {note_id} not found")
    
    return row.body 