# backend/app/generators/base.py
"""Base classes for video generators"""

from abc import ABC, abstractmethod
from typing import Literal, Optional, Any
from pydantic import BaseModel
from enum import Enum


class AspectRatio(str, Enum):
    """Supported aspect ratios"""
    VERTICAL = "9:16"      # Instagram Reels, TikTok, YouTube Shorts
    SQUARE = "1:1"         # Instagram Posts
    HORIZONTAL = "16:9"    # YouTube, standard video


class VideoDuration(str, Enum):
    """Video duration types"""
    SHORT = "short"   # 30-60 seconds
    LONG = "long"     # ~10 minutes


class OutputFormat(str, Enum):
    """Output video formats"""
    MP4 = "mp4"
    WEBM = "webm"
    MOV = "mov"


class VideoQuality(str, Enum):
    """Output quality presets"""
    HD = "720p"
    FULL_HD = "1080p"
    UHD = "4k"


class VideoConfig(BaseModel):
    """Common configuration for all video types"""
    aspect_ratio: AspectRatio = AspectRatio.VERTICAL
    duration: VideoDuration = VideoDuration.SHORT
    output_format: OutputFormat = OutputFormat.MP4
    quality: VideoQuality = VideoQuality.FULL_HD
    
    class Config:
        use_enum_values = True


class GenerationResult(BaseModel):
    """Result of video generation"""
    output_path: str
    duration_seconds: float
    file_size_bytes: Optional[int] = None
    metadata: dict = {}


class GeneratorInfo(BaseModel):
    """Information about a generator for API responses"""
    id: str
    display_name: str
    description: str
    supported_durations: list[str]
    config_schema: dict


class BaseVideoGenerator(ABC):
    """
    Abstract base class for all video generators.
    
    Implement this to create new video types.
    Each generator must be registered with the GeneratorRegistry.
    """
    
    @property
    @abstractmethod
    def generator_id(self) -> str:
        """Unique identifier for this generator (e.g., 'family_guy')"""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name (e.g., 'Explainer (Family Guy)')"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Short description of what this generator creates"""
        pass
    
    @property
    @abstractmethod
    def supported_durations(self) -> list[VideoDuration]:
        """List of supported duration types"""
        pass
    
    @property
    @abstractmethod
    def config_schema(self) -> dict:
        """JSON Schema for generator-specific configuration"""
        pass
    
    @abstractmethod
    async def generate(
        self,
        topic: str,
        video_config: VideoConfig,
        generator_config: dict,
        output_path: str,
        progress_callback: Optional[callable] = None
    ) -> GenerationResult:
        """
        Generate a video.
        
        Args:
            topic: The main topic/prompt for the video
            video_config: Common video settings (aspect ratio, duration, etc.)
            generator_config: Generator-specific options
            output_path: Where to save the output video
            progress_callback: Optional callback for progress updates
            
        Returns:
            GenerationResult with output path and metadata
        """
        pass
    
    def validate_config(self, generator_config: dict) -> dict:
        """
        Validate generator-specific configuration.
        Override to add custom validation.
        
        Args:
            generator_config: Configuration to validate
            
        Returns:
            Validated/normalized configuration
            
        Raises:
            ValueError: If configuration is invalid
        """
        return generator_config
    
    def get_info(self) -> GeneratorInfo:
        """Get generator information for API responses"""
        return GeneratorInfo(
            id=self.generator_id,
            display_name=self.display_name,
            description=self.description,
            supported_durations=[d.value for d in self.supported_durations],
            config_schema=self.config_schema
        )
