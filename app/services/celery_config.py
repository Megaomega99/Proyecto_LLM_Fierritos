# app/services/celery_config.py
from celery import Celery
from app.core.config import settings

celery_app = Celery('tasks', broker=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0')