# video_configs.py
"""
Centralized video configuration file for easy styling & layout changes.
"""

# --- Text (Subtitles) Configuration ---
TEXT_STYLE = {
    "width_ratio": 0.85,           # Slightly narrower to prevent overflow
    "max_chars_per_line": 36,      # Max characters per line
    "max_lines": 2,                # Allow up to 2 lines
    "bottom_margin": 350,          # Not used anymore, text is in middle

    "font": "Arial-Bold",          # More reliable font (change to available font on your system)
    "fontsize": 46,                # Font size tuned for 1080p vertical
    "color": "white",              # White text as requested
    "align": "center",
    "stroke_color": None,          # No stroke as requested
    "stroke_width": 0,             # No border

    "pad_x": 20,                   # Padding for highlight bg
    "pad_y": 10,                   # Padding for highlight bg
    "bg_color_rgba": (255, 220, 0, 230),  # RGBA for rounded highlight background
    "bg_radius": 12,
    "reserve_extra": 50,
    "word_spacing": 12,            # Space between words

    # Chunking behavior
    "words_per_chunk": 3,          # default 3 words per chunk (can be 3 or 4)
    "min_chunk_duration": 0.5,     # avoid extremely short chunks

    # Highlight timing inside each chunk (fraction of chunk duration)
    "highlight_fraction": 0.75,    # highlight covers ~75% of chunk center
    "highlight_delay_frac": 0.12,  # delay before highlight starts as fraction of chunk dur
}

TEXT_ANIMATION = {
    "fade_in": 0.12,                # Smooth fade in
    "fade_out": 0.12,               # Smooth fade out
}

# --- Infographic Overlay Config ---
INFOGRAPHIC_CONFIG = {
    "max_height": 200,             # Top area
    "max_width": 350,
    "top_margin": 50,              # Position from top
}

# --- Character Image Overlay Config ---
CHARACTER_CONFIG = {
    "max_height": 250,             # Bottom area
    "max_width": 350,
    "bottom_margin": 50,           # Position from bottom
    "side_margin": 60,
}

# --- General Video Layout ---
VIDEO_LAYOUT = {
    "target_aspect_ratio": 9 / 16,
    "output_height": 1080,
    "output_width": 608,
    "fps": 24,
}
