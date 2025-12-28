"""Test script to verify assets service paths work correctly"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.assets_service import AssetsService


def test_assets_service():
    """Test the assets service with new paths"""

    print("🧪 Testing Assets Service with new paths")
    print("=" * 50)

    try:
        # Initialize the service
        assets_service = AssetsService()

        # Test character images
        print("\n👤 Testing character images...")
        try:
            peter_path = assets_service.get_peter_image()
            print(f"✅ Peter image: {peter_path}")
            print(f"   File exists: {Path(peter_path).exists()}")

            brian_path = assets_service.get_brian_image()
            print(f"✅ Brian image: {brian_path}")
            print(f"   File exists: {Path(brian_path).exists()}")

            stewie_path = assets_service.get_stewie_image()
            print(f"✅ Stewie image: {stewie_path}")
            print(f"   File exists: {Path(stewie_path).exists()}")

            lois_path = assets_service.get_lois_image()
            print(f"✅ Lois image: {lois_path}")
            print(f"   File exists: {Path(lois_path).exists()}")

        except Exception as e:
            print(f"❌ Character image test failed: {e}")

        # Test stock gameplay footage
        print("\n📹 Testing stock gameplay footage...")
        try:
            video_path = assets_service.get_stock_gameplay_footage()
            print(f"✅ Random video: {video_path}")
            print(f"   File exists: {Path(video_path).exists()}")

            # Test specific video
            specific_video = assets_service.get_stock_gameplay_footage("gameplay.mp4")
            print(f"✅ Specific video: {specific_video}")
            print(f"   File exists: {Path(specific_video).exists()}")

        except Exception as e:
            print(f"❌ Stock video test failed: {e}")

        # Test configuration paths
        print("\n⚙️ Testing configuration paths...")
        config = assets_service.config
        characters_dir = config.get_characters_dir()
        videos_dir = config.get_stock_videos_dir()

        print(f"✅ Characters directory: {characters_dir}")
        print(f"   Directory exists: {characters_dir.exists()}")
        print(f"   Files in directory: {list(characters_dir.glob('*.png'))}")

        print(f"✅ Videos directory: {videos_dir}")
        print(f"   Directory exists: {videos_dir.exists()}")
        print(f"   Files in directory: {list(videos_dir.glob('*.mp4'))}")

        print("\n🎉 All tests completed!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_assets_service()
