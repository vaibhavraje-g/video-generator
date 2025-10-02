from typing import List, Dict, Optional
from pydantic import BaseModel


class FrequencyConfig(BaseModel):
    type: str  # binaural, isochronic, solfeggio
    frequency_left: Optional[float]  # For binaural beats
    frequency_right: Optional[float]  # For binaural beats
    base_frequency: Optional[float]  # For isochronic/solfeggio
    volume: float
    tags: List[str]


class AudioConfig(BaseModel):
    tts: Dict[str, any]  # voice settings, volume, etc.
    background_music: Dict[str, str]  # theme, tags
    frequencies: List[FrequencyConfig]


class BackgroundVideoConfig(BaseModel):
    theme: str
    tags: List[str]


class SubliminalVideoConfig(BaseModel):
    language: str
    duration_minutes: int
    messages: List[str]
    message_repeat_strategy: str
    background_video: BackgroundVideoConfig
    audio: AudioConfig
