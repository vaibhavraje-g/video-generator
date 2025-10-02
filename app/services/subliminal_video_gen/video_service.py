from typing import List, Dict
import moviepy.editor as mp
from pathlib import Path


def generate_video(
    config: Dict,
    affirmation_paths: List[str],
    frequency_path: str,
    music_path: str,
    output_path: str,
    duration_minutes: int,
) -> str:
    """
    Generate the final subliminal video by combining video and audio layers.

    Args:
        config: The video configuration (background video, audio settings, etc.)
        affirmation_paths: List of paths to TTS audio files for affirmations
        frequency_path: Path to the generated frequencies audio file
        music_path: Path to the background music file
        output_path: Where to save the final video
        duration_minutes: Length of the final video in minutes
    """
    duration_seconds = duration_minutes * 60

    # Load background video - for now using a sample
    # TODO: Implement video fetching based on config['background_video']
    video = mp.VideoFileClip("assets/videos/sample_background.mp4")

    # Loop video if needed
    if video.duration < duration_seconds:
        video = video.loop(duration=duration_seconds)
    else:
        video = video.subclip(0, duration_seconds)

    # Load and arrange audio tracks
    affirmations = [mp.AudioFileClip(path) for path in affirmation_paths]
    frequencies = mp.AudioFileClip(frequency_path)
    background_music = mp.AudioFileClip(music_path)

    # Loop and arrange affirmations according to strategy
    gap_duration = 5  # 5 second gap between affirmations
    current_time = 0
    affirmation_clips = []

    while current_time < duration_seconds:
        for affirmation in affirmations:
            if current_time + affirmation.duration > duration_seconds:
                break

            affirmation_clips.append(
                affirmation.set_start(current_time).volumex(
                    0.3
                )  # Low volume for subliminal effect
            )
            current_time += affirmation.duration + gap_duration

    # Combine all audio
    frequencies = frequencies.loop(duration=duration_seconds).volumex(0.2)
    background_music = background_music.loop(duration=duration_seconds).volumex(0.4)

    final_audio = mp.CompositeAudioClip(
        [background_music, frequencies, *affirmation_clips]
    )

    # Combine video and audio
    final_video = video.set_audio(final_audio)

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Write final video
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=30)

    # Clean up
    video.close()
    for clip in affirmations:
        clip.close()
    frequencies.close()
    background_music.close()

    return output_path
