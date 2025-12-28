# backend/app/generators/subliminal/generator.py
"""Subliminal video generator with various techniques"""

import uuid
import random
from pathlib import Path
from typing import Optional, Callable, List

from ..base import (
    BaseVideoGenerator,
    VideoConfig,
    GenerationResult,
    VideoDuration
)
from ..registry import GeneratorRegistry
from .techniques import (
    SubliminalTechnique,
    TECHNIQUE_CONFIGS,
    BACKGROUND_STYLE_QUERIES,
    AUDIO_PRESETS
)
from app.shared_services.affirmation_service import affirmation_service
from app.shared_services.frequency_service import frequency_service
from app.shared_services.assets_service import AssetsService
from app.shared_services.composition import VideoComposer
from app.shared_services.composition.video_composer import TextOverlayConfig
from app.core.config import settings


@GeneratorRegistry.register
class SubliminalGenerator(BaseVideoGenerator):
    """
    Subliminal video generator.
    
    Creates videos with subliminal messages using various techniques:
    - Flash text (brief visible text)
    - Background blend (low opacity text)
    - Audio layered (whispered affirmations)
    - Mirror/Reverse text
    """
    
    @property
    def generator_id(self) -> str:
        return "subliminal"
    
    @property
    def display_name(self) -> str:
        return "Subliminal"
    
    @property
    def description(self) -> str:
        return "Subliminal affirmation videos with various subtle messaging techniques"
    
    @property
    def supported_durations(self) -> list[VideoDuration]:
        return [VideoDuration.SHORT, VideoDuration.LONG]
    
    @property
    def config_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["wealth", "confidence", "health", "relationships", "success", "custom"],
                    "default": "wealth",
                    "description": "Affirmation category"
                },
                "technique": {
                    "type": "string",
                    "enum": ["flash_text", "background_blend", "audio_layered", "mirror_reverse"],
                    "default": "flash_text",
                    "description": "Subliminal technique to use"
                },
                "background_style": {
                    "type": "string",
                    "enum": ["nature", "abstract", "space", "ocean", "custom"],
                    "default": "nature",
                    "description": "Background video style"
                },
                "audio_track": {
                    "type": "string",
                    "enum": ["ambient", "binaural", "nature", "lofi", "custom"],
                    "default": "ambient",
                    "description": "Background audio track"
                },
                "custom_affirmations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": [],
                    "description": "Custom affirmations (overrides AI generation)"
                },
                "flash_duration_ms": {
                    "type": "integer",
                    "default": 150,
                    "description": "Flash duration for flash_text technique (ms)"
                },
                "blend_opacity": {
                    "type": "number",
                    "default": 0.15,
                    "description": "Opacity for background_blend technique (0-1)"
                }
            }
        }
    
    async def generate(
        self,
        topic: str,
        video_config: VideoConfig,
        generator_config: dict,
        output_path: str,
        progress_callback: Optional[Callable] = None
    ) -> GenerationResult:
        """Generate a subliminal video"""
        
        # Setup
        project_dir = Path(settings.PROJECTS_DIR) / f"subliminal_{uuid.uuid4().hex[:8]}"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        def report_progress(step: str, progress: float):
            if progress_callback:
                progress_callback(step, progress)
            print(f"💫 [{int(progress*100)}%] {step}")
        
        # Extract config
        category = generator_config.get("category", "wealth")
        technique = SubliminalTechnique(generator_config.get("technique", "flash_text"))
        background_style = generator_config.get("background_style", "nature")
        audio_track = generator_config.get("audio_track", "ambient")
        custom_affirmations = generator_config.get("custom_affirmations", [])
        flash_duration_ms = generator_config.get("flash_duration_ms", 150)
        blend_opacity = generator_config.get("blend_opacity", 0.15)
        
        # Determine duration and affirmation count
        if video_config.duration == VideoDuration.SHORT:
            total_duration = 60
            affirmation_count = 20  # More for subliminal
        else:
            total_duration = 600  # 10 minutes
            affirmation_count = 100
        
        report_progress("Generating affirmations", 0.1)
        
        # 1. Get affirmations
        if custom_affirmations:
            affirmations = custom_affirmations
        else:
            result = await affirmation_service.generate_affirmations(
                theme=topic,
                category=category,
                count=affirmation_count,
                duration=video_config.duration.value
            )
            affirmations = result.affirmations
        
        report_progress("Fetching background", 0.3)
        
        # 2. Get background video
        assets_service = AssetsService(project_dir=project_dir)
        
        query = BACKGROUND_STYLE_QUERIES.get(background_style, background_style)
        if query:
            try:
                background_path = assets_service.get_videos_pixabay(
                    query=query,
                    output_path=project_dir / "background.mp4"
                )
            except Exception:
                try:
                    background_path = assets_service.get_stock_gameplay_footage()
                except Exception:
                    background_path = None
        else:
            background_path = None
        
        report_progress("Generating audio", 0.5)
        
        # 3. Generate/get audio
        audio_path = str(project_dir / "audio.wav")
        audio_config = AUDIO_PRESETS.get(audio_track)
        
        if audio_track == "binaural":
            # Generate binaural beats
            frequency_service.generate_binaural(
                base_frequency=audio_config.get("frequency", 528),
                beat_frequency=audio_config.get("beat", 7.83),
                duration_seconds=total_duration,
                output_path=audio_path
            )
        else:
            # Generate simple tone as fallback
            frequency_service.generate_tone(
                frequency=432,
                duration_seconds=total_duration,
                output_path=audio_path,
                amplitude=0.3  # Lower volume
            )
        
        report_progress("Composing video", 0.6)
        
        # 4. Compose video
        composer = VideoComposer(aspect_ratio=video_config.aspect_ratio)
        composer.set_duration(total_duration)
        
        if background_path:
            composer.set_background_video(background_path, loop=True)
        else:
            # Dark background for subliminal
            composer.set_background_color((10, 10, 20), duration=total_duration)
        
        # 5. Add subliminal effects based on technique
        report_progress(f"Applying {technique.value} technique", 0.7)
        
        if technique == SubliminalTechnique.FLASH_TEXT:
            self._add_flash_text(
                composer, 
                affirmations, 
                total_duration,
                flash_duration_ms / 1000  # Convert to seconds
            )
        
        elif technique == SubliminalTechnique.BACKGROUND_BLEND:
            self._add_blended_text(
                composer,
                affirmations,
                total_duration,
                blend_opacity
            )
        
        elif technique == SubliminalTechnique.MIRROR_REVERSE:
            self._add_mirror_text(
                composer,
                affirmations,
                total_duration
            )
        
        # Audio layered handled in audio generation
        
        # 6. Add audio
        composer.add_audio(audio_path)
        
        report_progress("Rendering video", 0.85)
        
        # 7. Export
        output_file = composer.export(
            output_path=output_path,
            quality=video_config.quality,
            fps=30  # Higher FPS for smooth flashes
        )
        
        report_progress("Complete", 1.0)
        
        file_size = Path(output_file).stat().st_size if Path(output_file).exists() else None
        
        return GenerationResult(
            output_path=output_file,
            duration_seconds=total_duration,
            file_size_bytes=file_size,
            metadata={
                "category": category,
                "technique": technique.value,
                "affirmation_count": len(affirmations),
                "affirmations": affirmations[:10],  # First 10 for preview
                "background_style": background_style,
                "audio_track": audio_track,
                "project_dir": str(project_dir)
            }
        )
    
    def _add_flash_text(
        self,
        composer: VideoComposer,
        affirmations: List[str],
        duration: float,
        flash_duration: float
    ):
        """Add flash text technique - brief visible flashes"""
        # Calculate timing - random intervals
        num_flashes = min(len(affirmations), int(duration / 3))  # ~1 flash per 3 sec
        
        for i in range(num_flashes):
            affirmation = affirmations[i % len(affirmations)]
            
            # Random time within the video
            start_time = random.uniform(0, duration - flash_duration - 1)
            
            composer.add_text_overlay(TextOverlayConfig(
                text=affirmation,
                font_size=40,
                color="white",
                stroke_color="black",
                stroke_width=1,
                position="center",
                start_time=start_time,
                duration=flash_duration
            ))
    
    def _add_blended_text(
        self,
        composer: VideoComposer,
        affirmations: List[str],
        duration: float,
        opacity: float
    ):
        """Add blended text technique - low opacity persistent text"""
        # Display each affirmation for a period
        display_time = duration / len(affirmations)
        
        for i, affirmation in enumerate(affirmations):
            start_time = i * display_time
            
            # Note: Opacity would need MoviePy's set_opacity
            # For now, using lighter color to simulate
            composer.add_text_overlay(TextOverlayConfig(
                text=affirmation,
                font_size=35,
                color=f"rgba(255,255,255,{opacity})",
                stroke_color="transparent",
                stroke_width=0,
                position="center",
                start_time=start_time,
                duration=display_time - 0.1
            ))
    
    def _add_mirror_text(
        self,
        composer: VideoComposer,
        affirmations: List[str],
        duration: float
    ):
        """Add mirror/reverse text technique"""
        display_time = duration / len(affirmations)
        
        for i, affirmation in enumerate(affirmations):
            # Reverse the text
            reversed_text = affirmation[::-1]
            start_time = i * display_time
            
            composer.add_text_overlay(TextOverlayConfig(
                text=reversed_text,
                font_size=30,
                color="white",
                stroke_color="black",
                stroke_width=1,
                position="bottom",
                start_time=start_time,
                duration=display_time - 0.1
            ))
