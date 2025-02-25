import requests
import psycopg2
from redis import Redis
from app.core.config import settings

def check_services():
    errors = []
    
    # Verificar Ollama
    try:
        response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
        if response.status_code != 200:
            errors.append("Ollama no está respondiendo correctamente")
    except Exception as e:
        errors.append(f"Error conectando con Ollama: {str(e)}")
    
    # Verificar PostgreSQL
    try:
        conn = psycopg2.connect(settings.SQLALCHEMY_DATABASE_URI)
        conn.close()
    except Exception as e:
        errors.append(f"Error conectando con PostgreSQL: {str(e)}")
    
    # Verificar Redis
    try:
        redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        redis.ping()
    except Exception as e:
        errors.append(f"Error conectando con Redis: {str(e)}")
    
    return errors

print(check_services())