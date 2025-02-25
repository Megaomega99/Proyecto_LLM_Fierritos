# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAG SaaS"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "Leuname9991gge")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ragsaas")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "aja")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Configuración de Ollama
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "30"))
    OLLAMA_MAX_RETRIES: int = int(os.getenv("OLLAMA_MAX_RETRIES", "3"))
    OLLAMA_RETRY_DELAY: int = int(os.getenv("OLLAMA_RETRY_DELAY", "1"))

    @property
    def get_ollama_config(self) -> dict:
        try:
            return {
                "base_url": self.OLLAMA_BASE_URL,
                "model": self.OLLAMA_MODEL,
                "timeout": self.OLLAMA_TIMEOUT,
                "max_retries": self.OLLAMA_MAX_RETRIES,
                "retry_delay": self.OLLAMA_RETRY_DELAY
            }
        except Exception as e:
            print(f"Error en la configuración de Ollama: {str(e)}")
            raise

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
settings.SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
)