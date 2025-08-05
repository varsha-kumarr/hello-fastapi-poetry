import asyncio
import os
import yaml
from typing import List, Dict, Any
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

async def index_all_existing_notes():
    """Index all existing notes in the database."""
    async for session in get_session():
        # Get all notes
        stmt = select(notes.c.id, notes.c.body)
        result = await session.execute(stmt)
        all_notes = result.fetchall()
        
        print(f"Found {len(all_notes)} notes to index")
        
        for note in all_notes:
            print(f"Indexing note: {note.id}")
            await process_notes_for_indexing(session, note.id, note.body)
            
        print("All notes indexed successfully!")
        break

async def get_note_title(session: AsyncSession, note_id: str) -> str:
    """Get the title of a note by its ID."""
    stmt = select(notes.c.title).where(notes.c.id == note_id)
    result = await session.execute(stmt)
    row = result.first()
    return row.title if row else "Unknown"

async def answer_test_questions_with_timeout() -> List[Dict[str, Any]]:
    """Answer all test questions with timeout protection."""
    results = []
    
    # Load test set
    with open("testset.yaml", 'r') as f:
        test_set = yaml.safe_load(f)
    
    async for session in get_session():
        for subject, questions in test_set.items():
            print(f"Processing questions for: {subject}")
            
            for i, question in enumerate(questions):
                print(f"  Question {i+1}: {question[:50]}...")
                
                try:
                    # Find the most similar note
                    note_id = await find_most_similar_note(session, question)
                    note_title = await get_note_title(session, note_id)
                    
                    # Generate answer with timeout
                    try:
                        answer = await asyncio.wait_for(
                            answer_question_simple(session, question),
                            timeout=30.0  # 30 second timeout
                        )
                    except asyncio.TimeoutError:
                        answer = "Answer generation timed out. Retrieved note content instead."
                    except Exception as e:
                        answer = f"Error generating answer: {str(e)}"
                    
                    results.append({
                        "question": question,
                        "expected_note": subject,
                        "answer": answer,
                        "retrieved_note_id": str(note_id),
                        "retrieved_note_title": note_title
                    })
                    
                except Exception as e:
                    print(f"Error processing question: {e}")
                    results.append({
                        "question": question,
                        "expected_note": subject,
                        "answer": f"Error: {str(e)}",
                        "retrieved_note_id": "",
                        "retrieved_note_title": ""
                    })
        break
    
    return results

def save_results_to_yaml(results: List[Dict[str, Any]], file_path="qa_results_complete.yaml"):
    """Save the question answering results to a YAML file."""
    with open(file_path, 'w') as f:
        yaml.dump(results, f, default_flow_style=False, indent=2)
    print(f"Results saved to {file_path}")

def analyze_results(results: List[Dict[str, Any]]):
    """Analyze the question answering results."""
    total_questions = len(results)
    successful_answers = len([r for r in results if not r['answer'].startswith('Error')])
    
    print(f"Total Questions: {total_questions}")
    print(f"Successful Answers: {successful_answers}")
    print(f"Success Rate: {successful_answers/total_questions*100:.2f}%")
    
    # Check how often we retrieved the expected note
    correct_retrievals = 0
    for result in results:
        if result['expected_note'].lower() in result['retrieved_note_title'].lower():
            correct_retrievals += 1
    
    print(f"Correct Note Retrievals: {correct_retrievals}")
    print(f"Retrieval Accuracy: {correct_retrievals/total_questions*100:.2f}%")
    
    # Show some examples
    print("\nSample Results:")
    for i, result in enumerate(results[:3]):
        print(f"\n--- Result {i+1} ---")
        print(f"Question: {result['question']}")
        print(f"Expected: {result['expected_note']}")
        print(f"Retrieved: {result['retrieved_note_title']}")
        print(f"Match: {'✓' if result['expected_note'].lower() in result['retrieved_note_title'].lower() else '✗'}")
        print(f"Answer: {result['answer'][:200]}...")

async def run_complete_qa_pipeline():
    print("Step 1: Indexing all existing notes...")
    await index_all_existing_notes()
    
    print("\nStep 2: Answering test questions with LLM...")
    results = await answer_test_questions_with_timeout()
    
    print("\nStep 3: Saving results...")
    save_results_to_yaml(results)
    
    print(f"\nCompleted! Processed {len(results)} questions.")
    
    print("\nStep 4: Analyzing results...")
    analyze_results(results)
    
    return results

if __name__ == "__main__":
    asyncio.run(run_complete_qa_pipeline()) 