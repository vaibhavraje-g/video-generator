from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)

def create_placeholder(search_term: str, output_path: Path) -> str | None:
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        img = Image.new("RGB", (500, 350), color="#34495e")
        draw = ImageDraw.Draw(img)

        # Try to use arial, fall back to default
        try:
            font_large = ImageFont.truetype("arial.ttf", 28)
            font_small = ImageFont.truetype("arial.ttf", 18)
        except OSError:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Clean title
        title = search_term.replace("infographic", "").replace("diagram", "").strip()
        display_title = " ".join(title.split()[:3]).title()

        # Center title
        try:
            bbox = draw.textbbox((0, 0), display_title, font=font_large)
            x = (500 - (bbox[2] - bbox[0])) // 2
        except:
            x = 50
        draw.text((x, 120), display_title, fill="#ecf0f1", font=font_large)

        # Subtitle
        draw.text((160, 170), "Visual Guide", fill="#bdc3c7", font=font_small)

        # Decorative elements
        draw.rectangle([30, 220, 470, 280], outline="#3498db", width=2)
        draw.text((40, 230), "• Technical Overview", fill="#3498db", font=font_small)
        draw.text((40, 250), "• System Architecture", fill="#3498db", font=font_small)

        img.save(output_path)
        logger.info(f"Created placeholder: {output_path}")
        return str(output_path)

    except Exception as e:
        logger.error(f"Failed to create placeholder: {e}")
        return None