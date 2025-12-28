import re
from gruut import sentences as gruut_sentences
from unidecode import unidecode
import emoji


class TTSPreprocessor:
    """
    Smart text preprocessing and normalization for TTS engines.
    Handles punctuation, emoji, numbers, and sentence segmentation.
    """

    def __init__(self):
        pass

    def clean(self, text: str, lang: str = "en") -> str:
        """Basic cleanup and normalization."""
        text = unidecode(text)  # Remove accents
        text = emoji.demojize(text)  # Convert emojis to words
        text = re.sub(r"http\S+", "", text)  # Remove URLs
        text = re.sub(r"[\(\)\[\]\{\}<>]", "", text)  # Remove brackets
        text = re.sub(r"[^a-zA-Z0-9,.!?'\s-]", " ", text)  # Clean symbols
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def segment(self, text: str, lang: str = "en"):
        """Split text into natural sentences using Gruut."""
        try:
            sents = [s.text for s in gruut_sentences(text, lang=lang)]
            return [s for s in sents if len(s.strip()) > 1]
        except Exception:
            return re.split(r"[.!?]\s+", text)

    def chunk_for_tts(self, sentences, max_chars=120):
        """Group sentences into chunks within character limits."""
        chunks, current = [], ""
        for s in sentences:
            if len(current) + len(s) + 1 > max_chars:
                chunks.append(current.strip())
                current = s
            else:
                current += " " + s
        if current.strip():
            chunks.append(current.strip())
        return chunks
