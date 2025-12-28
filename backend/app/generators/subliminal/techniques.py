# backend/app/generators/subliminal/techniques.py
"""Subliminal message techniques"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class SubliminalTechnique(str, Enum):
    """Available subliminal message techniques"""
    FLASH_TEXT = "flash_text"           # Brief flashes of text
    BACKGROUND_BLEND = "background_blend"  # Blended text layer
    AUDIO_LAYERED = "audio_layered"     # Whispered audio below threshold
    MIRROR_REVERSE = "mirror_reverse"   # Reversed/mirrored text


@dataclass
class TechniqueConfig:
    """Configuration for a subliminal technique"""
    technique: SubliminalTechnique
    display_name: str
    description: str
    requires_audio: bool = False
    requires_video: bool = True
    

TECHNIQUE_CONFIGS = {
    SubliminalTechnique.FLASH_TEXT: TechniqueConfig(
        technique=SubliminalTechnique.FLASH_TEXT,
        display_name="Flash Text",
        description="Brief visible affirmations that flash on screen (100-200ms)",
        requires_video=True
    ),
    SubliminalTechnique.BACKGROUND_BLEND: TechniqueConfig(
        technique=SubliminalTechnique.BACKGROUND_BLEND,
        display_name="Background Blend",
        description="Affirmations blended into the background at low opacity",
        requires_video=True
    ),
    SubliminalTechnique.AUDIO_LAYERED: TechniqueConfig(
        technique=SubliminalTechnique.AUDIO_LAYERED,
        display_name="Audio Layered",
        description="Whispered affirmations layered below main audio",
        requires_audio=True,
        requires_video=True
    ),
    SubliminalTechnique.MIRROR_REVERSE: TechniqueConfig(
        technique=SubliminalTechnique.MIRROR_REVERSE,
        display_name="Mirror/Reverse",
        description="Text displayed in reverse or mirrored format",
        requires_video=True
    ),
}


# Background style to search query mappings
BACKGROUND_STYLE_QUERIES = {
    "nature": "peaceful nature scenery forest river calm hd",
    "abstract": "abstract colorful flowing animation meditation",
    "space": "space stars galaxy cosmos nebula calm",
    "ocean": "calm ocean waves peaceful beach sunset",
    "custom": None  # User provides
}


# Audio track presets
AUDIO_PRESETS = {
    "ambient": {
        "query": "ambient calm meditation music",
        "description": "Calm ambient music"
    },
    "binaural": {
        "frequency": 528,
        "beat": 7.83,
        "description": "Binaural beats for deep relaxation"
    },
    "nature": {
        "query": "nature sounds rain forest birds",
        "description": "Natural ambient sounds"
    },
    "lofi": {
        "query": "lofi calm beats study",
        "description": "Lo-fi chill beats"
    },
    "custom": None
}
