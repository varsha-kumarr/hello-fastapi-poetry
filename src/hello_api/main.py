from fastapi import FastAPI
from hello_api.routes import notes

app = FastAPI()

app.include_router(notes.router, prefix="/notes", tags=["Notes"])

