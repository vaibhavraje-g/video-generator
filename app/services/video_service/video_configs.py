# video_configs.py
"""
Centralized video configuration file for easy styling & layout changes.
Edit values here to change fonts, sizes, margins, positions, and animations.
"""

# --- Text (Subtitles) Configuration ---
TEXT_STYLE = {
    "width_ratio": 0.9,          # fraction of video width used for wrapping
    "max_chars": 20,             # soft target per line
    "max_lines": 2,              # 1–2 lines typical for subtitles
    "bottom_margin": 350,        # Increased to position text in middle area

    "font": "Montserrat-Bold",
    "fontsize": 30,
    "color": "white",
    "align": "center",           # 'left' | 'center' | 'right'
    "stroke_color": "Yellow",
    "stroke_width": 2,

    "pad_x": 20,                 # horizontal padding around text box
    "pad_y": 10,                 # vertical padding around text box
    "bg_color": (0, 0, 0),       # RGB tuple
    "bg_opacity": 0.6,           # 0..1
    # Reserve this many extra pixels as a safety band for subtitles
    "reserve_extra": 80,
}

TEXT_ANIMATION = {
    "fade_in": 0.3,              # Increased for more visible animation
    "fade_out": 0.3,             # Increased for more visible animation
}

# --- Infographic Overlay Config ---
INFOGRAPHIC_CONFIG = {
    "max_height": 250,           # px
    "max_width": 400,            # Added max width for better centering
    "top_margin": 80,            # px from top
}

# --- Character Image Overlay Config ---
CHARACTER_CONFIG = {
    "max_height": 300,           # Reduced slightly to fit better
    "max_width": 400,            # Added max width for better centering
    "bottom_margin": 100,        # Adjusted for bottom positioning
    "side_margin": 60,
}

# --- General Video Layout ---
VIDEO_LAYOUT = {
    "target_aspect_ratio": 9 / 16,
    "output_height": 1080,
    "output_width": 608,
    "fps": 24,
}
