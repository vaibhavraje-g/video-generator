import numpy as np
from scipy.io import wavfile
from typing import List, Dict
import requests
from pathlib import Path


def generate_frequencies(
    frequency_configs: List[Dict], output_path: str, duration_seconds: int = 60
) -> str:
    """Generate audio frequencies (binaural beats, isochronic tones, solfeggio) and save as WAV."""
    sample_rate = 44100
    t = np.linspace(0, duration_seconds, sample_rate * duration_seconds)

    combined_audio = np.zeros_like(t)

    for config in frequency_configs:
        volume = config.get("volume", 0.2)

        if config["type"] == "binaural":
            # Generate binaural beats - different frequencies for left and right ears
            left = np.sin(2 * np.pi * config["frequency_left"] * t)
            right = np.sin(2 * np.pi * config["frequency_right"] * t)
            stereo = np.vstack((left, right)) * volume
            combined_audio += np.mean(stereo, axis=0)

        elif config["type"] == "isochronic":
            # Generate isochronic tones - amplitude modulated sine wave
            carrier = np.sin(2 * np.pi * config["base_frequency"] * t)
            modulator = (np.sin(2 * np.pi * 4 * t) + 1) / 2  # 4 Hz modulation
            combined_audio += carrier * modulator * volume

        elif config["type"] == "solfeggio":
            # Generate solfeggio frequency - pure sine wave at specific frequencies
            wave = np.sin(2 * np.pi * config["base_frequency"] * t)
            combined_audio += wave * volume

    # Normalize
    combined_audio = np.int16(combined_audio * 32767)

    # Save audio file
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(output_path, sample_rate, combined_audio)

    return output_path


def fetch_background_music(music_config: Dict[str, str], output_path: str) -> str:
    """Fetch background music from free APIs based on theme and tags."""
    # TODO: Implement actual API calls to Pixabay/FreeSound
    # For now, return a placeholder or sample file

    # Dummy implementation - replace with actual API integration
    sample_url = "https://example.com/sample_ambient.mp3"
    response = requests.get(sample_url)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(response.content)

    return output_path
