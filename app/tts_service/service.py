"""Main TTS Service - Unified interface for all TTS providers"""

from pathlib import Path
from typing import Literal, Optional
from .config import TTSConfig
from .gtts_provider import GTTSProvider
from .tiktok_provider import TikTokProvider
from .chatterbox_provider import ChatterboxProvider
from .subtitle_service import SubtitleService
from .text_preprocessor import TTSPreprocessor


class TTSService:
    """
    Unified TTS Service supporting multiple providers:
    - ChatterboxTTS for character voice cloning
    - gTTS for basic TTS with voice options
    - TikTok API for free high-quality TTS
    - Local subtitle generation
    """

    def __init__(self, config_path: str = None, project_dir: Optional[Path] = None):
        self.config = TTSConfig(config_path)
        self.project_dir = project_dir

        self.voice_samples_dir = self.config.get_voice_samples_dir()
        self.outputs_dir = self.config.get_outputs_dir()

        tiktok_config = self.config.get_tiktok_config()
        self.tiktok_provider = TikTokProvider(tiktok_config)

        gtts_config = self.config.get_gtts_config()
        self.gtts_provider = GTTSProvider(outputs_dir=self.outputs_dir)

        chatterbox_config = self.config.get_chatterbox_config()
        self.chatterbox_provider = ChatterboxProvider(
            character_voices=chatterbox_config.get("character_voices", {}),
            character_mappings=chatterbox_config.get("character_mappings", {}),
            voice_samples_dir=self.voice_samples_dir,
            outputs_dir=self.outputs_dir,
            device=self.config.get_device(),
        )

        subtitle_config = self.config.get_subtitle_config()
        self.subtitle_service = SubtitleService(subtitle_config)

        # Smart preprocessing engine (gruut-backed)
        self.preprocessor = TTSPreprocessor()

    # --- Unified Generation API ---
    def generate(
        self,
        text: str,
        output_path: str,
        provider: Literal["chatterbox", "gtts", "tiktok"] = "gtts",
        **kwargs,
    ) -> str:
        # Preprocess text for natural speech
        clean_text = self.preprocessor.clean(text)

        if provider == "chatterbox":
            character = kwargs.pop("character", None)
            if not character:
                raise ValueError("Character name required for chatterbox provider")
            return self.generate_character_voice(
                clean_text, character, output_path, **kwargs
            )
        elif provider == "tiktok":
            return self.generate_tiktok_tts(clean_text, output_path, **kwargs)
        else:
            return self.generate_gtts(clean_text, output_path, **kwargs)

    # --- Individual Provider Methods ---
    def generate_character_voice(
        self, text: str, character: str, output_path: str, **kwargs
    ) -> str:
        try:
            return self.chatterbox_provider.generate(
                text, character, output_path, **kwargs
            )
        except Exception as e:
            print(f"WARNING Character TTS failed: {e}")
            print("Falling back to basic gTTS...")
            return self.generate_gtts(text, output_path)

    def generate_gtts(
        self,
        text: str,
        output_path: str,
        voice: Literal["male", "female"] = "male",
        lang: str = "en",
        slow: bool = False,
    ) -> str:
        return self.gtts_provider.generate(
            text, output_path, voice=voice, lang=lang, slow=slow
        )

    def generate_tiktok_tts(
        self,
        text: str,
        output_path: str,
        voice_id: str = None,
        project_dir: Optional[Path] = None,
        **kwargs,
    ) -> str:
        try:
            return self.tiktok_provider.generate(
                text,
                output_path,
                voice_id=voice_id,
                project_dir=project_dir or self.project_dir,
                **kwargs,
            )
        except Exception as e:
            print(f"WARNING TikTok TTS failed: {e}")
            print("Falling back to gTTS...")
            return self.generate_gtts(text, output_path)

    # --- Subtitles ---
    def generate_subtitles(self, sentences: list, audio_clips: list) -> str:
        return self.subtitle_service.generate_subtitles(sentences, audio_clips)

    def add_subtitles_to_video(
        self,
        video_path: str,
        subtitles_path: str,
        output_path: str,
        position: str = "center,bottom",
        font_path: str = None,
        font_size: int = 100,
        color: str = "white",
        stroke_color: str = "black",
        stroke_width: int = 5,
        threads: int = 2,
    ) -> str:
        return self.subtitle_service.add_subtitles_to_video(
            video_path,
            subtitles_path,
            output_path,
            position,
            font_path,
            font_size,
            color,
            stroke_color,
            stroke_width,
            threads,
        )

    # --- Utility Metho
