"""
Main video generation orchestrator.
Uses:
 - text overlay (text_overlay.build_animated_text_overlay)
 - image overlay service (image_overlay_service.build_image_overlays)
This file is a cleaned-up version of your earlier service; it imports the modular overlay builders.
"""

import os
import tempfile
from multiprocessing import cpu_count
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, vfx

from .video_configs import INFOGRAPHIC_CONFIG, CHARACTER_CONFIG, VIDEO_LAYOUT

from moviepy.config import change_settings
from PIL import Image

from .video_utils import crop_to_vertical
from .text_overlay import build_animated_text_overlay
from .image_overlay import build_image_overlays
from .video_configs import VIDEO_LAYOUT, VIDEO_SPEED

# Ensure ImageMagick path is configured (if needed elsewhere)
change_settings(
    {"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe"}
)

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS


def clean_segment(segment):
    """Placeholder for cleaning (e.g., trim black frames). Keep simple for now."""
    try:
        return segment
    except Exception:
        return segment


def generate_video(
    script,
    tts_files,
    bg_video,
    output_path="output/final.mp4",
    char_images=None,
    infographic_images=None,
):
    """
    Entry point for generating the final video.
    - script: object with dialogues list (each dlg has .text and .character)
    - tts_files: list of paths to audio files (parallel to dialogues)
    - bg_video: path to background video
    - char_images: dict mapping character_key -> image_path
    - infographic_images: list of infographic image paths (index -> file)
    """
    clips_to_close, temp_files = [], []

    infographic_map = {i: path for i, path in enumerate(infographic_images or [])}

    try:
        # Load background video efficiently; targeting output height keeps scale consistent
        base_clip = VideoFileClip(bg_video, target_resolution=(VIDEO_LAYOUT["output_height"], None))
        clips_to_close.append(base_clip)

        # Ensure vertical crop if needed
        base_clip = crop_to_vertical(
            base_clip,
            VIDEO_LAYOUT["target_aspect_ratio"],
            VIDEO_LAYOUT["output_height"],
            VIDEO_LAYOUT["output_width"],
        )

        segments = []
        current_time = 0.0

        for i, dlg in enumerate(script.dialogues):
            # ensure matching audio
            if i >= len(tts_files) or not os.path.exists(tts_files[i]):
                print(f"[WARN] Missing audio for dialogue {i}, skipping.")
                continue

            audio = AudioFileClip(tts_files[i])
            clips_to_close.append(audio)
            duration = audio.duration
            if duration < 0.2:
                continue

            # Choose background segment slice (wrap-around allowed)
            if current_time + duration <= base_clip.duration:
                bg_segment = base_clip.subclip(current_time, current_time + duration)
            else:
                # if we run out of background video, restart from 0 to fill duration
                bg_segment = base_clip.subclip(0, min(duration, base_clip.duration))
                current_time = 0.0

            clips_to_close.append(bg_segment)

            # Build overlays: images first (top + character), then text overlays
            image_overlays = build_image_overlays(dlg, duration, bg_segment, i, char_images, infographic_map)
            text_overlays = build_animated_text_overlay(dlg, duration, bg_segment, used_areas=[])

            # Compose overlay list: background + image overlays + text overlays
            overlay_clips = [bg_segment]
            if image_overlays:
                # image_overlays may be a list of clips (or single clip) — normalize
                if isinstance(image_overlays, list):
                    overlay_clips.extend(image_overlays)
                else:
                    overlay_clips.append(image_overlays)
            if text_overlays:
                overlay_clips.extend(text_overlays)

            # Composite and set audio
            segment = CompositeVideoClip(overlay_clips, size=bg_segment.size).set_audio(audio)

            # Optional segment cleaning
            segment = clean_segment(segment)

            segments.append(segment)
            clips_to_close.append(segment)

            # advance background time; wrap if hitting end
            current_time += duration
            if current_time >= base_clip.duration:
                current_time = 0.0

        if not segments:
            print("[ERROR] No segments generated.")
            return None

        # Concatenate segments; method=compose keeps sizes consistent
        final = concatenate_videoclips(segments, method="compose")

        # Apply playback speed if configured
        if VIDEO_SPEED != 1.0:
            final = final.fx(vfx.speedx, VIDEO_SPEED)

        clips_to_close.append(final)

        # Export to a temp file first for safe atomic replace
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tf:
            temp_output = tf.name
            temp_files.append(temp_output)

        final.write_videofile(
            temp_output,
            fps=VIDEO_LAYOUT["fps"],
            codec="libx264",
            audio_codec="aac",
            preset="fast",
            threads=max(1, cpu_count() // 2),
            ffmpeg_params=["-crf", "22", "-movflags", "+faststart"],
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            logger=None,
            verbose=False,
        )

        # Move temp output to final path
        if os.path.exists(temp_output) and os.path.getsize(temp_output) > 0:
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(temp_output, output_path)
            temp_files.remove(temp_output)
        else:
            print(f"[ERROR] Generated video missing or zero-length: {temp_output}")
            return None

        print(f"[INFO] ✅ Video generated successfully at {output_path}")
        return output_path

    except Exception as exc:
        print(f"[ERROR] generating video: {exc}")
        return None

    finally:
        # Clean up MoviePy clips (close in reverse order)
        for clip in reversed(clips_to_close):
            try:
                clip.close()
            except Exception:
                pass
        # remove any leftover temp files
        for fpath in temp_files:
            try:
                os.remove(fpath)
            except Exception:
                pass
