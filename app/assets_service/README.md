# Assets Service

A centralized, maintainable, and extensible assets service for managing various types of media assets including images, videos, and character assets.

## Features

- **Multi-provider support**: Pixabay API, DuckDuckGo search
- **Character management**: Local character image assets
- **Stock footage**: Random or specific gameplay videos
- **Download management**: Automatic file validation and project directory enforcement
- **Configurable**: JSON-based configuration system
- **Extensible**: Easy to add new providers

## Quick Start

```python
from app.assets_service import AssetsService

# Initialize the service
assets_service = AssetsService()

# Get stock gameplay footage
video_path = assets_service.get_stock_gameplay_footage()

# Get character image
peter_image = assets_service.get_peter_image()

# Search for infographics
infographic = assets_service.get_assets_infographics(
    query="javascript event loop diagram"
)

# Search for videos
video = assets_service.get_videos_pixabay(
    query="coding tutorial"
)
```

## Configuration

The service uses `config.json` for configuration:

```json
{
  "pixabay_api": {
    "enabled": true,
    "api_key": "your_pixabay_api_key",
    "max_results": 5
  },
  "duckduckgo": {
    "enabled": true,
    "max_results": 5
  },
  "character_images": {
    "enabled": true,
    "characters_dir": "assets/characters",
    "character_mappings": {
      "peter": "peter.png",
      "brian": "brian.png"
    }
  }
}
```

## API Reference

### AssetsService

#### `get_stock_gameplay_footage(filename=None)`
Get stock gameplay footage (random or specific file).

#### `get_assets_infographics(query, sources=None, output_path=None, max_results=5)`
Search and download infographics from multiple sources.

#### `get_videos_pixabay(query, api_key=None, output_path=None, max_results=5)`
Search and download videos using Pixabay API.

#### `get_character_image(character_name, mood_descriptor=None)`
Get character image from local assets.

#### `search_assets(query, asset_type="images", sources=None, max_results=5)`
Search for assets using multiple providers.

#### `download_asset(url, output_path, asset_type="image")`
Download an asset from URL with validation.

## Providers

### PixabayProvider
- Images and videos from Pixabay API
- Requires API key
- High-quality assets

### DuckDuckGoProvider
- Image search using DuckDuckGo
- No API key required
- Good fallback option

### CharacterProvider
- Local character image management
- Character name mapping
- Mood-based image selection

### DownloadService
- File download with validation
- Project directory enforcement
- File size and type validation

## Directory Structure

```
app/assets_service/
├── __init__.py              # Module exports
├── config.py                # Configuration management
├── config.json              # Service configuration
├── service.py               # Main AssetsService class
├── pixabay_provider.py      # Pixabay API provider
├── duckduckgo_provider.py   # DuckDuckGo provider
├── character_provider.py    # Character image provider
├── download_service.py      # Download management
└── example_usage.py         # Usage examples
```

## Requirements

- `requests` - HTTP requests
- `ddgs` (duckduckgo-search) - DuckDuckGo search
- `Pillow` - Image processing (for placeholders)

## Installation

```bash
pip install requests duckduckgo-search Pillow
```

## Error Handling

The service includes comprehensive error handling:
- Provider failures fall back to alternatives
- Invalid downloads are skipped
- File validation ensures quality
- Project directory enforcement prevents unauthorized access

