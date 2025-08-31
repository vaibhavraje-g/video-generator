import asyncio
from typing import List, Optional
from pydantic import BaseModel
from app.services.llm_service import invoke_llm_with_prompt


# --- Schema ---
class DialogueLine(BaseModel):
    character: str
    text: str
    infographic: Optional[str] = None  # keyword/topic for infographic


class VideoScript(BaseModel):
    topic: str
    dialogues: List[DialogueLine]


# --- Prompt Template ---
SCRIPT_PROMPT_TEMPLATE = """
You are a scriptwriter for short engaging explainer videos.

Generate a conversational script in strict JSON format for a vertical video
where cartoon characters (like Family Guy characters) discuss and explain "{topic}".

Requirements:
- Script length: 30–60 sec, 3–6 dialogue lines.
- Each line must include `character` and `text`.
- **MANDATORY:** At least 1–3 dialogue lines MUST include an `infographic` field. 
  This field should be a short keyword or phrase describing a relevant concept, chart, or diagram
  that can visually support that dialogue line.
  Example: {{"character": "Peter Griffin", "text": "AI is everywhere!", "infographic": "AI basics"}}
- Keep it funny + informative (TikTok/MrBeast style).
- Maintain Family Guy character style (Peter, Stewie, Brian, etc.).
- Reply ONLY with valid JSON. No commentary outside JSON.
"""


# --- Service Function ---
async def generate_script(topic: str) -> VideoScript:
    """
    Generate a video script for a given topic.
    Ensures that at least one infographic keyword is included.
    """
    prompt = SCRIPT_PROMPT_TEMPLATE.format(topic=topic)
    result = await invoke_llm_with_prompt(prompt, response_model=VideoScript)

    # --- Handle errors ---
    if isinstance(result, dict) and "error" in result:
        raise ValueError(f"Script generation failed: {result['error']}")

    script = VideoScript(**result)

    # --- Ensure at least one infographic per script ---
    dialogues_with_infographics = [d for d in script.dialogues if d.infographic]

    if len(dialogues_with_infographics) == 0:
        print(f"⚠️ No infographics found; adding fallback keywords for topic '{topic}'")
        keyword = topic.split()[0].capitalize()  # Simple keyword from topic
        # Add infographics to every alternate dialogue
        for i, dlg in enumerate(script.dialogues):
            if i % 2 == 0:
                dlg.infographic = f"{keyword} concept"

    print(f"✅ Generated script for topic '{topic}' with {len(script.dialogues)} lines")
    return script
