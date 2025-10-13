import textwrap
import random
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests
import base64

from .tiktok_constants import (
    API_BASE_URL,
    ALL_VOICES,
    DEFAULT_VOICE,
    CHUNK_SIZE,
    DEFAULT_HEADERS,
)
from .text_preprocessor import TTSTextPreprocessor


class TikTokProvider:
    """TikTok API provider for TTS with extended voice support"""

    def __init__(self, config: Dict[str, Any], outputs_dir: Path = None):
        """
        Initialize TikTok provider

        Args:
            config: TikTok API configuration from config.json
            outputs_dir: Output directory for generated files (deprecated, use project_dir in generate())
        """
        self.config = config
        self.enabled = config.get("enabled", False)
        self.session_id = config.get("session_id")  # TikTok session ID for API access

        # Voice configuration
        self.default_voice = config.get("default_voice", DEFAULT_VOICE)
        self.available_voices = ALL_VOICES

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for TikTok API compatibility"""
        # First, use common text preprocessing
        text = TTSTextPreprocessor.clean_text(text, provider="tiktok")

        # Additional TikTok-specific formatting
        text = text.replace(" ", "+")
        return text

    def _make_tts_request(self, text: str, voice_id: str, **kwargs) -> bytes:
        """Make TTS API request and return audio data"""
        if (
            not self.session_id
            or not isinstance(self.session_id, str)
            or len(self.session_id.strip()) == 0
        ):
            raise ValueError(
                "Valid TikTok session ID is required. Please check your config.json"
            )

        # Update headers with session and additional required fields
        headers = DEFAULT_HEADERS.copy()
        headers.update(
            {
                "Cookie": f"sessionid={self.session_id}",
                "X-Bogus": self._generate_x_bogus(),  # TikTok security parameter
                "X-Ladon": "com.zhiliaoapp.musically",
            }
        )

        # Request parameters with voice quality controls
        params = {
            "text_speaker": voice_id,
            "req_text": self._preprocess_text(text),
            "speaker_map_type": "0",
            "aid": "1988",  # Updated app ID
            "text_speed": min(
                max(float(kwargs.get("speed", 1.0)), 0.5), 2.0
            ),  # Speed control (0.5-2.0)
            "voice_pitch": min(
                max(float(kwargs.get("pitch", 1.0)), 0.5), 2.0
            ),  # Pitch control (0.5-2.0)
            "voice_denoise": bool(kwargs.get("denoise", True)),  # Voice enhancement
            "emotion": kwargs.get(
                "emotion", "neutral"
            ),  # Voice emotion (neutral/happy/sad/angry)
        }

        # Make request with proper timeout and retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    API_BASE_URL,
                    headers=headers,
                    json=params,  # Use JSON format
                    timeout=10,
                )
                response.raise_for_status()
                data = response.json()

                if data.get("message") == "Couldn't load speech. Try again.":
                    if attempt < max_retries - 1:
                        print(f"🔄 Retrying... (attempt {attempt + 2}/{max_retries})")
                        continue
                    raise ValueError("Invalid session ID or API error")

                if "data" not in data or "v_str" not in data["data"]:
                    raise RuntimeError(
                        f"API error: {data.get('message', 'Unknown error')}"
                    )

                audio_data = base64.b64decode(data["data"]["v_str"])

                # Verify audio data
                if len(audio_data) < 100:  # Too small to be valid audio
                    raise ValueError("Invalid audio data received")

                return audio_data

            except (requests.exceptions.RequestException, ValueError) as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Request failed, retrying... ({e})")
                    continue
                raise RuntimeError(f"TikTok API request failed: {e}")

    def _generate_x_bogus(self) -> str:
        """Generate X-Bogus parameter required by TikTok API"""
        # This is a simplified version - in production, you'd need a proper X-Bogus generator
        import time
        import hashlib

        timestamp = int(time.time())
        device_id = hashlib.md5(str(timestamp).encode()).hexdigest()[:16]
        return f"{device_id}{timestamp}"

    def _process_long_text(
        self,
        text: str,
        voice_id: str,
        speed: float = 1.0,
        pitch: float = 1.0,
        denoise: bool = True,
        emotion: str = "normal",
        **kwargs,
    ) -> List[bytes]:
        """Process long text by splitting into chunks"""
        chunks = textwrap.wrap(
            text, width=CHUNK_SIZE, break_long_words=True, break_on_hyphens=False
        )

        audio_chunks = []
        for chunk in chunks:
            audio_data = self._make_tts_request(
                chunk,
                voice_id,
                speed=speed,
                pitch=pitch,
                denoise=denoise,
                emotion=emotion,
                **kwargs,
            )
            audio_chunks.append(audio_data)

        return audio_chunks

    def get_random_voice(self, category: Optional[str] = None) -> str:
        """Get a random voice ID, optionally from a specific category"""
        if category:
            category_dict = {
                "disney": "DISNEY_VOICES",
                "english": "ENGLISH_VOICES",
                "europe": "EUROPE_VOICES",
                "america": "AMERICA_VOICES",
                "asia": "ASIA_VOICES",
                "singing": "SINGING_VOICES",
                "special": "SPECIAL_VOICES",
            }.get(category.lower())

            if not category_dict:
                raise ValueError(f"Unknown voice category: {category}")

            voices = list(globals()[category_dict].values())
        else:
            voices = list(ALL_VOICES.values())

        return random.choice(voices)

    def generate(
        self,
        text: str,
        output_path: str,
        voice_id: str = None,
        random_voice: bool = False,
        voice_category: str = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        denoise: bool = True,
        emotion: str = "normal",
        project_dir: Optional[Path] = None,
        **kwargs,
    ) -> str:
        """
        Generate TTS using TikTok API

        Args:
            text: Text to synthesize
            output_path: Output file name (will be stored in project_dir/audio if project_dir is provided)
            voice_id: TikTok voice ID (optional)
            random_voice: Use random voice (overrides voice_id)
            voice_category: Category for random voice selection
            project_dir: Project directory where audio should be stored (under audio/ subdirectory)
            **kwargs: Additional parameters

        Returns:
            Path to generated audio file
        """
        if not self.enabled:
            raise RuntimeError("TikTok API is not enabled in config")

        print("🎵 Generating TikTok TTS audio...")
        print(f"📝 Text: {text[:100]}..." if len(text) > 100 else f"📝 Text: {text}")

        # Determine voice ID
        if random_voice:
            voice_id = self.get_random_voice(voice_category)
        else:
            voice_id = voice_id or self.default_voice

        print(f"🎤 Using voice: {voice_id}")

        try:
            # Determine output directory and path
            if project_dir:
                audio_dir = Path(project_dir) / "audio"
                output_file = audio_dir / output_path
            else:
                output_file = Path(output_path)

            # Create output directory
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Process text (handle long text if needed)
            if len(text) > CHUNK_SIZE:
                audio_chunks = self._process_long_text(text, voice_id)

                # Combine audio chunks
                with open(output_file, "wb") as out:
                    for chunk in audio_chunks:
                        out.write(chunk)
            else:
                # Single request for short text
                audio_data = self._make_tts_request(
                    text,
                    voice_id,
                    speed=speed,
                    pitch=pitch,
                    denoise=denoise,
                    emotion=emotion,
                    **kwargs,
                )
                with open(output_file, "wb") as out:
                    out.write(audio_data)

            print(f"OK TikTok TTS audio saved to: {output_file}")
            return str(output_file)

        except Exception as e:
            raise RuntimeError(f"TikTok TTS generation failed: {str(e)}")
