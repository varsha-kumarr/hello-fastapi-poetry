from fastapi import FastAPI
from hello_api.config import settings
from fastapi import APIRouter
from hello_api.notes.routes import router as notes_router

app = FastAPI()

@app.get("/hello")
def say_hello():
    return {"message": f"Hello, welcome to {settings.project_name}!"}

@app.get("/")
def root():
    return {"message": "Welcome to the root!"}

router = APIRouter()
router.include_router(notes_router)
