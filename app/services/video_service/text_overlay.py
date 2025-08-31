# text_overlay.py
from moviepy.editor import TextClip, CompositeVideoClip, vfx, ImageClip
from .video_configs import TEXT_STYLE, TEXT_ANIMATION
from .video_utils import overlaps_with_used_areas
from moviepy.config import change_settings
from PIL import Image, ImageDraw, ImageFont
import math
import numpy as np
import os

change_settings({"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe"})

# -------------------------
# Helpers
# -------------------------
def split_text_to_chunks(text, duration, words_per_chunk=None):
    """
    Split dialogue into chunks of 'words_per_chunk' words, but enforce max chars
    per line and max lines by reducing the words per chunk as necessary.
    Returns list of (chunk_text, start, dur, word_count).
    """
    if words_per_chunk is None:
        words_per_chunk = TEXT_STYLE.get("words_per_chunk", 3)

    words = text.split()
    n = len(words)
    if n == 0:
        return []

    max_chars = TEXT_STYLE.get("max_chars_per_line", 36)
    max_lines = TEXT_STYLE.get("max_lines", 2)
    max_total_chars = max_chars * max_lines

    min_chunk_dur = TEXT_STYLE.get("min_chunk_duration", 0.5)
    chunks = []
    i = 0

    total_words = n
    word_base = duration / max(1, total_words)
    current_time = 0.0
    while i < n:
        # Start with configured words_per_chunk but shrink if chunk too long
        take = words_per_chunk
        while take > 0:
            chunk_words = words[i:i + take]
            chunk_text = " ".join(chunk_words)
            if len(chunk_text) <= max_total_chars:
                break
            take -= 1
        if take == 0:
            # force at least one word if single word too long
            take = 1
            chunk_words = words[i:i + take]
            chunk_text = " ".join(chunk_words)

        chunk_len = len(chunk_words)
        dur = max(min_chunk_dur, word_base * chunk_len)
        chunks.append((chunk_text, current_time, dur, chunk_len))
        current_time += dur
        i += take

    # Clamp overflow on last chunk
    if chunks:
        last_end = chunks[-1][1] + chunks[-1][2]
        if last_end > duration:
            overflow = last_end - duration
            chunks[-1] = (chunks[-1][0], chunks[-1][1], max(0.15, chunks[-1][2] - overflow), chunks[-1][3])

    return chunks


def make_rounded_bg_image(w, h, radius=16, color=(255, 215, 0, 230)):
    """
    Return a numpy array RGBA image (h,w,4) containing rounded-rect background.
    color: RGBA tuple.
    """
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    rect = (0, 0, w, h)
    try:
        draw.rounded_rectangle(rect, radius=radius, fill=color)
    except Exception:
        draw.rectangle(rect, fill=color)
    return np.array(img)


def create_text_clip_for_chunk(text, max_width_px, fontsize, font_name, max_lines):
    """
    Create a TextClip using method='caption' constrained to max_width_px and
    max_lines (via a computed height). Text color set by caller.
    Returns the TextClip.
    """
    # compute a reasonable height to allow up to max_lines
    line_height = int(fontsize * 1.2)
    h_px = line_height * max_lines + 8

    txt_clip = TextClip(
        txt=text,
        fontsize=fontsize,
        color=TEXT_STYLE["color"],
        font=font_name,
        method="caption",
        size=(max_width_px, h_px),
        align=TEXT_STYLE.get("align", "center")
    )
    return txt_clip


# -------------------------
# Main: build_text_overlay
# -------------------------
def build_text_overlay(dlg, duration, bg_segment, used_areas):
    """
    Build subtitles as short chunks (3 words by default) with a rounded yellow background.
    Text is white by default; during each chunk a yellow-text overlay briefly appears to
    highlight the chunk (this helps sync visually with audio).
    Returns list of clips ready to CompositeVideoClip.
    """
    overlays = []
    video_w, video_h = bg_segment.size

    # config
    words_per_chunk = TEXT_STYLE.get("words_per_chunk", 3)
    max_width_px = int(video_w * TEXT_STYLE.get("width_ratio", 0.9))
    fontsize = TEXT_STYLE.get("fontsize", 46)
    font_name = TEXT_STYLE.get("font") or "Arial"
    max_lines = TEXT_STYLE.get("max_lines", 2)
    pad_x = TEXT_STYLE.get("pad_x", 20)
    pad_y = TEXT_STYLE.get("pad_y", 10)
    bg_rgba = TEXT_STYLE.get("bg_color_rgba", (255, 220, 0, 230))
    bg_radius = TEXT_STYLE.get("bg_radius", 12)

    # compute chunk timings
    chunks = split_text_to_chunks(dlg.text, duration, words_per_chunk)

    # choose vertical position (center-ish, above bottom area)
    y_pos = video_h - TEXT_STYLE.get("bottom_margin", 350)
    y_pos = max(int(video_h * 0.45), y_pos - 40)

    for chunk_text, start, dur, wc in chunks:
        try:
            # create the base white text clip (caption method wraps text)
            txt_clip = create_text_clip_for_chunk(chunk_text, max_width_px, fontsize, font_name, max_lines)
            tw, th = txt_clip.size

            # Build rounded background sized slightly larger than text clip
            bg_w = int(min(video_w - 40, tw + pad_x))
            bg_h = int(th + pad_y)

            rounded_arr = make_rounded_bg_image(bg_w, bg_h, radius=bg_radius, color=bg_rgba)
            bg_clip = ImageClip(rounded_arr, ismask=False).set_duration(dur).set_start(start)

            # Position background centered horizontally and vertically at y_pos
            x_center = (video_w - bg_w) // 2
            y_top = int(y_pos - bg_h // 2)
            bg_clip = bg_clip.set_position((x_center, y_top))

            # fade in/out
            fade_d = min(TEXT_ANIMATION.get("fade_in", 0.12), dur / 6)
            if fade_d > 0:
                bg_clip = bg_clip.fx(vfx.fadein, fade_d).fx(vfx.fadeout, fade_d)

            # position white text on top of bg
            txt_clip = txt_clip.set_start(start).set_duration(dur)
            txt_x = x_center + (bg_w - tw) // 2
            txt_y = y_top + (bg_h - th) // 2
            txt_clip = txt_clip.set_position((txt_x, txt_y))
            if fade_d > 0:
                txt_clip = txt_clip.fx(vfx.fadein, fade_d).fx(vfx.fadeout, fade_d)

            overlays.append(bg_clip)
            overlays.append(txt_clip)

            # Create a short yellow-highlight overlay that appears during most of the chunk
            # This gives a visual "sync" pulse while audio plays the chunk.
            highlight_frac = TEXT_STYLE.get("highlight_fraction", 0.75)
            delay_frac = TEXT_STYLE.get("highlight_delay_frac", 0.12)
            hl_dur = max(0.12, dur * highlight_frac)
            hl_start = start + max(0, dur * delay_frac)
            # Clip must fit inside chunk
            if hl_start + hl_dur > start + dur:
                hl_dur = max(0.08, (start + dur) - hl_start)

            # create highlighted text (same layout) but colored yellow
            try:
                highlight_txt = TextClip(
                    txt=chunk_text,
                    fontsize=fontsize,
                    color="yellow",
                    font=font_name,
                    method="caption",
                    size=(bg_w - 4, bg_h - 4),  # slightly smaller to fit nicely
                    align=TEXT_STYLE.get("align", "center")
                )
                highlight_txt = highlight_txt.set_start(hl_start).set_duration(hl_dur).set_position((txt_x, txt_y))
                # add a tiny fade for the highlight
                fade_h = min(0.06, hl_dur / 4)
                if fade_h > 0:
                    highlight_txt = highlight_txt.fx(vfx.fadein, fade_h).fx(vfx.fadeout, fade_h)
                overlays.append(highlight_txt)
            except Exception as e_hl:
                # if highlighted clip fails, ignore highlight but keep base white text
                print(f"[WARN] highlight clip failed for '{chunk_text}': {e_hl}")

        except Exception as e:
            print(f"[ERROR] building chunk '{chunk_text}': {e}")
            # fallback plain TextClip centered for whole duration chunk
            try:
                fallback = TextClip(chunk_text, fontsize=fontsize, color=TEXT_STYLE["color"], font="Arial",
                                    method="caption", size=(max_width_px, None), align=TEXT_STYLE.get("align", "center"))
                fallback = fallback.set_start(start).set_duration(dur).set_position(('center', y_pos))
                overlays.append(fallback)
            except Exception as e2:
                print(f"[ERROR] fallback also failed: {e2}")

    # reserve area so other overlays don't overlap (x,y,w,h)
    reserve_h = int(TEXT_STYLE.get("fontsize", 46) * 1.4) + TEXT_STYLE.get("pad_y", 10) + TEXT_STYLE.get("reserve_extra", 40)
    used_areas.append((0, y_pos - reserve_h // 2, video_w, reserve_h))

    return overlays
