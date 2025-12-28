# backend/app/models/user.py
"""User model for MongoDB"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from bson import ObjectId


class PyObjectId(str):
    """Custom ObjectId type for Pydantic v2"""
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )
    
    @classmethod
    def validate(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            if ObjectId.is_valid(v) or v == "dev_user_id":
                return v
            raise ValueError(f"Invalid ObjectId: {v}")
        raise ValueError(f"Invalid ObjectId type: {type(v)}")


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    username: str
    is_active: bool = True


class UserCreate(UserBase):
    """User creation model"""
    password: str


class UserInDB(UserBase):
    """User model as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserResponse(UserBase):
    """User response model (without password)"""
    id: str = Field(alias="_id")
    created_at: datetime
    
    class Config:
        populate_by_name = True


class User(UserInDB):
    """Full user model"""
    pass
