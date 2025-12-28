# backend/app/generators/family_guy/generator.py
"""Family Guy style explainer video generator"""

import asyncio
import uuid
from pathlib import Path
from typing import Optional, Callable
from collections import defaultdict

from ..base import (
    BaseVideoGenerator,
    VideoConfig,
    GenerationResult,
    VideoDuration
)
from ..registry import GeneratorRegistry
from .prompts import VideoScript, SCRIPT_PROMPT_TEMPLATE

from app.shared_services.script_service import script_service
from app.shared_services.tts_service import TTSService
from app.shared_services.assets_service import AssetsService
from app.shared_services.composition import VideoComposer, OverlayPresets
from app.core.config import settings


@GeneratorRegistry.register
class FamilyGuyGenerator(BaseVideoGenerator):
    """
    Family Guy style explainer video generator.
    
    Creates short-form educational content with:
    - Peter, Stewie, and Brian character dialogues
    - TTS voice synthesis per character
    - Character image overlays
    - Gaming/abstract background footage
    - Infographic overlays
    """
    
    @property
    def generator_id(self) -> str:
        return "family_guy"
    
    @property
    def display_name(self) -> str:
        return "Explainer (Family Guy)"
    
    @property
    def description(self) -> str:
        return "Short comedy explainer videos with Family Guy style characters discussing topics"
    
    @property
    def supported_durations(self) -> list[VideoDuration]:
        return [VideoDuration.SHORT]  # Only short form for now
    
    @property
    def config_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "style": {
                    "type": "string",
                    "enum": ["family_guy"],
                    "default": "family_guy",
                    "description": "Video style"
                },
                "background": {
                    "type": "string",
                    "enum": ["gaming", "abstract", "custom"],
                    "default": "gaming",
                    "description": "Background video type"
                },
                "background_url": {
                    "type": "string",
                    "description": "Custom background video URL (if background=custom)"
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
        """Generate a Family Guy style explainer video"""
        
        # Setup project directory
        project_dir = Path(settings.PROJECTS_DIR) / f"family_guy_{uuid.uuid4().hex[:8]}"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        def report_progress(step: str, progress: float):
            if progress_callback:
                progress_callback(step, progress)
            print(f"📹 [{int(progress*100)}%] {step}")
        
        report_progress("Generating script", 0.1)
        
        # 1. Generate script
        script = await script_service.generate_script(
            topic=topic,
            prompt_template=SCRIPT_PROMPT_TEMPLATE,
            response_model=VideoScript
        )
        print(f"✅ Generated script with {len(script.dialogues)} lines")
        
        report_progress("Loading assets", 0.2)
        
        # 2. Initialize services
        assets_service = AssetsService(project_dir=project_dir)
        tts_service = TTSService()
        
        # 3. Load character images
        unique_characters = {d.character.lower().strip() for d in script.dialogues}
        character_images = {}
        for char in unique_characters:
            try:
                path = assets_service.get_character_image(char)
                character_images[char] = path
            except Exception as e:
                print(f"⚠️ Missing image for {char}: {e}")
        
        # 4. Get background video
        background_type = generator_config.get("background", "gaming")
        if background_type == "custom" and generator_config.get("background_url"):
            # TODO: Download custom background
            background_path = assets_service.get_stock_gameplay_footage()
        else:
            background_path = assets_service.get_stock_gameplay_footage()
        
        report_progress("Generating audio", 0.3)
        
        # 5. Generate TTS - group by character for efficiency
        dialogues_by_char = defaultdict(list)
        for i, d in enumerate(script.dialogues):
            dialogues_by_char[d.character.lower().strip()].append((i, d))
        
        audio_paths = {}
        total_chars = len(dialogues_by_char)
        for idx, (character, items) in enumerate(dialogues_by_char.items()):
            progress = 0.3 + (0.3 * (idx / total_chars))
            report_progress(f"Generating voice for {character}", progress)
            
            texts = [d.text for _, d in items]
            paths = await tts_service.generate_character_batch(
                character=character,
                texts=texts,
                output_dir=str(project_dir)
            )
            
            for (orig_idx, _), path in zip(items, paths):
                audio_paths[orig_idx] = path
        
        # Reorder audio paths
        ordered_audio = [audio_paths[i] for i in range(len(script.dialogues))]
        
        report_progress("Fetching infographics", 0.6)
        
        # 6. Fetch infographics
        infographic_paths = []
        for i, d in enumerate(script.dialogues):
            if d.infographic:
                try:
                    path = project_dir / "infographics" / f"info_{i}.jpg"
                    assets_service.get_assets_infographics(
                        query=d.infographic,
                        output_path=path
                    )
                    infographic_paths.append((i, str(path)))
                except Exception as e:
                    print(f"⚠️ Failed to fetch infographic: {e}")
        
        report_progress("Composing video", 0.7)
        
        # 7. Compose video
        from moviepy.editor import AudioFileClip
        
        # Calculate audio durations and total length
        audio_clips = []
        audio_timings = []
        current_time = 0
        
        for path in ordered_audio:
            clip = AudioFileClip(path)
            audio_timings.append({
                "start": current_time,
                "duration": clip.duration
            })
            current_time += clip.duration + 0.1  # Small gap between clips
            clip.close()
        
        total_duration = current_time
        
        # Create composer
        composer = VideoComposer(aspect_ratio=video_config.aspect_ratio)
        composer.set_duration(total_duration)
        composer.set_background_video(background_path)
        
        # Add character overlays for each dialogue
        for i, d in enumerate(script.dialogues):
            char = d.character.lower().strip()
            if char in character_images:
                # Alternate left/right positions based on character
                position = "left" if char == "peter" else "right"
                
                composer.add_image_overlay(
                    image_path=character_images[char],
                    position=position,
                    start_time=audio_timings[i]["start"],
                    duration=audio_timings[i]["duration"]
                )
        
        # Add infographics
        for idx, path in infographic_paths:
            composer.add_image_overlay(
                image_path=path,
                position="center",  # Will use infographic preset
                start_time=audio_timings[idx]["start"],
                duration=audio_timings[idx]["duration"],
                opacity=0.9
            )
        
        # Add audio sequence
        composer.add_audio_sequence(ordered_audio, gap=0.1)
        
        report_progress("Rendering video", 0.85)
        
        # 8. Export
        output_file = composer.export(
            output_path=output_path,
            quality=video_config.quality,
            fps=24
        )
        
        report_progress("Complete", 1.0)
        
        # Get file size
        file_size = Path(output_file).stat().st_size if Path(output_file).exists() else None
        
        return GenerationResult(
            output_path=output_file,
            duration_seconds=total_duration,
            file_size_bytes=file_size,
            metadata={
                "topic": topic,
                "dialogue_count": len(script.dialogues),
                "characters": list(unique_characters),
                "project_dir": str(project_dir)
            }
        )
