from fastapi import FastAPI
from hello_api.config import settings

app = FastAPI()

@app.get("/hello")
def say_hello():
    return {"message": f"Hello, welcome to {settings.project_name}!"}

@app.get("/")
def root():
    return {"message": "Welcome to the root!"}


