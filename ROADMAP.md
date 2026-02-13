# 🗺️ Locivox Development Roadmap

Detailed timeline and feature planning for Locivox's evolution from CLI to full-featured desktop app.

---

## ✅ Phase 1: MVP CLI (Week 1) - **COMPLETE**

**Status:** ✅ Done

**Goal:** Basic command-line tool for record → transcribe → save workflow

**Delivered:**
- ✅ Virtual environment setup
- ✅ Microphone capture with sounddevice
- ✅ Faster-Whisper and OpenAI-Whisper integration
- ✅ Model-agnostic architecture (TranscriberFactory pattern)
- ✅ Configuration system (YAML)
- ✅ Multiple output formats (TXT, JSON, SRT)
- ✅ Logging system
- ✅ CLI argument parsing
- ✅ Audio file transcription support

**Key Files:**
- `src/cli.py` - Main entry point
- `src/audio_capture.py` - Recording logic
- `src/transcriber.py` - STT engines
- `src/utils.py` - Helpers
- `config.yaml` - Settings

---

## 🚧 Phase 2: Real-time Streaming (Week 2-3)

**Status:** 📋 Planned

**Goal:** Live transcription with minimal latency for continuous speech

**Tasks:**
- [ ] Implement VAD (Voice Activity Detection) with `webrtcvad` or `silero-vad`
- [ ] Chunked audio buffer system (sliding window)
- [ ] Background thread for continuous transcription
- [ ] Stream output to console + file simultaneously
- [ ] Configurable chunk size and overlap (500ms - 5s)
- [ ] Performance metrics (latency, processing time)
- [ ] Handle long pauses gracefully

**Technical Approach:**
```python
# Pseudo-architecture
AudioCapture (threaded) 
    → VAD Filter 
    → Chunk Buffer (5s with 1s overlap)
    → Transcription Queue
    → Whisper Model
    → Output Stream
```

**Benchmarks to Hit:**
- < 2s latency on base model (CPU)
- < 1s latency on faster-whisper (CPU)
- Stable 30+ minute recordings

---

## 📊 Phase 3: Enhanced CLI (Week 4)

**Status:** 📋 Planned

**Goal:** Production-ready CLI with advanced features

**Features:**

### 3.1 Speaker Diarization
- [ ] Integrate `pyannote-audio` for speaker detection
- [ ] Label segments by speaker (Speaker 1, Speaker 2, etc.)
- [ ] Optional speaker name mapping
- [ ] Output format: `[Speaker 1]: Hello there...`

### 3.2 Multiple Output Formats
- [ ] WebVTT (.vtt) for web videos
- [ ] Markdown (.md) with timestamps
- [ ] CSV export for analysis
- [ ] PDF report generation

### 3.3 Advanced CLI Options
```bash
# Examples of new flags
--speakers N              # Enable diarization with N speakers
--format srt,txt,json     # Multiple simultaneous outputs
--language-detect         # Show language probabilities
--confidence-threshold    # Filter low-confidence segments
--post-process            # Apply punctuation restoration
--hotwords "name1,name2"  # Boost recognition of specific words
```

### 3.4 Progress & Stats
- [ ] Real-time progress bar (tqdm)
- [ ] Live transcription preview
- [ ] Post-completion stats:
  - Total duration
  - Processing time
  - Words per minute
  - Confidence scores

### 3.5 Quality Improvements
- [ ] Punctuation restoration with `deepmultilingualpunctuation`
- [ ] Number formatting (spoken → digits)
- [ ] Profanity filtering (optional)
- [ ] Noise reduction preprocessing

---

## 🖥️ Phase 4: GUI Desktop App (Week 5-7)

**Status:** 📋 Planned

**Goal:** User-friendly desktop application with visual interface

### 4.1 Technology Stack Decision

**Option A: PyQt6/PySide6** (Recommended)
- ✅ Native performance
- ✅ Professional look
- ✅ Cross-platform
- ✅ Easy packaging
- ❌ Slightly steeper learning curve

**Option B: Electron + Python Backend**
- ✅ Web tech (HTML/CSS/JS)
- ✅ Modern UI possibilities
- ❌ Larger bundle size
- ❌ Higher memory usage

**Option C: Tauri**
- ✅ Lightweight alternative to Electron
- ✅ Rust backend + web frontend
- ❌ More complex setup

**Decision:** Start with PyQt6, evaluate Electron/Tauri later

### 4.2 Core UI Components

**Main Window:**
```
┌─────────────────────────────────────────┐
│  Locivox                          [_][□][X]│
├─────────────────────────────────────────┤
│  Model: Base ▼  Language: English ▼    │
│  Input: MacBook Mic ▼                   │
├─────────────────────────────────────────┤
│                                         │
│    [●] Start Recording                  │
│    [ ] Stop Recording                   │
│                                         │
│    ▓▓▓▓▓▓▓▓░░░░ Audio Level            │
│                                         │
├─────────────────────────────────────────┤
│  Live Transcription:                    │
│  ┌───────────────────────────────────┐ │
│  │ This is the text being            │ │
│  │ transcribed in real-time...       │ │
│  │                                   │ │
│  │ [Auto-scroll]                     │ │
│  └───────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  [Save] [Copy] [Export ▼] [Settings]   │
└─────────────────────────────────────────┘
```

### 4.3 Features
- [ ] Start/Stop recording buttons
- [ ] Live waveform visualization
- [ ] Audio level meter (VU meter)
- [ ] Scrolling transcription display
- [ ] Model selector dropdown
- [ ] Language selector
- [ ] Input device selector (auto-refresh)
- [ ] Output format selector
- [ ] Settings panel
- [ ] Export menu (Save, Copy, Email, etc.)
- [ ] Keyboard shortcuts (Ctrl+R to record, Ctrl+S to stop)
- [ ] System tray integration
- [ ] Dark/Light theme

### 4.4 Settings Panel
```
Settings
├── General
│   ├── Auto-start on boot
│   ├── Minimize to tray
│   └── Theme (Light/Dark/System)
├── Audio
│   ├── Input device
│   ├── Sample rate
│   └── Silence detection threshold
├── Model
│   ├── Engine (Faster-Whisper/OpenAI)
│   ├── Model size
│   ├── Compute type
│   └── Language
├── Output
│   ├── Default format
│   ├── Output directory
│   └── Filename template
└── Advanced
    ├── Enable speaker diarization
    ├── Post-processing options
    └── Hotword vocabulary
```

---

## 🚀 Phase 5: Advanced Features (Week 8-12)

**Status:** 📋 Planned

**Goal:** Match and exceed commercial STT apps

### 5.1 Translation
- [ ] Transcribe in any language → translate to English
- [ ] Multi-language output (transcribe + translate side-by-side)
- [ ] Powered by Whisper's built-in translation

### 5.2 Custom Vocabulary
- [ ] User-defined word lists (technical terms, names)
- [ ] Boost recognition confidence for specific words
- [ ] Industry-specific presets (medical, legal, tech)

### 5.3 Keyboard Shortcuts
- [ ] Global hotkeys (work outside the app)
- [ ] Customizable keybindings
- [ ] Push-to-talk mode

### 5.4 Audio Playback Sync
- [ ] Play recorded audio
- [ ] Highlight current word/segment
- [ ] Click text to jump to timestamp
- [ ] Edit transcription while listening

### 5.5 Search & Edit
- [ ] Full-text search across transcripts
- [ ] In-app text editor
- [ ] Find & replace
- [ ] Export edited version

### 5.6 Batch Processing
- [ ] Process multiple audio files
- [ ] Queue system
- [ ] Progress tracking for bulk jobs
- [ ] Scheduled transcription

### 5.7 Cloud Backup (Optional)
- [ ] Local-first, cloud backup optional
- [ ] Encrypted sync to user's cloud storage
- [ ] Google Drive / Dropbox / OneDrive integration

### 5.8 Performance Optimizations
- [ ] Model quantization (int8, int4)
- [ ] GPU auto-detection and fallback
- [ ] Memory-mapped models for faster loading
- [ ] Streaming inference for long files

---

## 📦 Phase 6: Distribution & Polish (Ongoing)

**Status:** 📋 Planned

**Goal:** Easy installation and professional packaging

### 6.1 Packaging
- [ ] PyInstaller standalone executable
- [ ] Platform-specific builds:
  - Windows: `.exe` installer (Inno Setup)
  - macOS: `.dmg` with code signing
  - Linux: `.AppImage` and `.deb` packages
- [ ] Bundled models vs. download-on-demand

### 6.2 Auto-updates
- [ ] Check for updates on startup
- [ ] Download and install updates
- [ ] Changelog display

### 6.3 Installers
- [ ] Windows: NSIS or Inno Setup
- [ ] macOS: DMG with drag-to-Applications
- [ ] Linux: AppImage for universal compatibility

### 6.4 Code Quality
- [ ] Unit tests (pytest)
- [ ] Integration tests
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Code coverage >80%

### 6.5 Documentation
- [ ] User manual
- [ ] Video tutorials
- [ ] API documentation (for developers)
- [ ] Contribution guidelines

---

## 🔮 Future Vision (Phase 7+)

**Potential Expansions:**

### Mobile Support
- React Native or Flutter app
- On-device inference on mobile
- Cross-device sync

### Plugin System
- Third-party integrations
- Custom post-processing plugins
- Community marketplace

### Advanced AI Features
- Summarization of long transcripts
- Action item extraction
- Sentiment analysis
- Multi-turn conversation analysis

### Multi-Model Support
- Vosk integration
- Coqui STT
- wav2vec 2.0
- DeepSpeech 2
- Assembly AI (cloud fallback)

### Collaboration Features
- Real-time collaborative transcription
- Team workspaces
- Shared vocabulary

---

## 📅 Timeline Summary

| Phase | Duration | Complexity | Status |
|-------|----------|------------|--------|
| Phase 1: MVP CLI | 1 week | ⚡ Low | ✅ Done |
| Phase 2: Streaming | 2-3 weeks | ⚡⚡ Medium | 📋 Planned |
| Phase 3: Enhanced CLI | 1 week | ⚡⚡ Medium | 📋 Planned |
| Phase 4: GUI App | 2-3 weeks | ⚡⚡⚡ High | 📋 Planned |
| Phase 5: Advanced | 4 weeks | ⚡⚡⚡ High | 📋 Planned |
| Phase 6: Distribution | Ongoing | ⚡⚡ Medium | 📋 Planned |

**Total estimated time:** 10-12 weeks for Phase 1-5

---

## 🤝 How to Contribute

Want to help build Locivox? Here's where you can jump in:

### Beginner-Friendly
- [ ] Documentation improvements
- [ ] Bug fixes
- [ ] Test coverage
- [ ] UI/UX design

### Intermediate
- [ ] New output format support
- [ ] Audio preprocessing filters
- [ ] Performance benchmarking

### Advanced
- [ ] New STT model integrations
- [ ] GUI development
- [ ] Mobile app development
- [ ] Advanced AI features

See `CONTRIBUTING.md` for guidelines (coming soon).

---

**This roadmap is a living document and will be updated as development progresses.**

Last updated: February 2026
