"""
Tests for utility functions in src/utils.py
"""

import pytest
import os
from pathlib import Path
from src.utils import (
    load_config,
    generate_output_filename,
    format_timestamp,
    print_banner,
    print_status
)


class TestLoadConfig:
    """Tests for config loading"""
    
    def test_load_valid_config(self, temp_config_file):
        """Test loading a valid config file"""
        config = load_config(temp_config_file)
        
        assert config is not None
        assert 'model' in config
        assert 'audio' in config
        assert config['model']['engine'] == 'faster-whisper'
    
    def test_load_nonexistent_config(self):
        """Test loading a non-existent config file raises error"""
        with pytest.raises(FileNotFoundError):
            load_config('nonexistent_config.yaml')


class TestGenerateOutputFilename:
    """Tests for output filename generation"""
    
    def test_generate_with_timestamp(self, sample_config):
        """Test filename generation with timestamp"""
        filename = generate_output_filename(sample_config)
        
        assert 'transcript_' in filename
        assert filename.endswith('.txt')
        assert os.path.dirname(filename) == './output'
    
    def test_generate_without_timestamp(self, sample_config):
        """Test filename generation without timestamp"""
        sample_config['output']['timestamp'] = False
        filename = generate_output_filename(sample_config)
        
        assert filename == './output/transcript.txt'
    
    def test_generate_with_custom_format(self, sample_config):
        """Test filename generation with custom format"""
        sample_config['output']['format'] = 'json'
        filename = generate_output_filename(sample_config)
        
        assert filename.endswith('.json')
    
    def test_generate_creates_directory(self, sample_config, temp_output_dir):
        """Test that output directory is created if it doesn't exist"""
        sample_config['output']['directory'] = os.path.join(temp_output_dir, 'new_output')
        filename = generate_output_filename(sample_config)
        
        assert os.path.exists(os.path.dirname(filename))


class TestFormatTimestamp:
    """Tests for timestamp formatting"""
    
    def test_format_zero_seconds(self):
        """Test formatting zero seconds"""
        result = format_timestamp(0.0)
        assert result == "00:00:00.000"
    
    def test_format_one_hour(self):
        """Test formatting one hour"""
        result = format_timestamp(3600.0)
        assert result == "01:00:00.000"
    
    def test_format_mixed_time(self):
        """Test formatting mixed hours, minutes, seconds"""
        result = format_timestamp(3661.5)  # 1h 1m 1.5s
        assert result == "01:01:01.500"
    
    def test_format_milliseconds(self):
        """Test formatting with milliseconds"""
        result = format_timestamp(1.234)
        assert result == "00:00:01.234"


class TestPrintFunctions:
    """Tests for print utility functions"""
    
    def test_print_banner_no_error(self, capsys):
        """Test that print_banner executes without error"""
        print_banner()
        captured = capsys.readouterr()
        assert 'LOCIVOX' in captured.out
    
    def test_print_status_info(self, capsys):
        """Test print_status with info level"""
        print_status("Test message", "info")
        captured = capsys.readouterr()
        assert "Test message" in captured.out
        assert "[INFO]" in captured.out.upper()
    
    def test_print_status_success(self, capsys):
        """Test print_status with success level"""
        print_status("Success message", "success")
        captured = capsys.readouterr()
        assert "Success message" in captured.out
        assert "[SUCCESS]" in captured.out.upper()
    
    def test_print_status_error(self, capsys):
        """Test print_status with error level"""
        print_status("Error message", "error")
        captured = capsys.readouterr()
        assert "Error message" in captured.out
        assert "[ERROR]" in captured.out.upper()
