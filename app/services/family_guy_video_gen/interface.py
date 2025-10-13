import asyncio
from typing import Optional
from pathlib import Path

from .script_service import generate_script
from ...tts_service import TTSService
from ...assets_service import AssetsService
from .project_manager import ProjectManager
from .video_service.video_service import generate_video


async def generate_family_guy_video(topic: str, output_path: Optional[str] = None) -> str:
    """
    Generate a Family Guy style educational video for a given topic.
    """
    short_topic = "peter_tech_video"
    project_manager = ProjectManager()
    project_paths = project_manager.create_project(short_topic)
    print(f"📁 Project: {project_paths['project_dir']}")

    # 1️⃣ Generate script
    script = await generate_script(topic)
    print(f"🧠 Generated script for topic: {topic}")

    # 2️⃣ Initialize services
    assets_service = AssetsService(project_dir=Path(project_paths["project_dir"]))
    tts_service = TTSService()

    # 3️⃣ Character images
    unique_characters = {d.character for d in script.dialogues}
    character_image_map = {}
    for char in unique_characters:
        try:
            path = assets_service.get_character_image(char)
            character_image_map[char.lower().strip()] = path
        except Exception as e:
            print(f"⚠️ Missing image for {char}: {e}")

    # 4️⃣ Background gameplay video
    background_video_path = assets_service.get_stock_gameplay_footage()

    # 5️⃣ Generate TTS and infographics in parallel
    async def generate_all_audio():
        async def generate_single_audio(index, dialogue):
            out_path = project_manager.get_audio_path(project_paths["project_dir"], index)
            audio_path = tts_service.generate_character_voice(dialogue.text, dialogue.character, out_path)
            return index, audio_path

        results = await asyncio.gather(
            *[generate_single_audio(i, d) for i, d in enumerate(script.dialogues)]
        )
        return [path for _, path in sorted(results)]

    async def fetch_all_infographics():
        async def fetch_single_infographic(index, dialogue):
            infographic_hint = getattr(dialogue, "infographic", None)
            if not infographic_hint:
                return index, None

            # Generate consistent infographic path (don’t re-download)
            infographic_path = project_manager.get_infographic_path(
                project_paths["project_dir"], index
            )

            # Try using local if exists, otherwise fetch via AssetsService
            if not Path(infographic_path).exists():
                try:
                    assets_service.get_assets_infographics(
                        query=infographic_hint,
                        output_path=Path(infographic_path),
                    )
                except Exception as e:
                    print(f"⚠️ Failed to fetch infographic for {infographic_hint}: {e}")
                    return index, None

            return index, infographic_path

        results = await asyncio.gather(
            *[fetch_single_infographic(i, d) for i, d in enumerate(script.dialogues)]
        )
        return [path for _, path in sorted(results) if path is not None]

    audio_paths, infographic_paths = await asyncio.gather(
        generate_all_audio(),
        fetch_all_infographics(),
    )

    # 6️⃣ Compose final video
    output_video_path = output_path or project_paths["final_video"]
    generate_video(
        script=script,
        tts_files=audio_paths,
        bg_video=background_video_path,
        output_path=output_video_path,
        char_images=character_image_map,
        infographic_images=infographic_paths,
    )

    print(f"✅ Final video generated at: {output_video_path}")
    print(f"🗂️ Assets stored in: {project_paths['project_dir']}")
    return output_video_path
