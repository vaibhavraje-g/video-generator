"""
Main video generation orchestrator.
Handles:
 - text overlay (build_animated_text_overlay)
 - image overlay service (build_image_overlays)
Optimized for faster, isolated, and stable compilation.
"""

import os
import tempfile
from multiprocessing import cpu_count
from pathlib import Path
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    vfx,
)
from moviepy.config import change_settings
from PIL import Image

from .video_configs import INFOGRAPHIC_CONFIG, CHARACTER_CONFIG, VIDEO_LAYOUT, VIDEO_SPEED
from .video_utils import crop_to_vertical
from .text_overlay import build_animated_text_overlay
from .image_overlay import build_image_overlays

# Ensure ImageMagick path is configured (if needed elsewhere)
change_settings(
    {"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe"}
)

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS


def clean_segment(segment):
    """Placeholder for cleaning (e.g., trim black frames)."""
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
    Generate the final Family Guy–style video.
    Handles overlays, audio sync, speed effects, and export.
    """

    clips_to_close, temp_files = [], []

    try:
        # --- Setup project directories ---
        project_dir = Path(output_path).parent.parent
        temp_dir = project_dir / "tmp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        temp_audiofile = temp_dir / "temp_audio.m4a"
        temp_output = temp_dir / "temp_output.mp4"

        infographic_map = {i: path for i, path in enumerate(infographic_images or [])}

        # --- Load background video efficiently ---
        base_clip = VideoFileClip(
            bg_video,
            target_resolution=(VIDEO_LAYOUT["output_height"], None),
        )
        clips_to_close.append(base_clip)

        # Ensure vertical crop
        base_clip = crop_to_vertical(
            base_clip,
            VIDEO_LAYOUT["target_aspect_ratio"],
            VIDEO_LAYOUT["output_height"],
            VIDEO_LAYOUT["output_width"],
        )

        segments = []
        current_time = 0.0

        for i, dlg in enumerate(script.dialogues):
            if i >= len(tts_files) or not os.path.exists(tts_files[i]):
                print(f"[WARN] Missing audio for dialogue {i}, skipping.")
                continue

            audio = AudioFileClip(tts_files[i])
            clips_to_close.append(audio)
            duration = audio.duration
            if duration < 0.2:
                continue

            # Pick background segment
            if current_time + duration <= base_clip.duration:
                bg_segment = base_clip.subclip(current_time, current_time + duration)
            else:
                bg_segment = base_clip.subclip(0, min(duration, base_clip.duration))
                current_time = 0.0

            clips_to_close.append(bg_segment)

            # --- Build overlays ---
            image_overlays = build_image_overlays(
                dlg, duration, bg_segment, i, char_images, infographic_map
            )
            text_overlays = build_animated_text_overlay(
                dlg, duration, bg_segment, used_areas=[]
            )

            overlay_clips = [bg_segment]
            if image_overlays:
                overlay_clips.extend(image_overlays if isinstance(image_overlays, list) else [image_overlays])
            if text_overlays:
                overlay_clips.extend(text_overlays)

            # --- Compose ---
            segment = CompositeVideoClip(overlay_clips, size=bg_segment.size).set_audio(audio)
            segment = clean_segment(segment)

            segments.append(segment)
            clips_to_close.append(segment)

            current_time += duration
            if current_time >= base_clip.duration:
                current_time = 0.0

        if not segments:
            print("[ERROR] No segments generated.")
            return None

        # --- Concatenate ---
        final = concatenate_videoclips(segments, method="compose")

        # --- Apply video speed ---
        if VIDEO_SPEED != 1.0:
            final = final.fx(vfx.speedx, VIDEO_SPEED)

        # --- Ensure even dimensions (fix for H.264 encoding) ---
        final = final.resize(newsize=(final.w // 2 * 2, final.h // 2 * 2))

        clips_to_close.append(final)

        # --- Export final video ---
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        final.write_videofile(
            str(temp_output),
            fps=VIDEO_LAYOUT["fps"],
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",  # ⚡️ Faster encoding
            threads=max(1, cpu_count() - 1),
            ffmpeg_params=[
                "-crf", "23",
                "-movflags", "+faststart",
                "-pix_fmt", "yuv420p",
            ],
            temp_audiofile=str(temp_audiofile),
            remove_temp=True,
            logger=None,
            verbose=False,
        )

        # Move result to final output
        if os.path.exists(temp_output) and os.path.getsize(temp_output) > 0:
            os.replace(temp_output, output_path)
        else:
            print(f"[ERROR] Generated video missing or zero-length: {temp_output}")
            return None

        print(f"[INFO] ✅ Video generated successfully at {output_path}")
        return output_path

    except Exception as exc:
        print(f"[ERROR] generating video: {exc}")
        return None

    finally:
        # --- Cleanup ---
        for clip in reversed(clips_to_close):
            try:
                clip.close()
            except Exception:
                pass

        for f in temp_files:
            try:
                os.remove(f)
            except Exception:
                pass

        # 🧹 Remove temp folder
        if temp_dir.exists():
            for p in temp_dir.glob("*"):
                try:
                    p.unlink()
                except Exception:
                    pass

        # 🧹 Delete audio + infographic assets (keep only video)
        for folder_name in ["infographics", "audio"]:
            folder_path = project_dir / folder_name
            if folder_path.exists():
                for f in folder_path.glob("*"):
                    try:
                        f.unlink()
                    except Exception:
                        pass
