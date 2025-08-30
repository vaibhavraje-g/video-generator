import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Paths
    ASSETS_DIR = "assets"
    CHARACTERS_DIR = os.path.join(ASSETS_DIR, "characters")
    VIDEOS_DIR = os.path.join(ASSETS_DIR, "videos")
    TEMP_DIR = os.path.join(ASSETS_DIR, "temp")
    OUTPUT_DIR = os.path.join(ASSETS_DIR, "output")
    
    # Audio settings
    TTS_LANGUAGE = "en"
    AUDIO_FORMAT = "mp3"
    
    # Video settings
    VIDEO_FPS = 24
    VIDEO_CODEC = "libx264"
    AUDIO_CODEC = "aac"
    
    # Character positions
    CHARACTER_POSITIONS = {
        "peter": "left",
        "stewie": "right",
        "default": "center"
    }
    
    # Text styling
    SUBTITLE_CONFIG = {
        "fontsize": 95,
        "color": "yellow",
        "font": "DejaVu-Sans-Bold",
        "stroke_color": "black",
        "stroke_width": 0.3
    }
    
    TITLE_CONFIG = {
        "fontsize": 60,
        "color": "white",
        "font": "Arial-Bold",
        "bg_color": "black"
    }

    @classmethod
    def ensure_directories(cls):
        """Create all necessary directories if they don't exist"""
        directories = [
            cls.ASSETS_DIR,
            cls.CHARACTERS_DIR,
            cls.VIDEOS_DIR,
            cls.TEMP_DIR,
            cls.OUTPUT_DIR
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

settings = Settings()