import ollama
from sqlalchemy.ext.asyncio import AsyncSession
from .embeddings import find_most_similar_note, get_note_content

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided study notes. 
Answer the question accurately using only the information from the notes. 
If the notes don't contain enough information to answer the question, say so.
Be concise but thorough in your response."""

async def answer_question_with_context(
    session: AsyncSession,
    question: str
) -> str:
    """Answer a question using the most relevant note as context."""
    try:
        # Find the most similar note
        note_id = await find_most_similar_note(session, question)
        
        # Get the note content
        note_content = await get_note_content(session, note_id)
        
        # Generate answer using llama3.2
        response = await ollama.chat(
            model="llama3",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Notes:\n{note_content}\n\nQuestion: {question}"}
            ]
        )
        
        return response["message"]["content"]
    
    except Exception as e:
        return f"Error answering question: {str(e)}"

async def answer_question_with_note_id(
    session: AsyncSession,
    question: str,
    note_id: str
) -> str:
    """Answer a question using a specific note as context."""
    try:
        # Get the note content
        note_content = await get_note_content(session, note_id)
        
        # Generate answer using llama3.2
        response = await ollama.chat(
            model="llama3",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Notes:\n{note_content}\n\nQuestion: {question}"}
            ]
        )
        
        return response["message"]["content"]
    
    except Exception as e:
        return f"Error answering question: {str(e)}" 