# backend/app/generators/family_guy/prompts.py
"""Prompt templates for Family Guy script generation"""

from typing import List, Optional
from pydantic import BaseModel


class DialogueLine(BaseModel):
    """Single dialogue line in the script"""
    character: str
    text: str
    infographic: Optional[str] = None
    mood_descriptor: Optional[str] = None


class VideoScript(BaseModel):
    """Complete video script"""
    topic: str
    dialogues: List[DialogueLine]


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
    - Stewie: sarcastic genius, calls Peter "fat man," uses sharp wit.
    - Brian: dry humor, intellectual tone.
- Use **natural conversational phrasing** for TTS:
    - Prefer commas, ellipses (...), or dashes (—) for pauses.
    - Avoid repeated hyphens or letter stutters like "g-g-g" or "uh--".
    - You can use fillers like "uh...", "hmm," "wait—what?" for realism.
- Use only the following characters: Peter, Stewie, Brian.
- Include 1–3 dialogue lines with an `infographic` field 
  (short keyword or phrase for a supporting visual).
  Example: {{"character": "Peter", "text": "AI is everywhere!", "infographic": "AI basics"}}
- Make it sound natural when read aloud — no awkward breaks.
- Reply ONLY with valid JSON, no commentary outside JSON.

Return format:
{{
    "topic": "{topic}",
    "dialogues": [
        {{"character": "Peter", "text": "...", "infographic": "optional keyword"}},
        ...
    ]
}}
"""


LONG_SCRIPT_PROMPT_TEMPLATE = """
You are a witty, Family Guy–style scriptwriter for educational explainer videos.

Generate a longer conversational script in strict JSON format for a video
where cartoon characters discuss and explain "{topic}" in depth.

Requirements:
- Script length: 2-3 minutes, 15-20 dialogue lines.
- Start with a hook and build up the explanation gradually.
- Each line must include `character` and `text`.
- Include **Family Guy character traits**:
    - Peter: naive, overconfident, and says silly analogies.
    - Stewie: sarcastic genius, calls Peter "fat man," uses sharp wit.
    - Brian: dry humor, intellectual tone.
- Include 4-6 dialogue lines with an `infographic` field.
- Make it educational but entertaining.
- Reply ONLY with valid JSON.

Return format:
{{
    "topic": "{topic}",
    "dialogues": [
        {{"character": "Peter", "text": "...", "infographic": "optional keyword"}},
        ...
    ]
}}
"""
