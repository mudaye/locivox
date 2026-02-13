# Contributing to Locivox

First off, thank you for considering contributing to Locivox! 🎉

## 🌟 How Can I Contribute?

### Reporting Bugs

**Before submitting a bug report:**
- Check the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide
- Search existing [issues](https://github.com/mudaye/locivox/issues) to avoid duplicates

**When submitting a bug report, include:**
- OS and version (Windows 11, macOS 14, Ubuntu 22.04, etc.)
- Python version (`python --version`)
- Complete error message and stack trace
- Steps to reproduce
- Expected vs actual behavior
- Relevant config from `config.yaml`
- Log file contents from `logs/locivox.log`

### Suggesting Features

We love feature ideas! Please:
- Check the [ROADMAP.md](ROADMAP.md) first - it might already be planned
- Search existing feature requests
- Open an issue with the `enhancement` label
- Describe the use case and expected behavior

### Pull Requests

**We welcome PRs for:**
- Bug fixes
- Documentation improvements
- New STT engine integrations
- Performance optimizations
- Test coverage improvements
- New output formats
- UI/UX enhancements

**Before submitting:**
1. Fork the repo
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Update documentation if needed
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

## 🏗️ Development Setup

```bash
# Clone your fork
git clone https://github.com/mudaye/locivox.git
cd locivox

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (coming soon)
# pip install -r requirements-dev.txt

# Run tests (coming soon)
# pytest tests/
```

## 📝 Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Add docstrings to all public functions/classes
- Keep functions focused and small
- Write descriptive variable names
- Add comments for complex logic

**Example:**
```python
def transcribe_audio(audio_data: np.ndarray, language: str = "en") -> Dict[str, Any]:
    """
    Transcribe audio data to text.
    
    Args:
        audio_data: NumPy array of audio samples (float32, mono, 16kHz)
        language: ISO language code or "auto" for detection
        
    Returns:
        Dictionary containing:
            - text: Full transcription
            - segments: List of timestamped segments
            - language: Detected or specified language
            
    Raises:
        RuntimeError: If model not loaded
        ValueError: If audio_data is invalid
    """
    # Implementation
```

## 🧪 Testing Guidelines (Coming Soon)

- Write unit tests for new functions
- Add integration tests for features
- Ensure tests pass before submitting PR
- Aim for >80% code coverage

## 📚 Documentation

- Update README.md if adding features
- Add entries to TROUBLESHOOTING.md for common issues
- Update ROADMAP.md if implementing planned features
- Include docstrings for all public APIs
- Add examples for new functionality

## 🎯 Priority Areas

**Beginner-Friendly:**
- Documentation improvements
- Bug fixes with clear reproduction steps
- Adding tests
- UI/UX polish

**Intermediate:**
- New output format support (VTT, Markdown, PDF)
- Audio preprocessing (noise reduction, normalization)
- Performance benchmarking
- CLI enhancements

**Advanced:**
- New STT model integrations (Vosk, Coqui, wav2vec2)
- Real-time streaming implementation (Phase 2)
- GUI development (Phase 4)
- Speaker diarization (Phase 3)
- Mobile app development

## 💬 Communication

- Use GitHub Issues for bug reports and feature requests
- Use GitHub Discussions for questions and general discussion
- Be respectful and constructive
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md)

## 🏆 Recognition

Contributors will be:
- Listed in the README credits section
- Mentioned in release notes
- Given credit in commit messages

## ❓ Questions?

Not sure where to start? Open an issue with the `question` label or check existing discussions.

Thank you for contributing to Locivox! 🎤✨
