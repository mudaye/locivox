# 🎤 Locivox

**Local Voice Transcription System** - Privacy-first, model-agnostic speech-to-text powered by AI

Locivox (Latin: *loci* = local, *vox* = voice) is an open-source STT system designed to run entirely on your machine with no cloud dependencies. Start with Whisper, expand to any model.

---

## ✨ Features (Phase 1 - MVP)

- ✅ **Real-time microphone capture** with configurable settings
- ✅ **Multiple STT engines**: Faster-Whisper (recommended) and OpenAI-Whisper
- ✅ **CPU-optimized** for laptops without GPU
- ✅ **Model-agnostic architecture** - easily add new engines
- ✅ **Multiple output formats**: TXT, JSON, SRT subtitles
- ✅ **Automatic language detection** or manual selection
- ✅ **Self-contained virtual environment** - no global dependencies

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- FFmpeg (required for audio processing)

**Install FFmpeg:**

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows (use Chocolatey)
choco install ffmpeg
```

### Installation

1. **Clone or download the project:**

```bash
cd locivox
```

2. **Create virtual environment:**

```bash
python -m venv venv

# Activate it:
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

This will download the required models on first run (~140MB for base model).

---

## 💻 Usage

### Interactive Recording Mode

Record from your microphone and transcribe:

```bash
python src/cli.py
```

**Workflow:**
1. Select your microphone device
2. Press ENTER to start recording
3. Speak into your microphone
4. Press ENTER to stop
5. Transcription appears in console and saves to `output/` folder

### Transcribe Existing Audio File

```bash
python src/cli.py --file path/to/audio.wav
```

### Advanced Options

```bash
# Use a different model size
python src/cli.py --model small

# Force a specific language (skip auto-detection)
python src/cli.py --language es

# Change output format
python src/cli.py --output-format json

# Use custom config file
python src/cli.py --config my_config.yaml

# Combine options
python src/cli.py --file audio.mp3 --model medium --output-format srt
```

---

## ⚙️ Configuration

Edit `config.yaml` to customize behavior:

```yaml
model:
  engine: "faster-whisper"  # or "openai-whisper"
  size: "base"              # tiny, base, small, medium, large
  language: "en"            # or "auto" for detection

audio:
  sample_rate: 16000        # Whisper expects 16kHz
  chunk_duration: 5         # Seconds per chunk

output:
  format: "txt"             # txt, json, srt
  timestamp: true           # Include timestamp in filename
```

### Model Sizes & Performance

| Model  | Size  | Speed (CPU) | Quality | Memory |
|--------|-------|-------------|---------|--------|
| tiny   | 39M   | ~10x RT     | Basic   | <1GB   |
| base   | 74M   | ~5x RT      | Good    | ~1GB   |
| small  | 244M  | ~3x RT      | Better  | ~2GB   |
| medium | 769M  | ~1x RT      | Great   | ~5GB   |
| large  | 1.5G  | ~0.5x RT    | Best    | ~10GB  |

*RT = Real-time (1x means transcribes at speaking speed)*

**Recommendation:** Start with `base` for best speed/quality balance on CPU.

---

## 📁 Project Structure

```
locivox/
├── venv/                   # Virtual environment (created on setup)
├── src/
│   ├── __init__.py         # Package init
│   ├── cli.py              # Main CLI entry point
│   ├── audio_capture.py    # Microphone recording
│   ├── transcriber.py      # STT engine wrappers
│   └── utils.py            # Helper functions
├── output/                 # Generated transcripts
├── logs/                   # Application logs
├── models/                 # Downloaded models (auto-created)
├── config.yaml             # User configuration
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🛠️ Troubleshooting

### "No audio devices found"

```bash
# List available devices
python -c "import sounddevice; print(sounddevice.query_devices())"
```

### "FFmpeg not found"

Ensure FFmpeg is installed and in your PATH:

```bash
ffmpeg -version
```

### Slow transcription on CPU

- Use `faster-whisper` engine (2-4x faster than openai-whisper)
- Use smaller models (tiny/base)
- Reduce chunk duration in config

### Import errors

Make sure virtual environment is activated:

```bash
# Check if venv is active (should show venv path)
which python  # macOS/Linux
where python  # Windows
```

---

## 🗺️ Roadmap

- [x] **Phase 1: MVP CLI** (You are here!)
- [ ] **Phase 2: Real-time streaming** with chunked processing
- [ ] **Phase 3: Enhanced CLI** with speaker diarization, multiple formats
- [ ] **Phase 4: GUI Desktop App** with Electron/PyQt
- [ ] **Phase 5: Advanced features** (translation, punctuation, custom vocabulary)
- [ ] **Phase 6: Multi-platform distribution** with installers

See [ROADMAP.md](ROADMAP.md) for detailed timeline.

---

## 🤝 Contributing

Contributions welcome! This is an open-source project.

**Areas to contribute:**
- New STT engine integrations (Vosk, Coqui, wav2vec2)
- Performance optimizations
- GUI development
- Documentation improvements
- Bug fixes and testing

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- **OpenAI Whisper** - State-of-the-art STT model
- **Faster-Whisper** - Optimized inference engine
- **sounddevice** - Python audio library

---

## 📞 Support

- **Issues**: Open an issue on GitHub
- **Discussions**: Start a discussion for features/ideas
- **Logs**: Check `logs/locivox.log` for debugging

---

**Built with ❤️ for privacy-conscious developers**
