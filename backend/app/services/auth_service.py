# backend/app/services/auth_service.py
"""Authentication service for user management and JWT tokens"""

from typing import Optional, Dict
from datetime import datetime
from bson import ObjectId

from app.db import get_database
from app.models import UserCreate, User
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
)


class AuthService:
    """Authentication service for user operations"""
    
    def __init__(self):
        self.db = get_database()
        self.users_collection = self.db.users
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if email exists
        existing_user = await self.users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check if username exists
        existing_user = await self.users_collection.find_one({"username": user_data.username})
        if existing_user:
            raise ValueError("Username already taken")
        
        # Create user document
        user_dict = {
            "email": user_data.email,
            "username": user_data.username,
            "hashed_password": get_password_hash(user_data.password),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = await self.users_collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        
        return User(**user_dict)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password"""
        user_dict = await self.users_collection.find_one({"email": email})
        
        if not user_dict:
            return None
        
        if not verify_password(password, user_dict["hashed_password"]):
            return None
        
        return User(**user_dict)
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        # BYPASS FOR TESTING
        if user_id == "dev_user_id":
            return User(
                _id="dev_user_id",
                email="dev@vidgen.ai",
                username="developer",
                hashed_password="hashed_bypass_password",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

        if not ObjectId.is_valid(user_id):
            return None
        
        user_dict = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user_dict:
            return None
        
        return User(**user_dict)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_dict = await self.users_collection.find_one({"email": email})
        
        if not user_dict:
            return None
        
        return User(**user_dict)
    
    def create_tokens(self, user: User) -> Dict[str, str]:
        """Create access and refresh tokens for a user"""
        token_data = {"sub": str(user.id), "email": user.email}
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
