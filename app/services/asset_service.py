import os
import time
import json
import requests
from pathlib import Path
import random
import logging

# Directories (always relative to project root)
BASE_DIR = Path(__file__).resolve().parents[2]  # project root
CHARACTER_IMAGES_DIR = BASE_DIR / "assets" / "characters"
BACKGROUND_VIDEOS_DIR = BASE_DIR / "assets" / "videos"
INFOGRAPHICS_DIR = BASE_DIR / "assets" / "infographics"

# Map long names → filenames (keys stored lowercase)
CHARACTER_MAP = {
    "peter griffin": "peter.png",
    "brian griffin": "brian.png",
    "stewie griffin": "stewie.png",
    "lois griffin": "lois.png",
    "chris griffin": "chris.png",
    # add more if needed
}

class InfographicDownloader:
    def __init__(self, download_folder=None):
        self.download_folder = download_folder or INFOGRAPHICS_DIR
        self.download_folder.mkdir(parents=True, exist_ok=True)
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging for image downloader"""
        os.makedirs("runtime_logs", exist_ok=True)
        log_path = os.path.join("runtime_logs", "infographic_downloader.log")

        self.logger = logging.getLogger("InfographicDownloader")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_path)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.logger.info("Infographic downloader initialized.")

    def search_images_duckduckgo(self, search_term, max_images=3):
        """Primary method: Use DuckDuckGo search library"""
        self.logger.info(f"Starting DuckDuckGo search for: {search_term}")
        
        try:
            from duckduckgo_search import DDGS
            
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            with DDGS() as ddgs:
                search_results = ddgs.images(
                    keywords=search_term,
                    region="us-en",
                    safesearch="moderate",
                    size="Medium",
                    max_results=max_images
                )
                image_data = list(search_results)
                
            self.logger.info(f"Found {len(image_data)} images for: {search_term}")
            return image_data
            
        except ImportError:
            self.logger.warning("duckduckgo-search library not installed")
            return []
        except Exception as e:
            self.logger.error(f"DuckDuckGo search failed: {e}")
            return []

    def search_images_selenium_fallback(self, search_term, max_images=3):
        """Fallback method: Use Selenium for DuckDuckGo if main method fails"""
        self.logger.info(f"Using Selenium fallback for: {search_term}")
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import re
            
            # Setup headless Chrome
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # Navigate to DuckDuckGo images
                search_url = f"https://duckduckgo.com/?q={search_term}&iar=images&iax=images&ia=images"
                driver.get(search_url)
                
                # Wait for images to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "img[src*='external-content']"))
                )
                
                # Find image elements
                img_elements = driver.find_elements(By.CSS_SELECTOR, "img[src*='external-content']")
                
                image_data = []
                for i, img in enumerate(img_elements[:max_images]):
                    src = img.get_attribute("src")
                    if src and "external-content" in src:
                        # Extract actual image URL from DuckDuckGo's proxy URL
                        match = re.search(r'u=([^&]+)', src)
                        if match:
                            from urllib.parse import unquote
                            actual_url = unquote(match.group(1))
                            image_data.append({"image": actual_url})
                
                self.logger.info(f"Selenium found {len(image_data)} images for: {search_term}")
                return image_data
                
            finally:
                driver.quit()
                
        except ImportError:
            self.logger.warning("Selenium not installed, skipping fallback")
            return []
        except Exception as e:
            self.logger.error(f"Selenium fallback failed: {e}")
            return []

    def download_image(self, image_url, output_filename):
        """Download a single image from URL"""
        try:
            output_path = self.download_folder / output_filename
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "image/webp,image/apng,image/jpeg,image/png,image/*,*/*;q=0.8",
                "Referer": "https://duckduckgo.com/"
            }
            
            self.logger.info(f"Downloading image: {image_url}")
            response = requests.get(image_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Check if it's actually an image and has reasonable size
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/') or len(response.content) < 1000:
                self.logger.warning(f"Invalid image or too small: {image_url}")
                return None
            
            with open(output_path, 'wb') as img_file:
                img_file.write(response.content)
            
            self.logger.info(f"Successfully downloaded: {output_path}")
            return str(output_path)
            
        except requests.RequestException as e:
            self.logger.error(f"Request error downloading {image_url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to download {image_url}: {e}")
            return None

    def search_and_download(self, search_term, output_filename):
        """Main method: Search and download the best image"""
        self.logger.info(f"Starting search and download for: '{search_term}'")
        
        # Try DuckDuckGo search first
        image_data = self.search_images_duckduckgo(search_term, max_images=5)
        
        # If DuckDuckGo fails, try Selenium fallback
        if not image_data:
            self.logger.info("DuckDuckGo failed, trying Selenium fallback...")
            image_data = self.search_images_selenium_fallback(search_term, max_images=5)
        
        # Try to download images until one works
        for idx, item in enumerate(image_data):
            image_url = item.get("image")
            if not image_url:
                continue
                
            result_path = self.download_image(image_url, output_filename)
            if result_path:
                return result_path
            
            # Small delay between download attempts
            time.sleep(random.uniform(0.5, 1.5))
        
        self.logger.warning(f"All download attempts failed for: {search_term}")
        return None

    def create_placeholder(self, search_term, output_filename):
        """Create a placeholder image if download fails"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            output_path = self.download_folder / output_filename
            
            # Create attractive placeholder
            img = Image.new('RGB', (500, 350), color='#34495e')
            draw = ImageDraw.Draw(img)
            
            # Try to load a system font
            try:
                font_large = ImageFont.truetype("arial.ttf", 28)
                font_small = ImageFont.truetype("arial.ttf", 18)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Clean and format text
            title = search_term.replace("infographic", "").replace("diagram", "").strip()
            words = title.split()[:3]
            display_title = " ".join(words).title()
            
            # Draw title
            try:
                bbox = draw.textbbox((0, 0), display_title, font=font_large)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(display_title) * 15
                
            x = (500 - text_width) // 2
            draw.text((x, 120), display_title, fill='#ecf0f1', font=font_large)
            
            # Draw subtitle
            subtitle = "Visual Guide"
            try:
                bbox = draw.textbbox((0, 0), subtitle, font=font_small)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(subtitle) * 10
                
            x = (500 - text_width) // 2
            draw.text((x, 170), subtitle, fill='#bdc3c7', font=font_small)
            
            # Add decorative border
            draw.rectangle([30, 220, 470, 280], outline='#3498db', width=2)
            draw.text((40, 230), "• Technical Overview", fill='#3498db', font=font_small)
            draw.text((40, 250), "• System Architecture", fill='#3498db', font=font_small)
            
            img.save(output_path)
            self.logger.info(f"Created placeholder: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to create placeholder: {e}")
            return None

# Global downloader instance
_infographic_downloader = None

def get_infographic_downloader():
    """Get or create global infographic downloader instance"""
    global _infographic_downloader
    if _infographic_downloader is None:
        _infographic_downloader = InfographicDownloader()
    return _infographic_downloader

def fetch_character_image(character: str) -> str:
    """Return local path to character PNG (mapped from canonical name)."""
    key = character.lower().strip()
    filename = CHARACTER_MAP.get(key)
    if not filename:
        raise ValueError(f"No mapping found for character: {character}")
    path = CHARACTER_IMAGES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Character image not found: {path}")
    print(f"✅ Found character image for {character}: {path}")
    return str(path)

def fetch_background_video(filename: str) -> str:
    """Fetch background video (local file)."""
    video_path = BACKGROUND_VIDEOS_DIR / filename
    if not video_path.exists():
        raise FileNotFoundError(f"Background video not found: {video_path}")
    print(f"✅ Using background video: {video_path}")
    return str(video_path)

def generate_smart_search_query(topic: str, dialogue_text: str, infographic_hint: str = None) -> str:
    """Generate contextually relevant search queries based on dialogue content and hints."""
    # Base topic keywords
    topic_clean = topic.replace("What is ", "").replace("?", "").strip()
    
    # Extract key technical terms from dialogue
    technical_keywords = []
    dialogue_lower = dialogue_text.lower()
    
    # Common technical terms to look for
    tech_terms = [
        "streaming", "platform", "data", "event", "message", "queue", "pipeline", 
        "distributed", "fault-tolerant", "high-throughput", "producer", "consumer",
        "topic", "partition", "cluster", "architecture", "diagram", "flow", "system"
    ]
    
    for term in tech_terms:
        if term in dialogue_lower:
            technical_keywords.append(term)
    
    # Use infographic hint if provided
    if infographic_hint:
        hint_clean = infographic_hint.lower().strip()
        # Extract meaningful words from the hint
        hint_words = [word for word in hint_clean.split() if len(word) > 2 and word not in ['the', 'and', 'for', 'with']]
        technical_keywords.extend(hint_words[:3])
    
    # Build search query with multiple relevant terms
    search_terms = [topic_clean]
    search_terms.extend(technical_keywords[:3])  # Limit to prevent long queries
    
    # Add context words for better image results
    context_words = ["diagram", "architecture", "infographic"]
    search_terms.extend(context_words[:2])
    
    query = " ".join(search_terms)
    return query[:80]  # Keep query concise

def fetch_infographic(topic: str, dialogue_text: str, output_filename: str, infographic_hint: str = None) -> str | None:
    """
    Smart infographic fetching with improved DuckDuckGo + Selenium fallback
    """
    
    # Generate smart search query
    query = generate_smart_search_query(topic, dialogue_text, infographic_hint)
    print(f"[INFO] Smart query: '{query}' (hint: '{infographic_hint}')")
    
    # Get downloader instance
    downloader = get_infographic_downloader()
    
    # Try to download image
    result_path = downloader.search_and_download(query, output_filename)
    
    if result_path:
        print(f"✅ Infographic downloaded: {result_path}")
        return result_path
    
    # Create placeholder if all else fails
    placeholder_path = downloader.create_placeholder(query, output_filename)
    if placeholder_path:
        print(f"✅ Created placeholder infographic: {placeholder_path}")
        return placeholder_path
    
    print(f"⚠️ Complete failure for query: {query}")
    return None
