import asyncio
from typing import Optional, List, Literal

from app.services.family_guy_video_gen.interface import generate_family_guy_video
# from app.services.frequencies_video_gen.interface import generate_frequencies_video
# from app.services.subliminal_video_gen.interface import generate_subliminal_video

VideoType = Literal["family_guy", "frequencies", "subliminal"]


async def generate_video(video_type: VideoType, **kwargs) -> str:
    """
    Main interface for video generation. Delegates to appropriate video generator based on type.

    Args:
        video_type: Type of video to generate
        **kwargs: Arguments specific to each video type:

            For "family_guy":
                topic: str - The educational topic
                output_path: Optional[str] - Custom output path

            For "frequencies":
                frequencies: List[float] - List of frequencies in Hz
                duration: float - Duration in seconds
                output_path: Optional[str] - Custom output path

            For "subliminal":
                messages: List[str] - Subliminal messages
                background_video_path: str - Background video path
                flash_duration_ms: Optional[float] - Flash duration in ms
                output_path: Optional[str] - Custom output path

    Returns:
        str: Path to the generated video file
    """
    if video_type == "family_guy":
        return await generate_family_guy_video(
            topic=kwargs["topic"], output_path=kwargs.get("output_path")
        )

    # elif video_type == "frequencies":
    #     return await generate_frequencies_video(
    #         frequencies=kwargs["frequencies"],
    #         duration=kwargs["duration"],
    #         output_path=kwargs.get("output_path")
    #     )

    # elif video_type == "subliminal":
    #     return await generate_subliminal_video(
    #         messages=kwargs["messages"],
    #         background_video_path=kwargs["background_video_path"],
    #         flash_duration_ms=kwargs.get("flash_duration_ms", 33.3),
    #         output_path=kwargs.get("output_path")
    #     )

    else:
        raise ValueError(f"Unknown video type: {video_type}")


# Example usage
if __name__ == "__main__":

    async def main():
        # Example 1: Generate a Family Guy style educational video
        video_path = await generate_video(
            video_type="family_guy",
            topic="Create a short (50–60s) video where Peter explains how this video was made programmatically using MoviePy and Chatterbox for voice cloning. Keep it simple and engaging for the 'Peter Talks Tech' channel. End by saying: 'Comment below to get the free video generator link — I’ll DM it to you!'",
        )
        print("✅ Family Guy video generated:", video_path)

        # # Example 2: Generate a frequencies video
        # video_path = await generate_video(
        #     video_type="frequencies",
        #     frequencies=[432, 528, 639],  # Hz
        #     duration=60  # seconds
        # )
        # print("✅ Frequencies video generated:", video_path)

        # # Example 3: Generate a subliminal video
        # video_path = await generate_video(
        #     video_type="subliminal",
        #     messages=["Be productive", "Stay focused", "Keep learning"],
        #     background_video_path="assets/videos/nature_scene.mp4"
        # )
        # print("✅ Subliminal video generated:", video_path)

    asyncio.run(main())
