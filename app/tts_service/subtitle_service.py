"""Local subtitle generation service using MoviePy"""

import os
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import timedelta
from moviepy.editor import AudioFileClip, TextClip, VideoFileClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip

try:
    import srt_equalizer
    SRT_EQUALIZER_AVAILABLE = True
except ImportError:
    SRT_EQUALIZER_AVAILABLE = False


class SubtitleService:
    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get("enabled", True)
        self.max_chars = config.get("max_chars", 42)  # Increased for readability
        self.subtitles_dir = Path(config.get("subtitles_dir", "subtitles"))
        self.subtitles_dir.mkdir(exist_ok=True)

    def generate_subtitles_locally(
        self, sentences: List[str], audio_clips: List[AudioFileClip]
    ) -> str:
        def convert_to_srt_time_format(total_seconds):
            if total_seconds == 0:
                return "00:00:00,000"
            td = timedelta(seconds=total_seconds)
            hours, remainder = divmod(td.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            milliseconds = int((seconds - int(seconds)) * 1000)
            return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"

        start_time = 0.0
        subtitles = []

        for i, (sentence, audio_clip) in enumerate(zip(sentences, audio_clips), start=1):
            duration = audio_clip.duration
            end_time = start_time + duration
            entry = f"{i}\n{convert_to_srt_time_format(start_time)} --> {convert_to_srt_time_format(end_time)}\n{sentence}\n"
            subtitles.append(entry)
            start_time = end_time

        return "\n".join(subtitles)

    def generate_subtitles(
        self, sentences: List[str], audio_clips: List[AudioFileClip]
    ) -> str:
        if not self.enabled:
            raise RuntimeError("Subtitle service is disabled")
        if not sentences or not audio_clips:
            raise ValueError("Sentences and audio_clips are required")

        subtitle_id = uuid.uuid4()
        subtitles_path = self.subtitles_dir / f"{subtitle_id}.srt"

        try:
            print("🎬 Creating subtitles locally")
            srt_content = self.generate_subtitles_locally(sentences, audio_clips)
            with open(subtitles_path, "w", encoding="utf-8") as f:
                f.write(srt_content)
            self.equalize_subtitles(str(subtitles_path))
            print(f"✅ Subtitles generated: {subtitles_path}")
            return str(subtitles_path)
        except Exception as e:
            print(f"❌ Subtitle generation failed: {e}")
            raise

    def equalize_subtitles(self, srt_path: str, max_chars: int = None) -> None:
        if not SRT_EQUALIZER_AVAILABLE:
            return
        if max_chars is None:
            max_chars = self.max_chars
        try:
            srt_equalizer.equalize_srt_file(srt_path, srt_path, max_chars)
        except Exception as e:
            print(f"⚠️ Subtitle equalization failed: {e}")

    def create_subtitle_clip(
        self,
        subtitles_path: str,
        font_path: str = None,
        font_size: int = 100,
        color: str = "white",
        stroke_color: str = "black",
        stroke_width: int = 5,
    ) -> SubtitlesClip:
        def generator(txt):
            # Use system-safe fonts
            if font_path and os.path.exists(font_path):
                font = font_path
            else:
                font = "Arial-Bold" if os.name == "nt" else "Helvetica-Bold"
            try:
                return TextClip(
                    txt,
                    font=font,
                    fontsize=font_size,
                    color=color,
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                    method='caption',
                    size=(1000, None),  # Constrain width
                    align='center'
                )
            except Exception as e:
                print(f"⚠️ TextClip fallback for: {txt[:30]}... | Error: {e}")
                return TextClip(
                    txt,
                    fontsize=font_size,
                    color=color,
                    method='caption',
                    size=(1000, None),
                    align='center'
                )
        return SubtitlesClip(subtitles_path, generator)