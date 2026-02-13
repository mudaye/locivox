# Locivox Examples

This directory contains example scripts demonstrating various ways to use Locivox.

## Available Examples

### 1. Basic Transcription (`basic_transcription.py`)

The simplest example showing core functionality.

**Usage:**
```bash
python basic_transcription.py
```

**What it does:**
- Lists available microphones
- Records audio from selected device
- Transcribes the recording
- Saves to text file

**Learn:**
- How to initialize Locivox components
- Basic recording and transcription flow
- Working with configuration

---

### 2. Batch Processing (`batch_processing.py`)

Process multiple audio files in a directory.

**Usage:**
```bash
# Process all audio files in a directory
python batch_processing.py /path/to/audio/files

# Specify output directory
python batch_processing.py /path/to/audio --output-dir output/transcripts

# Use different model
python batch_processing.py /path/to/audio --model small

# Custom file extensions
python batch_processing.py /path/to/audio --extensions wav,mp3,flac
```

**What it does:**
- Finds all audio files in directory
- Transcribes each file
- Shows progress bar
- Generates summary report
- Handles errors gracefully

**Learn:**
- Programmatic file processing
- Error handling
- Progress tracking
- Generating reports

---

### 3. Custom Model Example (`custom_model_example.py`)

Compare different models and engines.

**Usage:**
```bash
# Compare multiple models on same audio
python custom_model_example.py audio.wav

# Test specific model
python custom_model_example.py audio.wav --model small

# Test different engine
python custom_model_example.py audio.wav --engine openai-whisper
```

**What it does:**
- Benchmarks different model sizes
- Measures load time and transcription speed
- Compares accuracy across models
- Shows speed vs quality tradeoff

**Learn:**
- Creating custom configurations
- Performance benchmarking
- Switching between engines
- Model comparison

---

## Setup

### Install Locivox

```bash
cd ..
pip install -e .
```

Or install from PyPI:
```bash
pip install locivox
```

### Install Example Dependencies

Some examples need additional packages:

```bash
pip install tqdm librosa soundfile
```

## Running Examples

### From Project Root

```bash
python examples/basic_transcription.py
python examples/batch_processing.py audio_files/
python examples/custom_model_example.py test_audio.wav
```

### From Examples Directory

```bash
cd examples
python basic_transcription.py
```

## Sample Audio Files

Get free sample audio for testing:

**Public Domain Sources:**
- [LibriVox](https://librivox.org/) - Free public domain audiobooks
- [Freesound](https://freesound.org/) - Creative Commons audio
- [Common Voice](https://commonvoice.mozilla.org/) - Open speech dataset

**Generate Test Audio:**
```python
# Create a simple test file
import numpy as np
import soundfile as sf

# 5 seconds of 440Hz tone (A4 note)
sample_rate = 16000
duration = 5
t = np.linspace(0, duration, int(sample_rate * duration))
audio = np.sin(2 * np.pi * 440 * t).astype(np.float32)

sf.write('test_tone.wav', audio, sample_rate)
```

## Example Output

### Basic Transcription
```
🎤 Locivox Basic Example
==================================================

🎤 Available Audio Input Devices:
============================================================
0: MacBook Pro Microphone [DEFAULT]
   Channels: 1, Sample Rate: 48000 Hz
============================================================

Select device (press Enter for default): 

Press ENTER to start recording...
🔴 Recording... Press ENTER to stop
✅ Recorded 80000 samples

🤖 Transcribing...

==================================================
TRANSCRIPTION:
==================================================
This is a test of the Locivox transcription system.
==================================================

🌍 Detected language: en
💾 Saved to: output/basic_example.txt
```

### Batch Processing
```
🎤 Locivox Batch Processing
📁 Input: audio_files
💾 Output: output/batch
📊 Files found: 10
🤖 Model: base
============================================================
Transcribing: 100%|████████████████| 10/10 [00:45<00:00,  4.51s/it]

============================================================
SUMMARY
============================================================
✅ Successful: 10
❌ Failed: 0
📝 Total words transcribed: 5,234

📊 Detailed report: output/batch/batch_report.txt
```

### Model Comparison
```
🎤 Locivox Model Comparison
============================================================

============================================================
Testing: faster-whisper / tiny
============================================================
Audio duration: 10.50s
Loading model...
✓ Model loaded in 2.34s
Transcribing...
✓ Transcribed in 1.23s
✓ Speed: 8.54x real-time
✓ Text length: 245 chars
✓ Word count: 42 words
✓ Language: en

[... results for base and small models ...]

============================================================
COMPARISON SUMMARY
============================================================

Model      Load Time    Trans Time    Speed     
------------------------------------------------------------
tiny           2.34s        1.23s      8.54x
base           3.21s        2.15s      4.88x
small          5.67s        3.89s      2.70x

🏆 Fastest: tiny (8.54x real-time)
✓ All models produced identical transcriptions
```

## Common Patterns

### Custom Configuration

```python
from src.transcriber import TranscriberFactory

# Create custom config
config = {
    'model': {
        'engine': 'faster-whisper',
        'size': 'small',
        'device': 'cpu',
        'language': 'es'  # Spanish
    }
}

transcriber = TranscriberFactory.create_transcriber(config)
```

### Error Handling

```python
try:
    result = transcriber.transcribe(audio_data)
    print(result['text'])
except RuntimeError as e:
    print(f"Transcription failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Progress Tracking

```python
from tqdm import tqdm

for audio_file in tqdm(audio_files, desc="Processing"):
    result = transcribe_file(audio_file)
    # Process result
```

## Next Steps

- Read the [API Documentation](../docs/api/modules.rst)
- Check [Usage Guide](../docs/usage.rst) for more options
- See [Contributing Guide](../CONTRIBUTING.md) to add examples

## Contributing Examples

Have a cool use case? Add an example!

1. Create a new `.py` file
2. Add clear comments and docstrings
3. Include usage instructions
4. Update this README
5. Submit a pull request

**Good Example Topics:**
- Real-time streaming transcription
- Integration with other tools
- Custom output formats
- Advanced audio processing
- GUI applications
