from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str = "Hello FastAPI"

    class Config:
        env_file = ".env"

settings = Settings()

