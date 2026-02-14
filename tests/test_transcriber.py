"""
Tests for transcription module in src/transcriber.py
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.transcriber import (
    TranscriberFactory,
    FasterWhisperTranscriber,
)

# Check if openai-whisper is available
try:
    import whisper
    OPENAI_WHISPER_AVAILABLE = True
except ImportError:
    OPENAI_WHISPER_AVAILABLE = False
    OpenAIWhisperTranscriber = None


class TestTranscriberFactory:
    """Tests for TranscriberFactory"""
    
    def test_create_faster_whisper_transcriber(self, sample_config):
        """Test creating Faster-Whisper transcriber"""
        sample_config['model']['engine'] = 'faster-whisper'
        
        with patch('src.transcriber.FasterWhisperTranscriber.__init__', return_value=None):
            transcriber = TranscriberFactory.create_transcriber(sample_config)
            assert isinstance(transcriber, FasterWhisperTranscriber)
    
    @pytest.mark.skipif(not OPENAI_WHISPER_AVAILABLE, reason="openai-whisper not installed")
    def test_create_openai_whisper_transcriber(self, sample_config):
        """Test creating OpenAI-Whisper transcriber"""
        sample_config['model']['engine'] = 'openai-whisper'
        
        with patch('src.transcriber.OpenAIWhisperTranscriber.__init__', return_value=None):
            transcriber = TranscriberFactory.create_transcriber(sample_config)
            assert isinstance(transcriber, OpenAIWhisperTranscriber)
    
    def test_create_unknown_engine_raises_error(self, sample_config):
        """Test that unknown engine raises ValueError"""
        sample_config['model']['engine'] = 'unknown-engine'
        
        with pytest.raises(ValueError, match="Unknown transcription engine"):
            TranscriberFactory.create_transcriber(sample_config)


class TestFasterWhisperTranscriber:
    """Tests for FasterWhisperTranscriber"""
    
    @patch('faster_whisper.WhisperModel')
    def test_init_loads_model(self, mock_model_class, sample_config):
        """Test that initialization loads the model"""
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        transcriber = FasterWhisperTranscriber(sample_config)
        
        assert transcriber.model is not None
        mock_model_class.assert_called_once_with(
            'tiny',
            device='cpu',
            compute_type='int8'
        )
    
    @patch('faster_whisper.WhisperModel')
    def test_transcribe_returns_dict(self, mock_model_class, sample_config, sample_audio_data):
        """Test that transcribe returns a dictionary with expected keys"""
        mock_model = MagicMock()
        mock_segment = MagicMock()
        mock_segment.start = 0.0
        mock_segment.end = 1.0
        mock_segment.text = "Test transcription"
        
        mock_info = MagicMock()
        mock_info.language = 'en'
        mock_info.language_probability = 0.95
        
        mock_model.transcribe.return_value = ([mock_segment], mock_info)
        mock_model_class.return_value = mock_model
        
        transcriber = FasterWhisperTranscriber(sample_config)
        result = transcriber.transcribe(sample_audio_data)
        
        assert isinstance(result, dict)
        assert 'text' in result
        assert 'segments' in result
        assert 'language' in result
        assert result['text'] == "Test transcription"
    
    @patch('faster_whisper.WhisperModel')
    def test_transcribe_handles_stereo_audio(self, mock_model_class, sample_config):
        """Test that transcribe handles stereo audio by flattening"""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([], MagicMock())
        mock_model_class.return_value = mock_model
        
        # Create stereo audio (2 channels)
        stereo_audio = np.random.randn(1000, 2).astype(np.float32)
        
        transcriber = FasterWhisperTranscriber(sample_config)
        transcriber.transcribe(stereo_audio)
        
        # Check that the audio passed to model is 1D
        call_args = mock_model.transcribe.call_args
        audio_arg = call_args[0][0]
        assert len(audio_arg.shape) == 1
    
    @patch('faster_whisper.WhisperModel')
    def test_transcribe_with_auto_language(self, mock_model_class, sample_config, sample_audio_data):
        """Test transcription with automatic language detection"""
        sample_config['model']['language'] = 'auto'
        
        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([], MagicMock())
        mock_model_class.return_value = mock_model
        
        transcriber = FasterWhisperTranscriber(sample_config)
        transcriber.transcribe(sample_audio_data)
        
        # Verify language=None was passed for auto-detection
        call_args = mock_model.transcribe.call_args
        assert call_args[1]['language'] is None


@pytest.mark.skipif(not OPENAI_WHISPER_AVAILABLE, reason="openai-whisper not installed")
class TestOpenAIWhisperTranscriber:
    """Tests for OpenAIWhisperTranscriber"""
    
    @patch('whisper.load_model')
    def test_init_loads_model(self, mock_load_model, sample_config):
        """Test that initialization loads the model"""
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        transcriber = OpenAIWhisperTranscriber(sample_config)
        
        assert transcriber.model is not None
        mock_load_model.assert_called_once_with('tiny', device='cpu')
    
    @patch('whisper.load_model')
    def test_transcribe_returns_dict(self, mock_load_model, sample_config, sample_audio_data):
        """Test that transcribe returns a dictionary"""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            'text': 'Test transcription',
            'segments': [],
            'language': 'en'
        }
        mock_load_model.return_value = mock_model
        
        transcriber = OpenAIWhisperTranscriber(sample_config)
        result = transcriber.transcribe(sample_audio_data)
        
        assert isinstance(result, dict)
        assert 'text' in result
        assert result['text'] == 'Test transcription'
    
    @patch('whisper.load_model')
    def test_transcribe_converts_audio_dtype(self, mock_load_model, sample_config):
        """Test that transcribe converts audio to float32"""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {'text': '', 'language': 'en'}
        mock_load_model.return_value = mock_model
        
        # Create int16 audio
        audio = np.random.randint(-32768, 32767, 1000, dtype=np.int16)
        
        transcriber = OpenAIWhisperTranscriber(sample_config)
        transcriber.transcribe(audio)
        
        # Check that float32 audio was passed to model
        call_args = mock_model.transcribe.call_args
        audio_arg = call_args[0][0]
        assert audio_arg.dtype == np.float32


class TestTranscriberErrorHandling:
    """Tests for error handling in transcribers"""
    
    @patch('faster_whisper.WhisperModel')
    def test_transcribe_with_unloaded_model_raises_error(self, mock_model_class, sample_config, sample_audio_data):
        """Test that transcribing with unloaded model raises RuntimeError"""
        mock_model_class.return_value = None
        
        transcriber = FasterWhisperTranscriber(sample_config)
        transcriber.model = None
        
        with pytest.raises(RuntimeError, match="Model not loaded"):
            transcriber.transcribe(sample_audio_data)
    
    @patch('faster_whisper.WhisperModel')
    def test_load_model_import_error(self, mock_model_class, sample_config):
        """Test handling of ImportError when model package not installed"""
        mock_model_class.side_effect = ImportError("faster-whisper not installed")
        
        with pytest.raises(ImportError):
            FasterWhisperTranscriber(sample_config)
