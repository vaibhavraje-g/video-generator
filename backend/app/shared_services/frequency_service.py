# backend/app/shared_services/frequency_service.py
"""Frequency tone generation service for healing/manifestation videos"""

import math
import wave
import struct
import tempfile
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class FrequencyPreset:
    """Solfeggio frequency preset"""
    frequency: int
    name: str
    description: str
    color: str  # Associated color for visuals


# Solfeggio frequencies and their properties
SOLFEGGIO_PRESETS = {
    432: FrequencyPreset(
        frequency=432,
        name="Relaxing",
        description="Natural frequency for deep relaxation and harmony with nature",
        color="#4CAF50"  # Green
    ),
    528: FrequencyPreset(
        frequency=528,
        name="Healing",
        description="DNA repair, transformation, and miracles",
        color="#2196F3"  # Blue
    ),
    639: FrequencyPreset(
        frequency=639,
        name="Love",
        description="Harmonious relationships and connections",
        color="#E91E63"  # Pink
    ),
    741: FrequencyPreset(
        frequency=741,
        name="Cleansing",
        description="Purification, solutions, and self-expression",
        color="#9C27B0"  # Purple (internal use, not UI)
    ),
    852: FrequencyPreset(
        frequency=852,
        name="Intuition",
        description="Spiritual awakening and inner wisdom",
        color="#3F51B5"  # Indigo
    ),
    963: FrequencyPreset(
        frequency=963,
        name="Divine",
        description="Connection to higher consciousness and source",
        color="#FFC107"  # Gold
    )
}


class FrequencyService:
    """
    Generate frequency tones and binaural beats for healing videos.
    
    Supports:
    - Pure sine wave tones at solfeggio frequencies
    - Binaural beats (requires stereo)
    - Layered frequencies
    """
    
    SAMPLE_RATE = 44100  # CD quality
    PRESETS = SOLFEGGIO_PRESETS
    
    def get_preset(self, frequency: int) -> Optional[FrequencyPreset]:
        """Get preset info for a frequency"""
        return self.PRESETS.get(frequency)
    
    def list_presets(self) -> list[FrequencyPreset]:
        """List all available frequency presets"""
        return list(self.PRESETS.values())
    
    def generate_tone(
        self,
        frequency: int,
        duration_seconds: float,
        output_path: Optional[str] = None,
        amplitude: float = 0.5,
        fade_in: float = 0.5,
        fade_out: float = 0.5
    ) -> str:
        """
        Generate a pure sine wave tone.
        
        Args:
            frequency: Frequency in Hz
            duration_seconds: Duration of the tone
            output_path: Where to save (auto-generated if None)
            amplitude: Volume (0.0 to 1.0)
            fade_in: Fade in duration in seconds
            fade_out: Fade out duration in seconds
            
        Returns:
            Path to generated WAV file
        """
        if output_path is None:
            output_path = tempfile.mktemp(suffix=f"_{frequency}hz.wav")
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        num_samples = int(self.SAMPLE_RATE * duration_seconds)
        
        samples = []
        for i in range(num_samples):
            t = i / self.SAMPLE_RATE
            
            # Generate sine wave
            value = amplitude * math.sin(2 * math.pi * frequency * t)
            
            # Apply fade in
            if t < fade_in:
                value *= t / fade_in
            
            # Apply fade out
            time_from_end = duration_seconds - t
            if time_from_end < fade_out:
                value *= time_from_end / fade_out
            
            # Convert to 16-bit integer
            samples.append(int(value * 32767))
        
        # Write WAV file
        with wave.open(output_path, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.SAMPLE_RATE)
            
            for sample in samples:
                wav_file.writeframes(struct.pack('<h', sample))
        
        return output_path
    
    def generate_binaural(
        self,
        base_frequency: int,
        beat_frequency: float,
        duration_seconds: float,
        output_path: Optional[str] = None,
        amplitude: float = 0.5
    ) -> str:
        """
        Generate binaural beats (stereo).
        
        Left ear gets base_frequency, right ear gets base_frequency + beat_frequency.
        The perceived "beat" is the difference between them.
        
        Common beat frequencies:
        - Delta (0.5-4 Hz): Deep sleep
        - Theta (4-8 Hz): Meditation, creativity
        - Alpha (8-14 Hz): Relaxation
        - Beta (14-30 Hz): Focus, alertness
        
        Args:
            base_frequency: Base frequency for left ear
            beat_frequency: Difference frequency (the "beat")
            duration_seconds: Duration in seconds
            output_path: Where to save
            amplitude: Volume
            
        Returns:
            Path to generated stereo WAV file
        """
        if output_path is None:
            output_path = tempfile.mktemp(suffix=f"_binaural_{base_frequency}hz.wav")
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        num_samples = int(self.SAMPLE_RATE * duration_seconds)
        right_frequency = base_frequency + beat_frequency
        
        # Prepare stereo data
        with wave.open(output_path, 'w') as wav_file:
            wav_file.setnchannels(2)  # Stereo
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.SAMPLE_RATE)
            
            for i in range(num_samples):
                t = i / self.SAMPLE_RATE
                
                # Left channel: base frequency
                left = amplitude * math.sin(2 * math.pi * base_frequency * t)
                # Right channel: base + beat frequency
                right = amplitude * math.sin(2 * math.pi * right_frequency * t)
                
                # Apply fade in/out
                fade_time = 1.0
                if t < fade_time:
                    fade = t / fade_time
                    left *= fade
                    right *= fade
                elif t > duration_seconds - fade_time:
                    fade = (duration_seconds - t) / fade_time
                    left *= fade
                    right *= fade
                
                # Convert to 16-bit
                left_sample = int(left * 32767)
                right_sample = int(right * 32767)
                
                # Write stereo frame (left, right)
                wav_file.writeframes(struct.pack('<hh', left_sample, right_sample))
        
        return output_path
    
    def generate_layered(
        self,
        frequencies: list[int],
        duration_seconds: float,
        output_path: Optional[str] = None,
        amplitude_per_freq: float = 0.3
    ) -> str:
        """
        Generate layered frequencies (multiple tones combined).
        
        Args:
            frequencies: List of frequencies to layer
            duration_seconds: Duration
            output_path: Where to save
            amplitude_per_freq: Amplitude for each frequency
            
        Returns:
            Path to generated WAV file
        """
        if output_path is None:
            freq_str = "_".join(str(f) for f in frequencies[:3])
            output_path = tempfile.mktemp(suffix=f"_layered_{freq_str}.wav")
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        num_samples = int(self.SAMPLE_RATE * duration_seconds)
        
        with wave.open(output_path, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.SAMPLE_RATE)
            
            for i in range(num_samples):
                t = i / self.SAMPLE_RATE
                
                # Sum all frequencies
                value = 0
                for freq in frequencies:
                    value += amplitude_per_freq * math.sin(2 * math.pi * freq * t)
                
                # Normalize to prevent clipping
                value = max(-1, min(1, value))
                
                # Fade in/out
                fade_time = 1.0
                if t < fade_time:
                    value *= t / fade_time
                elif t > duration_seconds - fade_time:
                    value *= (duration_seconds - t) / fade_time
                
                sample = int(value * 32767)
                wav_file.writeframes(struct.pack('<h', sample))
        
        return output_path


# Singleton instance
frequency_service = FrequencyService()
