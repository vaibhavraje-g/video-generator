import os
from pathlib import Path
from gtts import gTTS
import requests
import zipfile
import io

# ----------------------------
# CONFIG
# ----------------------------
RVC_API_URL = "http://localhost:5500/convert"  # Your RVC WebUI Docker API
MODELS_DIR = Path("models/family_guy")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Mapping of characters to model download URLs
CHARACTER_MODELS = {
    "peter": "https://huggingface.co/AIMan2001/PeterGriffin/resolve/main/Peter%20Griffin.zip",
    "stewie": "https://voice-models.com/model/1q9IaVn8Ege",
    "meg": "https://huggingface.co/iatop65/RVC_Voices/resolve/main/Meg_Griffin_Mila_Kunis.zip"
}


# ----------------------------
# UTILITY FUNCTIONS
# ----------------------------
def download_and_extract_model(character: str):
    """Download character model if not already present."""
    model_path = MODELS_DIR / f"{character}.pth"
    if model_path.exists():
        return model_path

    url = CHARACTER_MODELS.get(character)
    if not url:
        raise ValueError(f"No model URL defined for character: {character}")

    print(f"📥 Downloading {character} model from {url} ...")
    r = requests.get(url)
    r.raise_for_status()

    # Handle zip extraction if needed
    if url.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            # Extract first .pth file found (assumes RVC model format)
            for file in z.namelist():
                if file.endswith(".pth"):
                    z.extract(file, MODELS_DIR)
                    extracted_path = MODELS_DIR / os.path.basename(file)
                    os.rename(extracted_path, model_path)
                    print(f"✅ Extracted model to {model_path}")
                    break
            else:
                raise RuntimeError(f"No .pth file found in zip for {character}")
    else:
        # Directly save as .pth
        with open(model_path, "wb") as f:
            f.write(r.content)
        print(f"✅ Saved model to {model_path}")

    return model_path


def convert_with_rvc(base_audio_path: str, character: str, output_path: str) -> str:
    """Send base audio to RVC API to convert to character voice."""
    # Ensure model is downloaded
    model_path = download_and_extract_model(character)

    print(f"🎭 Converting '{base_audio_path}' to {character} voice via RVC API ...")
    with open(base_audio_path, "rb") as f:
        files = {"audio": f}
        data = {"model": str(model_path.name)}
        response = requests.post(RVC_API_URL, files=files, data=data)

    if response.status_code == 200:
        Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as out_f:
            out_f.write(response.content)
        print(f"✅ Converted audio saved to {output_path}")
        return output_path
    else:
        raise RuntimeError(f"RVC conversion failed: {response.status_code} {response.text}")


# ----------------------------
# MAIN FUNCTION
# ----------------------------
def generate_tts(
    text: str, output_path: str, character: str = None, language: str = "en"
) -> str:
    """
    Generate TTS for given text and save as mp3.
    
    If `character` is provided, generate cloned voice via RVC.
    Otherwise, fallback to normal gTTS.
    """
    Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)

    if not character:
        # Normal gTTS
        tts = gTTS(text=text, lang=language)
        tts.save(output_path)
        print(f"✅ Normal TTS saved to {output_path}")
        return output_path
    else:
        # Generate base audio using gTTS
        base_path = MODELS_DIR / "base_temp.wav"
        tts = gTTS(text=text, lang=language)
        tts.save(base_path)

        # Convert via RVC
        result_path = convert_with_rvc(str(base_path), character, output_path)
        os.remove(base_path)  # clean up temp
        return result_path

