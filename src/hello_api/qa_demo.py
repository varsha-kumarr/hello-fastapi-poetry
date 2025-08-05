from sqlalchemy.ext.asyncio import AsyncSession
from .embeddings import find_most_similar_note, get_note_content

async def answer_question_demo(
    session: AsyncSession,
    question: str
) -> str:
    """Answer a question for demo purposes without requiring Ollama."""
    try:
        # Find the most similar note
        note_id = await find_most_similar_note(session, question)
        
        # Get the note content
        note_content = await get_note_content(session, note_id)
        
        # Return a formatted answer for demo
        return f"Based on the retrieved note, here is the relevant information:\n\n{note_content[:500]}..."
    
    except Exception as e:
        return f"Error answering question: {str(e)}"

async def answer_question_with_note_id_demo(
    session: AsyncSession,
    question: str,
    note_id: str
) -> str:
    """Answer a question using a specific note for demo purposes."""
    try:
        # Get the note content
        note_content = await get_note_content(session, note_id)
        
        # Return a formatted answer for demo
        return f"Based on the specified note, here is the relevant information:\n\n{note_content[:500]}..."
    
    except Exception as e:
        return f"Error answering question: {str(e)}" 