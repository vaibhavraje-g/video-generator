# text_overlay.py
from moviepy.editor import TextClip, vfx
from moviepy.video.tools.subtitles import SubtitlesClip
from .video_configs import TEXT_STYLE, TEXT_ANIMATION
from .video_utils import overlaps_with_used_areas
from moviepy.config import change_settings 
change_settings({"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe"})


def split_text_to_chunks(text, duration, max_chars, max_lines):
    """
    Split text into 1–2 line subtitle chunks that fit the screen,
    and compute simple start/duration intervals across 'duration'.
    """
    words = text.split()
    n = len(words)
    if n == 0:
        return []

    word_dur = duration / max(n, 1)
    chunks = []
    i = 0
    while i < n:
        lines = []
        idx = i
        for _ in range(max_lines):
            line_words = []
            line_len = 0
            while idx < n:
                w = words[idx]
                add = len(w) + (1 if line_words else 0)
                if line_len + add > max_chars and line_words:
                    break
                line_words.append(w)
                line_len += add
                idx += 1
            if not line_words and idx < n:
                line_words = [words[idx]]
                idx += 1
            lines.append(" ".join(line_words))
            if idx >= n:
                break
        text_chunk = "\n".join(lines)
        start = i * word_dur
        dur = max(0.2, (idx - i) * word_dur)
        chunks.append((text_chunk, start, dur))
        i = idx
    return chunks


def build_text_overlay(dlg, duration, bg_segment, used_areas):
    """
    Build per-caption TextClips with background boxes, set duration before applying fades,
    position them in the middle area, and reserve the middle band in used_areas.
    """
    overlays = []
    video_w, video_h = bg_segment.size

    # Split into subtitle chunks
    chunks = split_text_to_chunks(
        dlg.text, duration, TEXT_STYLE["max_chars"], TEXT_STYLE["max_lines"]
    )

    # Position text in middle area of screen
    middle_y = video_h // 2

    for (txt, start, dur) in chunks:
        try:
            base = TextClip(
                txt=txt,
                fontsize=TEXT_STYLE["fontsize"],
                color=TEXT_STYLE["color"],
                font=TEXT_STYLE["font"],
                method='caption',  # auto-wrap within given width
                size=(int(video_w * TEXT_STYLE["width_ratio"]), None),
                align=TEXT_STYLE["align"],
                stroke_color=TEXT_STYLE["stroke_color"],
                stroke_width=TEXT_STYLE["stroke_width"],
            )

            padded = base.on_color(
                size=(base.w + 2 * TEXT_STYLE["pad_x"], base.h + 2 * TEXT_STYLE["pad_y"]),
                color=TEXT_STYLE["bg_color"],
                col_opacity=TEXT_STYLE["bg_opacity"],
                pos=('center', 'center'),
            )

            # Set duration and start BEFORE applying fades
            padded = padded.set_duration(dur).set_start(start)

            # Apply fade animations with increased duration for visibility
            if TEXT_ANIMATION.get("fade_in", 0) and dur > TEXT_ANIMATION["fade_in"]:
                padded = padded.fx(vfx.fadein, TEXT_ANIMATION["fade_in"])
            if TEXT_ANIMATION.get("fade_out", 0) and dur > TEXT_ANIMATION["fade_out"]:
                padded = padded.fx(vfx.fadeout, TEXT_ANIMATION["fade_out"])

            # Position: middle area, centered both horizontally and vertically
            y_pos = middle_y - (padded.h // 2)  # Center vertically in middle
            padded = padded.set_position(("center", y_pos))

            overlays.append(padded)
        except Exception as e:
            print(f"[ERROR] Could not create caption overlay: {e}")

    # Reserve middle band area for text
    reserve_h = (TEXT_STYLE["pad_y"] * 2) + (TEXT_STYLE["fontsize"] * TEXT_STYLE["max_lines"]) + TEXT_STYLE.get("reserve_extra", 80)
    middle_reserve_y = middle_y - (reserve_h // 2)
    used_areas.append((0, middle_reserve_y, video_w, reserve_h))

    return overlays