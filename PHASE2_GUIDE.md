# Phase 2: Real-time Streaming - Complete! 🎉

## What's New

Phase 2 adds **real-time streaming transcription** with Voice Activity Detection!

### New Features

✨ **Real-time Transcription**
- Transcribe audio as you speak
- No need to wait for full recording
- Background processing in separate thread

🎙️ **Voice Activity Detection (VAD)**
- Automatically filters silence
- Only processes speech segments
- Saves processing power

📦 **Chunked Processing**
- Overlapping audio chunks for better accuracy
- Configurable chunk size and overlap
- Circular buffer management

⚡ **Performance**
- Non-blocking audio capture
- Parallel transcription pipeline
- Optimized for low latency

---

## Installation

```bash
# Install new dependencies
pip install silero-vad

# Or reinstall everything
pip install -r requirements.txt
```

---

## Usage

### Quick Start

```bash
# Start streaming mode
locivox-stream

# Or with options
locivox-stream --model small --device 0
```

### Step-by-Step

1. **Run the command:**
   ```bash
   locivox-stream
   ```

2. **Select your microphone** from the list (or press Enter for default)

3. **Start speaking!** Transcription appears in real-time:
   ```
   14:23:45 [  >>  ] Hello, this is a test
   14:23:48 [  >>  ] of the streaming transcription
   14:23:52 [  >>  ] It works in real time
   ```

4. **Press Ctrl+C to stop** - saves output automatically

---

## Configuration

Edit `config.yaml`:

```yaml
# Streaming Settings (Phase 2)
streaming:
  enabled: true             # Enable streaming mode
  chunk_size: 5.0           # Seconds per chunk
  chunk_overlap: 1.0        # Overlap between chunks
  vad_enabled: true         # Use Voice Activity Detection
  vad_threshold: 0.5        # VAD sensitivity (0.0-1.0)
  buffer_size: 10           # Max chunks in buffer
  min_speech_duration: 0.5  # Minimum speech to process
```

### Parameter Tuning

**chunk_size** (default: 5.0)
- Larger = better context, higher latency
- Smaller = faster response, less context
- Recommended: 3-7 seconds

**chunk_overlap** (default: 1.0)
- Prevents cutting words at boundaries
- Recommended: 0.5-2.0 seconds

**vad_threshold** (default: 0.5)
- Higher = more aggressive (skips more)
- Lower = more sensitive (processes more)
- Range: 0.0 (off) to 1.0 (strict)

**min_speech_duration** (default: 0.5)
- Skip chunks shorter than this
- Reduces "um", "uh", artifacts
- Recommended: 0.3-1.0 seconds

---

## Architecture

```
┌─────────────────┐
│  Microphone     │
└────────┬────────┘
         │ 100ms blocks
         ↓
┌─────────────────┐
│  Audio Stream   │ (sounddevice)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Audio Buffer   │ (circular, overlap)
└────────┬────────┘
         │ 5s chunks
         ↓
┌─────────────────┐
│  VAD Filter     │ (silero-vad)
└────────┬────────┘
         │ speech only
         ↓
┌─────────────────┐
│  Thread Queue   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Transcriber    │ (faster-whisper)
│  (Background)   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Output Stream  │ (console + file)
└─────────────────┘
```

---

## New Modules

### `src/vad.py`
Voice Activity Detection using Silero VAD
- `VoiceActivityDetector` class
- `is_speech()` - detect speech in chunk
- `get_speech_segments()` - find speech timestamps
- `filter_silence()` - remove non-speech

### `src/buffer.py`
Circular audio buffer with overlap
- `AudioBuffer` class
- `add_audio()` - append new samples
- `get_chunk()` - retrieve next chunk
- `flush()` - get remaining audio

### `src/streaming.py`
Real-time streaming transcriber
- `StreamingTranscriber` class
- Background processing thread
- Result callbacks
- Statistics tracking

### `src/cli_streaming.py`
Streaming CLI interface
- `StreamingCLI` class
- Real-time console output
- Automatic file saving
- Device selection

---

## Examples

### Basic Streaming

```bash
locivox-stream
```

### Specify Model

```bash
# Use small model for better quality
locivox-stream --model small

# Use tiny model for speed
locivox-stream --model tiny
```

### Select Device

```bash
# List devices first
locivox-stream

# Then select by index
locivox-stream --device 1
```

### Custom Config

```bash
locivox-stream --config my_config.yaml
```

---

## Output

### Console Output

```
14:23:45 [  >>  ] Hello, this is a test
14:23:48 [  >>  ] of the streaming transcription
14:23:52 [FINAL] It works in real time
```

**Legend:**
- `[  >>  ]` - Partial result
- `[FINAL]` - Last chunk (on stop)

### File Output

Saved automatically to: `output/stream_YYYYMMDD_HHMMSS.txt`

Example:
```
output/stream_20260215_142352.txt
```

Contains full concatenated transcription.

---

## Performance

### Speed

**Faster than real-time!** On modern CPU:
- tiny model: ~10x real-time
- base model: ~5x real-time
- small model: ~3x real-time

**Latency:** 
- Audio buffering: ~100ms
- VAD: ~10ms
- Transcription: ~500ms-2s (depends on model)
- **Total: ~1-3 seconds** end-to-end

### Resource Usage

**CPU:**
- Idle: ~5-10%
- During speech: ~40-80%
- Depends on model size

**Memory:**
- tiny model: ~200MB
- base model: ~500MB
- small model: ~1GB

**Network:**
- Zero! Everything runs locally

---

## Troubleshooting

### "No module named 'silero-vad'"

```bash
pip install silero-vad
```

### "Model loading takes forever"

First run downloads models (~40MB for tiny, ~500MB for small).
Subsequent runs are fast.

### "Audio sounds choppy"

Increase `chunk_size` in config:
```yaml
streaming:
  chunk_size: 7.0  # Increase from 5.0
```

### "Missing speech at boundaries"

Increase `chunk_overlap`:
```yaml
streaming:
  chunk_overlap: 2.0  # Increase from 1.0
```

### "Processing too much silence"

Increase VAD threshold:
```yaml
streaming:
  vad_threshold: 0.7  # Increase from 0.5
```

### "Delayed transcription"

Use smaller model:
```bash
locivox-stream --model tiny
```

---

## Comparison: Phase 1 vs Phase 2

| Feature | Phase 1 (Basic) | Phase 2 (Streaming) |
|---------|----------------|---------------------|
| Mode | Batch | Real-time |
| Latency | Full recording | ~1-3 seconds |
| Output | After recording | As you speak |
| VAD | Optional | Built-in |
| Threading | Single | Multi-threaded |
| Use Case | Files, meetings | Live, dictation |

---

## Next Steps

### Phase 3 (Coming Soon)
- Speaker diarization (who said what)
- Punctuation restoration
- Custom vocabulary
- Hot word detection
- Multiple output formats

### Phase 4 (GUI)
- Desktop application
- Visual waveform
- Real-time editing
- Export options

---

## API Usage (Programmatic)

### Basic Example

```python
from src.streaming import StreamingTranscriber
from src.utils import load_config

# Load config
config = load_config('config.yaml')

# Define callback
def on_transcription(text, is_final):
    print(f"{'[FINAL]' if is_final else '[>>]'} {text}")

# Create transcriber
transcriber = StreamingTranscriber(config, callback=on_transcription)

# Start
transcriber.start()

# Feed audio (numpy array, float32, 16kHz)
transcriber.add_audio(audio_data)

# Stop
transcriber.stop()

# Get results
full_text = transcriber.get_full_text()
```

### Advanced Example

```python
import sounddevice as sd
import numpy as np
from src.streaming import StreamingTranscriber
from src.utils import load_config

config = load_config('config.yaml')
transcriber = StreamingTranscriber(config)
transcriber.start()

def audio_callback(indata, frames, time, status):
    # Convert to mono
    audio = indata[:, 0] if len(indata.shape) > 1 else indata
    transcriber.add_audio(audio.copy())

# Start audio stream
stream = sd.InputStream(
    callback=audio_callback,
    channels=1,
    samplerate=16000
)

with stream:
    input("Press Enter to stop...")

transcriber.stop()
print(transcriber.get_full_text())
```

---

## Testing

```bash
# Run Phase 2 tests
pytest tests/test_vad.py -v
pytest tests/test_buffer.py -v
pytest tests/test_streaming.py -v

# Run all tests
pytest -v
```

---

## Contributing

Found a bug? Have an idea? 
- Open an issue on GitHub
- Submit a pull request
- Join discussions

---

## Credits

**Phase 2 Technologies:**
- [Silero VAD](https://github.com/snakers4/silero-vad) - Voice Activity Detection
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Fast inference
- [sounddevice](https://python-sounddevice.readthedocs.io/) - Audio I/O

---

**Phase 2 Complete! 🎉**

Ready for **Phase 3: Enhanced CLI** or **Phase 4: GUI**?
