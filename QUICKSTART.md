# ⚡ Locivox Quick Start

Get transcribing in 3 minutes!

## 1️⃣ Install FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
choco install ffmpeg
```

## 2️⃣ Setup Locivox

```bash
# Unix (macOS/Linux)
chmod +x setup.sh
./setup.sh

# Windows
setup.bat
```

## 3️⃣ Activate & Run

```bash
# Unix
source venv/bin/activate

# Windows
venv\Scripts\activate

# Run
python src/cli.py
```

## 🎤 First Recording

1. Press ENTER to start recording
2. Speak clearly into your microphone
3. Press ENTER to stop
4. Wait for transcription
5. Find output in `output/` folder

## 💡 Pro Tips

**Better Performance:**
```bash
# Use faster-whisper (default, recommended)
# Edit config.yaml: engine: "faster-whisper"

# Use smaller model for speed
python src/cli.py --model tiny
```

**Transcribe a File:**
```bash
python src/cli.py --file audio.wav
```

**Change Output Format:**
```bash
python src/cli.py --output-format srt
```

**Force Language:**
```bash
python src/cli.py --language es
```

## 🆘 Troubleshooting

**No sound?**
```bash
python src/cli.py
# List shows your devices - pick the right number
```

**Slow on CPU?**
- Use `base` model (default)
- Or use `tiny` for 2x speed
- `faster-whisper` is already 4x faster than openai-whisper

**Can't find FFmpeg?**
```bash
# Verify installation
ffmpeg -version

# Add to PATH if installed but not found
```

## 📖 Learn More

- `README.md` - Full documentation
- `ROADMAP.md` - Future features
- `config.yaml` - Customize settings

**Ready to build something amazing? Let's go! 🚀**
