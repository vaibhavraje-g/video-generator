# main.py
import asyncio
import uuid
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.family_guy_video_gen.interface import generate_family_guy_video

app = FastAPI(title="Family Guy Video Generator")

# Correct static folder path
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class VideoRequest(BaseModel):
    video_type: Literal["family_guy"]
    topic: str


@app.post("/generate")
async def generate_video_endpoint(request: VideoRequest):
    try:
        # Generate unique filename
        filename = f"output_{uuid.uuid4().hex}.mp4"
        output_path = STATIC_DIR / filename

        # Call your existing async generator
        if request.video_type == "family_guy":
            video_path = await generate_family_guy_video(
                topic=request.topic,
                output_path=str(output_path)
            )
        else:
            raise ValueError("Unsupported video type")

        # Return URL to access video
        return {
            "status": "success",
            "video_url": f"/static/{filename}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve the HTML page from static folder
@app.get("/", response_class=FileResponse)
def home():
    index_file = STATIC_DIR / "index.html"  # Make sure your HTML file is named index.html
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html not found in static folder")
    return index_file
