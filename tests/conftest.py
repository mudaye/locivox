"""
Pytest configuration and fixtures for Locivox tests
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import yaml


@pytest.fixture
def sample_config():
    """Provide a sample configuration dictionary for testing"""
    return {
        'model': {
            'engine': 'faster-whisper',
            'size': 'tiny',
            'device': 'cpu',
            'compute_type': 'int8',
            'language': 'en'
        },
        'audio': {
            'sample_rate': 16000,
            'channels': 1,
            'chunk_duration': 5,
            'silence_threshold': 0.01
        },
        'recording': {
            'format': 'wav',
            'auto_stop': False,
            'max_duration': 3600
        },
        'output': {
            'directory': './output',
            'format': 'txt',
            'timestamp': True,
            'include_timestamps': False
        },
        'logging': {
            'level': 'INFO',
            'file': './logs/locivox.log',
            'console': True
        }
    }


@pytest.fixture
def sample_audio_data():
    """Generate sample audio data for testing"""
    # Create 1 second of sine wave at 440Hz (A4 note)
    sample_rate = 16000
    duration = 1.0
    frequency = 440.0
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * frequency * t).astype(np.float32)
    
    return audio


@pytest.fixture
def silent_audio_data():
    """Generate silent audio data for testing"""
    sample_rate = 16000
    duration = 1.0
    return np.zeros(int(sample_rate * duration), dtype=np.float32)


@pytest.fixture
def temp_config_file(sample_config):
    """Create a temporary config file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(sample_config, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_transcription_result():
    """Provide a mock transcription result"""
    return {
        'text': 'This is a test transcription.',
        'segments': [
            {
                'start': 0.0,
                'end': 2.5,
                'text': 'This is a test'
            },
            {
                'start': 2.5,
                'end': 4.0,
                'text': 'transcription.'
            }
        ],
        'language': 'en',
        'language_probability': 0.95
    }
