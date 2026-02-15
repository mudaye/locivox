"""
Tests for streaming transcriber module (Phase 2)
"""

import pytest
import numpy as np
import time
from unittest.mock import Mock, MagicMock, patch
from src.streaming import StreamingTranscriber


@pytest.fixture
def basic_config():
    """Basic streaming configuration"""
    return {
        'audio': {
            'sample_rate': 16000
        },
        'streaming': {
            'chunk_size': 5.0,
            'chunk_overlap': 1.0,
            'vad_enabled': False,  # Disable for testing
            'buffer_size': 10,
            'min_speech_duration': 0.5
        },
        'model': {
            'engine': 'faster-whisper',
            'size': 'tiny',
            'device': 'cpu'
        },
        'vocabulary': {
            'enabled': False
        }
    }


class TestStreamingTranscriber:
    """Tests for StreamingTranscriber"""
    
    @patch('src.streaming.VoiceActivityDetector')
    @patch('src.streaming.TranscriberFactory.create_transcriber')
    def test_init(self, mock_transcriber, mock_vad, basic_config):
        """Test streaming transcriber initialization"""
        transcriber = StreamingTranscriber(basic_config)
        
        assert transcriber.is_running is False
        assert transcriber.buffer is not None
        assert transcriber.transcriber is not None
        assert len(transcriber.transcription_results) == 0
    
    @patch('src.streaming.VoiceActivityDetector')
    @patch('src.streaming.TranscriberFactory.create_transcriber')
    def test_start(self, mock_transcriber, mock_vad, basic_config):
        """Test starting streaming transcription"""
        transcriber = StreamingTranscriber(basic_config)
        
        transcriber.start()
        
        assert transcriber.is_running is True
        assert transcriber.processing_thread is not None
        assert transcriber.processing_thread.daemon is True
        
        # Cleanup
        transcriber.stop()
    
    @patch('src.streaming.VoiceActivityDetector')
    @patch('src.streaming.TranscriberFactory.create_transcriber')
    def test_stop(self, mock_transcriber, mock_vad, basic_config):
        """Test stopping streaming transcription"""
        transcriber = StreamingTranscriber(basic_config)
        
        transcriber.start()
        time.sleep(0.1)  # Let thread start
        transcriber.stop()
        
        assert transcriber.is_running is False
        assert transcriber.stop_event.is_set()
    
    @patch('src.streaming.VoiceActivityDetector')
    @patch('src.streaming.TranscriberFactory.create_transcriber')
    def test_add_audio(self, mock_transcriber, mock_vad, basic_config):
        """Test adding audio data"""
        transcriber = StreamingTranscriber(basic_config)
        transcriber.start()
        
        audio_data = np.random.randn(16000).astype(np.float32)
        
        # Should not raise exception
        transcriber.add_audio(audio_data)
        
        # Cleanup
        transcriber.stop()
    
    @patch('src.streaming.VoiceActivityDetector')
    @patch('src.streaming.TranscriberFactory.create_transcriber')
    def test_add_audio_not_running(self, mock_transcriber, mock_vad, basic_config):
        """Test adding audio when not running"""
        transcriber = StreamingTranscriber(basic_config)
        
        audio_data = np.random.randn(16000).astype(np.float32)
        
        # Should not process (just log warning)
        transcriber.add_audio(audio_data)
        
        # No exception should be raised
    
    @patch('src.streaming.VoiceActivityDetector')
    @patch('src.streaming.TranscriberFactory.create_transcriber')
    def test_get_results(self, mock_transcriber, mock_vad, basic_config):
        """Test getting transcription results"""
        transcriber = StreamingTranscriber(basic_config)
        
        # Add mock result
        transcriber.transcription_results.append({
            'text': 'Test transcription',
            'duration': 5.0,
            'is_final': False,
            'timestamp': time.time()
        })
        
        results = transcriber.get_results()
        
        assert len(results) == 1
        assert results[0]['text'] == 'Test transcription'
    
    @patch('src.streaming.VoiceActivityDetector')
    @patch('src.streaming.TranscriberFactory.create_transcriber')
    def test_get_full_text(self, mock_transcriber, mock_vad, basic_config):
        """Test getting concatenated full text"""
        transcriber = StreamingTranscriber(basic_config)
        
        # Add mock results
        transcriber.transcription_results = [
            {'text': 'First segment', 'duration': 5.0, 'is_final': False, 'timestamp': time.time()},
            {'text': 'Second segment', 'duration': 5.0, 'is_final': False, 'timestamp': time.time()}
        ]
        
        full_text = transcriber.get_full_text()
        
        assert full_text == 'First segment Second segment'
    
    @patch('src.streaming.VoiceActivityDetector')
    @patch('src.streaming.TranscriberFactory.create_transcriber')
    def test_clear_results(self, mock_transcriber, mock_vad, basic_config):
        """Test clearing results"""
        transcriber = StreamingTranscriber(basic_config)
        
        # Add mock result
        transcriber.transcription_results.append({
            'text': 'Test',
            'duration': 5.0,
            'is_final': False,
            'timestamp': time.time()
        })
        
        transcriber.clear_results()
        
        assert len(transcriber.transcription_results) == 0
    
    @patch('src.streaming.VoiceActivityDetector')
    @patch('src.streaming.TranscriberFactory.create_transcriber')
    def test_get_stats(self, mock_transcriber, mock_vad, basic_config):
        """Test getting statistics"""
        transcriber = StreamingTranscriber(basic_config)
        
        # Add mock results
        transcriber.transcription_results = [
            {'text': 'Test one', 'duration': 5.0, 'is_final': False, 'timestamp': time.time()},
            {'text': 'Test two', 'duration': 5.0, 'is_final': False, 'timestamp': time.time()}
        ]
        
        stats = transcriber.get_stats()
        
        assert stats['num_transcriptions'] == 2
        assert stats['total_words'] == 4
        assert stats['total_chars'] > 0
        assert 'buffer_stats' in stats
    
    @patch('src.streaming.VoiceActivityDetector')
    @patch('src.streaming.TranscriberFactory.create_transcriber')
    def test_callback(self, mock_transcriber_factory, mock_vad, basic_config):
        """Test callback functionality"""
        callback_called = []
        
        def test_callback(text, is_final):
            callback_called.append((text, is_final))
        
        # Mock transcriber
        mock_transcriber = MagicMock()
        mock_transcriber.transcribe.return_value = {'text': 'Test transcription'}
        mock_transcriber_factory.create_transcriber.return_value = mock_transcriber
        
        transcriber = StreamingTranscriber(basic_config, callback=test_callback)
        transcriber.start()
        
        # Add enough audio for a chunk
        audio_data = np.random.randn(80000).astype(np.float32)
        transcriber.add_audio(audio_data)
        
        # Give time for processing
        time.sleep(0.5)
        
        transcriber.stop()
        
        # Callback should have been called
        assert len(callback_called) > 0


class TestStreamingTranscriberEdgeCases:
    """Edge case tests for streaming transcriber"""
    
    @patch('src.streaming.VoiceActivityDetector')
    @patch('src.streaming.TranscriberFactory.create_transcriber')
    def test_process_chunk_too_short(self, mock_transcriber, mock_vad, basic_config):
        """Test processing chunk shorter than minimum duration"""
        transcriber = StreamingTranscriber(basic_config)
        
        # Very short audio (less than min_speech_duration)
        short_audio = np.random.randn(1000).astype(np.float32)
        
        # Should not raise exception
        transcriber._process_chunk(short_audio, is_final=False)
    
    @patch('src.streaming.VoiceActivityDetector')
    @patch('src.streaming.TranscriberFactory.create_transcriber')
    def test_empty_transcription(self, mock_transcriber_factory, mock_vad, basic_config):
        """Test handling empty transcription result"""
        mock_transcriber = MagicMock()
        mock_transcriber.transcribe.return_value = {'text': ''}
        mock_transcriber_factory.create_transcriber.return_value = mock_transcriber
        
        transcriber = StreamingTranscriber(basic_config, transcriber_factory=mock_transcriber_factory)
        
        audio_data = np.random.randn(80000).astype(np.float32)
        transcriber._process_chunk(audio_data, is_final=False)
        
        # Should not add empty result
        assert len(transcriber.transcription_results) == 0
    
    @patch('src.streaming.VoiceActivityDetector')
    @patch('src.streaming.TranscriberFactory.create_transcriber')
    def test_stop_not_running(self, mock_transcriber, mock_vad, basic_config):
        """Test stopping when not running"""
        transcriber = StreamingTranscriber(basic_config)
        
        # Should not raise exception
        transcriber.stop()
        
        assert transcriber.is_running is False
    
    @patch('src.streaming.VoiceActivityDetector')
    @patch('src.streaming.TranscriberFactory.create_transcriber')
    def test_double_start(self, mock_transcriber, mock_vad, basic_config):
        """Test starting twice"""
        transcriber = StreamingTranscriber(basic_config)
        
        transcriber.start()
        
        # Starting again should be handled gracefully
        transcriber.start()
        
        assert transcriber.is_running is True
        
        # Cleanup
        transcriber.stop()
