# backend/tests/unit/test_generators.py
"""Unit tests for video generators"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.generators.base import (
    BaseVideoGenerator,
    VideoConfig,
    GenerationResult,
    VideoDuration,
    AspectRatio,
    OutputFormat,
    VideoQuality
)
from app.generators.registry import GeneratorRegistry


class TestVideoConfig:
    """Tests for VideoConfig model"""
    
    def test_default_values(self):
        config = VideoConfig()
        assert config.aspect_ratio == AspectRatio.VERTICAL
        assert config.duration == VideoDuration.SHORT
        assert config.output_format == OutputFormat.MP4
        assert config.quality == VideoQuality.FULL_HD
    
    def test_custom_values(self):
        config = VideoConfig(
            aspect_ratio=AspectRatio.HORIZONTAL,
            duration=VideoDuration.LONG,
            output_format=OutputFormat.WEBM,
            quality=VideoQuality.UHD
        )
        assert config.aspect_ratio == AspectRatio.HORIZONTAL
        assert config.duration == VideoDuration.LONG


class TestGeneratorRegistry:
    """Tests for GeneratorRegistry"""
    
    def setup_method(self):
        """Clear registry before each test"""
        GeneratorRegistry.clear()
    
    def test_register_generator(self):
        """Test registering a generator"""
        class MockGenerator(BaseVideoGenerator):
            @property
            def generator_id(self): return "mock_gen"
            @property
            def display_name(self): return "Mock"
            @property
            def description(self): return "Test"
            @property
            def supported_durations(self): return [VideoDuration.SHORT]
            @property
            def config_schema(self): return {}
            async def generate(self, *args, **kwargs): pass
        
        GeneratorRegistry.register(MockGenerator)
        assert GeneratorRegistry.is_registered("mock_gen")
    
    def test_get_generator(self):
        """Test getting a registered generator"""
        class MockGenerator(BaseVideoGenerator):
            @property
            def generator_id(self): return "mock_get"
            @property
            def display_name(self): return "Mock"
            @property
            def description(self): return "Test"
            @property
            def supported_durations(self): return [VideoDuration.SHORT]
            @property
            def config_schema(self): return {}
            async def generate(self, *args, **kwargs): pass
        
        GeneratorRegistry.register(MockGenerator)
        gen = GeneratorRegistry.get("mock_get")
        assert gen.generator_id == "mock_get"
    
    def test_get_nonexistent_generator(self):
        """Test getting a non-existent generator raises error"""
        with pytest.raises(KeyError):
            GeneratorRegistry.get("nonexistent")
    
    def test_list_generators(self):
        """Test listing all generators"""
        class MockGen1(BaseVideoGenerator):
            @property
            def generator_id(self): return "mock1"
            @property
            def display_name(self): return "Mock 1"
            @property
            def description(self): return "Test 1"
            @property
            def supported_durations(self): return [VideoDuration.SHORT]
            @property
            def config_schema(self): return {}
            async def generate(self, *args, **kwargs): pass
        
        class MockGen2(BaseVideoGenerator):
            @property
            def generator_id(self): return "mock2"
            @property
            def display_name(self): return "Mock 2"
            @property
            def description(self): return "Test 2"
            @property
            def supported_durations(self): return [VideoDuration.LONG]
            @property
            def config_schema(self): return {}
            async def generate(self, *args, **kwargs): pass
        
        GeneratorRegistry.register(MockGen1)
        GeneratorRegistry.register(MockGen2)
        
        ids = GeneratorRegistry.list_ids()
        assert "mock1" in ids
        assert "mock2" in ids


class TestGenerationResult:
    """Tests for GenerationResult model"""
    
    def test_creation(self):
        result = GenerationResult(
            output_path="/path/to/video.mp4",
            duration_seconds=60.0,
            file_size_bytes=1024000,
            metadata={"topic": "test"}
        )
        assert result.output_path == "/path/to/video.mp4"
        assert result.duration_seconds == 60.0
        assert result.file_size_bytes == 1024000
        assert result.metadata["topic"] == "test"
