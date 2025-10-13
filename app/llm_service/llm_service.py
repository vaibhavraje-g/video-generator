import asyncio
import json
import re
from typing import Type, TypeVar, Dict, Any, Optional
from pydantic import BaseModel, ValidationError
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from google.generativeai.types.safety_types import HarmBlockThreshold, HarmCategory
from app.core.config import settings

T = TypeVar("T", bound=BaseModel)


async def invoke_llm_with_prompt(
    prompt: str,
    response_model: Type[T],
    model_name: Optional[str] = None,
    max_retries: Optional[int] = None,
) -> Dict[str, Any]:
    """Invoke Gemini LLM, clean JSON, validate via Pydantic, retry if needed."""

    if not response_model:
        raise ValueError("response_model is required")

    llm = ChatGoogleGenerativeAI(
        model=model_name or settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        generation_config={
            "temperature": settings.TEMPERATURE,
            "max_output_tokens": settings.MAX_OUTPUT_TOKENS,
            "top_p": settings.TOP_P,
            "top_k": settings.TOP_K,
        },
        safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        },  # FIXED: Added this closing brace
    )

    parser = PydanticOutputParser(pydantic_object=response_model)
    prompt_template = PromptTemplate(
        input_variables=["input"],
        template="{input}\n\n{format_instructions}",
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt_template | llm | StrOutputParser()

    def clean_json(text: str) -> str:
        """Remove markdown fences and keep only the first valid JSON object."""
        text = re.sub(r"^``````$", "", text.strip())
        start, end = text.find("{"), text.rfind("}")
        return text[start : end + 1] if start != -1 and end != -1 else text

    retries = max_retries or settings.MAX_LLM_RETRIES

    for attempt in range(retries):
        try:
            ai_response = await chain.ainvoke({"input": prompt})
            cleaned = clean_json(ai_response)

            # 1st try: Pydantic validation
            try:
                return parser.parse(cleaned).model_dump()
            except ValidationError as ve:
                print(f"Validation failed (attempt {attempt + 1}): {ve}")

            # 2nd try: Raw JSON parsing
            try:
                parsed_json = json.loads(cleaned)
                if isinstance(parsed_json, dict):
                    return parsed_json
                else:
                    return {"error": "LLM output was JSON but not a dict"}
            except json.JSONDecodeError as je:
                print(f"JSON parse failed (attempt {attempt + 1}): {je}")

        except Exception as e:
            print(f"Invocation error (attempt {attempt + 1}): {e}")

        if attempt < retries - 1:
            await asyncio.sleep(settings.RETRY_DELAY)

    return {"error": "Max retries reached or validation failed"}
