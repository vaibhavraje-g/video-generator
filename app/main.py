import asyncio
from typing import Literal

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

    Returns:
        str: Path to the generated video file
    """
    if video_type == "family_guy":
        return await generate_family_guy_video(
            topic=kwargs["topic"], output_path=kwargs.get("output_path")
        )

    else:
        raise ValueError(f"Unknown video type: {video_type}")


# Example usage
if __name__ == "__main__":

    async def main():
        # Example 1: Generate a Family Guy style educational video
        video_path = await generate_video(
            video_type="family_guy",
            topic="Peter tries to go viral on TikTok, but Stewie points out, 'Your dance moves are a biohazard.' Brian suggests, 'Maybe just stick to reviewing AI tools.' Meanwhile, Meg secretly becomes the influencer everyone talks about.'",
        )
        print("✅ Family Guy video generated:", video_path)

    asyncio.run(main())
