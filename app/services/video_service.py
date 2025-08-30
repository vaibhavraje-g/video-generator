from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    concatenate_videoclips,
    CompositeVideoClip,
    AudioFileClip
)
import os
from PIL import Image

# --- Compatibility fix for Pillow >= 10.0 ---
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# --- Helper Functions ---
def crop_to_vertical(clip, target_aspect=9/16):
    """Crop a clip to 9:16 aspect ratio (608x1080)."""
    h, w = clip.h, clip.w
    if w / h > target_aspect:  # too wide → crop sides
        new_w = int(h * target_aspect)
        x1 = (w - new_w) // 2
        clip = clip.crop(x1=x1, y1=0, x2=x1 + new_w, y2=h)
    else:  # too tall → crop top/bottom
        new_h = int(w / target_aspect)
        y1 = (h - new_h) // 2
        clip = clip.crop(x1=0, y1=y1, x2=w, y2=y1 + new_h)
    return clip.resize(height=1080).resize(width=608)

def create_positioned_overlay(image_path, duration, video_size, position, max_height=300):
    """Create overlay with specific position and safe bounds."""
    if not os.path.exists(image_path):
        print(f"[WARN] Image not found: {image_path}")
        return None
    try:
        img = ImageClip(image_path).resize(height=max_height)
        # Ensure position is within bounds
        x = max(0, min(position[0], video_size[0] - img.w))
        y = max(0, min(position[1], video_size[1] - img.h))
        print(f"[DEBUG] Overlay prepared → {os.path.basename(image_path)} "
              f"size=({img.w}x{img.h}), position=({x}, {y}), duration={duration:.2f}s")
        return img.set_duration(duration).set_position((x, y))
    except Exception as e:
        print(f"[ERROR] Could not load image {image_path}: {e}")
        return None

def overlaps_with_used_areas(pos, width, height, used_areas):
    """Check if a rectangle overlaps with any used areas."""
    x, y = pos
    new_rect = (x, y, x + width, y + height)
    for used_x, used_y, used_w, used_h in used_areas:
        used_rect = (used_x, used_y, used_x + used_w, used_y + used_h)
        if not (new_rect[2] <= used_rect[0] or  # new is left of used
                new_rect[0] >= used_rect[2] or  # new is right of used
                new_rect[3] <= used_rect[1] or  # new is above used
                new_rect[1] >= used_rect[3]):   # new is below used
            print(f"[DEBUG] Overlap detected → pos={pos}, "
                  f"new_rect={new_rect}, used_rect={used_rect}")
            return True
    return False

# --- Overlay Step Function ---
def build_overlays_for_dialogue(dlg, duration, bg_segment, char_images, infographic_images, i):
    """Build all overlays (character + infographic) for one dialogue step."""
    overlay_clips = [bg_segment]
    used_areas = []

    # --- Character Overlay ---
    char_key = dlg.character.lower().strip()
    if char_images and char_key in char_images:
        char_path = char_images[char_key]
        print(f"\n[STEP] Adding character → {dlg.character} from {char_path}")
        
        # Fixed: Access width and height properly from the tuple
        video_width, video_height = bg_segment.size
        char_positions = [
            (60, video_height - 410),                           # bottom-left
            (video_width - 260, video_height - 410),            # bottom-right
            (60, video_height - 760),                           # middle-left
            (video_width - 260, video_height - 760),            # middle-right
        ]
        
        for pos in char_positions:
            char_overlay = create_positioned_overlay(
                char_path, duration, bg_segment.size, pos, max_height=350
            )
            if char_overlay:
                ow, oh = char_overlay.w, char_overlay.h
                if not overlaps_with_used_areas(pos, ow, oh, used_areas):
                    overlay_clips.append(char_overlay)
                    used_areas.append((pos[0], pos[1], ow, oh))
                    print(f"[SUCCESS] Character added at {pos} (size={ow}x{oh})")
                    break
        else:
            print("[WARN] Character NOT added → no free position found")
    else:
        print(f"[WARN] No character image found for key '{char_key}'")

    # --- Infographic Overlay ---
    if infographic_images and i < len(infographic_images):
        info_path = infographic_images[i]
        if info_path and os.path.exists(info_path):
            print(f"\n[STEP] Adding infographic → {info_path}")
            
            # Fixed: Access width and height properly from the tuple
            video_width, video_height = bg_segment.size
            info_positions = [
                ((video_width - 250) // 2, 80),                        # top-center
                ((video_width - 250) // 2, 200),                       # upper-center
                ((video_width - 250) // 2, video_height // 2 - 125),   # middle-center
            ]
            
            for pos in info_positions:
                info_overlay = create_positioned_overlay(
                    info_path, duration, bg_segment.size, pos, max_height=250
                )
                if info_overlay:
                    ow, oh = info_overlay.w, info_overlay.h
                    if not overlaps_with_used_areas(pos, ow, oh, used_areas):
                        overlay_clips.append(info_overlay)
                        used_areas.append((pos[0], pos[1], ow, oh))
                        print(f"[SUCCESS] Infographic added at {pos} (size={ow}x{oh})")
                        break
            else:
                print("[WARN] Infographic NOT added → no free position found")
        else:
            print(f"[WARN] Infographic path missing or invalid at index {i}: {info_path}")
    else:
        print(f"[INFO] No infographic provided for dialogue index {i}")

    return overlay_clips

# --- Main Video Generation ---
def generate_video(script, tts_files, bg_video, output_path="output/final.mp4",
                   char_images=None, infographic_images=None):
    base_clip = VideoFileClip(bg_video)
    base_clip = crop_to_vertical(base_clip)

    overlays = []
    total_audio_duration = 0

    for i, dlg in enumerate(script.dialogues):
        print(f"\n========== Dialogue {i+1}/{len(script.dialogues)} ==========")
        audio = AudioFileClip(tts_files[i])
        duration = audio.duration
        total_audio_duration += duration

        bg_segment = base_clip.subclip(0, min(duration, base_clip.duration))

        # Build overlays for this dialogue
        overlay_clips = build_overlays_for_dialogue(
            dlg, duration, bg_segment, char_images, infographic_images, i
        )

        # Build final segment
        segment = CompositeVideoClip(overlay_clips).set_audio(audio).set_duration(duration)
        print(f"[DEBUG] Segment overlays count (incl. bg) = {len(overlay_clips)}")
        overlays.append(segment)

    # --- Concatenate and adjust duration ---
    final = concatenate_videoclips(overlays)
    if final.duration > total_audio_duration:
        final = final.subclip(0, total_audio_duration)
    elif final.duration < total_audio_duration:
        loops = int(total_audio_duration // final.duration) + 1
        final = concatenate_videoclips([final] * loops).subclip(0, total_audio_duration)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=4
    )
    print(f"\n[SUCCESS] Video generated: {output_path}")
    return output_path
