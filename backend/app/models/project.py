# backend/app/models/project.py
"""Project model for MongoDB"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId

from .user import PyObjectId


class ProjectBase(BaseModel):
    """Base project model"""
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Project creation model"""
    pass


class ProjectInDB(ProjectBase):
    """Project model as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ProjectResponse(ProjectBase):
    """Project response model"""
    id: str = Field(alias="_id")
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True


class Project(ProjectInDB):
    """Full project model"""
    pass
