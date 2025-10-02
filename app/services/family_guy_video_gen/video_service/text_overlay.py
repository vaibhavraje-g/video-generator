# text_overlay.py
from moviepy.editor import TextClip, vfx
from moviepy.config import change_settings
from .video_configs import TEXT_STYLE, TEXT_ANIMATION, VIDEO_LAYOUT

change_settings(
    {"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe"}
)


# -------------------------
# Helpers
# -------------------------
def split_text_to_chunks(text, duration, words_per_chunk=3):
    """Split dialogue into fixed-size chunks of 3-4 words."""
    words = text.split()
    if not words:
        return []

    chunks, i = [], 0
    word_time = duration / len(words)
    current_time = 0.0

    while i < len(words):
        chunk_words = words[i : i + words_per_chunk]
        chunk_text = " ".join(chunk_words)
        chunk_dur = word_time * len(chunk_words)
        chunks.append((chunk_text, current_time, chunk_dur))
        current_time += chunk_dur
        i += words_per_chunk

    return chunks


# -------------------------
# Main: build_text_overlay
# -------------------------
def build_text_overlay(dlg, duration, bg_segment, used_areas):
    """
    Build professional subtitles with white text and black stroke
    """
    overlays = []
    video_w, video_h = bg_segment.size
    fontsize = TEXT_STYLE.get("fontsize", 60)
    font_name = TEXT_STYLE.get("font", "Arial-Bold")
    words_per_chunk = TEXT_STYLE.get("words_per_chunk", 3)

    chunks = split_text_to_chunks(dlg.text, duration, words_per_chunk)

    # Position in MIDDLE third of screen
    middle_start = video_h * VIDEO_LAYOUT["top_section"]
    middle_end = video_h * (
        VIDEO_LAYOUT["top_section"] + VIDEO_LAYOUT["middle_section"]
    )
    y_pos = int((middle_start + middle_end) / 2)

    for text, start, dur in chunks:
        try:
            txt_clip = (
                TextClip(
                    txt=text,
                    fontsize=fontsize,
                    color=TEXT_STYLE["color"],
                    stroke_color=TEXT_STYLE["stroke_color"],
                    stroke_width=TEXT_STYLE["stroke_width"],
                    font=font_name,
                    method="caption",
                    align="center",
                    size=(int(video_w * 0.85), None),  # Wider for middle section
                )
                .set_position(("center", y_pos))
                .set_start(start)
                .set_duration(dur)
            )

            # Smooth fade in/out
            fade_d = min(TEXT_ANIMATION.get("fade_in", 0.1), dur / 4)
            if fade_d > 0:
                txt_clip = txt_clip.fx(vfx.fadein, fade_d).fx(vfx.fadeout, fade_d)

            overlays.append(txt_clip)
        except Exception as e:
            print(f"[ERROR] text overlay failed for '{text}': {e}")

    return overlays
