# backend/app/db/mongodb.py
"""MongoDB connection manager with async support"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager singleton"""
    
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls):
        """Initialize MongoDB connection"""
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            # Verify connection
            await cls.client.admin.command('ping')
            logger.info(f"✅ Connected to MongoDB: {settings.MONGODB_URL}")
        except ConnectionFailure as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("🔒 Closed MongoDB connection")
    
    @classmethod
    def get_db(cls):
        """Get database instance"""
        if not cls.client:
            raise RuntimeError("Database not initialized. Call connect_db() first.")
        return cls.client[settings.MONGODB_DB_NAME]
    
    @classmethod
    async def check_health(cls) -> bool:
        """Check database connection health"""
        try:
            if not cls.client:
                return False
            await cls.client.admin.command('ping')
            return True
        except Exception:
            return False


# Convenience function to get database
def get_database():
    """Get database instance"""
    return MongoDB.get_db()
