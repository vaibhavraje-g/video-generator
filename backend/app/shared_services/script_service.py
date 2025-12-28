# backend/app/shared_services/script_service.py
"""Generic script generation service using LLM"""

from typing import Type, Optional, Any
from pydantic import BaseModel

from .llm_service.llm_service import invoke_llm_with_prompt


class ScriptService:
    """
    Generic script generation service.
    Uses LLM to generate structured scripts based on customizable prompts.
    """
    
    async def generate_script(
        self,
        topic: str,
        prompt_template: str,
        response_model: Type[BaseModel],
        extra_context: Optional[dict] = None
    ) -> BaseModel:
        """
        Generate a script using LLM.
        
        Args:
            topic: The main topic to generate content about
            prompt_template: Template string with {topic} placeholder
            response_model: Pydantic model for structured response
            extra_context: Additional context to format into template
            
        Returns:
            Parsed response matching the response_model
            
        Raises:
            ValueError: If LLM fails to generate valid response
        """
        # Format the prompt
        format_args = {"topic": topic}
        if extra_context:
            format_args.update(extra_context)
        
        prompt = prompt_template.format(**format_args)
        
        # Call LLM
        result = await invoke_llm_with_prompt(prompt, response_model=response_model)
        
        # Handle errors
        if isinstance(result, dict) and "error" in result:
            raise ValueError(f"Script generation failed: {result['error']}")
        
        # Parse if needed
        if isinstance(result, dict):
            return response_model(**result)
        
        return result


# Singleton instance
script_service = ScriptService()
