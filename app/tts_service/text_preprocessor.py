"""Common text preprocessing utilities for TTS services"""

import re
from typing import Optional, List
import unicodedata


class TTSTextPreprocessor:
    """Text preprocessing utilities for TTS services"""

    # Common replacements for improved speech synthesis
    COMMON_REPLACEMENTS = {
        # Numbers and units
        r"\b(\d+)([kK])\b": r"\1 thousand",  # 10k -> 10 thousand
        r"\b(\d+)([mM])\b": r"\1 million",  # 5m -> 5 million
        r"\b(\d+)([bB])\b": r"\1 billion",  # 2b -> 2 billion
        r"\$(\d+)": r"\1 dollars",  # $10 -> 10 dollars
        r"(\d+)%": r"\1 percent",  # 50% -> 50 percent
        # Common abbreviations
        r"\bdr\.\s": "doctor ",
        r"\bmr\.\s": "mister ",
        r"\bmrs\.\s": "missus ",
        r"\bst\.\s": "street ",
        r"\bprof\.\s": "professor ",
        # Technical terms
        r"\bAPI\b": "A P I",
        r"\bSQL\b": "S Q L",
        r"\bJSON\b": "Jason",
        r"\bHTML\b": "H T M L",
        r"\bCSS\b": "C S S",
        r"\bAI\b": "A I",
        r"\bML\b": "M L",
        r"\bUI\b": "U I",
        r"\bUX\b": "U X",
        # Common symbols
        r"&": " and ",
        r"@": " at ",
        r"#": " hash tag ",
        r"\+": " plus ",
        r"=": " equals ",
        r"\/": " or ",
        r"\b-\b": " minus ",
        # URLs and emails
        r"https?://\S+": " U R L ",
        r"www\.\S+": " website ",
        r"\S+@\S+\.\S+": " email address ",
        # Time format
        r"(\d{1,2}):(\d{2})\s*(am|pm)": r"\1 \2 \3",  # 9:30am -> 9 30 am
        r"(\d{1,2}):(\d{2})\s*(AM|PM)": r"\1 \2 \3",  # 9:30AM -> 9 30 AM
        # Date format
        r"(\d{1,2})/(\d{1,2})/(\d{2,4})": r"\1 \2 \3",  # 10/12/2023 -> 10 12 2023
    }

    # Special character mappings for different languages
    CHAR_REPLACEMENTS = {
        # German
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
        # French
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "à": "a",
        "â": "a",
        "ù": "u",
        "û": "u",
        "ç": "c",
        # Spanish
        "ñ": "n",
        "á": "a",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ü": "u",
    }

    @classmethod
    def clean_text(
        cls,
        text: str,
        provider: Optional[str] = None,
        lang: Optional[str] = None,
        preserve_case: bool = False,
    ) -> str:
        """
        Clean and preprocess text for TTS synthesis

        Args:
            text: Input text to clean
            provider: TTS provider name ('gtts', 'tiktok', 'chatterbox', etc.)
            lang: Language code (e.g., 'en', 'de', 'fr', etc.)
            preserve_case: Whether to preserve original text case

        Returns:
            Cleaned text ready for TTS synthesis
        """
        if not text:
            return text

        # 1. Basic cleaning
        text = text.strip()

        # 2. Handle quotes and apostrophes
        text = cls._normalize_quotes(text)

        # 3. Apply common replacements
        text = cls._apply_replacements(text)

        # 4. Handle special characters based on language
        if lang:
            text = cls._handle_language_chars(text, lang)

        # 5. Provider-specific cleaning
        text = cls._provider_specific_cleaning(text, provider)

        # 6. Final formatting
        if not preserve_case:
            text = text.lower()

        # 7. Remove extra whitespace
        text = " ".join(text.split())

        return text

    @classmethod
    def _normalize_quotes(cls, text: str) -> str:
        """Normalize different types of quotes"""
        # Convert fancy quotes to simple quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(""", "'").replace(""", "'")

        # Handle contractions
        text = text.replace("'s", " is")
        text = text.replace("'re", " are")
        text = text.replace("'ve", " have")
        text = text.replace("'ll", " will")
        text = text.replace("'d", " would")
        text = text.replace("n't", " not")

        return text

    @classmethod
    def _apply_replacements(cls, text: str) -> str:
        """Apply common text replacements"""
        for pattern, replacement in cls.COMMON_REPLACEMENTS.items():
            text = re.sub(pattern, replacement, text)
        return text

    @classmethod
    def _handle_language_chars(cls, text: str, lang: str) -> str:
        """Handle special characters based on language"""
        if lang.startswith("en"):  # English - remove diacritics
            return "".join(
                c
                for c in unicodedata.normalize("NFD", text)
                if unicodedata.category(c) != "Mn"
            )

        # For other languages, replace special chars with their ASCII equivalents
        for special_char, replacement in cls.CHAR_REPLACEMENTS.items():
            text = text.replace(special_char, replacement)

        return text

    @classmethod
    def _provider_specific_cleaning(cls, text: str, provider: Optional[str]) -> str:
        """Apply provider-specific text cleaning"""
        if provider == "tiktok":
            # TikTok specific replacements
            text = text.replace("+", "plus")
            text = text.replace("&", "and")

        elif provider == "gtts":
            # gTTS specific handling
            # Remove characters that gTTS doesn't handle well
            text = re.sub(r"[^\w\s.,!?-]", " ", text)

        elif provider == "chatterbox":
            # ChatterboxTTS specific handling
            # Handle emphasis with repeated characters
            text = re.sub(r"(.)\1{2,}", r"\1\1", text)  # convert 'yaaay' to 'yaay'

        return text

    @classmethod
    def split_long_text(
        cls,
        text: str,
        max_length: int = 200,
        split_on: List[str] = [".", "!", "?", ";", ","],
    ) -> List[str]:
        """
        Split long text into smaller chunks for TTS processing

        Args:
            text: Long text to split
            max_length: Maximum length of each chunk
            split_on: List of characters to split on, in priority order

        Returns:
            List of text chunks
        """
        # If text is short enough, return as is
        if len(text) <= max_length:
            return [text]

        chunks = []
        current_chunk = ""

        # Split text into sentences first
        sentences = cls._split_into_sentences(text)

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                if len(sentence) > max_length:
                    # Split long sentence on allowed characters
                    sub_chunks = cls._split_sentence(sentence, max_length, split_on)
                    chunks.extend(sub_chunks)
                else:
                    current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    @classmethod
    def _split_into_sentences(cls, text: str) -> List[str]:
        """Split text into sentences"""
        # Handle common abbreviations to avoid incorrect splits
        text = re.sub(r"(?<=Mr)\.", "@period@", text)
        text = re.sub(r"(?<=Dr)\.", "@period@", text)
        text = re.sub(r"(?<=Mrs)\.", "@period@", text)
        text = re.sub(r"(?<=Ms)\.", "@period@", text)

        # Split on sentence endings
        sentences = re.split(r"(?<=[.!?])\s+", text)

        # Restore periods in abbreviations
        sentences = [s.replace("@period@", ".") for s in sentences]

        return sentences

    @classmethod
    def _split_sentence(
        cls, sentence: str, max_length: int, split_chars: List[str]
    ) -> List[str]:
        """Split a long sentence into smaller chunks"""
        if len(sentence) <= max_length:
            return [sentence]

        chunks = []
        current_chunk = ""
        words = sentence.split()

        for word in words:
            if len(current_chunk) + len(word) + 1 <= max_length:
                current_chunk += " " + word if current_chunk else word
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = word

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
