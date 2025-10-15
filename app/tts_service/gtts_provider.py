from gtts import gTTS
from pathlib import Path
from typing import Literal
from .text_preprocessor import TTSPreprocessor  # <-- new preprocessor
import shutil


class GTTSProvider:
    """
    Google Text-to-Speech provider with smart text preprocessing,
    automatic chunking, and basic voice control.
    """

    SUPPORTED_VOICES = {
        "male": "default",  # gTTS doesn’t support true male/female voices
        "female": "default",  # but pitch/filters can be added later if needed
    }

    def __init__(self, outputs_dir: Path = None):
        self.outputs_dir = outputs_dir or Path("outputs")
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

        # Initialize advanced text preprocessor
        self.preprocessor = TTSPreprocessor()

    def generate(
        self,
        text: str,
        output_path: str,
        voice: Literal["male", "female"] = "male",
        lang: str = "en",
        slow: bool = False,
    ) -> str:
        """
        Generate TTS using gTTS with smart preprocessing and chunk handling.

        Args:
            text: Text to synthesize.
            output_path: Output .mp3 file path.
            voice: Voice type ('male' or 'female') – gTTS only simulates difference.
            lang: Language code (default 'en').
            slow: Slow speech rate (default False).

        Returns:
            Path to generated audio file.
        """
        print(f"[gTTS] Generating audio (voice={voice}, lang={lang})...")

        # 1️⃣ Clean, normalize, and segment text
        cleaned_text = self.preprocessor.clean(text, lang=lang)
        sentences = self.preprocessor.segment(cleaned_text)

        if not sentences:
            raise ValueError("No valid text to synthesize after preprocessing.")

        # 2️⃣ Merge short sentences to fit gTTS limits (~100 chars per chunk)
        chunks = self.preprocessor.chunk_for_tts(sentences, max_chars=120)

        print(f"[gTTS] {len(chunks)} chunks prepared for synthesis.")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        temp_dir = Path(output_path).parent / "temp_gtts_chunks"
        temp_dir.mkdir(exist_ok=True)
        temp_files = []

        try:
            # 3️⃣ Generate TTS for each chunk
            for i, chunk in enumerate(chunks):
                temp_file = temp_dir / f"chunk_{i}.mp3"
                tts = gTTS(text=chunk, lang=lang, slow=slow)
                tts.save(str(temp_file))
                temp_files.append(temp_file)

            # 4️⃣ Combine all chunks into final output
            with open(output_path, "wb") as outfile:
                for temp_file in temp_files:
                    outfile.write(temp_file.read_bytes())

            print(f"[gTTS] ✅ Audio saved: {output_path}")
            return str(output_path)

        except Exception as e:
            print(f"[gTTS] ❌ Error during synthesis: {e}")
            raise

        finally:
            # 5️⃣ Cleanup temporary files
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
