# backend/app/api/v1/routes/videos.py
"""Video generation routes"""

from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal

from app.services.video_service import VideoService
from app.models import VideoResponse, VideoStatus, User, VideoConfigModel
from app.middleware import get_current_active_user
from app.generators import GeneratorRegistry

router = APIRouter(prefix="/videos", tags=["videos"])


class VideoGenerateRequest(BaseModel):
    """Video generation request"""
    project_id: str
    generator_id: str = "family_guy"
    topic: str
    
    # Common video config
    aspect_ratio: Literal["9:16", "1:1", "16:9"] = "9:16"
    duration: Literal["short", "long"] = "short"
    output_format: Literal["mp4", "webm", "mov"] = "mp4"
    quality: Literal["720p", "1080p", "4k"] = "1080p"
    
    # Generator-specific config
    generator_config: Optional[Dict[str, Any]] = None


@router.post("/generate", response_model=VideoResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_video(
    request: VideoGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a video (async background task)
    
    Returns:
        Video record with pending status
    """
    # Validate generator exists
    if not GeneratorRegistry.is_registered(request.generator_id):
        available = GeneratorRegistry.list_ids()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Generator '{request.generator_id}' not found. Available: {available}"
        )
    
    # Check duration support
    generator = GeneratorRegistry.get(request.generator_id)
    supported = [d.value for d in generator.supported_durations]
    if request.duration not in supported:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Generator '{request.generator_id}' does not support '{request.duration}' duration. Supported: {supported}"
        )
    
    video_service = VideoService()
    
    # Build video config
    video_config = VideoConfigModel(
        aspect_ratio=request.aspect_ratio,
        duration=request.duration,
        output_format=request.output_format,
        quality=request.quality
    )
    
    # Create video record
    video = await video_service.create_video_record(
        project_id=request.project_id,
        user_id=str(current_user.id),
        topic=request.topic,
        generator_id=request.generator_id,
        video_config=video_config.model_dump(),
        generator_config=request.generator_config or {}
    )
    
    # Schedule video generation in background
    background_tasks.add_task(video_service.generate_video, str(video.id))
    
    return VideoResponse(
        _id=str(video.id),
        project_id=str(video.project_id),
        user_id=str(video.user_id),
        topic=video.topic,
        generator_id=video.generator_id,
        video_config=video.video_config,
        generator_config=video.generator_config,
        video_url=video.video_url,
        status=video.status,
        progress=video.progress,
        current_step=video.current_step,
        metadata=video.metadata,
        error_message=video.error_message,
        created_at=video.created_at,
        completed_at=video.completed_at,
    )


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get video details
    
    Returns:
        Video information
    """
    video_service = VideoService()
    video = await video_service.get_video(video_id, str(current_user.id))
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    return VideoResponse(
        _id=str(video.id),
        project_id=str(video.project_id),
        user_id=str(video.user_id),
        topic=video.topic,
        generator_id=video.generator_id,
        video_config=video.video_config,
        generator_config=video.generator_config,
        video_url=video.video_url,
        status=video.status,
        progress=video.progress,
        current_step=video.current_step,
        metadata=video.metadata,
        error_message=video.error_message,
        created_at=video.created_at,
        completed_at=video.completed_at,
    )
