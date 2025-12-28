# backend/app/api/v1/routes/generators.py
"""Generator discovery routes"""

from fastapi import APIRouter
from typing import List

from app.generators import GeneratorRegistry, GeneratorInfo

# Import generators to register them
from app.generators.family_guy import FamilyGuyGenerator
from app.generators.frequency import FrequencyGenerator
from app.generators.subliminal import SubliminalGenerator

router = APIRouter(prefix="/generators", tags=["generators"])


@router.get("", response_model=List[dict])
async def list_generators():
    """
    List all available video generators.
    
    Returns:
        List of generator info including id, name, description,
        supported durations, and config schema.
    """
    generators = GeneratorRegistry.list_all()
    return [g.model_dump() for g in generators]


@router.get("/{generator_id}")
async def get_generator(generator_id: str):
    """
    Get details about a specific generator.
    
    Args:
        generator_id: The generator's unique identifier
        
    Returns:
        Generator info including config schema
    """
    generator = GeneratorRegistry.get(generator_id)
    return generator.get_info().model_dump()


@router.get("/{generator_id}/schema")
async def get_generator_schema(generator_id: str):
    """
    Get the configuration schema for a generator.
    
    Args:
        generator_id: The generator's unique identifier
        
    Returns:
        JSON Schema for generator configuration
    """
    generator = GeneratorRegistry.get(generator_id)
    return generator.config_schema
