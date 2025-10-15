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


def ease_in_out_cubic(t):
    """Cubic easing function for smooth animation."""
    if t < 0.5:
        return 4 * t * t * t
    p = 2 * t - 2
    return 1 + p * p * p / 2


def ease_out_back(t):
    """Ease out with slight overshoot for bounce effect."""
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)


def create_animated_overlay(
    image_path,
    duration,
    video_size,
    final_position,
    max_height=300,
    animation_type="slide_left",
    animation_config=None,
):
    """Create ImageClip with smooth slide transitions and animations."""
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        return None

    try:
        # Load image with transparency support
        img = ImageClip(image_path, transparent=True, duration=duration)

        # Resize maintaining aspect ratio
        img = img.resize(height=max_height)

        video_w, video_h = video_size
        final_x, final_y = final_position

        # Get animation settings
        if animation_config is None:
            animation_config = {}

        slide_duration = animation_config.get("slide_duration", 0.3)
        fade_duration = animation_config.get("fade_duration", 0.2)
        ease_type = animation_config.get("ease_type", "cubic")

        # Choose easing function
        if ease_type == "bounce":
            ease_func = ease_out_back
        else:
            ease_func = ease_in_out_cubic

        # Create position function for slide animation
        def make_position_func(t):
            # Slide in animation (first part)
            if t < slide_duration:
                progress = ease_func(t / slide_duration)

                if animation_type == "slide_left":
                    # Start from left side, slide to center
                    start_x = -img.w
                    current_x = start_x + (final_x - start_x) * progress
                    return (current_x, final_y)

                elif animation_type == "slide_right":
                    # Start from right side, slide to center
                    start_x = video_w
                    current_x = start_x + (final_x - start_x) * progress
                    return (current_x, final_y)

                else:  # fade only
                    return (final_x, final_y)

            # Stay in position (middle part)
            elif t < duration - slide_duration:
                return (final_x, final_y)

            # Slide out animation (last part)
            else:
                exit_progress = ease_func(
                    (t - (duration - slide_duration)) / slide_duration
                )

                if animation_type == "slide_left":
                    # Exit to left side
                    end_x = -img.w
                    current_x = final_x + (end_x - final_x) * exit_progress
                    return (current_x, final_y)

                elif animation_type == "slide_right":
                    # Exit to right side
                    end_x = video_w
                    current_x = final_x + (end_x - final_x) * exit_progress
                    return (current_x, final_y)

                else:  # fade only
                    return (final_x, final_y)

        # Apply position animation
        img = img.set_position(make_position_func)

        # Add fade effects for smoother transitions
        if duration > fade_duration * 2:
            img = img.fx(vfx.fadein, fade_duration)
            img = img.fx(vfx.fadeout, fade_duration)

        return img

    except Exception as e:
        print(f"[ERROR] Could not load image {image_path}: {e}")
        return None


def create_positioned_overlay(
    image_path, duration, video_size, position, max_height=300, with_animation=True
):
    """Legacy function for backward compatibility - redirects to animated version."""
    return create_animated_overlay(
        image_path,
        duration,
        video_size,
        position,
        max_height,
        animation_type="fade" if not with_animation else "slide_left",
        animation_config={"slide_duration": 0.3, "fade_duration": 0.2},
    )


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
