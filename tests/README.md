# Locivox Tests

This directory contains the test suite for Locivox.

## Running Tests

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_utils.py

# Run specific test class
pytest tests/test_audio_capture.py::TestAudioCaptureInit

# Run specific test function
pytest tests/test_utils.py::TestLoadConfig::test_load_valid_config
```

## Test Structure

```
tests/
├── __init__.py              # Package marker
├── conftest.py              # Shared fixtures
├── test_utils.py            # Tests for src/utils.py
├── test_audio_capture.py    # Tests for src/audio_capture.py
├── test_transcriber.py      # Tests for src/transcriber.py
└── README.md                # This file
```

## Test Coverage

View coverage report after running tests with `--cov-report=html`:

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Writing New Tests

### Test File Naming

- Name test files `test_*.py`
- Place in `tests/` directory
- Mirror the structure of `src/`

### Test Function Naming

```python
def test_function_does_something():
    """Test that function_name does X when Y"""
    # Test implementation
```

### Using Fixtures

Fixtures are defined in `conftest.py`:

```python
def test_with_config(sample_config):
    """Use sample_config fixture"""
    assert sample_config['model']['engine'] == 'faster-whisper'

def test_with_audio(sample_audio_data):
    """Use sample_audio_data fixture"""
    assert len(sample_audio_data) > 0
```

### Mocking External Dependencies

```python
from unittest.mock import patch, MagicMock

@patch('src.audio_capture.sd.InputStream')
def test_recording(mock_stream_class):
    """Mock sounddevice InputStream"""
    mock_stream = MagicMock()
    mock_stream_class.return_value = mock_stream
    # Test code
```

## Continuous Integration

Tests run automatically on GitHub Actions for:
- Every push to main branch
- Every pull request
- Python versions: 3.9, 3.10, 3.11, 3.12
- OS: Ubuntu, macOS, Windows

## Test Guidelines

1. **One assertion per test** (when possible)
2. **Use descriptive names** that explain what's being tested
3. **Follow AAA pattern**: Arrange, Act, Assert
4. **Mock external dependencies** (file I/O, network, audio devices)
5. **Test edge cases** (empty input, None values, etc.)
6. **Add docstrings** to explain test purpose

## Example Test

```python
def test_format_timestamp_handles_zero():
    """Test that format_timestamp correctly formats zero seconds"""
    # Arrange
    seconds = 0.0
    
    # Act
    result = format_timestamp(seconds)
    
    # Assert
    assert result == "00:00:00.000"
```

## Debugging Tests

```bash
# Run with debug output
pytest -v -s

# Drop into debugger on failure
pytest --pdb

# Run last failed tests only
pytest --lf

# Run with full traceback
pytest --tb=long
```

## Performance Testing

```bash
# Show slowest tests
pytest --durations=10

# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto
```

## Contributing Tests

When adding new features:
1. Write tests first (TDD)
2. Ensure >80% code coverage
3. Test both success and failure cases
4. Include integration tests for complex features

## Current Coverage

Run `pytest --cov=src` to see current coverage. Target: **>80%**
