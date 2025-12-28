# backend/tests/unit/test_shared_services.py
"""Unit tests for shared services"""

import pytest
import tempfile
from pathlib import Path

from app.shared_services.frequency_service import frequency_service, SOLFEGGIO_PRESETS


class TestFrequencyService:
    """Tests for FrequencyService"""
    
    def test_get_preset(self):
        """Test getting frequency presets"""
        preset = frequency_service.get_preset(528)
        assert preset is not None
        assert preset.frequency == 528
        assert preset.name == "Healing"
    
    def test_list_presets(self):
        """Test listing all presets"""
        presets = frequency_service.list_presets()
        assert len(presets) == 6
        frequencies = [p.frequency for p in presets]
        assert 432 in frequencies
        assert 528 in frequencies
        assert 963 in frequencies
    
    def test_generate_tone(self):
        """Test generating a simple tone"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name
        
        result = frequency_service.generate_tone(
            frequency=432,
            duration_seconds=2.0,
            output_path=output_path
        )
        
        assert Path(result).exists()
        assert Path(result).stat().st_size > 0
        
        # Cleanup
        Path(result).unlink()
    
    def test_generate_binaural(self):
        """Test generating binaural beats"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name
        
        result = frequency_service.generate_binaural(
            base_frequency=432,
            beat_frequency=7.83,
            duration_seconds=2.0,
            output_path=output_path
        )
        
        assert Path(result).exists()
        assert Path(result).stat().st_size > 0
        
        # Cleanup
        Path(result).unlink()


class TestOverlayPresets:
    """Tests for overlay position presets"""
    
    def test_get_resolution(self):
        from app.shared_services.composition.overlay_presets import OverlayPresets
        
        res = OverlayPresets.get_resolution("9:16")
        assert res == (1080, 1920)
        
        res = OverlayPresets.get_resolution("16:9")
        assert res == (1920, 1080)
        
        res = OverlayPresets.get_resolution("1:1")
        assert res == (1080, 1080)
    
    def test_character_positions(self):
        from app.shared_services.composition.overlay_presets import OverlayPresets
        
        left_pos = OverlayPresets.get_character_position("9:16", "left")
        assert left_pos is not None
        assert left_pos.position is not None
        
        right_pos = OverlayPresets.get_character_position("9:16", "right")
        assert right_pos.position != left_pos.position
