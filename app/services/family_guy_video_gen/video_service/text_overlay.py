from moviepy.editor import TextClip, CompositeVideoClip, ColorClip
from moviepy.config import change_settings

change_settings(
    {"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe"}
)

from .video_configs import TEXT_STYLE, VIDEO_LAYOUT


def build_animated_text_overlay(dlg, duration, bg_segment, used_areas):
    """
    Smooth karaoke-style overlay (single centered line):
    - One line of text on screen at a time
    - Highlights only the exact word (no spaces)
    - Centered vertically & horizontally
    """
    overlays = []
    video_w, video_h = bg_segment.size
    fontsize = TEXT_STYLE["fontsize"]
    font_name = TEXT_STYLE["font"]
    pad = 6
    max_line_width = int(video_w * 0.85)
    max_chars_per_line = 40

    words = dlg.text.split()
    if not words:
        return []

    # Break into short lines
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        test_clip = TextClip(test_line, fontsize=fontsize, font=font_name, method="label")
        if test_clip.w <= max_line_width and len(test_line) <= max_chars_per_line:
            current_line.append(word)
        else:
            if current_line:
                lines.append(current_line)
            current_line = [word]
        test_clip.close()
    if current_line:
        lines.append(current_line)

    total_words = len(words)
    word_duration = duration / total_words
    clips = []

    # Center vertically
    y_center = int(
        video_h * (VIDEO_LAYOUT["top_section"] + VIDEO_LAYOUT["middle_section"] / 2)
    )

    word_idx = 0
    for line_words in lines:
        line_text = " ".join(line_words)

        # Center horizontally
        temp_clip = TextClip(line_text, fontsize=fontsize, font=font_name, method="label")
        line_x = (video_w - temp_clip.w) // 2
        line_y = y_center - temp_clip.h // 2
        temp_clip.close()

        for i, word in enumerate(line_words):
            # Compute prefix width accurately including spaces before current word
            pre_words = line_words[:i]
            pre_width = 0
            if pre_words:
                pre_text = " ".join(pre_words) + " "  # include the actual space
                pre_clip = TextClip(pre_text, fontsize=fontsize, font=font_name, method="label")
                pre_width = pre_clip.w
                pre_clip.close()

            cur_word_clip = TextClip(word, fontsize=fontsize, font=font_name, method="label")

            # Highlight only the word area
            highlight = (
                ColorClip(
                    size=(cur_word_clip.w + pad * 2, cur_word_clip.h + pad * 2),
                    color=(255, 230, 100),
                )
                .set_start(word_idx * word_duration)
                .set_duration(word_duration)
            ).set_position((line_x + pre_width - pad, line_y - pad))
            clips.append(highlight)

            # Base text (always visible)
            base_line_clip = (
                TextClip(
                    line_text,
                    fontsize=fontsize,
                    font=font_name,
                    color=TEXT_STYLE["color"],
                    stroke_color=TEXT_STYLE["stroke_color"],
                    stroke_width=TEXT_STYLE["stroke_width"],
                    method="label",
                )
                .set_start(word_idx * word_duration)
                .set_duration(word_duration)
                .set_position((line_x, line_y))
            )
            clips.append(base_line_clip)

            word_idx += 1
            cur_word_clip.close()

    composite = CompositeVideoClip(clips, size=bg_segment.size).set_duration(duration)
    overlays.append(composite)
    return overlays
