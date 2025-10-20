from typing import List, Optional
from pydantic import BaseModel
from app.shared_services.llm_service.llm_service import invoke_llm_with_prompt


# --- Schema ---
class DialogueLine(BaseModel):
    character: str
    text: str
    infographic: Optional[str] = None  # keyword/topic for infographic
    mood_descriptor: Optional[str] = (
        None  # mood/description for character image selection
    )


class VideoScript(BaseModel):
    topic: str
    dialogues: List[DialogueLine]


# --- Prompt Template ---
SCRIPT_PROMPT_TEMPLATE = """
You are a witty, Family Guy–style scriptwriter for short, engaging explainer videos.

Generate a conversational script in strict JSON format for a vertical video
where cartoon characters (like Family Guy) discuss and explain "{topic}".

Requirements:
- Start with a strong HOOK line (funny, sarcastic, or surprising).
- Script length: 50–60 sec, 5–8 dialogue lines.
- Each line must include `character` and `text`.
- Include **Family Guy character traits**:
    - Peter: naive, overconfident, and says silly analogies.
    - Stewie: sarcastic genius, calls Peter “fat man,” uses sharp wit.
    - Brian: dry humor, intellectual tone.
- Use **natural conversational phrasing** for TTS:
    - Prefer commas, ellipses (...), or dashes (—) for pauses.
    - Avoid repeated hyphens or letter stutters like "g-g-g" or "uh--".
    - You can use fillers like “uh...”, “hmm,” “wait—what?” for realism.
- Use only the following characters: Peter, Stewie, Brian.
- Include 1–3 dialogue lines with an `infographic` field 
  (short keyword or phrase for a supporting visual).
  Example: {{"character": "Peter", "text": "AI is everywhere!", "infographic": "AI basics"}}
- Make it sound natural when read aloud — no awkward breaks.
- Reply ONLY with valid JSON, no commentary outside JSON.
"""


# --- Service Function ---
async def generate_script(topic: str) -> VideoScript:
    """
    Generate a vertical video script for a given topic with Family Guy humor,
    ensuring at least one infographic keyword is included.
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
        for i, dlg in enumerate(script.dialogues):
            if i % 2 == 0:
                dlg.infographic = f"{keyword} concept"

    print(f"OK Generated script for topic '{topic}' with {len(script.dialogues)} lines")
    return script
