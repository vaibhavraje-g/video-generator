# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Dict


class Settings(BaseSettings):
     # --- Core API ---
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False

    # --- LLM Config ---
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # --- Video backend ---
    COMPOSE_BACKEND: str = "moviepy"  # or "ffmpeg"

    class Config:
        env_file = ".env"
        case_sensitive = False

    # LLM config
    MAX_LLM_RETRIES: int = 3
    RETRY_DELAY: float = 1.5
    TEMPERATURE: float = 0.7
    MAX_OUTPUT_TOKENS: int = 2048
    TOP_P: float = 0.9
    TOP_K: int = 40

    SAFETY_SETTINGS: Dict[str, str] = {
        "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
    }

    # Other project configs
    PROJECTS_DIR: str = "projects"
    COMMON_ASSETS_DIR: str = "assets/common"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
