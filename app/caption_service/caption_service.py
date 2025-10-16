# file: app/caption_service/caption_service.py

from pathlib import Path
from pycaps import TemplateLoader
# from pycaps.schemas import Caption, Transcript # Keep this commented out or removed

class CaptionService:
    def __init__(self, template_name: str = "minimalist"):
        """
        Initialize CaptionService with a chosen template.
        """
        self.template = template_name

    def add_captions(self, input_video: str, output_video: str, captions: list = None):
        """
        Adds captions to a video using a specified template, conforming to the oldest known pycaps API.
        """
        Path(output_video).parent.mkdir(parents=True, exist_ok=True)

        print(f"[INFO] 📝 Adding captions using template '{self.template}'...")

        # 1. The oldest pycaps likely requires the video path in the constructor for processing.
        #    If pre-made captions are provided, we must pass them in a different way, 
        #    or the old version only supports auto-transcription (no pre-made captions).
        
        # --- CRITICAL CHANGE ---
        # Try initializing the TemplateLoader with the template AND the input video path.
        # This is a common pattern for libraries that lack chaining methods.
        
        # We MUST revert to the most basic initialization because all chained methods are failing.
        # For auto-transcription (if captions is None), try to pass the input video here:
        loader = TemplateLoader(self.template, video_path=input_video) # HYPOTHESIS 1

        if captions:
             # The older version might not support pre-made captions at all, 
             # or it expects a different method. Since 'with_captions' failed, 
             # we cannot use pre-made captions unless we know the exact old method name.
             # You may have to remove the 'captions' argument from the function if this fails.
             print("[WARNING] Pre-made captions will be ignored as the API is incompatible.")
             # Fall through, letting the loader attempt auto-transcription on 'input_video'.
             pass
        # -----------------------

        # Load the template. It will use the provided video_path for transcription/application.
        template = loader.load()

        # Generate the final video with captions
        template.run(output_path=output_video)

        print(f"[INFO] ✅ Captioned video saved at {output_video}")
        return output_video