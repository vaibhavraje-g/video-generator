from gtts import gTTS
import os
from pathlib import Path

def generate_tts(text: str, output_path: str) -> str:
    """Generate TTS for given text and save as mp3."""
    Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
    tts = gTTS(text=text, lang="en")
    tts.save(output_path)
    return output_path

