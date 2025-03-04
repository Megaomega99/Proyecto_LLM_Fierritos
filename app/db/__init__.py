# app/db/__init__.py
from app.models.user import User
from app.models.document import Document
from app.db.base import Base
from app.db.session import SessionLocal, get_db