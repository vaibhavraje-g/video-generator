# backend/app/api/v1/__init__.py
from fastapi import APIRouter
from .routes import auth_router, projects_router, videos_router
from .routes.generators import router as generators_router

api_router = APIRouter(prefix="/v1")

# Include all route modules
api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(videos_router)
api_router.include_router(generators_router)

__all__ = ["api_router"]
