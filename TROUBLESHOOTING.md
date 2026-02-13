# 🔧 Locivox Troubleshooting Guide

Common issues and their solutions.

---

## Setup Issues

### ❌ `ModuleNotFoundError: No module named 'pkg_resources'`

**Cause:** Missing setuptools (common in Python 3.12+)

**Solution:**

```bash
# Activate your virtual environment first
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Then install setuptools
pip install --upgrade pip setuptools wheel

# Now install requirements
pip install -r requirements.txt
```

**Prevention:** The updated setup scripts now handle this automatically.

---

### ❌ `Python is not recognized as a command`

**Cause:** Python not in PATH

**Solution:**

**Windows:**
1. Run Python installer again
2. Check "Add Python to PATH"
3. Or manually add: `C:\Users\YourName\AppData\Local\Programs\Python\Python3X\`

**macOS/Linux:**
```bash
# Check if Python is installed
python3 --version

# If not, install:
# macOS:
brew install python3

# Ubuntu:
sudo apt install python3 python3-pip
```

---

### ❌ `FFmpeg not found`

**Cause:** FFmpeg not installed or not in PATH

**Solution:**

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# Windows (with Chocolatey)
choco install ffmpeg

# Windows (with Scoop)
scoop install ffmpeg

# Windows (manual)
# Download from https://ffmpeg.org/download.html
# Extract and add to PATH
```

**Verify:**
```bash
ffmpeg -version
```

---

### ❌ `Virtual environment activation failed`

**Windows PowerShell Execution Policy Error:**

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate again
venv\Scripts\activate
```

**Alternative (Windows):**
Use Command Prompt (cmd.exe) instead of PowerShell:
```cmd
venv\Scripts\activate.bat
```

---

## Runtime Issues

### ❌ `No audio devices found`

**Cause:** No microphone detected or permissions denied

**Solution:**

1. **Check device list:**
```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

2. **Grant microphone permissions:**
   - **macOS:** System Preferences → Security & Privacy → Microphone
   - **Windows:** Settings → Privacy → Microphone
   - **Linux:** Check PulseAudio/ALSA settings

3. **Test microphone:**
```bash
# macOS/Linux
rec -c 1 -r 16000 test.wav

# Windows
# Use Sound Recorder app to verify mic works
```

---

### ❌ Slow transcription on CPU

**Expected behavior on CPU:**
- `tiny` model: ~10x faster than real-time
- `base` model: ~5x faster than real-time
- `small` model: ~3x faster than real-time
- `medium` model: ~1x (real-time)

**Solutions:**

1. **Use faster-whisper** (default, 2-4x faster):
```yaml
# config.yaml
model:
  engine: "faster-whisper"
```

2. **Use smaller model:**
```bash
python src/cli.py --model tiny
# or
python src/cli.py --model base
```

3. **Reduce chunk duration:**
```yaml
# config.yaml
audio:
  chunk_duration: 3  # default is 5
```

---

### ❌ `RuntimeError: Failed to load model`

**Cause:** Model download failed or insufficient disk space

**Solution:**

1. **Check disk space** (models are 40MB - 1.5GB)

2. **Manual download:**
```bash
# Python console
import whisper
whisper.load_model("base")  # Will download to ~/.cache/whisper/
```

3. **Check internet connection** for first run

4. **Clear cache and retry:**
```bash
# macOS/Linux
rm -rf ~/.cache/whisper

# Windows
rmdir /s %USERPROFILE%\.cache\whisper
```

---

### ❌ Poor transcription quality

**Solutions:**

1. **Use larger model:**
```bash
python src/cli.py --model small
# or
python src/cli.py --model medium
```

2. **Specify language explicitly:**
```bash
python src/cli.py --language en
```

3. **Improve audio quality:**
   - Speak closer to microphone
   - Reduce background noise
   - Use better microphone
   - Check audio levels (not too quiet, not clipping)

4. **Adjust silence threshold:**
```yaml
# config.yaml
audio:
  silence_threshold: 0.005  # Lower = more sensitive
```

---

### ❌ `PermissionError: [Errno 13] Permission denied`

**Cause:** No write permissions for output directory

**Solution:**

```bash
# Check permissions
ls -l output/

# Fix permissions (Unix)
chmod 755 output/

# Windows: Right-click folder → Properties → Security → Edit permissions
```

---

### ❌ `CUDA out of memory` (if using GPU)

**Solution:**

1. **Fall back to CPU:**
```yaml
# config.yaml
model:
  device: "cpu"
```

2. **Use smaller model:**
```yaml
model:
  size: "base"  # or "small"
```

3. **Use int8 quantization:**
```yaml
model:
  compute_type: "int8"
```

---

## Dependency Issues

### ❌ `ImportError: cannot import name 'something' from 'package'`

**Cause:** Version conflicts

**Solution:**

```bash
# Clear and reinstall
pip uninstall -y -r requirements.txt
pip install -r requirements.txt

# Or recreate venv
deactivate
rm -rf venv  # Windows: rmdir /s venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### ❌ `torch._C` import errors

**Cause:** PyTorch CPU/GPU mismatch or corrupted install

**Solution:**

```bash
# Reinstall PyTorch (CPU version)
pip uninstall torch torchaudio
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

---

## Audio File Issues

### ❌ `Error loading audio file`

**Supported formats:** WAV, MP3, FLAC, OGG, M4A

**Solution:**

1. **Convert to WAV:**
```bash
ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav
python src/cli.py --file output.wav
```

2. **Check file corruption:**
```bash
ffmpeg -i audio.mp3 -f null -
```

---

## Configuration Issues

### ❌ `Error parsing config file`

**Cause:** Invalid YAML syntax

**Solution:**

1. **Validate YAML:**
```bash
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

2. **Reset to default:**
```bash
# Backup current config
cp config.yaml config.backup.yaml

# Download fresh config from project repo
# Or manually check indentation and syntax
```

**Common YAML mistakes:**
- Mixed tabs and spaces (use spaces only)
- Missing colons
- Incorrect indentation (use 2 or 4 spaces consistently)

---

## Getting Help

If your issue isn't listed here:

1. **Check logs:**
   ```bash
   cat logs/locivox.log  # Unix
   type logs\locivox.log  # Windows
   ```

2. **Enable debug logging:**
   ```yaml
   # config.yaml
   logging:
     level: "DEBUG"
   ```

3. **Run with verbose output:**
   ```bash
   python src/cli.py --verbose  # if implemented
   ```

4. **Test individual components:**
   ```bash
   # Test audio capture
   python -c "import sounddevice as sd; print(sd.query_devices())"
   
   # Test Whisper
   python -c "import whisper; whisper.load_model('base')"
   ```

5. **Report issue** with:
   - OS and version
   - Python version (`python --version`)
   - Error message from logs
   - Steps to reproduce

---

## Quick Diagnostics

Run this to check your setup:

```bash
python -c "
import sys
import platform
print(f'OS: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
try:
    import sounddevice
    print('✓ sounddevice')
except: print('✗ sounddevice')
try:
    import whisper
    print('✓ whisper')
except: print('✗ whisper')
try:
    import faster_whisper
    print('✓ faster-whisper')
except: print('✗ faster-whisper')
try:
    import torch
    print(f'✓ torch {torch.__version__}')
except: print('✗ torch')
"
```

---

**Still stuck? Check the logs and create a detailed issue report!**
