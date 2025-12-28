# backend/app/shared_services/affirmation_service.py
"""Affirmation generation service for frequency and subliminal videos"""

from typing import Optional
from pydantic import BaseModel

from .llm_service.llm_service import invoke_llm_with_prompt


class AffirmationList(BaseModel):
    """Response model for affirmation generation"""
    affirmations: list[str]
    theme: str
    category: str


# Prompt templates for different affirmation categories
AFFIRMATION_CATEGORIES = {
    "wealth": "abundance, prosperity, financial freedom, success with money",
    "confidence": "self-confidence, self-esteem, inner strength, courage",
    "health": "physical health, healing, vitality, energy",
    "relationships": "love, connection, harmonious relationships, attracting the right people",
    "success": "career success, achievement, reaching goals, professional growth",
    "custom": ""
}


AFFIRMATION_PROMPT_TEMPLATE = """
You are an expert in positive affirmations and manifestation psychology.

Generate {count} powerful, positive affirmations for the following:
- Theme: {theme}
- Category: {category_description}
- Duration context: {duration_context}

Requirements:
- Each affirmation should be in first person ("I am...", "I have...", "I attract...")
- Keep them short and memorable (5-15 words each)
- Make them present tense and positive (no negations)
- Include a mix of being/having/doing affirmations
- Make them emotionally resonant and believable

For {duration_type} videos:
{duration_instructions}

Return ONLY valid JSON with the structure:
{{
    "affirmations": ["affirmation 1", "affirmation 2", ...],
    "theme": "{theme}",
    "category": "{category}"
}}
"""


class AffirmationService:
    """
    Generate affirmations for frequency and subliminal videos.
    Uses LLM to create contextually appropriate affirmations.
    """
    
    CATEGORIES = AFFIRMATION_CATEGORIES
    
    async def generate_affirmations(
        self,
        theme: str,
        category: str = "custom",
        count: int = 10,
        duration: str = "short"
    ) -> AffirmationList:
        """
        Generate affirmations using LLM.
        
        Args:
            theme: User's custom theme/topic
            category: Predefined category or "custom"
            count: Number of affirmations to generate
            duration: "short" (30-60s) or "long" (~10min)
            
        Returns:
            AffirmationList with generated affirmations
        """
        # Get category description
        category_description = self.CATEGORIES.get(category, theme)
        if category == "custom":
            category_description = theme
        
        # Duration-specific instructions
        if duration == "short":
            duration_context = "30-60 second video"
            duration_instructions = "- Keep affirmations punchy and impactful\n- Focus on core messages"
        else:
            duration_context = "10 minute video"
            duration_instructions = "- Include varied affirmations for sustained engagement\n- Build from simple to more powerful\n- Include some longer, detailed affirmations"
        
        prompt = AFFIRMATION_PROMPT_TEMPLATE.format(
            count=count,
            theme=theme,
            category=category,
            category_description=category_description,
            duration_context=duration_context,
            duration_type=duration,
            duration_instructions=duration_instructions
        )
        
        result = await invoke_llm_with_prompt(prompt, response_model=AffirmationList)
        
        if isinstance(result, dict):
            if "error" in result:
                raise ValueError(f"Affirmation generation failed: {result['error']}")
            return AffirmationList(**result)
        
        return result
    
    async def generate_for_frequency(
        self,
        frequency: int,
        theme: Optional[str] = None,
        count: int = 10
    ) -> AffirmationList:
        """
        Generate affirmations tailored to a specific frequency.
        
        Args:
            frequency: Solfeggio frequency (432, 528, etc.)
            theme: Optional custom theme
            count: Number to generate
        """
        # Map frequencies to themes if not provided
        frequency_themes = {
            432: "deep relaxation and natural harmony",
            528: "healing, transformation, and DNA repair",
            639: "love, connection, and harmonious relationships",
            741: "cleansing, purification, and finding solutions",
            852: "intuition, spiritual awakening, and inner wisdom",
            963: "divine connection and higher consciousness"
        }
        
        effective_theme = theme or frequency_themes.get(frequency, "positive transformation")
        
        return await self.generate_affirmations(
            theme=effective_theme,
            category="custom",
            count=count
        )


# Singleton instance
affirmation_service = AffirmationService()
