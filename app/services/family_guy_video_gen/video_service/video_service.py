from moviepy.editor import VideoFileClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips, vfx
from moviepy.config import change_settings
from PIL import Image
import os, tempfile

change_settings({"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe"})

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from .video_utils import crop_to_vertical, create_animated_overlay
from .text_overlay import build_animated_text_overlay
from .video_configs import VIDEO_LAYOUT, CHARACTER_CONFIG, INFOGRAPHIC_CONFIG, ANIMATION_CONFIG, VIDEO_SPEED

def clean_segment(segment):
    """Trim black frames if needed."""
    try:
        return segment
    except:
        return segment

def build_overlays_for_dialogue(dlg, duration, bg_segment, i, script, char_images, infographic_map):
    overlay_clips = [bg_segment]
    video_w, video_h = bg_segment.size
    used_areas = []

    # Infographic top
    info_img = infographic_map.get(i)
    if info_img and os.path.exists(info_img):
        info_clip = create_animated_overlay(
            info_img, duration, (video_w, video_h),
            final_position=((video_w-INFOGRAPHIC_CONFIG["max_width"])//2, INFOGRAPHIC_CONFIG["top_margin"]),
            max_height=INFOGRAPHIC_CONFIG["max_height"],
            animation_type="slide_right",
            animation_config=ANIMATION_CONFIG
        )
        if info_clip: overlay_clips.append(info_clip)

    # Animated text
    text_overlays = build_animated_text_overlay(dlg, duration, bg_segment, used_areas)
    overlay_clips.extend(text_overlays)

    # Character bottom
    char_img = char_images.get(dlg.character.lower().strip()) if char_images else None
    if char_img and os.path.exists(char_img):
        char_clip = create_animated_overlay(
            char_img, duration, (video_w, video_h),
            final_position=((video_w-CHARACTER_CONFIG["max_width"])//2,
                            video_h-CHARACTER_CONFIG["max_height"]-CHARACTER_CONFIG["bottom_margin"]),
            max_height=CHARACTER_CONFIG["max_height"],
            animation_type="slide_left",
            animation_config=ANIMATION_CONFIG
        )
        if char_clip: overlay_clips.append(char_clip)

    return overlay_clips

def generate_video(script, tts_files, bg_video, output_path="output/final.mp4",
                   char_images=None, infographic_images=None):
    clips_to_close, temp_files = [], []

    infographic_map = {i: path for i, path in enumerate(infographic_images or [])}

    try:
        base_clip = VideoFileClip(bg_video)
        clips_to_close.append(base_clip)
        base_clip = crop_to_vertical(base_clip,
                                     VIDEO_LAYOUT["target_aspect_ratio"],
                                     VIDEO_LAYOUT["output_height"],
                                     VIDEO_LAYOUT["output_width"])

        segments, current_time = [], 0
        for i, dlg in enumerate(script.dialogues):
            if i>=len(tts_files) or not os.path.exists(tts_files[i]):
                print(f"[WARN] Missing audio for dialogue {i}, skipping.")
                continue

            audio = AudioFileClip(tts_files[i])
            clips_to_close.append(audio)
            duration = audio.duration
            if duration < 0.2: continue

            # video slice
            if current_time+duration <= base_clip.duration:
                bg_segment = base_clip.subclip(current_time, current_time+duration)
            else:
                bg_segment = base_clip.subclip(0, min(duration, base_clip.duration))
                current_time = 0
            clips_to_close.append(bg_segment)

            overlay_clips = build_overlays_for_dialogue(dlg, duration, bg_segment, i, script, char_images, infographic_map)
            segment = CompositeVideoClip(overlay_clips, size=bg_segment.size).set_audio(audio)
            clips_to_close.append(segment)

            segment = clean_segment(segment)
            segments.append(segment)
            current_time += duration
            if current_time >= base_clip.duration:
                current_time = 0

        if not segments:
            print("[ERROR] No segments generated.")
            return None

        final = concatenate_videoclips(segments, method="compose")
        # Apply video speed
        if VIDEO_SPEED != 1.0:
            final = final.fx(vfx.speedx, VIDEO_SPEED)

        clips_to_close.append(final)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            temp_output = temp_file.name
            temp_files.append(temp_output)

        final.write_videofile(temp_output,
                              fps=VIDEO_LAYOUT["fps"],
                              codec="libx264",
                              audio_codec="aac",
                              preset="medium",
                              threads=4,
                              temp_audiofile="temp-audio.m4a",
                              remove_temp=True,
                              logger=None,
                              verbose=False)

        if os.path.exists(temp_output) and os.path.getsize(temp_output) > 0:
            if os.path.exists(output_path): os.remove(output_path)
            os.rename(temp_output, output_path)
            temp_files.remove(temp_output)
        else:
            print(f"[ERROR] Generated video missing: {temp_output}")
            return None

        return output_path

    except Exception as e:
        print(f"[ERROR] generating video: {e}")
        return None

    finally:
        for clip in reversed(clips_to_close):
            try: clip.close()
            except: pass
        for temp_file in temp_files:
            try: os.remove(temp_file)
            except: pass
