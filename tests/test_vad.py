"""
Tests for Voice Activity Detection module (Phase 2)
"""

import pytest
import numpy as np
import torch
from unittest.mock import Mock, MagicMock, patch
from src.vad import VoiceActivityDetector


class TestVoiceActivityDetector:
    """Tests for VoiceActivityDetector"""
    
    @pytest.fixture
    def basic_config(self):
        """Basic VAD configuration"""
        return {
            'audio': {
                'sample_rate': 16000
            },
            'streaming': {
                'vad_threshold': 0.5
            }
        }
    
    @pytest.fixture
    def vad_with_mock_model(self, basic_config):
        """Create VAD with mocked model"""
        with patch('torch.hub.load') as mock_load:
            # Mock model and utilities
            mock_model = MagicMock()
            mock_utils = (
                MagicMock(),  # get_speech_timestamps
                MagicMock(),  # save_audio
                MagicMock(),  # read_audio
                MagicMock(),  # VADIterator
                MagicMock(),  # collect_chunks
            )
            mock_load.return_value = (mock_model, mock_utils)
            
            vad = VoiceActivityDetector(basic_config)
            vad.model = mock_model
            vad.get_speech_timestamps = mock_utils[0]
            
            return vad
    
    def test_init(self, basic_config):
        """Test VAD initialization"""
        with patch('torch.hub.load'):
            vad = VoiceActivityDetector(basic_config)
            
            assert vad.threshold == 0.5
            assert vad.sample_rate == 16000
    
    def test_init_custom_threshold(self):
        """Test initialization with custom threshold"""
        config = {
            'audio': {'sample_rate': 16000},
            'streaming': {'vad_threshold': 0.7}
        }
        
        with patch('torch.hub.load'):
            vad = VoiceActivityDetector(config)
            assert vad.threshold == 0.7
    
    @patch('torch.hub.load')
    def test_load_model_success(self, mock_load, basic_config):
        """Test successful model loading"""
        mock_model = MagicMock()
        mock_utils = (MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock())
        mock_load.return_value = (mock_model, mock_utils)
        
        vad = VoiceActivityDetector(basic_config)
        
        assert vad.model is not None
        mock_load.assert_called_once()
    
    @patch('torch.hub.load')
    def test_load_model_failure(self, mock_load, basic_config):
        """Test model loading failure"""
        mock_load.side_effect = Exception("Model load failed")
        
        vad = VoiceActivityDetector(basic_config)
        
        # Should handle gracefully and set model to None
        assert vad.model is None
    
    def test_is_speech_model_disabled(self, basic_config):
        """Test is_speech when model is None"""
        with patch('torch.hub.load'):
            vad = VoiceActivityDetector(basic_config)
            vad.model = None
            
            audio = np.random.randn(16000).astype(np.float32)
            result = vad.is_speech(audio)
            
            # Should assume speech when model disabled
            assert result is True
    
    def test_is_speech_with_speech(self, vad_with_mock_model):
        """Test is_speech detects speech"""
        # Mock get_speech_timestamps to return speech segments
        vad_with_mock_model.get_speech_timestamps.return_value = [
            {'start': 0, 'end': 16000}
        ]
        
        audio = np.random.randn(16000).astype(np.float32)
        result = vad_with_mock_model.is_speech(audio)
        
        assert result is True
    
    def test_is_speech_without_speech(self, vad_with_mock_model):
        """Test is_speech detects silence"""
        # Mock to return no speech segments
        vad_with_mock_model.get_speech_timestamps.return_value = []
        
        audio = np.random.randn(16000).astype(np.float32)
        result = vad_with_mock_model.is_speech(audio)
        
        assert result is False
    
    def test_is_speech_converts_dtype(self, vad_with_mock_model):
        """Test that is_speech converts audio dtype"""
        vad_with_mock_model.get_speech_timestamps.return_value = [
            {'start': 0, 'end': 16000}
        ]
        
        # Int16 audio
        audio = np.random.randint(-32768, 32767, size=16000).astype(np.int16)
        result = vad_with_mock_model.is_speech(audio)
        
        # Should work despite wrong dtype
        assert isinstance(result, bool)
    
    def test_is_speech_flattens_stereo(self, vad_with_mock_model):
        """Test that is_speech handles stereo audio"""
        vad_with_mock_model.get_speech_timestamps.return_value = [
            {'start': 0, 'end': 16000}
        ]
        
        # Stereo audio
        audio = np.random.randn(16000, 2).astype(np.float32)
        result = vad_with_mock_model.is_speech(audio)
        
        # Should work despite stereo input
        assert isinstance(result, bool)
    
    def test_is_speech_error_handling(self, vad_with_mock_model):
        """Test error handling in is_speech"""
        # Mock to raise exception
        vad_with_mock_model.get_speech_timestamps.side_effect = Exception("VAD error")
        
        audio = np.random.randn(16000).astype(np.float32)
        result = vad_with_mock_model.is_speech(audio)
        
        # Should assume speech on error to avoid dropping audio
        assert result is True
    
    def test_get_speech_segments_with_speech(self, vad_with_mock_model):
        """Test getting speech segments"""
        # Mock segments
        mock_segments = [
            {'start': 0.0, 'end': 2.5},
            {'start': 3.0, 'end': 5.0}
        ]
        vad_with_mock_model.get_speech_timestamps.return_value = mock_segments
        
        audio = np.random.randn(80000).astype(np.float32)
        segments = vad_with_mock_model.get_speech_segments(audio)
        
        assert len(segments) == 2
        assert segments[0]['start'] == 0.0
        assert segments[0]['end'] == 2.5
    
    def test_get_speech_segments_no_model(self, basic_config):
        """Test get_speech_segments with no model"""
        with patch('torch.hub.load'):
            vad = VoiceActivityDetector(basic_config)
            vad.model = None
            
            audio = np.random.randn(16000).astype(np.float32)
            segments = vad.get_speech_segments(audio)
            
            # Should return entire audio as one segment
            assert len(segments) == 1
            assert segments[0]['start'] == 0.0
    
    def test_get_speech_segments_error_handling(self, vad_with_mock_model):
        """Test error handling in get_speech_segments"""
        vad_with_mock_model.get_speech_timestamps.side_effect = Exception("Error")
        
        audio = np.random.randn(16000).astype(np.float32)
        segments = vad_with_mock_model.get_speech_segments(audio)
        
        # Should return full audio as segment on error
        assert len(segments) == 1
    
    def test_filter_silence_with_speech(self, vad_with_mock_model):
        """Test filtering silence from audio"""
        # Mock segments (in seconds)
        mock_segments = [
            {'start': 1.0, 'end': 2.0},
            {'start': 3.0, 'end': 4.0}
        ]
        
        with patch.object(vad_with_mock_model, 'get_speech_segments', return_value=mock_segments):
            audio = np.random.randn(80000).astype(np.float32)
            filtered = vad_with_mock_model.filter_silence(audio)
            
            # Should have removed silence
            assert len(filtered) < len(audio)
            assert filtered.dtype == audio.dtype
    
    def test_filter_silence_no_speech(self, vad_with_mock_model):
        """Test filtering when no speech detected"""
        with patch.object(vad_with_mock_model, 'get_speech_segments', return_value=[]):
            audio = np.random.randn(16000).astype(np.float32)
            filtered = vad_with_mock_model.filter_silence(audio)
            
            # Should return empty array
            assert len(filtered) == 0


class TestVADEdgeCases:
    """Edge case tests for VAD"""
    
    @pytest.fixture
    def vad_with_mock(self):
        """Create VAD with mocked model"""
        config = {
            'audio': {'sample_rate': 16000},
            'streaming': {'vad_threshold': 0.5}
        }
        
        with patch('torch.hub.load') as mock_load:
            mock_model = MagicMock()
            mock_utils = (MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock())
            mock_load.return_value = (mock_model, mock_utils)
            
            vad = VoiceActivityDetector(config)
            vad.get_speech_timestamps = mock_utils[0]
            return vad
    
    def test_empty_audio(self, vad_with_mock):
        """Test with empty audio array"""
        vad_with_mock.get_speech_timestamps.return_value = []
        
        audio = np.array([], dtype=np.float32)
        result = vad_with_mock.is_speech(audio)
        
        # Should handle gracefully
        assert isinstance(result, bool)
    
    def test_very_short_audio(self, vad_with_mock):
        """Test with very short audio"""
        vad_with_mock.get_speech_timestamps.return_value = []
        
        audio = np.random.randn(100).astype(np.float32)
        result = vad_with_mock.is_speech(audio)
        
        assert isinstance(result, bool)
    
    def test_very_long_audio(self, vad_with_mock):
        """Test with very long audio"""
        vad_with_mock.get_speech_timestamps.return_value = [
            {'start': 0, 'end': 160000}
        ]
        
        # 10 seconds
        audio = np.random.randn(160000).astype(np.float32)
        result = vad_with_mock.is_speech(audio)
        
        assert result is True
    
    def test_different_thresholds(self):
        """Test different VAD thresholds"""
        for threshold in [0.3, 0.5, 0.7, 0.9]:
            config = {
                'audio': {'sample_rate': 16000},
                'streaming': {'vad_threshold': threshold}
            }
            
            with patch('torch.hub.load'):
                vad = VoiceActivityDetector(config)
                assert vad.threshold == threshold
