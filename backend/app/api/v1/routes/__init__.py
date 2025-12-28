# backend/app/api/v1/routes/__init__.py
from .auth import router as auth_router
from .projects import router as projects_router
from .videos import router as videos_router

__all__ = ["auth_router", "projects_router", "videos_router"]
