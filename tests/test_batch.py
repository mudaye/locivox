"""
Tests for batch processing module (Phase 3)
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from src.batch import BatchProcessor


@pytest.fixture
def basic_config():
    """Basic batch processor configuration"""
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
def temp_audio_dir():
    """Create temporary directory with audio files"""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    
    # Create dummy audio files
    for i in range(3):
        audio_file = temp_path / f"test_{i}.wav"
        audio_file.touch()
    
    yield temp_path
    
    # Cleanup
    for file in temp_path.glob("*"):
        file.unlink()
    temp_path.rmdir()


class TestBatchProcessor:
    """Tests for BatchProcessor"""
    
    def test_init(self, basic_config):
        """Create temporary directory with audio files"""
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)
        
        # Create dummy audio files
        for i in range(3):
            audio_file = temp_path / f"test_{i}.wav"
            audio_file.touch()
        
        yield temp_path
        
        # Cleanup
        for file in temp_path.glob("*"):
            file.unlink()
        temp_path.rmdir()
    
    def test_init(self, basic_config):
        """Test batch processor initialization"""
        with patch('src.batch.load_config', return_value=basic_config):
            processor = BatchProcessor()
            
            assert processor.transcriber is None
            assert processor.stats['total_files'] == 0
            assert processor.stats['successful'] == 0
    
    def test_find_audio_files(self, temp_audio_dir):
        """Test finding audio files in directory"""
        config = {
            'model': {'engine': 'faster-whisper', 'size': 'tiny', 'device': 'cpu'},
            'audio': {'sample_rate': 16000},
            'output': {'directory': './output', 'format': 'txt'},
            'vocabulary': {'enabled': False}
        }
        
        with patch('src.batch.load_config', return_value=config):
            processor = BatchProcessor()
            
            files = processor._find_audio_files(
                temp_audio_dir,
                ['.wav'],
                recursive=False
            )
            
            assert len(files) == 3
            assert all(f.suffix == '.wav' for f in files)
    
    def test_find_audio_files_empty_directory(self):
        """Test finding files in empty directory"""
        config = {
            'model': {'engine': 'faster-whisper', 'size': 'tiny', 'device': 'cpu'},
            'audio': {'sample_rate': 16000},
            'output': {'directory': './output', 'format': 'txt'},
            'vocabulary': {'enabled': False}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.batch.load_config', return_value=config):
                processor = BatchProcessor()
                
                files = processor._find_audio_files(
                    Path(temp_dir),
                    ['.wav'],
                    recursive=False
                )
                
                assert len(files) == 0
    
    def test_find_audio_files_multiple_extensions(self, temp_audio_dir):
        """Test finding multiple file types"""
        # Add mp3 file
        mp3_file = temp_audio_dir / "test.mp3"
        mp3_file.touch()
        
        config = {
            'model': {'engine': 'faster-whisper', 'size': 'tiny', 'device': 'cpu'},
            'audio': {'sample_rate': 16000},
            'output': {'directory': './output', 'format': 'txt'},
            'vocabulary': {'enabled': False}
        }
        
        with patch('src.batch.load_config', return_value=config):
            processor = BatchProcessor()
            
            files = processor._find_audio_files(
                temp_audio_dir,
                ['.wav', '.mp3'],
                recursive=False
            )
            
            assert len(files) == 4
    
    def test_generate_output_path(self, basic_config):
        """Test output path generation"""
        with patch('src.batch.load_config', return_value=basic_config):
            processor = BatchProcessor()
            
            input_file = Path('/input/test.wav')
            output_dir = '/output'
            
            output_path = processor._generate_output_path(input_file, output_dir)
            
            assert output_path.name == 'test.txt'
            assert output_path.parent == Path(output_dir)
    
    def test_generate_output_path_different_formats(self, basic_config):
        """Test output path with different formats"""
        formats = ['txt', 'json', 'srt']
        
        for fmt in formats:
            basic_config['output']['format'] = fmt
            
            with patch('src.batch.load_config', return_value=basic_config):
                processor = BatchProcessor()
                
                input_file = Path('/input/test.wav')
                output_path = processor._generate_output_path(input_file, '/output')
                
                assert output_path.suffix == f'.{fmt}'
    
    def test_save_txt(self, basic_config):
        """Test saving text output"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.batch.load_config', return_value=basic_config):
                processor = BatchProcessor()
                
                text = "This is a test transcription"
                output_file = Path(temp_dir) / "test.txt"
                
                processor._save_txt(text, output_file)
                
                assert output_file.exists()
                content = output_file.read_text()
                assert text in content
    
    def test_save_json(self, basic_config):
        """Test saving JSON output"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.batch.load_config', return_value=basic_config):
                processor = BatchProcessor()
                
                result = {
                    'text': 'Test transcription',
                    'language': 'en'
                }
                output_file = Path(temp_dir) / "test.json"
                
                processor._save_json(result, output_file)
                
                assert output_file.exists()
                with open(output_file) as f:
                    data = json.load(f)
                assert data['text'] == 'Test transcription'
    
    def test_save_srt(self, basic_config):
        """Test saving SRT subtitle output"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.batch.load_config', return_value=basic_config):
                processor = BatchProcessor()
                
                result = {
                    'segments': [
                        {'start': 0.0, 'end': 2.0, 'text': 'First segment'},
                        {'start': 2.0, 'end': 4.0, 'text': 'Second segment'}
                    ]
                }
                output_file = Path(temp_dir) / "test.srt"
                
                processor._save_srt(result, output_file)
                
                assert output_file.exists()
                content = output_file.read_text()
                assert 'First segment' in content
                assert 'Second segment' in content
                assert '00:00:00,000 --> 00:00:02,000' in content
    
    def test_format_srt_time(self, basic_config):
        """Test SRT timestamp formatting"""
        with patch('src.batch.load_config', return_value=basic_config):
            processor = BatchProcessor()
            
            # Test various timestamps
            assert processor._format_srt_time(0.0) == "00:00:00,000"
            assert processor._format_srt_time(65.5) == "00:01:05,500"
            assert processor._format_srt_time(3661.123) == "01:01:01,123"
    
    def test_stats_initialization(self, basic_config):
        """Test statistics initialization"""
        with patch('src.batch.load_config', return_value=basic_config):
            processor = BatchProcessor()
            
            assert processor.stats['total_files'] == 0
            assert processor.stats['successful'] == 0
            assert processor.stats['failed'] == 0
            assert processor.stats['skipped'] == 0
            assert processor.stats['total_duration'] == 0.0
            assert processor.stats['total_words'] == 0
            assert isinstance(processor.stats['errors'], list)
    
    @patch('src.batch.sf.read')
    @patch('src.batch.TranscriberFactory.create_transcriber')
    def test_process_file_success(self, mock_transcriber, mock_sf_read, basic_config):
        """Test successful file processing"""
        # Mock audio data
        mock_sf_read.return_value = (np.random.randn(16000).astype(np.float32), 16000)
        
        # Mock transcriber
        mock_trans = MagicMock()
        mock_trans.transcribe.return_value = {'text': 'Test transcription'}
        mock_transcriber.return_value = mock_trans
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.batch.load_config', return_value=basic_config):
                processor = BatchProcessor()
                processor.transcriber = mock_trans
                
                audio_file = Path(temp_dir) / "test.wav"
                audio_file.touch()
                
                processor._process_file(audio_file, temp_dir, overwrite=True)
                
                assert processor.stats['successful'] == 1
    
    @patch('src.batch.sf.read')
    def test_process_file_skip_existing(self, mock_sf_read, basic_config):
        """Test skipping existing transcriptions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.batch.load_config', return_value=basic_config):
                processor = BatchProcessor()
                
                # Create existing output file
                audio_file = Path(temp_dir) / "test.wav"
                audio_file.touch()
                output_file = Path(temp_dir) / "test.txt"
                output_file.write_text("Existing transcription")
                
                processor._process_file(audio_file, temp_dir, overwrite=False)
                
                assert processor.stats['skipped'] == 1
                # sf.read should not be called
                mock_sf_read.assert_not_called()
    
    def test_save_report(self, basic_config):
        """Test saving processing report"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.batch.load_config', return_value=basic_config):
                processor = BatchProcessor()
                processor.stats['total_files'] = 5
                processor.stats['successful'] = 4
                processor.stats['failed'] = 1
                
                report_file = Path(temp_dir) / "report.json"
                processor.save_report(str(report_file))
                
                assert report_file.exists()
                
                with open(report_file) as f:
                    report = json.load(f)
                
                assert report['statistics']['total_files'] == 5
                assert report['statistics']['successful'] == 4
                assert 'timestamp' in report
                assert 'config' in report


class TestBatchProcessorEdgeCases:
    """Edge case tests for batch processor"""
    
    def test_process_directory_not_found(self, basic_config):
        """Test processing non-existent directory"""
        with patch('src.batch.load_config', return_value=basic_config):
            processor = BatchProcessor()
            
            with pytest.raises(FileNotFoundError):
                processor.process_directory('/nonexistent/directory')
    
    @patch('src.batch.sf.read')
    @patch('src.batch.TranscriberFactory.create_transcriber')
    def test_process_file_with_resampling(self, mock_transcriber, mock_sf_read, basic_config):
        """Test processing file that needs resampling"""
        # Mock audio at different sample rate
        mock_sf_read.return_value = (np.random.randn(44100).astype(np.float32), 44100)
        
        mock_trans = MagicMock()
        mock_trans.transcribe.return_value = {'text': 'Test'}
        mock_transcriber.return_value = mock_trans
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.batch.load_config', return_value=basic_config):
                with patch('librosa.resample') as mock_resample:
                    mock_resample.return_value = np.random.randn(16000).astype(np.float32)
                    
                    processor = BatchProcessor()
                    processor.transcriber = mock_trans
                    
                    audio_file = Path(temp_dir) / "test.wav"
                    audio_file.touch()
                    
                    processor._process_file(audio_file, temp_dir, overwrite=True)
                    
                    # Resample should be called
                    mock_resample.assert_called_once()
    
    @patch('src.batch.sf.read')
    @patch('src.batch.TranscriberFactory.create_transcriber')
    def test_process_file_stereo_to_mono(self, mock_transcriber, mock_sf_read, basic_config):
        """Test processing stereo audio"""
        # Stereo audio
        mock_sf_read.return_value = (np.random.randn(16000, 2).astype(np.float32), 16000)
        
        mock_trans = MagicMock()
        mock_trans.transcribe.return_value = {'text': 'Test'}
        mock_transcriber.return_value = mock_trans
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.batch.load_config', return_value=basic_config):
                processor = BatchProcessor()
                processor.transcriber = mock_trans
                
                audio_file = Path(temp_dir) / "test.wav"
                audio_file.touch()
                
                processor._process_file(audio_file, temp_dir, overwrite=True)
                
                # Should process successfully
                assert processor.stats['successful'] == 1
