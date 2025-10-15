import random
import numpy as np
import torch
from pathlib import Path
from typing import Dict, Optional
from scipy.io import wavfile
from .text_preprocessor import TTSPreprocessor  # <-- new smart preprocessor


class ChatterboxProvider:
    """ChatterboxTTS provider for character voice cloning with smart preprocessing"""

    _model_instance = None

    def __init__(
        self,
        character_voices: Dict[str, str],
        character_mappings: Dict[str, str],
        voice_samples_dir: Path,
        outputs_dir: Path,
        device: str = "auto",
    ):
        """
        Initialize Chatterbox provider.

        Args:
            character_voices: Character to voice file mapping.
            character_mappings: Character name variations mapping.
            voice_samples_dir: Directory containing reference voice samples.
            outputs_dir: Output directory for generated files.
            device: Device to use ('cuda', 'cpu', or 'auto').
        """
        self.character_voices = character_voices
        self.character_mappings = character_mappings
        self.voice_samples_dir = Path(voice_samples_dir)
        self.outputs_dir = Path(outputs_dir)
        self.device = self._resolve_device(device)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

        # ✅ Unified text preprocessor for all TTS
        self.preprocessor = TTSPreprocessor()

    @staticmethod
    def _resolve_device(device: str) -> str:
        """Resolve device configuration."""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device

    def normalize_character_name(self, character: str) -> Optional[str]:
        """Normalize character name to match available voices."""
        if not character:
            return None

        character_lower = character.lower().strip()

        if character_lower in self.character_mappings:
            return self.character_mappings[character_lower]

        for known_name, mapped_name in self.character_mappings.items():
            if known_name in character_lower:
                return mapped_name

        for base_char in self.character_voices.keys():
            if base_char in character_lower:
                return base_char

        return None

    def _set_seed(self, seed: int):
        """Set random seed for reproducibility."""
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        random.seed(seed)
        np.random.seed(seed)

    def get_model(self):
        """Get or load the ChatterboxTTS model (singleton pattern)."""
        if ChatterboxProvider._model_instance is None:
            try:
                from chatterbox.tts import ChatterboxTTS
            except ImportError:
                raise ImportError(
                    "ChatterboxTTS not installed. Install via: pip install chatterbox-tts"
                )

            print(f"🔊 Loading ChatterboxTTS model on {self.device}...")
            ChatterboxProvider._model_instance = ChatterboxTTS.from_pretrained(self.device)
            print("✅ Model loaded successfully!")

        return ChatterboxProvider._model_instance

    def generate(
        self,
        text: str,
        character: str,
        output_path: str,
        exaggeration: float = 0.5,
        temperature: float = 0.8,
        seed: int = 0,
        cfg_weight: float = 0.5,
        min_p: float = 0.05,
        top_p: float = 1.0,
        repetition_penalty: float = 1.2,
    ) -> str:
        """Generate TTS with character voice using ChatterboxTTS."""

        normalized_char = self.normalize_character_name(character)

        if not normalized_char:
            raise ValueError(
                f"❌ Unknown character: {character}. Available voices: {list(self.character_voices.keys())}"
            )

        audio_prompt_path = self.voice_samples_dir / self.character_voices[normalized_char]

        if not audio_prompt_path.exists():
            raise FileNotFoundError(f"🎙️ Voice sample not found: {audio_prompt_path}")

        print(f"🧠 Generating TTS for character: {character} → {normalized_char}")

        # ✅ Step 1: Preprocess and clean the text
        cleaned_text = self.preprocessor.clean(text)
        sentences = self.preprocessor.segment(cleaned_text)
        chunks = self.preprocessor.chunk_for_tts(sentences, max_chars=160)

        print(f"📜 Text cleaned and split into {len(chunks)} chunk(s).")
        print(f"🎤 Using reference voice: {audio_prompt_path}")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        model = self.get_model()

        if seed:
            self._set_seed(seed)

        # ✅ Step 2: Generate and combine chunks
        combined_audio = []
        for i, chunk in enumerate(chunks):
            print(f"🎧 Synthesizing chunk {i + 1}/{len(chunks)} ({len(chunk)} chars)...")
            wav = model.generate(
                chunk,
                audio_prompt_path=str(audio_prompt_path),
                exaggeration=exaggeration,
                temperature=temperature,
                cfg_weight=cfg_weight,
                min_p=min_p,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
            )
            combined_audio.append(wav.squeeze(0).numpy())

        # ✅ Step 3: Add natural pause between chunks
        pause_samples = int(0.25 * model.sr)  # 250ms pause
        pause = np.zeros(pause_samples)

        final_audio = np.concatenate(
            [np.concatenate([chunk, pause]) for chunk in combined_audio]
        )

        wavfile.write(output_path, model.sr, final_audio)
        print(f"✅ Character TTS saved: {output_path}")

        return str(output_path)
