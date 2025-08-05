import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from src.hello_api.embeddings import find_most_similar_note, process_notes_for_indexing
from src.hello_api.qa_simple import answer_question_simple
from src.hello_api.notes.models import notes

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

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

async def get_note_title(session: AsyncSession, note_id: str) -> str:
    """Get the title of a note by its ID."""
    stmt = select(notes.c.title).where(notes.c.id == note_id)
    result = await session.execute(stmt)
    row = result.first()
    return row.title if row else "Unknown"

async def answer_question_interactive(question: str):
    """Answer a single question interactively."""
    async for session in get_session():
        try:
            print(f"\n🔍 Processing question: {question}")
            
            # Find the most similar note
            note_id = await find_most_similar_note(session, question)
            note_title = await get_note_title(session, note_id)
            
            print(f"📚 Retrieved note: {note_title}")
            
            # Generate answer
            answer = await answer_question_simple(session, question)
            
            print(f"💡 Answer: {answer}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        break

async def interactive_test():
    """Interactive testing session."""
    print("🤖 Question Answering System - Interactive Test")
    print("=" * 50)
    print("Type your questions and press Enter. Type 'quit' to exit.")
    print()
    
    while True:
        question = input("❓ Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not question:
            continue
            
        await answer_question_interactive(question)
        print("\n" + "-" * 50)

if __name__ == "__main__":
    print("🚀 Starting interactive question answering system...")
    asyncio.run(interactive_test()) 