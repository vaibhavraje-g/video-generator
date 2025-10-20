#!/usr/bin/env python3
"""
Standalone Chatterbox TTS client.
Generates speech by calling a remote Chatterbox TTS web service.
Supports voice cloning, custom reference uploads, and multilingual TTS.
"""

import requests
import json
from pathlib import Path
from typing import Optional, Union


class ChatterboxClient:
    def __init__(self, base_url: str = "http://localhost:8004", **kwargs):
        """
        Initialize ChatterboxClient.

        Args:
            base_url: Base URL of the Chatterbox TTS server.
            **kwargs: Extra arguments for compatibility (e.g., character_voices, api_key, etc.)
        """
        self.base_url = base_url.rstrip("/")

        # store optional mappings or metadata (for backward compatibility)
        self.character_voices = kwargs.get("character_voices", {})
        self.character_mappings = kwargs.get("character_mappings", {})
        self.voice_samples_dir = kwargs.get("voice_samples_dir")
        self.outputs_dir = kwargs.get("outputs_dir")

    def upload_reference_audio(self, filepath: Union[str, Path]) -> str:
        """
        Upload a reference audio file (WAV) to the server.
        Returns the filename as stored on the server (e.g., 'my_voice.wav').
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Reference audio not found: {filepath}")

        with open(filepath, "rb") as f:
            files = {"files": (filepath.name, f, "audio/wav")}
            resp = requests.post(f"{self.base_url}/upload_reference", files=files)

        resp.raise_for_status()
        result = resp.json()
        uploaded = result.get("uploaded_files")
        if not uploaded:
            raise RuntimeError("Upload succeeded but no filename returned.")
        return uploaded[0]

    def generate(
        self,
        text: str,
        reference_audio_filename: Optional[str] = None,
        reference_audio_path: Optional[Union[str, Path]] = None,
        language: str = "en",  # ISO 639-1 code
        output_path: Union[str, Path] = "output.wav",
        temperature: float = 0.8,
        exaggeration: float = 0.5,
        cfg_weight: float = 0.5,
        speed_factor: float = 1.0,
        seed: int = 0,
        split_text: bool = True,
        chunk_size: int = 120,
        output_format: str = "wav",
        character: Optional[str] = None,  # ✅ Added for compatibility
        **kwargs,
    ) -> str:
        """
        Generate TTS audio using the Chatterbox web service.

        Args:
            text: Input text to synthesize.
            reference_audio_filename: Name of already-uploaded reference file on server.
            reference_audio_path: Local path to upload as reference (overrides filename).
            character: Optional character name for automatic reference lookup.
        """

        # --- Handle character voice mapping (if provided)
        if character and not reference_audio_path and not reference_audio_filename:
            mapped = self.character_voices.get(character)
            if mapped:
                reference_audio_filename = mapped
                print(f"🎭 Using mapped reference for '{character}': {mapped}")
            else:
                print(f"⚠️ No mapped voice found for '{character}', will require manual upload or fallback.")

        # --- Handle reference upload if needed
        if reference_audio_path:
            print(f"📤 Uploading reference audio: {reference_audio_path}")
            reference_audio_filename = self.upload_reference_audio(reference_audio_path)

        if not reference_audio_filename:
            raise ValueError(
                "No reference audio provided. Must provide either `reference_audio_filename`, `reference_audio_path`, or mapped `character` voice."
            )

        # Build payload (matches UI's getTTSFormData())
        payload = {
            "text": text.strip(),
            "voice_mode": "clone",
            "reference_audio_filename": reference_audio_filename,
            "language": language,
            "temperature": float(temperature),
            "exaggeration": float(exaggeration),
            "cfg_weight": float(cfg_weight),
            "speed_factor": float(speed_factor),
            "seed": int(seed),
            "split_text": bool(split_text),
            "chunk_size": int(chunk_size),
            "output_format": output_format,
        }

        print(f"📡 Sending TTS request (lang={language}) using reference: {reference_audio_filename}")
        try:
            resp = requests.post(
                f"{self.base_url}/tts",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
            )
            resp.raise_for_status()
        except requests.HTTPError as e:
            try:
                detail = resp.json().get("detail", str(e))
            except Exception:
                detail = resp.text or str(e)
            raise RuntimeError(f"TTS request failed: {detail}") from e

        # --- Save output
        output_path = Path(output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(resp.content)

        print(f"✅ Audio saved to: {output_path}")
        return str(output_path)


# Backward-compatible alias
ChatterboxProvider = ChatterboxClient


