"""
Centralized video configuration file for styling, layout, and speed control.
"""

# --- Text (Subtitles) Configuration ---
TEXT_STYLE = {
    "width_ratio": 0.85,
    "max_chars_per_line": 36,
    "max_lines": 2,
    "font": "Impact",
    "fontsize": 56,
    "font_name": ".LuckiestGuy-Regular.ttf",
    "color": "white",
    "gradient_colors": ["#FFD700", "#FFA500"],
    "align": "center",
    "stroke_color": "black",
    "stroke_width": 3,
    "shadow_color": "rgba(0,0,0,0.7)",
    "shadow_offset": (3, 3),
    "pad_x": 25,
    "pad_y": 15,
    "bg_color_rgba": (255, 255, 255, 25),
    "bg_radius": 15,
    "reserve_extra": 50,
    "word_spacing": 14,
    "words_per_chunk": 3,
    "min_chunk_duration": 0.5,
    "highlight_fraction": 0.75,
    "highlight_delay_frac": 0.12,
}

TEXT_ANIMATION = {
    "fade_in": 0.15,
    "fade_out": 0.15,
    "slide_in": True,
    "slide_direction": "bottom",
    "bounce_effect": True,
    "scale_in": 1.1,
}

# --- Animation Configuration ---
ANIMATION_CONFIG = {
    "slide_duration": 0.3,
    "fade_duration": 0.2,
    "ease_type": "cubic",
    "overshoot": 1.05,
    "stagger_delay": 0.05,
}

# --- Infographic Overlay Config ---
INFOGRAPHIC_CONFIG = {
    "max_height": 300,
    "max_width": 500,
    "top_margin": 80,
    "animation": "slide_right",
}

# --- Character Image Overlay Config ---
CHARACTER_CONFIG = {
    "max_height": 325,
    "max_width": 450,
    "bottom_margin": 30,
    "side_margin": 50,
    "animation": "slide_left",
}

# --- General Video Layout ---
VIDEO_LAYOUT = {
    "target_aspect_ratio": 9 / 16,
    "output_height": 1080,
    "output_width": 608,
    "fps": 24,
    "top_section": 0.33,
    "middle_section": 0.34,
    "bottom_section": 0.33,
}

# --- Playback speed ---
VIDEO_SPEED = 1.1  # 1.0 = normal speed, 1.1 = 10% faster
