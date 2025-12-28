# backend/app/shared_services/__init__.py
"""Shared services package - reusable across all generators"""

from .llm_service.llm_service import invoke_llm_with_prompt

__all__ = [
    "invoke_llm_with_prompt",
]
