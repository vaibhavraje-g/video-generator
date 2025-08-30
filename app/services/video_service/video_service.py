# video_service.py
from moviepy.editor import VideoFileClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
from moviepy.config import change_settings
from PIL import Image
import os

# Keep ImageMagick config EXACTLY as before (many systems require this)
change_settings({"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe"})

# Pillow >=10 compatibility
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from .video_utils import crop_to_vertical, create_positioned_overlay, overlaps_with_used_areas
from .text_overlay import build_text_overlay
from .video_configs import VIDEO_LAYOUT, CHARACTER_CONFIG, INFOGRAPHIC_CONFIG


def build_character_overlay(dlg, duration, bg_segment, char_images, used_areas):
    overlays = []
    char_key = getattr(dlg, "character", "").lower().strip()
    if char_images and char_key in char_images:
        char_path = char_images[char_key]
        video_w, video_h = bg_segment.size
        # Fixed positioning: bottom area, centered horizontally
        x_pos = (video_w - CHARACTER_CONFIG["max_width"]) // 2
        y_pos = video_h - CHARACTER_CONFIG["bottom_margin"] - CHARACTER_CONFIG["max_height"]
        
        overlay = create_positioned_overlay(
            char_path, duration, (video_w, video_h), 
            (x_pos, y_pos), 
            CHARACTER_CONFIG["max_height"],
            with_animation=True  # Enable animation for character
        )
        if overlay and not overlaps_with_used_areas((x_pos, y_pos), overlay.w, overlay.h, used_areas):
            overlays.append(overlay)
            used_areas.append((x_pos, y_pos, overlay.w, overlay.h))
    return overlays


def build_infographic_overlay(i, duration, bg_segment, infographic_images, used_areas):
    overlays = []
    if infographic_images and i < len(infographic_images):
        path = infographic_images[i]
        if path and os.path.exists(path):
            video_w, video_h = bg_segment.size
            # Fixed positioning: top area, centered horizontally
            x_pos = (video_w - INFOGRAPHIC_CONFIG["max_width"]) // 2
            y_pos = INFOGRAPHIC_CONFIG["top_margin"]
            
            overlay = create_positioned_overlay(
                path, duration, bg_segment.size, 
                (x_pos, y_pos), 
                INFOGRAPHIC_CONFIG["max_height"],
                with_animation=True  # Enable animation for infographic
            )
            if overlay and not overlaps_with_used_areas((x_pos, y_pos), overlay.w, overlay.h, used_areas):
                overlays.append(overlay)
                used_areas.append((x_pos, y_pos, overlay.w, overlay.h))
    return overlays


def build_overlays_for_dialogue(dlg, duration, bg_segment, char_images, infographic_images, i):
    overlay_clips = [bg_segment]
    used_areas = []

    # Fixed order: infographic (top), text (middle), character (bottom)
    overlay_clips += build_infographic_overlay(i, duration, bg_segment, infographic_images, used_areas)
    overlay_clips += build_text_overlay(dlg, duration, bg_segment, used_areas)
    overlay_clips += build_character_overlay(dlg, duration, bg_segment, char_images, used_areas)
    
    return overlay_clips


def generate_video(script, tts_files, bg_video, output_path="output/final.mp4",
                   char_images=None, infographic_images=None):
    base_clip = VideoFileClip(bg_video)
    base_clip = crop_to_vertical(base_clip, VIDEO_LAYOUT["target_aspect_ratio"],
                                 VIDEO_LAYOUT["output_height"], VIDEO_LAYOUT["output_width"])
    overlays = []
    for i, dlg in enumerate(script.dialogues):
        audio = AudioFileClip(tts_files[i])
        duration = audio.duration
        # Ensure we don't exceed the base clip length
        bg_segment = base_clip.subclip(0, min(duration, base_clip.duration))
        segment = CompositeVideoClip(
            build_overlays_for_dialogue(dlg, duration, bg_segment, char_images, infographic_images, i)
        ).set_audio(audio).set_duration(duration)
        overlays.append(segment)

    final = concatenate_videoclips(overlays)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final.write_videofile(output_path, fps=VIDEO_LAYOUT["fps"], codec="libx264", audio_codec="aac")
    return output_path