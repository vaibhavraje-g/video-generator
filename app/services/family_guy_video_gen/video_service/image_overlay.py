"""
Image overlay service: builds infographic + character overlays for a dialogue.
The character overlay re-uses your existing create_animated_overlay utility.
The infographic overlay ensures:
 - aspect-ratio preserving resize,
 - downscale for over-large images,
 - gentle upscaling for very small images (bounded by upscale_limit),
 - horizontal centering inside the top section,
 - optional simple entry animation (crossfade + slight scale).
"""

import os
import tempfile
import numpy as np
from PIL import Image

from moviepy.editor import ImageClip, CompositeVideoClip
from moviepy.config import change_settings
from moviepy.editor import vfx

from .video_configs import (
    INFOGRAPHIC_CONFIG,
    CHARACTER_CONFIG,
    VIDEO_LAYOUT,
    ANIMATION_CONFIG,
)
from .video_utils import create_animated_overlay  # keeps your existing character animation

# If ImageMagick is used anywhere else, keep path (optional)
change_settings(
    {"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe"}
)


def _load_and_resample_image(img_path, target_size=None, resample=Image.LANCZOS):
    """
    Load with PIL and optionally resize to target_size (w,h) using high-quality resampling.
    Returns a PIL.Image instance.
    """
    img = Image.open(img_path).convert("RGBA")
    if target_size is not None:
        img = img.resize(target_size, resample=resample)
    return img


def build_infographic_overlay(img_path, bg_segment, duration):
    """
    Build a clean, centered infographic overlay clip.

    Behavior:
     - Preserve aspect ratio.
     - Downscale images larger than INFOGRAPHIC_CONFIG limits.
     - Gently upscale smaller images (bounded by upscale_limit).
     - Center horizontally and position within the top section (respecting top_margin).
     - Apply a short crossfade-in and a subtle scale-in effect for polish.
    """
    video_w, video_h = bg_segment.size
    max_w = INFOGRAPHIC_CONFIG["max_width"]
    max_h = INFOGRAPHIC_CONFIG["max_height"]
    top_margin = INFOGRAPHIC_CONFIG.get("top_margin", 80)
    upscale_limit = INFOGRAPHIC_CONFIG.get("upscale_limit", 1.25)
    upscale_threshold_frac = INFOGRAPHIC_CONFIG.get("upscale_threshold_frac", 0.8)

    if not os.path.exists(img_path):
        return None

    # Load original size with PIL to get precise sampling control
    with Image.open(img_path).convert("RGBA") as pil_img:
        iw, ih = pil_img.size

        # Compute scale factors
        scale_down_w = max_w / iw
        scale_down_h = max_h / ih
        scale = min(scale_down_w, scale_down_h, 1.0)  # default: downscale to fit, never >1

        # If image is significantly smaller than target, gently upscale (but capped)
        if iw < max_w * upscale_threshold_frac and ih < max_h * upscale_threshold_frac:
            # compute ideal upscale factor to bring closer to max size but cap it
            upscale_w = (max_w * 0.9) / iw
            upscale_h = (max_h * 0.9) / ih
            upscale_factor = min(upscale_w, upscale_h, upscale_limit)
            # only upscale if it improves balance (no extreme upscales)
            if upscale_factor > scale:
                scale = upscale_factor

        # final dimensions
        final_w = max(1, int(iw * scale))
        final_h = max(1, int(ih * scale))

        # Resize using high-quality resampling (LANCZOS)
        pil_resized = pil_img.resize((final_w, final_h), resample=Image.LANCZOS)

        # Convert to numpy and create ImageClip
        arr = np.array(pil_resized)
        img_clip = ImageClip(arr).set_duration(duration)

    # Position: horizontally centered, vertically within the top section
    x_pos = (video_w - final_w) // 2

    # We want the infographic to sit *inside* the top section visually.
    # Compute the vertical center for the top section and place the image centered there,
    # but pushed down by top_margin so it doesn't hug the very top.
    top_section_center_y = int(video_h * (VIDEO_LAYOUT["top_section"] / 2.0))
    # add configured top_margin: move down from the very top by top_margin pixels
    y_pos = max(0, top_margin + top_section_center_y - final_h // 2)

    img_clip = img_clip.set_position((x_pos, y_pos))

    # Apply a short crossfade-in for smoother entry
    fade_dur = ANIMATION_CONFIG.get("fade_duration", 0.2)
    # Small scale-in effect: animate size slightly from 1.05 -> 1.0 over slide_duration
    slide_dur = ANIMATION_CONFIG.get("slide_duration", 0.3)

    # clamp slide_dur to avoid divide by zero
    slide_dur = max(0.05, slide_dur)

    # Create a resize function that gently scales from 1.05 -> 1.0
    def resize_factor(t):
        # t in seconds relative to clip start
        frac = min(t / slide_dur, 1.0)
        return 1.05 - 0.05 * frac

    # Attach transform: resize by dynamic factor, then crossfadein
    try:
        animated = img_clip.resize(resize_factor).crossfadein(fade_dur)
    except Exception:
        # In case resize(lambda) is not supported in environment, fallback to static resized clip
        animated = img_clip.crossfadein(fade_dur)

    return animated


def build_image_overlays(dlg, duration, bg_segment, index, char_images, infographic_map):
    """
    Build image overlays for the dialogue:
      - infographic (top) — auto-resized & centered using build_infographic_overlay
      - character (bottom) — uses create_animated_overlay (keeps your existing behavior)
    Returns a list of clips to be composited on top of the background.
    """
    video_w, video_h = bg_segment.size
    overlays = []

    # Infographic (top)
    info_path = infographic_map.get(index)
    if info_path and os.path.exists(info_path):
        try:
            info_clip = build_infographic_overlay(info_path, bg_segment, duration)
            if info_clip:
                overlays.append(info_clip)
        except Exception as e:
            # keep pipeline robust — log and continue
            print(f"[WARN] infographic processing failed for {info_path}: {e}")

    # Character (bottom) - preserve existing behavior via create_animated_overlay
    char_img = char_images.get(dlg.character.lower().strip()) if char_images else None
    if char_img and os.path.exists(char_img):
        try:
            char_clip = create_animated_overlay(
                char_img,
                duration,
                (video_w, video_h),
                final_position=(
                    (video_w - CHARACTER_CONFIG["max_width"]) // 2,
                    video_h - CHARACTER_CONFIG["max_height"] - CHARACTER_CONFIG["bottom_margin"],
                ),
                max_height=CHARACTER_CONFIG["max_height"],
                animation_type=CHARACTER_CONFIG.get("animation", "slide_left"),
                animation_config=ANIMATION_CONFIG,
            )
            if char_clip:
                overlays.append(char_clip)
        except Exception as e:
            print(f"[WARN] character overlay failed for {char_img}: {e}")

    return overlays
