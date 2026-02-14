"""
Tests for audio capture module in src/audio_capture.py
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.audio_capture import AudioCapture


class TestAudioCaptureInit:
    """Tests for AudioCapture initialization"""
    
    def test_init_with_default_config(self, sample_config):
        """Test initialization with default configuration"""
        capture = AudioCapture(sample_config)
        
        assert capture.sample_rate == 16000
        assert capture.channels == 1
        assert capture.chunk_duration == 5
        assert capture.is_recording is False
    
    def test_init_with_custom_config(self, sample_config):
        """Test initialization with custom configuration"""
        sample_config['audio']['sample_rate'] = 44100
        sample_config['audio']['channels'] = 2
        
        capture = AudioCapture(sample_config)
        
        assert capture.sample_rate == 44100
        assert capture.channels == 2


class TestAudioCaptureDetectSilence:
    """Tests for silence detection"""
    
    def test_detect_silence_with_silent_audio(self, sample_config, silent_audio_data):
        """Test that silence is correctly detected"""
        capture = AudioCapture(sample_config)
        is_silent = capture.detect_silence(silent_audio_data)
        
        assert is_silent == True  # Use == for NumPy bool compatibility
    
    def test_detect_silence_with_audio(self, sample_config, sample_audio_data):
        """Test that audio is not detected as silence"""
        capture = AudioCapture(sample_config)
        is_silent = capture.detect_silence(sample_audio_data)
        
        assert is_silent == False  # Use == for NumPy bool compatibility
    
    def test_detect_silence_with_custom_threshold(self, sample_config, sample_audio_data):
        """Test silence detection with custom threshold"""
        capture = AudioCapture(sample_config)
        
        # Very high threshold - should detect as silence
        is_silent = capture.detect_silence(sample_audio_data, threshold=10.0)
        assert is_silent == True  # Use == for NumPy bool compatibility
        
        # Very low threshold - should not detect as silence
        is_silent = capture.detect_silence(sample_audio_data, threshold=0.0001)
        assert is_silent == False  # Use == for NumPy bool compatibility


class TestAudioCaptureSaveAudio:
    """Tests for saving audio to file"""
    
    def test_save_audio_creates_file(self, sample_config, sample_audio_data, temp_output_dir):
        """Test that audio is saved to file"""
        import os
        
        capture = AudioCapture(sample_config)
        filepath = os.path.join(temp_output_dir, 'test_audio.wav')
        
        capture.save_audio(sample_audio_data, filepath)
        
        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) > 0
    
    @patch('src.audio_capture.sf.write')
    def test_save_audio_calls_soundfile(self, mock_write, sample_config, sample_audio_data):
        """Test that save_audio calls soundfile.write correctly"""
        capture = AudioCapture(sample_config)
        filepath = 'test.wav'
        
        capture.save_audio(sample_audio_data, filepath)
        
        mock_write.assert_called_once()
        args, kwargs = mock_write.call_args
        assert args[0] == filepath
        assert np.array_equal(args[1], sample_audio_data)
        assert args[2] == 16000  # sample_rate


class TestAudioCaptureRecording:
    """Tests for recording functionality"""
    
    @patch('src.audio_capture.sd.InputStream')
    def test_start_recording_creates_stream(self, mock_stream_class, sample_config):
        """Test that start_recording creates an audio stream"""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        capture = AudioCapture(sample_config)
        capture.start_recording()
        
        assert capture.is_recording is True
        mock_stream.start.assert_called_once()
    
    @patch('src.audio_capture.sd.InputStream')
    def test_stop_recording_stops_stream(self, mock_stream_class, sample_config):
        """Test that stop_recording stops the audio stream"""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        capture = AudioCapture(sample_config)
        capture.start_recording()
        audio_data = capture.stop_recording()
        
        assert capture.is_recording is False
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()
    
    def test_stop_recording_returns_numpy_array(self, sample_config):
        """Test that stop_recording returns a numpy array"""
        capture = AudioCapture(sample_config)
        capture.is_recording = True
        
        # Simulate some recorded frames
        test_frames = [
            np.random.randn(1000, 1).astype(np.float32),
            np.random.randn(1000, 1).astype(np.float32)
        ]
        capture.recorded_frames = test_frames
        
        audio_data = capture.stop_recording()
        
        assert isinstance(audio_data, np.ndarray)
        assert len(audio_data) == 2000  # 1000 + 1000


class TestAudioCaptureDeviceListing:
    """Tests for device listing"""
    
    @patch('src.audio_capture.sd.query_devices')
    @patch('src.audio_capture.sd.default')
    def test_list_devices_displays_info(self, mock_default, mock_query, sample_config, capsys):
        """Test that list_devices displays device information"""
        # Mock device list
        mock_devices = [
            {
                'name': 'Microphone 1',
                'max_input_channels': 2,
                'default_samplerate': 44100
            },
            {
                'name': 'Microphone 2',
                'max_input_channels': 1,
                'default_samplerate': 48000
            }
        ]
        mock_query.return_value = mock_devices
        mock_default.device = [0, 0]  # Default input, Default output
        
        capture = AudioCapture(sample_config)
        capture.list_devices()
        
        captured = capsys.readouterr()
        assert 'Microphone 1' in captured.out
        assert 'Microphone 2' in captured.out
        assert '[DEFAULT]' in captured.out
