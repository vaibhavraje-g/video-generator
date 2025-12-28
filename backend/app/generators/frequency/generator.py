# backend/app/generators/frequency/generator.py
"""Frequency/Healing/Manifestation video generator"""

import uuid
from pathlib import Path
from typing import Optional, Callable

from ..base import (
    BaseVideoGenerator,
    VideoConfig,
    GenerationResult,
    VideoDuration
)
from ..registry import GeneratorRegistry
from app.shared_services.frequency_service import frequency_service
from app.shared_services.affirmation_service import affirmation_service
from app.shared_services.assets_service import AssetsService
from app.shared_services.composition import VideoComposer, OverlayPresets
from app.shared_services.composition.video_composer import TextOverlayConfig
from app.core.config import settings


# Visual style to background mappings
VISUAL_STYLE_QUERIES = {
    "sacred_geometry": "sacred geometry animation spiritual pattern",
    "nature": "peaceful nature forest river calm",
    "waves": "abstract waves flowing energy animation",
    "mandala": "mandala meditation spiritual circles",
    "particles": "particle energy light flowing abstract",
    "minimal": "minimal gradient calm abstract"
}


@GeneratorRegistry.register
class FrequencyGenerator(BaseVideoGenerator):
    """
    Frequency/Healing video generator.
    
    Creates videos with:
    - Solfeggio frequency tones (432Hz, 528Hz, etc.)
    - Optional binaural beats
    - Calming/spiritual visuals
    - AI-generated affirmations
    - Text overlays
    """
    
    @property
    def generator_id(self) -> str:
        return "frequency"
    
    @property
    def display_name(self) -> str:
        return "Frequency/Healing"
    
    @property
    def description(self) -> str:
        return "Healing and manifestation videos with solfeggio frequencies and positive affirmations"
    
    @property
    def supported_durations(self) -> list[VideoDuration]:
        return [VideoDuration.SHORT, VideoDuration.LONG]
    
    @property
    def config_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "frequency": {
                    "type": "integer",
                    "enum": [432, 528, 639, 741, 852, 963],
                    "default": 528,
                    "description": "Solfeggio frequency in Hz"
                },
                "visual_style": {
                    "type": "string",
                    "enum": ["sacred_geometry", "nature", "waves", "mandala", "particles", "minimal"],
                    "default": "sacred_geometry",
                    "description": "Visual style for the background"
                },
                "affirmation_theme": {
                    "type": "string",
                    "default": "",
                    "description": "Theme for AI-generated affirmations (e.g., 'abundance', 'healing')"
                },
                "include_binaural": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include binaural beats"
                },
                "binaural_beat_hz": {
                    "type": "number",
                    "default": 7.83,
                    "description": "Binaural beat frequency (Schumann resonance = 7.83)"
                },
                "text_overlay": {
                    "type": "boolean",
                    "default": True,
                    "description": "Show affirmation text on screen"
                },
                "fade_effects": {
                    "type": "boolean",
                    "default": True,
                    "description": "Add fade in/out transitions"
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
        """Generate a frequency/healing video"""
        
        # Setup
        project_dir = Path(settings.PROJECTS_DIR) / f"frequency_{uuid.uuid4().hex[:8]}"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        def report_progress(step: str, progress: float):
            if progress_callback:
                progress_callback(step, progress)
            print(f"🎵 [{int(progress*100)}%] {step}")
        
        # Extract config
        frequency = generator_config.get("frequency", 528)
        visual_style = generator_config.get("visual_style", "sacred_geometry")
        affirmation_theme = generator_config.get("affirmation_theme", topic)
        include_binaural = generator_config.get("include_binaural", False)
        binaural_beat_hz = generator_config.get("binaural_beat_hz", 7.83)
        text_overlay = generator_config.get("text_overlay", True)
        
        # Determine duration
        if video_config.duration == VideoDuration.SHORT:
            total_duration = 60  # 60 seconds
            affirmation_count = 5
        else:
            total_duration = 600  # 10 minutes
            affirmation_count = 30
        
        report_progress("Generating frequency tone", 0.1)
        
        # 1. Generate frequency audio
        audio_path = str(project_dir / f"frequency_{frequency}hz.wav")
        if include_binaural:
            frequency_service.generate_binaural(
                base_frequency=frequency,
                beat_frequency=binaural_beat_hz,
                duration_seconds=total_duration,
                output_path=audio_path
            )
        else:
            frequency_service.generate_tone(
                frequency=frequency,
                duration_seconds=total_duration,
                output_path=audio_path
            )
        
        report_progress("Generating affirmations", 0.3)
        
        # 2. Generate affirmations
        affirmations = await affirmation_service.generate_for_frequency(
            frequency=frequency,
            theme=affirmation_theme,
            count=affirmation_count
        )
        
        report_progress("Fetching background visuals", 0.5)
        
        # 3. Get background video/images
        assets_service = AssetsService(project_dir=project_dir)
        
        # Try to get a video matching the visual style
        visual_query = VISUAL_STYLE_QUERIES.get(visual_style, visual_style)
        try:
            background_path = assets_service.get_videos_pixabay(
                query=visual_query,
                output_path=project_dir / "background.mp4"
            )
        except Exception:
            # Fallback to stock footage
            try:
                background_path = assets_service.get_stock_gameplay_footage()
            except Exception:
                background_path = None
        
        report_progress("Composing video", 0.7)
        
        # 4. Compose video
        composer = VideoComposer(aspect_ratio=video_config.aspect_ratio)
        composer.set_duration(total_duration)
        
        if background_path:
            composer.set_background_video(background_path, loop=True)
        else:
            # Use gradient color based on frequency
            preset = frequency_service.get_preset(frequency)
            if preset:
                # Convert hex to RGB
                hex_color = preset.color.lstrip('#')
                rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                composer.set_background_color(rgb, duration=total_duration)
            else:
                composer.set_background_color((20, 20, 40), duration=total_duration)
        
        # 5. Add affirmation text overlays
        if text_overlay and affirmations.affirmations:
            # Calculate timing for each affirmation
            affirmation_duration = total_duration / len(affirmations.affirmations)
            
            for i, affirmation in enumerate(affirmations.affirmations):
                start_time = i * affirmation_duration
                
                composer.add_text_overlay(TextOverlayConfig(
                    text=affirmation,
                    font_size=50,
                    color="white",
                    stroke_color="black",
                    stroke_width=2,
                    position="center",
                    start_time=start_time,
                    duration=affirmation_duration - 0.5  # Small gap between
                ))
        
        # 6. Add frequency label
        preset = frequency_service.get_preset(frequency)
        freq_label = f"{frequency} Hz - {preset.name if preset else 'Healing'}"
        composer.add_text_overlay(TextOverlayConfig(
            text=freq_label,
            font_size=30,
            color="white",
            position="top",
            start_time=0,
            duration=total_duration
        ))
        
        # 7. Add audio
        composer.add_audio(audio_path)
        
        report_progress("Rendering video", 0.85)
        
        # 8. Export
        output_file = composer.export(
            output_path=output_path,
            quality=video_config.quality,
            fps=24
        )
        
        report_progress("Complete", 1.0)
        
        file_size = Path(output_file).stat().st_size if Path(output_file).exists() else None
        
        return GenerationResult(
            output_path=output_file,
            duration_seconds=total_duration,
            file_size_bytes=file_size,
            metadata={
                "frequency": frequency,
                "frequency_name": preset.name if preset else None,
                "visual_style": visual_style,
                "affirmation_count": len(affirmations.affirmations),
                "affirmations": affirmations.affirmations,
                "binaural_enabled": include_binaural,
                "project_dir": str(project_dir)
            }
        )
