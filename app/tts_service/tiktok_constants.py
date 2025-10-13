"""TikTok TTS API constants and voice configurations"""

# API Configuration
API_BASE_URL = (
    "https://api16-normal-c-useast1a.tiktokv.com/media/api/text/speech/invoke/"
)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Request Headers
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": "https://www.tiktok.com",
    "Referer": "https://www.tiktok.com/",
}

# Voice Categories and IDs
DISNEY_VOICES = {
    "ghost_face": "en_us_ghostface",
    "chewbacca": "en_us_chewbacca",
    "c3po": "en_us_c3po",
    "stitch": "en_us_stitch",
    "stormtrooper": "en_us_stormtrooper",
    "rocket": "en_us_rocket",
}

ENGLISH_VOICES = {
    "au_female": "en_au_001",
    "au_male": "en_au_002",
    "uk_male1": "en_uk_001",
    "uk_male2": "en_uk_003",
    "us_female1": "en_us_001",
    "us_female2": "en_us_002",
    "us_male1": "en_us_006",
    "us_male2": "en_us_007",
    "us_male3": "en_us_009",
    "us_male4": "en_us_010",
}

EUROPE_VOICES = {
    "fr_male1": "fr_001",
    "fr_male2": "fr_002",
    "de_female": "de_001",
    "de_male": "de_002",
    "es_male": "es_002",
}

AMERICA_VOICES = {
    "es_mx_male": "es_mx_002",
    "br_female1": "br_001",
    "br_female2": "br_003",
    "br_female3": "br_004",
    "br_male": "br_005",
}

ASIA_VOICES = {
    "id_female": "id_001",
    "jp_female1": "jp_001",
    "jp_female2": "jp_003",
    "jp_female3": "jp_005",
    "jp_male": "jp_006",
    "kr_male1": "kr_002",
    "kr_female": "kr_003",
    "kr_male2": "kr_004",
}

SINGING_VOICES = {
    "alto": "en_female_f08_salut_damour",
    "tenor": "en_male_m03_lobby",
    "warmy_breeze": "en_female_f08_warmy_breeze",
    "sunshine": "en_male_m03_sunshine_soon",
}

SPECIAL_VOICES = {
    "narrator": "en_male_narration",
    "wacky": "en_male_funny",
    "peaceful": "en_female_emotional",
}

# Combined voice list
ALL_VOICES = {
    **DISNEY_VOICES,
    **ENGLISH_VOICES,
    **EUROPE_VOICES,
    **AMERICA_VOICES,
    **ASIA_VOICES,
    **SINGING_VOICES,
    **SPECIAL_VOICES,
}

# Default voice ID if none specified
DEFAULT_VOICE = "en_us_002"  # US Female voice 2

# Batch processing settings
CHUNK_SIZE = 200  # Maximum text length per request
