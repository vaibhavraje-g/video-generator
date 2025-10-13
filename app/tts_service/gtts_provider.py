from gtts import gTTS
from pathlib import Path
from typing import Literal
from .text_preprocessor import TTSTextPreprocessor


class GTTSProvider:
    """Google Text-to-Speech provider with male/female voice options"""

    SUPPORTED_VOICES = {
        "male": "default",
        "female": "default",
    }

    def __init__(self, outputs_dir: Path = None):
        self.outputs_dir = outputs_dir or Path("outputs")
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        text: str,
        output_path: str,
        voice: Literal["male", "female"] = "male",
        lang: str = "en",
        slow: bool = False,
    ) -> str:
        """
        Generate TTS using gTTS

        Args:
            text: Text to synthesize
            output_path: Output file path
            voice: Voice type ('male' or 'female') - gTTS uses same synthesis, differentiated by pitch
            lang: Language code (default: 'en')
            slow: Slow speech rate (default: False)

        Returns:
            Path to generated audio file
        """
        print(f"Generating gTTS audio (voice: {voice})...")

        # Preprocess text using common preprocessor
        cleaned_text = TTSTextPreprocessor.clean_text(text, provider="gtts", lang=lang)
        print(
            f"Text: {cleaned_text[:100]}..."
            if len(cleaned_text) > 100
            else f"Text: {cleaned_text}"
        )

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Split long text if needed
        chunks = TTSTextPreprocessor.split_long_text(cleaned_text)
        if len(chunks) > 1:
            print(f"Text split into {len(chunks)} chunks for processing")

            # Create temporary directory for chunks
            temp_dir = Path(output_path).parent / "temp_chunks"
            temp_dir.mkdir(exist_ok=True)

            try:
                # Process each chunk

                temp_files = []
                for i, chunk in enumerate(chunks):
                    temp_file = temp_dir / f"chunk_{i}.mp3"
                    tts = gTTS(text=chunk, lang=lang, slow=slow)
                    tts.save(str(temp_file))
                    temp_files.append(temp_file)

                # Combine chunks
                with open(output_path, "wb") as outfile:
                    for temp_file in temp_files:
                        outfile.write(temp_file.read_bytes())

            finally:
                # Cleanup temp files
                import shutil

                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
        else:
            # Process single chunk
            tts = gTTS(text=cleaned_text, lang=lang, slow=slow)
            tts.save(output_path)

        print(f"OK gTTS audio saved to: {output_path}")
        return output_path
