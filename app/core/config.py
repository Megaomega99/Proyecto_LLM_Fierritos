# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv('aja.env')

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAG SaaS"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "aja")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ragsaas")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "aja")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    OLLAMA_API_URL: str = "http://localhost:11434"
    MODEL_NAME: str = "llama2"

settings = Settings()
settings.SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
)