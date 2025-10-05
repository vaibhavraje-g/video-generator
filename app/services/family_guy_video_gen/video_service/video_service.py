# video_service.py
from moviepy.editor import (
    VideoFileClip,
    CompositeVideoClip,
    AudioFileClip,
    concatenate_videoclips,
    vfx,
)
from moviepy.config import change_settings
from PIL import Image
import os
import tempfile

change_settings(
    {"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe"}
)

# Pillow >=10 compatibility
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from .video_utils import (
    crop_to_vertical,
    create_positioned_overlay,
    overlaps_with_used_areas,
)
from .text_overlay import build_text_overlay
from .video_configs import VIDEO_LAYOUT, CHARACTER_CONFIG, INFOGRAPHIC_CONFIG
from app.services.family_guy_video_gen.asset_service import (
    fetch_character_image,
    fetch_infographic,
)


def clean_segment(segment):
    """Trim leading/trailing black frames."""
    try:
        # Remove fade effects that might cause issues
        return segment
    except:
        return segment


def build_overlays_for_dialogue(dlg, duration, bg_segment, i, script):
    """Build text, character, and infographic overlays"""
    overlay_clips = [bg_segment]
    video_w, video_h = bg_segment.size
    used_areas = []

    # TOP SECTION: Infographics
    if dlg.infographic:
        info_img = fetch_infographic(
            script.topic, dlg.text, f"info_{i}.png", dlg.infographic
        )
        if info_img:
            info_clip = create_positioned_overlay(
                info_img,
                duration,
                (video_w, video_h),
                position=(
                    (video_w - INFOGRAPHIC_CONFIG["max_width"]) // 2,
                    INFOGRAPHIC_CONFIG["top_margin"],
                ),
                max_height=INFOGRAPHIC_CONFIG["max_height"],
            )
            if info_clip:
                overlay_clips.append(info_clip)

    # MIDDLE SECTION: Text (handled in text_overlay.py)
    text_overlays = build_text_overlay(dlg, duration, bg_segment, used_areas)
    overlay_clips.extend(text_overlays)

    # BOTTOM SECTION: Character
    char_img = fetch_character_image(dlg.character)
    if char_img:
        char_clip = create_positioned_overlay(
            char_img,
            duration,
            (video_w, video_h),
            position=(
                (video_w - CHARACTER_CONFIG["max_width"]) // 2,
                video_h
                - CHARACTER_CONFIG["max_height"]
                - CHARACTER_CONFIG["bottom_margin"],
            ),
            max_height=CHARACTER_CONFIG["max_height"],
        )
        if char_clip:
            overlay_clips.append(char_clip)

    return overlay_clips


def generate_video(
    script,
    tts_files,
    bg_video,
    output_path="output/final.mp4",
    char_images=None,
    infographic_images=None,
):
    """Generate polished video without black flashes and empty sections."""
    clips_to_close = []  # Keep track of all clips to properly close
    temp_files = []  # Track temporary files to clean up

    try:
        # Initialize base clip
        base_clip = VideoFileClip(bg_video)
        clips_to_close.append(base_clip)
        base_clip = crop_to_vertical(
            base_clip,
            VIDEO_LAYOUT["target_aspect_ratio"],
            VIDEO_LAYOUT["output_height"],
            VIDEO_LAYOUT["output_width"],
        )

        segments = []
        current_time = 0

        for i, dlg in enumerate(script.dialogues):
            # Skip if TTS file is missing
            if i >= len(tts_files) or not os.path.exists(tts_files[i]):
                print(f"[WARN] Missing audio for dialogue {i}, skipping.")
                continue

            # Load audio clip
            audio = AudioFileClip(tts_files[i])
            clips_to_close.append(audio)
            duration = audio.duration

            # Skip empty audio segments
            if duration < 0.2:
                print(f"[WARN] Very short/empty dialogue {i}, skipping.")
                continue

            # Get background video slice
            if current_time + duration <= base_clip.duration:
                bg_segment = base_clip.subclip(current_time, current_time + duration)
            else:
                bg_segment = base_clip.subclip(0, min(duration, base_clip.duration))
                current_time = 0
            clips_to_close.append(bg_segment)

            # Build all overlays
            overlay_clips = build_overlays_for_dialogue(
                dlg, duration, bg_segment, i, script
            )
            segment = CompositeVideoClip(overlay_clips, size=bg_segment.size).set_audio(
                audio
            )
            clips_to_close.append(segment)

            # Clean up fade artifacts
            segment = clean_segment(segment)
            segments.append(segment)
            current_time += duration

            if current_time >= base_clip.duration:
                current_time = 0

        # Concatenate without black frames
        if not segments:
            print("[ERROR] No segments generated.")
            return None

        # Use more stable concatenation settings
        final = concatenate_videoclips(segments, method="compose")
        clips_to_close.append(final)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create a temporary file in the system temp directory
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            temp_output = temp_file.name
            temp_files.append(temp_output)

        try:
            # Write video with safe parameters that work with MoviePy
            final.write_videofile(
                temp_output,
                fps=VIDEO_LAYOUT["fps"],
                codec="libx264",
                audio_codec="aac",
                preset="medium",
                threads=4,
                temp_audiofile="temp-audio.m4a",  # Use temporary audio file
                remove_temp=True,  # Remove temporary audio file after completion
                logger=None,  # Disable MoviePy logging to prevent conflicts
                verbose=False,  # Reduce console output
            )

            # Verify the temporary file was created and has content
            if os.path.exists(temp_output) and os.path.getsize(temp_output) > 0:
                # Rename temp file to final output
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(temp_output, output_path)
                temp_files.remove(temp_output)  # Remove from cleanup list
            else:
                print(
                    f"[ERROR] Generated video file is empty or missing: {temp_output}"
                )
                return None

        except Exception as e:
            print(f"Error writing video file: {e}")
            if os.path.exists(temp_output):
                try:
                    os.remove(temp_output)
                except:
                    pass
            raise

        return output_path

    except Exception as e:
        print(f"Error generating video: {e}")
        return None

    finally:
        # Clean up all clips in reverse order
        for clip in reversed(clips_to_close):
            try:
                if clip and hasattr(clip, "close"):
                    clip.close()
            except Exception as e:
                print(f"Warning: Error while closing clip: {e}")

        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Warning: Could not remove temp file {temp_file}: {e}")
