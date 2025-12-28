"""Example usage of the centralized Assets Service"""

from app.assets_service import AssetsService


def main():
    """Example usage of AssetsService"""

    # Initialize the service
    assets_service = AssetsService()

    print("🎬 Assets Service Example")
    print("=" * 50)

    # 1. Get stock gameplay footage
    try:
        print("\n📹 Getting stock gameplay footage...")
        video_path = assets_service.get_stock_gameplay_footage()
        print(f"✅ Found video: {video_path}")
    except FileNotFoundError as e:
        print(f"❌ No videos found: {e}")

    # 2. Get character images
    try:
        print("\n👤 Getting character images...")
        peter_path = assets_service.get_peter_image()
        print(f"✅ Peter image: {peter_path}")

        brian_path = assets_service.get_brian_image()
        print(f"✅ Brian image: {brian_path}")
    except ValueError as e:
        print(f"❌ Character not found: {e}")

    # 3. Search for infographics
    try:
        print("\n📊 Searching for infographics...")
        infographic_path = assets_service.get_assets_infographics(
            query="javascript event loop diagram", sources=["duckduckgo", "pixabay"]
        )
        print(f"✅ Downloaded infographic: {infographic_path}")
    except RuntimeError as e:
        print(f"❌ Failed to get infographic: {e}")

    # 4. Search for videos
    try:
        print("\n🎥 Searching for videos...")
        video_path = assets_service.get_videos_pixabay(query="coding tutorial")
        print(f"✅ Downloaded video: {video_path}")
    except RuntimeError as e:
        print(f"❌ Failed to get video: {e}")

    # 5. Search assets with multiple sources
    print("\n🔍 Searching assets...")
    results = assets_service.search_assets(
        query="programming concepts",
        asset_type="images",
        sources=["duckduckgo", "pixabay"],
        max_results=3,
    )
    print(f"✅ Found {len(results)} assets")
    for i, result in enumerate(results[:3]):
        print(
            f"  {i + 1}. {result.get('title', 'No title')} from {result.get('source')}"
        )


if __name__ == "__main__":
    main()
