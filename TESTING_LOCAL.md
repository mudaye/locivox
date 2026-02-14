# Running Tests Locally on Windows

This guide helps you run the full test suite on your Windows machine before pushing to GitHub.

## Prerequisites

1. **Virtual environment activated**
   ```cmd
   venv\Scripts\activate
   ```

2. **All dependencies installed**
   ```cmd
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

## Quick Test Run

```cmd
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html
```

## Step-by-Step Testing

### 1. Install PyTorch (CPU version)

```cmd
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 2. Install Test Dependencies

```cmd
pip install pytest pytest-cov pytest-mock
```

### 3. Verify Imports

```cmd
python -c "from src import utils, audio_capture, transcriber; print('✓ All modules import successfully')"
```

### 4. Run Specific Test Files

```cmd
# Test utilities
pytest tests/test_utils.py -v

# Test audio capture
pytest tests/test_audio_capture.py -v

# Test transcriber
pytest tests/test_transcriber.py -v
```

### 5. Run All Tests with Coverage

```cmd
pytest tests/ -v --cov=src --cov-report=html --cov-report=term
```

Coverage report will be in `htmlcov/index.html`

## Common Issues on Windows

### Issue: "No module named 'pkg_resources'"

**Fix:**
```cmd
pip install --upgrade setuptools
```

### Issue: "Could not find a version that satisfies torch"

**Fix:**
```cmd
# Use CPU index explicitly
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Issue: Import errors for sounddevice

**Fix:**
```cmd
pip install sounddevice --force-reinstall
```

### Issue: Tests fail with "model not found"

This is expected - tests use mocks and don't actually download models.

If you see errors about missing models, the tests are working correctly (they mock the model loading).

## Test Output Interpretation

### ✅ Success Example:
```
tests/test_utils.py::TestLoadConfig::test_load_valid_config PASSED
tests/test_audio_capture.py::TestAudioCaptureInit::test_init_with_default_config PASSED
...
==================== 39 passed in 2.34s ====================
```

### ❌ Failure Example:
```
tests/test_utils.py::TestLoadConfig::test_load_valid_config FAILED
...
FAILED tests/test_utils.py::TestLoadConfig::test_load_valid_config - AssertionError
```

## Pre-Push Checklist

Before pushing to GitHub, ensure:

- [ ] All tests pass locally: `pytest`
- [ ] No linting errors: `flake8 src/`
- [ ] Code is formatted: `black src/`
- [ ] Type checking passes: `mypy src/` (optional)
- [ ] Imports work: `python -c "from src import utils"`

## Quick Pre-Push Command

```cmd
# Run everything at once
pytest && flake8 src/ --max-line-length=100 && echo "✓ All checks passed!"
```

## CI vs Local Tests

**CI tests (GitHub Actions):**
- Run on Linux (primarily)
- Test Python 3.9, 3.10, 3.11, 3.12
- One Windows test (Python 3.11)
- One macOS test (Python 3.11)

**Local tests (your machine):**
- Windows-specific
- Your Python version only
- Faster iteration
- More detailed error messages

## Debugging Failed Tests

### 1. Run single failing test
```cmd
pytest tests/test_utils.py::TestLoadConfig::test_load_valid_config -v
```

### 2. Show print statements
```cmd
pytest -v -s
```

### 3. Drop into debugger on failure
```cmd
pytest --pdb
```

### 4. Show full traceback
```cmd
pytest --tb=long
```

## Coverage Goals

Target: **>80% code coverage**

Check coverage:
```cmd
pytest --cov=src --cov-report=term-missing
```

This shows which lines aren't covered by tests.

## Performance

**Expected test runtime:**
- Quick run: ~2-5 seconds
- With coverage: ~5-10 seconds
- With model loading (if not mocked): ~30-60 seconds

## Need Help?

If tests fail locally but you're not sure why:

1. Check the error message carefully
2. Verify all dependencies are installed
3. Make sure virtual environment is activated
4. Try running a single test file first
5. Check `TROUBLESHOOTING.md` for common issues

## Example Full Test Session

```cmd
C:\Projects\locivox> venv\Scripts\activate

(venv) C:\Projects\locivox> pip install -r requirements-dev.txt
...

(venv) C:\Projects\locivox> pytest -v
========================= test session starts =========================
platform win32 -- Python 3.11.5, pytest-7.4.0
collected 39 items

tests/test_utils.py::TestLoadConfig::test_load_valid_config PASSED    [  2%]
tests/test_utils.py::TestLoadConfig::test_load_nonexistent_config PASSED [  5%]
...
tests/test_transcriber.py::TestTranscriberErrorHandling::test_load_model_import_error PASSED [100%]

========================= 39 passed in 3.21s ==========================

(venv) C:\Projects\locivox> echo Ready to push!
Ready to push!
```

**You're ready to push when you see all tests passing!** ✅
