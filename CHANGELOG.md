# Changelog

All notable changes to Locivox will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.1] - 2026-02-17

### Fixed
- Correct GitHub repository URLs in package metadata

## [0.4.0] - 2026-02-17

### Added
- Full PyQt6 GUI with real-time transcription display
- Settings dialog (model, audio, streaming, vocabulary, advanced tabs)
- Vocabulary Manager — CRUD, import/export, fuzzy/phonetic test matcher
- Right-click word correction with optional vocabulary integration
- Analytics module — session tracking, deduplication/punctuation/vocab events, auto-export
- Word-level timestamps from Faster-Whisper throughout the pipeline
- SRT export with real word-level timestamps (millisecond precision)
- JSON export with `words[]` and `segments[]` arrays
- Timestamp-based deduplication replacing word-matching (resolves punctuation edge cases)
- Graceful fallback for models without word timestamp support
- Custom vocabulary file format v2 (multi-line `correct:` / `- variation` blocks)

### Fixed
- Vocabulary corrections replacing words with literal "correct" (file format mismatch)
- Punctuation rules (`add_periods`, `capitalize_first`) firing on mid-sentence chunks
- Word timestamps lost after recording stopped (worker lifecycle caching)
- `chunk_start_offset` advancing by full chunk duration instead of step duration
- Vocabulary analytics misattributed to punctuation events
- `VocabularyManager` attribute error in GUI worker thread
- Duplicate words in timestamp export arrays

### Changed
- Punctuation pipeline now only applies safe rules (spacing, artifact removal)
  — Whisper's own capitalization and sentence-ending periods are preserved
- Analytics vocabulary events now only fire on genuine vocabulary matches
- Debug logging cleaned from production paths (transcriber, streaming, SRT export)

## [0.1.0] - 2026-02-13

### Added
- Initial release of Locivox CLI
- Model-agnostic STT architecture with factory pattern
- Support for Faster-Whisper engine (recommended)
- Support for OpenAI-Whisper engine
- Real-time microphone recording with device selection
- Audio file transcription support (WAV, MP3, FLAC, OGG, M4A)
- Multiple output formats (TXT, JSON, SRT)
- Automatic language detection
- YAML-based configuration system
- Comprehensive logging system
- CLI argument parsing for flexible usage
- Cross-platform support (Windows, macOS, Linux)
- CPU-optimized inference
- Colored console output for better UX
- Virtual environment setup scripts (setup.sh, setup.bat)
- Complete documentation (README, QUICKSTART, ROADMAP, TROUBLESHOOTING)

### Technical Details
- Python 3.9+ support
- Modular architecture (audio_capture, transcriber, utils, cli)
- Type hints throughout codebase
- Graceful error handling
- Support for model sizes: tiny, base, small, medium, large

### Documentation
- Comprehensive README with installation and usage guide
- Quick start guide (3-minute setup)
- Detailed roadmap with 6-phase development plan
- Troubleshooting guide for common issues
- Project structure documentation
- Contributing guidelines
- Security policy
- GitHub issue and PR templates
- MIT License

### Dependencies
- faster-whisper 1.0.3
- openai-whisper 20231117
- sounddevice 0.4.6
- numpy 1.26.0
- soundfile 0.12.1
- librosa (for resampling)
- torch 2.1.0 (CPU)
- torchaudio 2.1.0
- pyyaml 6.0.1
- colorama 0.4.6
- tqdm 4.66.1

[Unreleased]: https://github.com/yourusername/locivox/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/locivox/releases/tag/v0.1.0
