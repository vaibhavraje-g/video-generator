# backend/app/main.py
"""Main FastAPI application"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db import MongoDB
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    print("🚀 Starting application...")
    
    # Connect to MongoDB
    await MongoDB.connect_db()
    
    # Ensure directories exist
    settings.ensure_directories()
    
    print("✅ Application started successfully")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application...")
    await MongoDB.close_db()
    print("👋 Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Video Generator API",
    description="Full-stack video generation platform with authentication and project management",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

# Mount static files for serving generated videos
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Video Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "api": "/api/v1"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_healthy = await MongoDB.check_health()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
