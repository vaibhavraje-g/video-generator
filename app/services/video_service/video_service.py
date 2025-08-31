# video_service.py
from moviepy.editor import VideoFileClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
from moviepy.config import change_settings
from PIL import Image
import os

change_settings({"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe"})

# Pillow >=10 compatibility
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from .video_utils import crop_to_vertical, create_positioned_overlay, overlaps_with_used_areas
from .text_overlay import build_text_overlay
from .video_configs import VIDEO_LAYOUT, CHARACTER_CONFIG, INFOGRAPHIC_CONFIG


def build_character_overlay(dlg, duration, bg_segment, char_images, used_areas):
    """Build character overlay at the bottom of the screen."""
    overlays = []
    char_key = getattr(dlg, "character", "").lower().strip()

    if not char_images:
        # no images provided, return empty
        return overlays

    if not char_key:
        # dialogue doesn't specify a character
        return overlays

    if char_key not in char_images:
        # not found; log and exit
        print(f"[WARN] Character '{char_key}' not found in images: {list(char_images.keys())}")
        return overlays

    char_path = char_images[char_key]
    if not os.path.exists(char_path):
        print(f"[ERROR] Character image file not found: {char_path}")
        return overlays

    video_w, video_h = bg_segment.size

    # calculate size & position to center bottom while respecting max constraints
    max_h = CHARACTER_CONFIG.get("max_height", 250)
    max_w = CHARACTER_CONFIG.get("max_width", 350)

    # place character horizontally centered, vertically above bottom_margin
    x_pos = max(0, (video_w - max_w) // 2)
    y_pos = max(0, video_h - CHARACTER_CONFIG.get("bottom_margin", 50) - max_h)

    overlay = create_positioned_overlay(
        char_path, duration, (video_w, video_h),
        (x_pos, y_pos),
        max_h,
        with_animation=True
    )

    if overlay:
        # ensure overlay doesn't overlap reserved areas
        if not overlaps_with_used_areas((x_pos, y_pos), overlay.w, overlay.h, used_areas):
            overlays.append(overlay)
            used_areas.append((x_pos, y_pos, overlay.w, overlay.h))
        else:
            print(f"[WARN] character overlay for '{char_key}' would overlap used areas; skipping.")
    return overlays


def build_infographic_overlay(i, duration, bg_segment, infographic_images, used_areas):
    """Build infographic overlay at the top of the screen."""
    overlays = []

    if not infographic_images:
        return overlays

    if i >= len(infographic_images):
        return overlays

    path = infographic_images[i]
    if not path or not os.path.exists(path):
        print(f"[ERROR] Infographic image not found: {path}")
        return overlays

    video_w, video_h = bg_segment.size
    max_h = INFOGRAPHIC_CONFIG.get("max_height", 200)
    max_w = INFOGRAPHIC_CONFIG.get("max_width", 350)

    x_pos = max(0, (video_w - max_w) // 2)
    y_pos = INFOGRAPHIC_CONFIG.get("top_margin", 50)

    overlay = create_positioned_overlay(
        path, duration, bg_segment.size,
        (x_pos, y_pos),
        max_h,
        with_animation=True
    )

    if overlay:
        if not overlaps_with_used_areas((x_pos, y_pos), overlay.w, overlay.h, used_areas):
            overlays.append(overlay)
            used_areas.append((x_pos, y_pos, overlay.w, overlay.h))
        else:
            print(f"[WARN] infographic at index {i} would overlap used areas; skipping.")

    return overlays


def build_overlays_for_dialogue(dlg, duration, bg_segment, char_images, infographic_images, i):
    """Build all overlays with proper layering order."""
    overlay_clips = [bg_segment]
    used_areas = []

    # Layer order (bottom -> top):
    # 1) infographic (top area)
    # 2) character (bottom)
    # 3) text (topmost)
    infographic_overlays = build_infographic_overlay(i, duration, bg_segment, infographic_images, used_areas)
    character_overlays = build_character_overlay(dlg, duration, bg_segment, char_images, used_areas)
    text_overlays = build_text_overlay(dlg, duration, bg_segment, used_areas)

    # Add in order: background already present
    # Infographic sits visually near top (should be behind text)
    overlay_clips.extend(infographic_overlays)
    # Character sits above infographic but below text
    overlay_clips.extend(character_overlays)
    # Finally text overlays should be on top
    overlay_clips.extend(text_overlays)

    return overlay_clips


def generate_video(script, tts_files, bg_video, output_path="output/final.mp4",
                   char_images=None, infographic_images=None):
    """Generate the final video with smooth transitions."""
    base_clip = VideoFileClip(bg_video)
    base_clip = crop_to_vertical(base_clip, VIDEO_LAYOUT["target_aspect_ratio"],
                                 VIDEO_LAYOUT["output_height"], VIDEO_LAYOUT["output_width"])
    
    segments = []
    current_time = 0
    
    for i, dlg in enumerate(script.dialogues):
        audio = AudioFileClip(tts_files[i])
        duration = audio.duration
        
        # Get background segment
        if current_time + duration <= base_clip.duration:
            bg_segment = base_clip.subclip(current_time, current_time + duration)
        else:
            # Loop back to beginning if we run out of background
            bg_segment = base_clip.subclip(0, duration)
            current_time = 0
        
        # Build composite with all overlays
        overlay_clips = build_overlays_for_dialogue(dlg, duration, bg_segment, char_images, infographic_images, i)
        segment = CompositeVideoClip(overlay_clips, size=bg_segment.size)
        segment = segment.set_audio(audio).set_duration(duration)
        
        segments.append(segment)
        current_time += duration
        
        # Reset if we exceed background duration
        if current_time >= base_clip.duration:
            current_time = 0

    # Concatenate with crossfade for smooth transitions
    if len(segments) > 1:
        # Add crossfade between segments to eliminate black frames
        final = segments[0]
        for i in range(1, len(segments)):
            final = CompositeVideoClip([final, segments[i].set_start(final.duration - 0.1)])
            final = final.set_duration(final.duration + segments[i].duration - 0.1)
    else:
        final = segments[0] if segments else None

    if final:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final.write_videofile(
            output_path, 
            fps=VIDEO_LAYOUT["fps"], 
            codec="libx264", 
            audio_codec="aac",
            preset="medium",  # Better quality
            threads=4
        )
    
    return output_path