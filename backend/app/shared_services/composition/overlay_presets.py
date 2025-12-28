# backend/app/shared_services/composition/overlay_presets.py
"""Position and styling presets for different aspect ratios"""

from dataclasses import dataclass
from typing import Tuple, Literal


AspectRatioType = Literal["9:16", "1:1", "16:9"]


@dataclass
class PositionPreset:
    """Position preset for an overlay element"""
    position: Tuple[int, int]  # (x, y) from top-left
    size: Tuple[int, int]      # (width, height)
    anchor: str = "center"


class OverlayPresets:
    """
    Predefined positions for overlays based on aspect ratio.
    
    Positions are designed for common video layouts:
    - Character overlays (left/right/center)
    - Text overlays (top/center/bottom)
    - Infographic positions
    """
    
    # Resolution presets by aspect ratio
    RESOLUTIONS = {
        "9:16": (1080, 1920),    # Vertical (shorts)
        "1:1": (1080, 1080),     # Square
        "16:9": (1920, 1080),    # Horizontal (YouTube)
    }
    
    # Character position presets
    CHARACTER_POSITIONS = {
        "9:16": {
            "left": PositionPreset(position=(100, 1400), size=(350, 350)),
            "right": PositionPreset(position=(630, 1400), size=(350, 350)),
            "center": PositionPreset(position=(365, 1400), size=(350, 350)),
            "bottom_left": PositionPreset(position=(100, 1500), size=(300, 300)),
            "bottom_right": PositionPreset(position=(680, 1500), size=(300, 300)),
        },
        "1:1": {
            "left": PositionPreset(position=(50, 700), size=(300, 300)),
            "right": PositionPreset(position=(730, 700), size=(300, 300)),
            "center": PositionPreset(position=(390, 700), size=(300, 300)),
            "bottom_left": PositionPreset(position=(50, 730), size=(280, 280)),
            "bottom_right": PositionPreset(position=(750, 730), size=(280, 280)),
        },
        "16:9": {
            "left": PositionPreset(position=(100, 600), size=(400, 400)),
            "right": PositionPreset(position=(1420, 600), size=(400, 400)),
            "center": PositionPreset(position=(760, 600), size=(400, 400)),
            "bottom_left": PositionPreset(position=(100, 630), size=(350, 350)),
            "bottom_right": PositionPreset(position=(1470, 630), size=(350, 350)),
        },
    }
    
    # Text overlay positions
    TEXT_POSITIONS = {
        "9:16": {
            "top": PositionPreset(position=(540, 150), size=(1000, 100)),
            "center": PositionPreset(position=(540, 960), size=(1000, 100)),
            "bottom": PositionPreset(position=(540, 1750), size=(1000, 100)),
            "subtitle": PositionPreset(position=(540, 1600), size=(1000, 150)),
        },
        "1:1": {
            "top": PositionPreset(position=(540, 100), size=(1000, 80)),
            "center": PositionPreset(position=(540, 540), size=(1000, 80)),
            "bottom": PositionPreset(position=(540, 950), size=(1000, 80)),
            "subtitle": PositionPreset(position=(540, 900), size=(1000, 120)),
        },
        "16:9": {
            "top": PositionPreset(position=(960, 80), size=(1600, 80)),
            "center": PositionPreset(position=(960, 540), size=(1600, 80)),
            "bottom": PositionPreset(position=(960, 980), size=(1600, 80)),
            "subtitle": PositionPreset(position=(960, 920), size=(1600, 120)),
        },
    }
    
    # Infographic/image overlay positions
    INFOGRAPHIC_POSITIONS = {
        "9:16": {
            "main": PositionPreset(position=(540, 700), size=(800, 600)),
            "small_top": PositionPreset(position=(540, 400), size=(500, 375)),
            "small_center": PositionPreset(position=(540, 800), size=(500, 375)),
        },
        "1:1": {
            "main": PositionPreset(position=(540, 400), size=(700, 525)),
            "small_top": PositionPreset(position=(540, 250), size=(450, 340)),
            "small_center": PositionPreset(position=(540, 450), size=(450, 340)),
        },
        "16:9": {
            "main": PositionPreset(position=(960, 450), size=(900, 675)),
            "small_left": PositionPreset(position=(400, 400), size=(500, 375)),
            "small_right": PositionPreset(position=(1520, 400), size=(500, 375)),
        },
    }
    
    @classmethod
    def get_resolution(cls, aspect_ratio: AspectRatioType) -> Tuple[int, int]:
        """Get resolution for aspect ratio"""
        return cls.RESOLUTIONS.get(aspect_ratio, cls.RESOLUTIONS["9:16"])
    
    @classmethod
    def get_character_position(
        cls, 
        aspect_ratio: AspectRatioType, 
        position: str
    ) -> PositionPreset:
        """Get character overlay position"""
        positions = cls.CHARACTER_POSITIONS.get(aspect_ratio, cls.CHARACTER_POSITIONS["9:16"])
        return positions.get(position, positions["center"])
    
    @classmethod
    def get_text_position(
        cls,
        aspect_ratio: AspectRatioType,
        position: str
    ) -> PositionPreset:
        """Get text overlay position"""
        positions = cls.TEXT_POSITIONS.get(aspect_ratio, cls.TEXT_POSITIONS["9:16"])
        return positions.get(position, positions["bottom"])
    
    @classmethod
    def get_infographic_position(
        cls,
        aspect_ratio: AspectRatioType,
        position: str
    ) -> PositionPreset:
        """Get infographic overlay position"""
        positions = cls.INFOGRAPHIC_POSITIONS.get(aspect_ratio, cls.INFOGRAPHIC_POSITIONS["9:16"])
        return positions.get(position, positions["main"])
