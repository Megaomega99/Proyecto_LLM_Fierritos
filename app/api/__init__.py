# app/api/__init__.py
from .auth import router as auth_router
from .documents import router as documents_router
from .users import router as users_router