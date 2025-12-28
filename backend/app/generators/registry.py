# backend/app/generators/registry.py
"""Generator registry for dynamic video type management"""

from typing import Dict, Type, Optional
from .base import BaseVideoGenerator, GeneratorInfo


class GeneratorRegistry:
    """
    Central registry for all video generators.
    
    Usage:
        # Register a generator
        @GeneratorRegistry.register
        class MyGenerator(BaseVideoGenerator):
            ...
        
        # Or manually
        GeneratorRegistry.register_class(MyGenerator)
        
        # Get a generator instance
        generator = GeneratorRegistry.get("my_generator_id")
        
        # List all available generators
        generators = GeneratorRegistry.list_all()
    """
    
    _generators: Dict[str, Type[BaseVideoGenerator]] = {}
    _instances: Dict[str, BaseVideoGenerator] = {}
    
    @classmethod
    def register(cls, generator_class: Type[BaseVideoGenerator]) -> Type[BaseVideoGenerator]:
        """
        Decorator to register a generator class.
        
        @GeneratorRegistry.register
        class MyGenerator(BaseVideoGenerator):
            generator_id = "my_generator"
            ...
        """
        # Create temporary instance to get the id
        temp_instance = generator_class()
        generator_id = temp_instance.generator_id
        
        if generator_id in cls._generators:
            raise ValueError(f"Generator '{generator_id}' is already registered")
        
        cls._generators[generator_id] = generator_class
        print(f"✅ Registered generator: {generator_id}")
        return generator_class
    
    @classmethod
    def register_class(cls, generator_class: Type[BaseVideoGenerator]) -> None:
        """Register a generator class manually"""
        cls.register(generator_class)
    
    @classmethod
    def get(cls, generator_id: str) -> BaseVideoGenerator:
        """
        Get a generator instance by ID.
        Instances are cached for reuse.
        
        Args:
            generator_id: The generator's unique identifier
            
        Returns:
            Generator instance
            
        Raises:
            KeyError: If generator not found
        """
        if generator_id not in cls._generators:
            available = list(cls._generators.keys())
            raise KeyError(
                f"Generator '{generator_id}' not found. "
                f"Available: {available}"
            )
        
        if generator_id not in cls._instances:
            cls._instances[generator_id] = cls._generators[generator_id]()
        
        return cls._instances[generator_id]
    
    @classmethod
    def get_optional(cls, generator_id: str) -> Optional[BaseVideoGenerator]:
        """Get a generator, returning None if not found"""
        try:
            return cls.get(generator_id)
        except KeyError:
            return None
    
    @classmethod
    def list_all(cls) -> list[GeneratorInfo]:
        """List all registered generators with their info"""
        infos = []
        for generator_id in cls._generators:
            generator = cls.get(generator_id)
            infos.append(generator.get_info())
        return infos
    
    @classmethod
    def list_ids(cls) -> list[str]:
        """List all registered generator IDs"""
        return list(cls._generators.keys())
    
    @classmethod
    def is_registered(cls, generator_id: str) -> bool:
        """Check if a generator is registered"""
        return generator_id in cls._generators
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registrations (mainly for testing)"""
        cls._generators.clear()
        cls._instances.clear()
