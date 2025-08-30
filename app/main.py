import asyncio
from app.services.script_service import generate_script
from app.services.tts_service import generate_tts
from app.services.asset_service import (
    fetch_background_video,
    fetch_character_image,
    fetch_infographic
)
from app.services.video_service.video_service import generate_video

async def main():
    topic = "What is Kafka?"

    # 1. Generate script
    script = await generate_script(topic)
    print("Generated script:", script.model_dump())

    # 2. Generate TTS for each dialogue
    tts_files = []
    for i, dlg in enumerate(script.dialogues):
        path = f"projects/demo_project/audio/line_{i}.mp3"
        tts_files.append(generate_tts(dlg.text, path))

    # 3. Fetch character images (store keys lowercase)
    char_images = {}
    for dlg in script.dialogues:
        key = dlg.character.lower().strip()
        if key not in char_images:
            try:
                char_images[key] = fetch_character_image(dlg.character)
            except Exception as e:
                print(f"⚠️ Character image missing for {dlg.character}: {e}")
    print("Fetched character images:", char_images)

    # 4. Fetch infographic images with context-aware queries
    infographic_images = []
    for i, dlg in enumerate(script.dialogues):
        # Use the infographic hint from the dialogue if available
        infographic_hint = getattr(dlg, 'infographic', None)
        
        if infographic_hint:  # Only fetch if there's a specific hint
            path = fetch_infographic(
                topic=topic,
                dialogue_text=dlg.text,
                output_filename=f"info_{i}.png",
                infographic_hint=infographic_hint
            )
            if path:
                infographic_images.append(path)
                print(f"[INFO] Added infographic for dialogue {i}: {infographic_hint}")
            else:
                print(f"[INFO] No infographic found for dialogue {i}, using placeholder")
        else:
            print(f"[INFO] No infographic hint for dialogue {i}, skipping")

    # 5. Background video
    bg_video = fetch_background_video("gameplay.mp4")

    # 6. Generate final video
    output_path = "projects/demo_project/output/final.mp4"
    generate_video(
        script,
        tts_files,
        bg_video,
        output_path,
        char_images=char_images,
        infographic_images=infographic_images
    )
    print("✅ Video generated:", output_path)

if __name__ == "__main__":
    asyncio.run(main())
