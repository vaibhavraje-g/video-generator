import os
import random
import numpy as np
import torch
from pathlib import Path
from gtts import gTTS
from chatterbox.tts import ChatterboxTTS

# Configuration
# Script location: app/services/shared_services/tts_service.py
# Navigate up to project root: ../../../
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
VOICE_SAMPLES_DIR = PROJECT_ROOT / "assets" / "voice_samples"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Device configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Character voice reference audio paths
CHARACTER_VOICES = {
    "peter": VOICE_SAMPLES_DIR / "peter_voice.mp3",
    "brian": VOICE_SAMPLES_DIR / "brian_voice.mp3",
    "stewie": VOICE_SAMPLES_DIR / "stewie_voice.mp3",
}

# Character name mappings (handles variations like "peter griffin", "Peter", etc.)
CHARACTER_MAPPINGS = {
    "peter": "peter",
    "peter griffin": "peter",
    "brian": "brian",
    "brian griffin": "brian",
    "stewie": "stewie",
    "stewie griffin": "stewie",
}


def normalize_character_name(character: str) -> str:
    """
    Normalize character name to match available voices.
    Handles variations like 'Peter Griffin', 'peter', 'STEWIE', etc.

    Args:
        character: Character name (can be 'peter', 'Peter Griffin', etc.)

    Returns:
        Normalized character name or None if not found
    """
    if not character:
        return None

    # Convert to lowercase for matching
    character_lower = character.lower().strip()

    # Direct match in mappings
    if character_lower in CHARACTER_MAPPINGS:
        return CHARACTER_MAPPINGS[character_lower]

    # Fuzzy search - check if any known character name is in the input
    for known_name, mapped_name in CHARACTER_MAPPINGS.items():
        if known_name in character_lower:
            return mapped_name

    # Check if input contains any of our base character names
    for base_char in CHARACTER_VOICES.keys():
        if base_char in character_lower:
            return base_char

    return None


# Global model instance (loaded once)
_model_instance = None


def set_seed(seed: int):
    """Set random seed for reproducibility"""
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    random.seed(seed)
    np.random.seed(seed)


def get_model():
    """Get or load the ChatterboxTTS model (singleton pattern)"""
    global _model_instance
    if _model_instance is None:
        print(f"🔧 Loading ChatterboxTTS model on {DEVICE}...")
        _model_instance = ChatterboxTTS.from_pretrained(DEVICE)
        print("✅ Model loaded successfully!")
    return _model_instance


def generate_gtts(text: str, output_path: str):
    """Generate basic TTS using gTTS (fallback)"""
    print("🔊 Generating basic TTS with gTTS...")
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(output_path)
    print(f"✅ Basic TTS saved to: {output_path}")
    return output_path


def generate_character_tts(
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
):
    """Generate TTS with character voice using ChatterboxTTS"""

    # Normalize character name
    normalized_char = normalize_character_name(character)

    if not normalized_char:
        raise ValueError(
            f"Unknown character: {character}. Available: {list(CHARACTER_VOICES.keys())}"
        )

    # Get reference audio path
    audio_prompt_path = CHARACTER_VOICES[normalized_char]

    if not audio_prompt_path.exists():
        raise FileNotFoundError(f"Voice sample not found: {audio_prompt_path}")

    print(f"🎭 Generating TTS for character: {character} → {normalized_char}")
    print(f"📝 Text: {text[:100]}..." if len(text) > 100 else f"📝 Text: {text}")
    print(f"🎤 Using reference: {audio_prompt_path}")

    # Load model
    model = get_model()

    # Set seed if specified
    if seed != 0:
        set_seed(seed)

    # Generate audio
    wav = model.generate(
        text,
        audio_prompt_path=str(audio_prompt_path),
        exaggeration=exaggeration,
        temperature=temperature,
        cfg_weight=cfg_weight,
        min_p=min_p,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
    )

    # Save audio
    import scipy.io.wavfile as wavfile

    wavfile.write(output_path, model.sr, wav.squeeze(0).numpy())

    print(f"✅ Character TTS saved to: {output_path}")
    return output_path


def generate_tts(text: str, output_path: str, character: str = None, **kwargs):
    """
    Main TTS generation function

    Args:
        text: Text to synthesize
        output_path: Output file path
        character: Character name (peter, brian, stewie, or variations like 'Peter Griffin') or None for basic TTS
        **kwargs: Additional parameters for ChatterboxTTS (exaggeration, temperature, etc.)

    Returns:
        Path to generated audio file
    """

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Normalize and check character
    if character:
        normalized_char = normalize_character_name(character)

        if normalized_char:
            # Use character voice
            try:
                return generate_character_tts(text, character, output_path, **kwargs)
            except Exception as e:
                print(f"⚠️ Character TTS failed: {e}")
                print("🔄 Falling back to basic TTS...")
                return generate_gtts(text, output_path)
        else:
            # Unknown character
            print(f"⚠️ Unknown character '{character}', using basic TTS")
            return generate_gtts(text, output_path)
    else:
        # No character specified - use basic gTTS
        return generate_gtts(text, output_path)


# Convenience functions for each character
def generate_peter_voice(text: str, output_path: str, **kwargs):
    """Generate TTS in Peter Griffin's voice"""
    return generate_tts(text, output_path, character="peter", **kwargs)


def generate_brian_voice(text: str, output_path: str, **kwargs):
    """Generate TTS in Brian's voice"""
    return generate_tts(text, output_path, character="brian", **kwargs)


def generate_stewie_voice(text: str, output_path: str, **kwargs):
    """Generate TTS in Stewie's voice"""
    return generate_tts(text, output_path, character="stewie", **kwargs)


if __name__ == "__main__":
    print("🚀 ChatterboxTTS Character Voice Service")
    print("=" * 60)

    # Test with each character
    test_text = "Hey there! This is a test of the character voice cloning system."

    test_cases = [
        ("peter", "Peter Griffin voice"),
        ("brian", "Brian voice"),
        ("stewie", "Stewie voice"),
        (None, "Basic gTTS voice"),
    ]

    for character, description in test_cases:
        print(f"\n🧪 Testing {description}...")
        output_file = OUTPUTS_DIR / f"test_{character or 'basic'}.wav"

        try:
            generate_tts(
                text=test_text,
                output_path=str(output_file),
                character=character,
                exaggeration=0.5,
                temperature=0.8,
                cfg_weight=0.5,
            )
            print(f"✅ Success! Output: {output_file}")
        except Exception as e:
            print(f"❌ Failed: {e}")

    print("\n" + "=" * 60)
    print("🎉 Testing complete!")
    print(f"📂 Check outputs in: {OUTPUTS_DIR}")
