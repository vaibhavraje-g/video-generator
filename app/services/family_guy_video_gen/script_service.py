from typing import List, Optional
from pydantic import BaseModel
from app.llm_service.llm_service import invoke_llm_with_prompt


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
- Start with a strong HOOK line to grab attention (e.g., Stewie mocking Peter, Peter making a fat joke, Brian sarcastically commenting, or a funny wordplay).
- Script length: 30–60 sec, 3–6 dialogue lines.
- Each line must include `character` and `text`.
- Include **Family Guy character traits**:
    - Peter: silly, naive, sometimes overconfident, loves making absurd analogies.
    - Stewie: sarcastic, cunning, often calls Peter “fat man,” obsessed with word domination and complex vocabulary.
    - Brian: sarcastic, intellectual, sometimes dry humor.
- **MANDATORY:** At least 1–3 dialogue lines MUST include an `infographic` field 
  (short keyword or phrase describing a concept, chart, or diagram to visually support that line).
  Example: {{"character": "Peter Griffin", "text": "AI is everywhere!", "infographic": "AI basics"}}
- Keep it funny, engaging, and informative (TikTok/MrBeast style).
- Reply ONLY with valid JSON. No commentary outside JSON.
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
