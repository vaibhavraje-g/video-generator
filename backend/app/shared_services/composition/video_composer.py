# backend/app/shared_services/composition/video_composer.py
"""Unified video composition service using MoviePy"""

from pathlib import Path
from typing import Optional, List, Tuple, Union
from dataclasses import dataclass
import tempfile

from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_audioclips,
    ColorClip
)

from .overlay_presets import OverlayPresets, AspectRatioType


@dataclass
class VideoLayer:
    """Represents a layer in the video composition"""
    clip: any  # MoviePy clip
    start_time: float = 0
    duration: Optional[float] = None
    position: Union[Tuple[int, int], str] = "center"
    opacity: float = 1.0


@dataclass 
class TextOverlayConfig:
    """Configuration for text overlay"""
    text: str
    font_size: int = 60
    color: str = "white"
    stroke_color: str = "black"
    stroke_width: float = 2
    font: str = "Arial-Bold"
    position: str = "subtitle"
    start_time: float = 0
    duration: Optional[float] = None


class VideoComposer:
    """
    Unified video composition service.
    
    Handles:
    - Background video/color setup
    - Image overlays (characters, infographics)
    - Text overlays (subtitles, affirmations)
    - Audio layering
    - Export with presets
    """
    
    # Quality presets
    QUALITY_PRESETS = {
        "720p": {"width": 1280, "bitrate": "5000k"},
        "1080p": {"width": 1920, "bitrate": "10000k"},
        "4k": {"width": 3840, "bitrate": "25000k"},
    }
    
    def __init__(self, aspect_ratio: AspectRatioType = "9:16"):
        self.aspect_ratio = aspect_ratio
        self.resolution = OverlayPresets.get_resolution(aspect_ratio)
        self.layers: List[VideoLayer] = []
        self.audio_clips: List[AudioFileClip] = []
        self.background = None
        self.total_duration = 0
    
    def set_background_video(
        self, 
        video_path: str,
        loop: bool = True
    ) -> "VideoComposer":
        """Set background video (will be resized/cropped to fit)"""
        clip = VideoFileClip(video_path)
        
        # Calculate crop/resize to match aspect ratio
        target_w, target_h = self.resolution
        target_ratio = target_w / target_h
        video_ratio = clip.w / clip.h
        
        if video_ratio > target_ratio:
            # Video is wider, crop sides
            new_width = int(clip.h * target_ratio)
            x_center = clip.w / 2
            clip = clip.crop(
                x1=x_center - new_width/2,
                x2=x_center + new_width/2
            )
        else:
            # Video is taller, crop top/bottom
            new_height = int(clip.w / target_ratio)
            y_center = clip.h / 2
            clip = clip.crop(
                y1=y_center - new_height/2,
                y2=y_center + new_height/2
            )
        
        clip = clip.resize(self.resolution)
        
        if loop and clip.duration < self.total_duration:
            clip = clip.loop(duration=self.total_duration)
        
        self.background = clip
        return self
    
    def set_background_color(
        self,
        color: Tuple[int, int, int] = (0, 0, 0),
        duration: Optional[float] = None
    ) -> "VideoComposer":
        """Set solid color background"""
        dur = duration or self.total_duration or 10
        self.background = ColorClip(
            size=self.resolution,
            color=color,
            duration=dur
        )
        return self
    
    def add_image_overlay(
        self,
        image_path: str,
        position: str = "center",
        start_time: float = 0,
        duration: Optional[float] = None,
        size: Optional[Tuple[int, int]] = None,
        opacity: float = 1.0
    ) -> "VideoComposer":
        """Add an image overlay (character, infographic, etc.)"""
        clip = ImageClip(image_path)
        
        # Get position preset
        preset = OverlayPresets.get_character_position(self.aspect_ratio, position)
        target_size = size or preset.size
        
        clip = clip.resize(target_size)
        clip = clip.set_position(preset.position)
        clip = clip.set_start(start_time)
        
        if duration:
            clip = clip.set_duration(duration)
        
        if opacity < 1.0:
            clip = clip.set_opacity(opacity)
        
        self.layers.append(VideoLayer(
            clip=clip,
            start_time=start_time,
            duration=duration,
            position=position,
            opacity=opacity
        ))
        return self
    
    def add_text_overlay(
        self,
        config: TextOverlayConfig
    ) -> "VideoComposer":
        """Add a text overlay"""
        preset = OverlayPresets.get_text_position(self.aspect_ratio, config.position)
        
        clip = TextClip(
            config.text,
            fontsize=config.font_size,
            color=config.color,
            font=config.font,
            stroke_color=config.stroke_color,
            stroke_width=config.stroke_width,
            method='caption',
            size=(preset.size[0], None)
        )
        
        clip = clip.set_position(('center', preset.position[1]))
        clip = clip.set_start(config.start_time)
        
        if config.duration:
            clip = clip.set_duration(config.duration)
        
        self.layers.append(VideoLayer(
            clip=clip,
            start_time=config.start_time,
            duration=config.duration,
            position=config.position
        ))
        return self
    
    def add_audio(
        self,
        audio_path: str,
        start_time: float = 0,
        volume: float = 1.0
    ) -> "VideoComposer":
        """Add an audio track"""
        clip = AudioFileClip(audio_path)
        
        if volume != 1.0:
            clip = clip.volumex(volume)
        
        clip = clip.set_start(start_time)
        self.audio_clips.append(clip)
        
        # Update total duration
        end_time = start_time + clip.duration
        self.total_duration = max(self.total_duration, end_time)
        
        return self
    
    def add_audio_sequence(
        self,
        audio_paths: List[str],
        gap: float = 0.0
    ) -> "VideoComposer":
        """Add multiple audio clips in sequence"""
        current_time = 0
        
        for path in audio_paths:
            self.add_audio(path, start_time=current_time)
            clip = AudioFileClip(path)
            current_time += clip.duration + gap
            clip.close()
        
        return self
    
    def set_duration(self, duration: float) -> "VideoComposer":
        """Set the total video duration"""
        self.total_duration = duration
        return self
    
    def compose(self) -> CompositeVideoClip:
        """Compose all layers into final video"""
        if not self.background:
            self.set_background_color(duration=self.total_duration)
        
        # Ensure background matches duration
        if self.background.duration != self.total_duration:
            if hasattr(self.background, 'loop'):
                self.background = self.background.loop(duration=self.total_duration)
            else:
                self.background = self.background.set_duration(self.total_duration)
        
        # Build clip list
        all_clips = [self.background]
        for layer in self.layers:
            all_clips.append(layer.clip)
        
        # Create composite
        video = CompositeVideoClip(all_clips, size=self.resolution)
        video = video.set_duration(self.total_duration)
        
        # Add audio
        if self.audio_clips:
            from moviepy.editor import CompositeAudioClip
            audio = CompositeAudioClip(self.audio_clips)
            video = video.set_audio(audio)
        
        return video
    
    def export(
        self,
        output_path: str,
        quality: str = "1080p",
        fps: int = 24,
        codec: str = "libx264",
        audio_codec: str = "aac"
    ) -> str:
        """Export the composed video"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        video = self.compose()
        
        preset = self.QUALITY_PRESETS.get(quality, self.QUALITY_PRESETS["1080p"])
        
        video.write_videofile(
            output_path,
            fps=fps,
            codec=codec,
            audio_codec=audio_codec,
            bitrate=preset["bitrate"],
            threads=4,
            preset='medium'
        )
        
        # Cleanup
        video.close()
        for audio in self.audio_clips:
            audio.close()
        if self.background:
            self.background.close()
        
        return output_path
    
    def cleanup(self):
        """Close all clips to free resources"""
        for layer in self.layers:
            if hasattr(layer.clip, 'close'):
                layer.clip.close()
        for audio in self.audio_clips:
            audio.close()
        if self.background:
            self.background.close()
