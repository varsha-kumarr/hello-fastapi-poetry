from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_username: str
    db_password: str
    db_database: str

    class Config:
        env_file = ".env"

settings = Settings()
