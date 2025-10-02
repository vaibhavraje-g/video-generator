# video_utils.py
from moviepy.editor import ImageClip, vfx
from PIL import Image
import os
from moviepy.config import change_settings

change_settings(
    {"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe"}
)

# Pillow >= 10 compatibility
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS


def crop_to_vertical(clip, target_aspect=9 / 16, height=1080, width=608):
    """Crop a clip to vertical aspect ratio and resize."""
    h, w = clip.h, clip.w
    if w / h > target_aspect:  # too wide → crop sides
        new_w = int(h * target_aspect)
        x1 = (w - new_w) // 2
        clip = clip.crop(x1=x1, y1=0, x2=x1 + new_w, y2=h)
    else:  # too tall → crop top/bottom
        new_h = int(w / target_aspect)
        y1 = (h - new_h) // 2
        clip = clip.crop(x1=0, y1=y1, x2=w, y2=y1 + new_h)
    return clip.resize(height=height).resize(width=width)


def create_positioned_overlay(
    image_path, duration, video_size, position, max_height=300, with_animation=True
):
    """Create ImageClip with proper animations and positioning."""
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        return None

    try:
        # Load image with transparency support
        img = ImageClip(image_path, transparent=True, duration=duration)

        # Resize maintaining aspect ratio
        img = img.resize(height=max_height)

        # Ensure position is within bounds
        x = max(0, min(position[0], video_size[0] - img.w))
        y = max(0, min(position[1], video_size[1] - img.h))

        # Set position
        img = img.set_position((x, y))

        # Apply smooth animations
        if with_animation and duration > 0.4:
            fade_duration = min(0.2, duration / 4)
            img = img.fx(vfx.fadein, fade_duration)
            img = img.fx(vfx.fadeout, fade_duration)

        return img

    except Exception as e:
        print(f"[ERROR] Could not load image {image_path}: {e}")
        return None


def overlaps_with_used_areas(pos, width, height, used_areas):
    """Check if new rectangle overlaps with any used areas."""
    x, y = pos
    new_rect = (x, y, x + width, y + height)

    for used_x, used_y, used_w, used_h in used_areas:
        used_rect = (used_x, used_y, used_x + used_w, used_y + used_h)

        # Check for intersection
        if not (
            new_rect[2] <= used_rect[0]
            or new_rect[0] >= used_rect[2]
            or new_rect[3] <= used_rect[1]
            or new_rect[1] >= used_rect[3]
        ):
            return True

    return False
