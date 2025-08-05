from sqlalchemy.ext.asyncio import AsyncSession
from .embeddings import find_most_similar_note, get_note_content
import ollama

async def answer_question_simple(
    session: AsyncSession,
    question: str
) -> str:
    """Answer a question by retrieving the most relevant note content."""
    try:
        # Find the most similar note
        note_id = await find_most_similar_note(session, question)
        
        # Get the note content
        note_content = await get_note_content(session, note_id)
        
        # Generate answer using llama3.2
        import os
        import asyncio
        ollama_host = os.getenv('OLLAMA_HOST', 'localhost')
        client = ollama.Client(host=f"http://{ollama_host}:11434")
        
        try:
            # Add timeout to prevent hanging
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    client.chat,
                    model="llama3",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided study notes. Answer the question accurately using only the information from the notes."},
                        {"role": "user", "content": f"Notes:\n{note_content}\n\nQuestion: {question}"}
                    ]
                ),
                timeout=60.0
            )
            
            return response["message"]["content"]
        except asyncio.TimeoutError:
            return f"Answer generation timed out. Here's the relevant note content:\n\n{note_content[:500]}..."
        except Exception as e:
            return f"Error generating answer: {str(e)}. Here's the relevant note content:\n\n{note_content[:500]}..."
    
    except Exception as e:
        return f"Error answering question: {str(e)}"

async def answer_question_with_note_id_simple(
    session: AsyncSession,
    question: str,
    note_id: str
) -> str:
    """Answer a question using a specific note as context."""
    try:
        # Get the note content
        note_content = await get_note_content(session, note_id)
        
        # Return a simple answer based on the note content
        return f"Based on the specified note, here is the relevant information:\n\n{note_content[:500]}..."
    
    except Exception as e:
        return f"Error answering question: {str(e)}" 