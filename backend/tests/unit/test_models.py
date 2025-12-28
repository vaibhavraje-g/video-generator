# backend/tests/unit/test_models.py
"""Unit tests for data models"""

import pytest
from datetime import datetime
from bson import ObjectId

from app.models import UserCreate, UserInDB, ProjectCreate, ProjectInDB, VideoCreate, VideoInDB, VideoStatus, VideoType


def test_user_create_validation():
    """Test UserCreate model validation"""
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="securepassword"
    )
    
    assert user_data.email == "test@example.com"
    assert user_data.username == "testuser"
    assert user_data.password == "securepassword"
    assert user_data.is_active is True


def test_user_in_db_defaults():
    """Test UserInDB model with defaults"""
    user = UserInDB(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword",
    )
    
    assert user.is_active is True
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)


def test_project_create_validation():
    """Test ProjectCreate model validation"""
    project_data = ProjectCreate(
        name="Test Project",
        description="Test description"
    )
    
    assert project_data.name == "Test Project"
    assert project_data.description == "Test description"


def test_project_in_db():
    """Test ProjectInDB model"""
    user_id = ObjectId()
    project = ProjectInDB(
        name="Test Project",
        user_id=user_id,
    )
    
    assert project.name == "Test Project"
    assert project.user_id == user_id
    assert isinstance(project.created_at, datetime)


def test_video_create_validation():
    """Test VideoCreate model validation"""
    video_data = VideoCreate(
        project_id=str(ObjectId()),
        topic="Test topic",
        video_type=VideoType.FAMILY_GUY
    )
    
    assert video_data.topic == "Test topic"
    assert video_data.video_type == VideoType.FAMILY_GUY


def test_video_status_enum():
    """Test VideoStatus enum values"""
    assert VideoStatus.PENDING == "pending"
    assert VideoStatus.PROCESSING == "processing"
    assert VideoStatus.COMPLETED == "completed"
    assert VideoStatus.FAILED == "failed"


def test_video_in_db_defaults():
    """Test VideoInDB model with defaults"""
    project_id = ObjectId()
    user_id = ObjectId()
    
    video = VideoInDB(
        project_id=project_id,
        user_id=user_id,
        topic="Test topic",
        video_type=VideoType.FAMILY_GUY
    )
    
    assert video.status == VideoStatus.PENDING
    assert video.video_url is None
    assert video.file_path is None
    assert isinstance(video.created_at, datetime)
    assert video.completed_at is None
