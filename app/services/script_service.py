import asyncio
from typing import List, Optional
from pydantic import BaseModel
from app.services.llm_service import invoke_llm_with_prompt

# --- Schema ---
class DialogueLine(BaseModel):
    character: str
    text: str
    infographic: Optional[str] = None  # new: keyword/topic for infographic


class VideoScript(BaseModel):
    topic: str
    dialogues: List[DialogueLine]


# --- Prompt Template ---
SCRIPT_PROMPT_TEMPLATE = """
You are a scriptwriter for short engaging explainer videos.

Generate a conversational script in JSON format for a vertical video
where cartoon characters (like Family Guy characters) discuss and explain "{topic}".

Requirements:
- Script length: 30–60 sec, 3–6 dialogue lines.
- Each line must include `character` and `text`.
- Some lines should include an optional `infographic` field (1–3 times).
  Example: {{"character": "Peter Griffin", "text": "...", "infographic": "AI basics"}}
- Keep it funny + informative (TikTok/MrBeast style).
- Reply ONLY with valid JSON.
"""


# --- Service Function ---
async def generate_script(topic: str) -> VideoScript:
    prompt = SCRIPT_PROMPT_TEMPLATE.format(topic=topic)
    result = await invoke_llm_with_prompt(prompt, response_model=VideoScript)

    if isinstance(result, dict) and "error" in result:
        raise ValueError(f"Script generation failed: {result['error']}")

    script = VideoScript(**result)
    print(f"✅ Generated script for topic '{topic}' with {len(script.dialogues)} lines")
    return script
