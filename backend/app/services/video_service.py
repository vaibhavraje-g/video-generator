# backend/app/services/video_service.py
"""Video generation service with database integration"""

from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import uuid
from bson import ObjectId

from app.db import get_database
from app.models import Video, VideoStatus
from app.generators import GeneratorRegistry
from app.generators.base import VideoConfig, AspectRatio, VideoDuration, OutputFormat, VideoQuality
from app.core.config import settings


class VideoService:
    """Service for video generation and management"""
    
    def __init__(self):
        self.db = get_database()
        self.videos_collection = self.db.videos
    
    async def create_video_record(
        self, 
        project_id: str, 
        user_id: str, 
        topic: str, 
        generator_id: str = "family_guy",
        video_config: Optional[Dict[str, Any]] = None,
        generator_config: Optional[Dict[str, Any]] = None
    ) -> Video:
        """
        Create a video record in the database
        """
        video_dict = {
            "project_id": ObjectId(project_id),
            "user_id": ObjectId(user_id),
            "topic": topic,
            "generator_id": generator_id,
            "video_config": video_config or {},
            "generator_config": generator_config or {},
            "status": VideoStatus.PENDING,
            "progress": 0,
            "current_step": "Queued",
            "created_at": datetime.utcnow(),
        }
        
        result = await self.videos_collection.insert_one(video_dict)
        video_dict["_id"] = result.inserted_id
        
        return Video(**video_dict)
    
    async def update_video_status(
        self, 
        video_id: str, 
        status: VideoStatus, 
        progress: Optional[float] = None,
        current_step: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Update video status and progress"""
        update_data = {"status": status}
        
        if progress is not None:
            update_data["progress"] = progress
        
        if current_step is not None:
            update_data["current_step"] = current_step
        
        if status == VideoStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()
            update_data["progress"] = 100
        
        if error_message:
            update_data["error_message"] = error_message
        
        await self.videos_collection.update_one(
            {"_id": ObjectId(video_id)},
            {"$set": update_data}
        )
    
    async def update_video_result(
        self, 
        video_id: str, 
        video_url: str, 
        file_path: str,
        metadata: dict
    ):
        """Update video with generation results"""
        await self.videos_collection.update_one(
            {"_id": ObjectId(video_id)},
            {"$set": {
                "video_url": video_url,
                "file_path": file_path,
                "metadata": metadata,
                "status": VideoStatus.COMPLETED,
                "progress": 100,
                "current_step": "Complete",
                "completed_at": datetime.utcnow(),
            }}
        )
    
    async def generate_video(self, video_id: str) -> Video:
        """Generate a video using the appropriate generator"""
        video_dict = await self.videos_collection.find_one({"_id": ObjectId(video_id)})
        if not video_dict:
            raise ValueError("Video not found")
        
        video = Video(**video_dict)
        
        try:
            await self.update_video_status(
                video_id, 
                VideoStatus.PROCESSING,
                progress=5,
                current_step="Initializing generator"
            )
            
            generator = GeneratorRegistry.get(video.generator_id)
            
            vc = video.video_config or {}
            video_config = VideoConfig(
                aspect_ratio=AspectRatio(vc.get("aspect_ratio", "9:16")),
                duration=VideoDuration(vc.get("duration", "short")),
                output_format=OutputFormat(vc.get("output_format", "mp4")),
                quality=VideoQuality(vc.get("quality", "1080p"))
            )
            
            output_dir = Path(settings.OUTPUT_DIR)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_filename = f"{video.generator_id}_{uuid.uuid4().hex[:8]}.{video_config.output_format}"
            output_path = str(output_dir / output_filename)
            
            async def progress_callback(step: str, progress: float):
                await self.update_video_status(
                    video_id,
                    VideoStatus.PROCESSING,
                    progress=progress * 100,
                    current_step=step
                )
            
            result = await generator.generate(
                topic=video.topic,
                video_config=video_config,
                generator_config=video.generator_config or {},
                output_path=output_path,
                progress_callback=progress_callback
            )
            
            video_url = f"/static/{output_filename}"
            
            await self.update_video_result(
                video_id,
                video_url=video_url,
                file_path=result.output_path,
                metadata={
                    "topic": video.topic,
                    "duration_seconds": result.duration_seconds,
                    "file_size_bytes": result.file_size_bytes,
                    **result.metadata
                }
            )
            
            video_dict = await self.videos_collection.find_one({"_id": ObjectId(video_id)})
            return Video(**video_dict)
            
        except Exception as e:
            await self.update_video_status(
                video_id, 
                VideoStatus.FAILED, 
                progress=0,
                current_step="Failed",
                error_message=str(e)
            )
            raise
    
    async def get_video(self, video_id: str, user_id: str) -> Optional[Video]:
        """Get a video with ownership verification"""
        if not ObjectId.is_valid(video_id):
            return None
        
        video_dict = await self.videos_collection.find_one({
            "_id": ObjectId(video_id),
            "user_id": ObjectId(user_id)
        })
        
        if not video_dict:
            return None
        
        return Video(**video_dict)
