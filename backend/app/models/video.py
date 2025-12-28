# backend/app/models/video.py
"""Video model for MongoDB"""

from datetime import datetime
from typing import Optional, Dict, Any, Literal
from enum import Enum
from pydantic import BaseModel, Field
from bson import ObjectId

from .user import PyObjectId


class VideoStatus(str, Enum):
    """Video generation status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Legacy enum for backward compatibility
class VideoType(str, Enum):
    """Video type enum (legacy, use generator_id instead)"""
    FAMILY_GUY = "family_guy"
    FREQUENCY = "frequency"
    SUBLIMINAL = "subliminal"


class VideoConfigModel(BaseModel):
    """Common video configuration"""
    aspect_ratio: Literal["9:16", "1:1", "16:9"] = "9:16"
    duration: Literal["short", "long"] = "short"
    output_format: Literal["mp4", "webm", "mov"] = "mp4"
    quality: Literal["720p", "1080p", "4k"] = "1080p"


class VideoBase(BaseModel):
    """Base video model"""
    topic: str
    generator_id: str = "family_guy"  # Dynamic generator ID
    video_config: Optional[VideoConfigModel] = None
    generator_config: Optional[Dict[str, Any]] = None


class VideoCreate(VideoBase):
    """Video creation model"""
    project_id: str


class VideoInDB(VideoBase):
    """Video model as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    project_id: PyObjectId
    user_id: PyObjectId
    video_url: Optional[str] = None
    file_path: Optional[str] = None
    status: VideoStatus = VideoStatus.PENDING
    progress: Optional[float] = None  # 0-100 progress
    current_step: Optional[str] = None  # Current processing step
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class VideoResponse(BaseModel):
    """Video response model"""
    id: str = Field(alias="_id")
    project_id: str
    user_id: str
    topic: str
    generator_id: str
    video_config: Optional[VideoConfigModel] = None
    generator_config: Optional[Dict[str, Any]] = None
    video_url: Optional[str] = None
    status: VideoStatus
    progress: Optional[float] = None
    current_step: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


class Video(VideoInDB):
    """Full video model"""
    pass
