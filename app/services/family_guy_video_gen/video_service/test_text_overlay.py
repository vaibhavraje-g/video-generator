from moviepy.editor import TextClip, CompositeVideoClip, ColorClip
from moviepy.config import change_settings

change_settings(
    {"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe"}
)

def test_highlight_positions(text, duration, video_w=1280, video_h=720, fontsize=48, font="Arial"):
    words = text.split()
    if not words:
        print("No words to test.")
        return

    total_words = len(words)
    word_duration = duration / total_words

    y_center = video_h // 2
    pad = 6

    # compute total line width for centering
    line_text = " ".join(words)
    line_clip = TextClip(line_text, fontsize=fontsize, font=font, method="label")
    line_x = (video_w - line_clip.w) // 2
    line_clip.close()

    for i, word in enumerate(words):
        pre_words = words[:i]
        pre_width = 0
        if pre_words:
            pre_text = " ".join(pre_words) + " "
            pre_clip = TextClip(pre_text, fontsize=fontsize, font=font, method="label")
            pre_width = pre_clip.w
            pre_clip.close()

        cur_clip = TextClip(word, fontsize=fontsize, font=font, method="label")
        start_time = i * word_duration
        end_time = start_time + word_duration
        print(
            f"[{start_time:.2f}s - {end_time:.2f}s] '{word}' "
            f"-> position x={line_x + pre_width}, width={cur_clip.w}"
        )
        cur_clip.close()


# Example test run
if __name__ == "__main__":
    test_highlight_positions("This is a sample text overlay test", duration=5)
