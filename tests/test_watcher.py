"""
Tests for folder watcher module (Phase 3)
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import numpy as np
from src.watcher import FolderWatcher


@pytest.fixture
def basic_config():
    """Basic watcher configuration"""
    return {
        'model': {
            'engine': 'faster-whisper',
            'size': 'tiny',
            'device': 'cpu'
        },
        'audio': {
            'sample_rate': 16000
        },
        'output': {
            'directory': './output',
            'format': 'txt'
        },
        'vocabulary': {
            'enabled': False
        }
    }


@pytest.fixture
def temp_watch_dir():
    """Create temporary watch directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestFolderWatcher:
    """Tests for FolderWatcher"""
    
    def test_init(self, basic_config):
        """Test watcher initialization"""
        with patch('src.watcher.load_config', return_value=basic_config):
            watcher = FolderWatcher()
            
            assert watcher.transcriber is None
            assert watcher.is_watching is False
            assert len(watcher.processed_files) == 0
            assert watcher.stats['files_processed'] == 0
    
    def test_scan_directory(self, temp_watch_dir, basic_config):
        """Test scanning directory for audio files"""
        # Create test files
        (temp_watch_dir / "test1.wav").touch()
        (temp_watch_dir / "test2.mp3").touch()
        (temp_watch_dir / "test.txt").touch()  # Non-audio
        
        with patch('src.watcher.load_config', return_value=basic_config):
            watcher = FolderWatcher()
            
            files = watcher._scan_directory(temp_watch_dir, ['.wav', '.mp3'])
            
            assert len(files) == 2
            assert all(f.suffix in ['.wav', '.mp3'] for f in files)
    
    def test_scan_directory_empty(self, temp_watch_dir, basic_config):
        """Test scanning empty directory"""
        with patch('src.watcher.load_config', return_value=basic_config):
            watcher = FolderWatcher()
            
            files = watcher._scan_directory(temp_watch_dir, ['.wav'])
            
            assert len(files) == 0
    
    def test_is_file_ready_exists(self, temp_watch_dir, basic_config):
        """Test checking if file is ready"""
        test_file = temp_watch_dir / "test.wav"
        test_file.write_text("test content")
        
        with patch('src.watcher.load_config', return_value=basic_config):
            watcher = FolderWatcher()
            
            # File should be ready (size stable)
            is_ready = watcher._is_file_ready(test_file)
            
            assert isinstance(is_ready, bool)
    
    def test_is_file_ready_not_exists(self, temp_watch_dir, basic_config):
        """Test checking non-existent file"""
        test_file = temp_watch_dir / "nonexistent.wav"
        
        with patch('src.watcher.load_config', return_value=basic_config):
            watcher = FolderWatcher()
            
            is_ready = watcher._is_file_ready(test_file)
            
            assert is_ready is False
    
    def test_generate_output_path(self, basic_config):
        """Test output path generation"""
        with patch('src.watcher.load_config', return_value=basic_config):
            watcher = FolderWatcher()
            
            input_file = Path('/input/test.wav')
            output_dir = '/output'
            
            output_path = watcher._generate_output_path(input_file, output_dir)
            
            assert output_path.name == 'test.txt'
            assert output_path.parent == Path(output_dir)
    
    @patch('src.watcher.sf.read')
    @patch('src.watcher.TranscriberFactory.create_transcriber')
    def test_process_file(self, mock_transcriber, mock_sf_read, temp_watch_dir, basic_config):
        """Test processing a single file"""
        # Mock audio data
        mock_sf_read.return_value = (np.random.randn(16000).astype(np.float32), 16000)
        
        # Mock transcriber
        mock_trans = MagicMock()
        mock_trans.transcribe.return_value = {'text': 'Test transcription'}
        mock_transcriber.return_value = mock_trans
        
        with patch('src.watcher.load_config', return_value=basic_config):
            watcher = FolderWatcher()
            watcher.transcriber = mock_trans
            
            audio_file = temp_watch_dir / "test.wav"
            audio_file.touch()
            
            watcher._process_file(audio_file, str(temp_watch_dir))
            
            assert watcher.stats['files_processed'] == 1
            
            # Output file should exist
            output_file = temp_watch_dir / "test.txt"
            assert output_file.exists()
    
    @patch('src.watcher.sf.read')
    @patch('src.watcher.TranscriberFactory.create_transcriber')
    def test_process_file_error(self, mock_transcriber, mock_sf_read, temp_watch_dir, basic_config):
        """Test handling file processing error"""
        # Mock to raise exception
        mock_sf_read.side_effect = Exception("File error")
        
        with patch('src.watcher.load_config', return_value=basic_config):
            watcher = FolderWatcher()
            watcher.transcriber = MagicMock()
            
            audio_file = temp_watch_dir / "test.wav"
            audio_file.touch()
            
            # Should not raise exception
            watcher._process_file(audio_file, str(temp_watch_dir))
            
            assert watcher.stats['files_failed'] == 1
    
    def test_stats_initialization(self, basic_config):
        """Test statistics initialization"""
        with patch('src.watcher.load_config', return_value=basic_config):
            watcher = FolderWatcher()
            
            assert watcher.stats['files_processed'] == 0
            assert watcher.stats['files_failed'] == 0
            assert watcher.stats['total_duration'] == 0.0
            assert watcher.stats['started_at'] is None
    
    def test_stop(self, basic_config):
        """Test stopping watcher"""
        with patch('src.watcher.load_config', return_value=basic_config):
            watcher = FolderWatcher()
            watcher.is_watching = True
            
            # Should not raise exception
            watcher.stop()
            
            assert watcher.is_watching is False


class TestFolderWatcherEdgeCases:
    """Edge case tests for folder watcher"""
    
    def test_watch_nonexistent_directory(self, basic_config):
        """Test watching non-existent directory"""
        with patch('src.watcher.load_config', return_value=basic_config):
            watcher = FolderWatcher()
            
            with pytest.raises(FileNotFoundError):
                watcher.watch('/nonexistent/directory')
    
    @patch('src.watcher.sf.read')
    @patch('src.watcher.TranscriberFactory.create_transcriber')
    def test_process_file_with_resampling(self, mock_transcriber, mock_sf_read, basic_config):
        """Test processing file that needs resampling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock audio at different sample rate
            mock_sf_read.return_value = (np.random.randn(44100).astype(np.float32), 44100)
            
            mock_trans = MagicMock()
            mock_trans.transcribe.return_value = {'text': 'Test'}
            mock_transcriber.return_value = mock_trans
            
            with patch('src.watcher.load_config', return_value=basic_config):
                with patch('librosa.resample') as mock_resample:
                    mock_resample.return_value = np.random.randn(16000).astype(np.float32)
                    
                    watcher = FolderWatcher()
                    watcher.transcriber = mock_trans
                    
                    audio_file = Path(temp_dir) / "test.wav"
                    audio_file.touch()
                    
                    watcher._process_file(audio_file, temp_dir)
                    
                    # Resample should be called
                    mock_resample.assert_called_once()
    
    @patch('src.watcher.sf.read')
    @patch('src.watcher.TranscriberFactory.create_transcriber')
    def test_process_file_stereo_to_mono(self, mock_transcriber, mock_sf_read, basic_config):
        """Test processing stereo audio"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Stereo audio
            mock_sf_read.return_value = (np.random.randn(16000, 2).astype(np.float32), 16000)
            
            mock_trans = MagicMock()
            mock_trans.transcribe.return_value = {'text': 'Test'}
            mock_transcriber.return_value = mock_trans
            
            with patch('src.watcher.load_config', return_value=basic_config):
                watcher = FolderWatcher()
                watcher.transcriber = mock_trans
                
                audio_file = Path(temp_dir) / "test.wav"
                audio_file.touch()
                
                watcher._process_file(audio_file, temp_dir)
                
                # Should process successfully
                assert watcher.stats['files_processed'] == 1
    
    def test_empty_audio_file(self, basic_config):
        """Test handling empty audio file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.watcher.load_config', return_value=basic_config):
                watcher = FolderWatcher()
                
                empty_file = Path(temp_dir) / "empty.wav"
                empty_file.touch()
                
                # is_file_ready should handle empty file
                is_ready = watcher._is_file_ready(empty_file)
                
                # Empty files have size 0, should return False
                assert is_ready is False
