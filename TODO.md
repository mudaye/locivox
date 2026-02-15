# Locivox TODO & Future Features 📋

## Immediate (Day 3) - IN PROGRESS 🔧

### Critical Fixes
- [ ] Remove Pause button (or fix properly)
- [ ] Remove `terms` from config.yaml (move to vocabulary.txt only)
- [ ] Fix duplicate transcription issue
- [ ] Add Export functionality (txt, json, srt)

### High Priority Features
- [ ] Vocabulary correction thread (background processing)
- [ ] Blinking cursor + confidence coloring
- [ ] Basic punctuation improvement (rules-based)
- [ ] Right-click word correction → add to vocabulary

---

## Short Term (Week 1-2) - PLANNED 📅

### GUI Enhancements
- [ ] Settings dialog (model, device, VAD, vocabulary settings)
- [ ] Vocabulary manager dialog (add/edit/delete terms)
- [ ] Copy to clipboard button
- [ ] Auto-save transcription (configurable interval)
- [ ] Session persistence (recover on crash)
- [ ] Undo/Redo for text edits

### Transcription Quality
- [ ] Word-level deduplication (better than current)
- [ ] Timestamp tracking for each word
- [ ] Diff algorithm for smart merging
- [ ] Speaker labels (if multiple speakers detected)

### UX Improvements
- [ ] Status icons (recording, processing, idle)
- [ ] Audio level meter (visual feedback)
- [ ] Keyboard shortcuts guide
- [ ] First-run tutorial
- [ ] Tooltips on all controls

---

## Medium Term (Month 1) - ROADMAP 🗺️

### Entry Modes System ⭐ (DREAM APP FEATURE)
- [ ] Plugin architecture for entry modes
- [ ] Freeform mode (default, no formatting)
- [ ] List mode (auto-bullets, detect items)
- [ ] Journal mode (timestamps, paragraphs)
- [ ] Todo mode (checkboxes, priorities)
- [ ] Brain Dump mode (smart paragraph breaks)
- [ ] Mode selector in UI
- [ ] Per-mode keyboard shortcuts
- [ ] Per-mode auto-save behavior
- [ ] Mode templates/customization

### Advanced Vocabulary ⭐
- [ ] User correction UI (right-click → correct)
- [ ] Vocabulary learning from corrections
- [ ] Import/Export vocabulary
- [ ] Merge multiple vocabulary files
- [ ] Vocabulary suggestions (AI-powered)
- [ ] Context-aware corrections
- [ ] Highlight corrected words in UI

### Advanced Punctuation ⭐
- [ ] Deep learning punctuation model (Option 2 PARKED)
  - Library: deepmultilingualpunctuation
  - Separate thread (like vocab correction)
  - Toggle on/off in settings
  - Model download on first use
  - Fallback to rules if model unavailable
- [ ] Smart capitalization
- [ ] Quote detection
- [ ] Sentence boundary detection
- [ ] Custom punctuation rules

### Clever Rendering ⭐
- [x] Blinking cursor for active transcription
- [x] Confidence coloring (high=black, medium=gray, low=light)
- [ ] Word-by-word appearance animation
- [ ] Typing effect for new text
- [ ] Highlight recent additions
- [ ] Fade-in effect for new words
- [ ] Visual pause indicators

---

## Long Term (Month 2-3) - FUTURE 🔮

### Smart Features
- [ ] Auto-summarization (end of session)
- [ ] Keyword extraction
- [ ] Topic detection
- [ ] Action item extraction (from todos)
- [ ] Meeting minutes template
- [ ] Email draft generation
- [ ] Document structure detection

### Multi-Language
- [ ] Language auto-detection
- [ ] Language switching during recording
- [ ] Multi-language vocabulary
- [ ] Translation mode (transcribe + translate)

### Cloud & Sync
- [ ] Optional cloud backup
- [ ] Cross-device sync
- [ ] Share transcriptions
- [ ] Collaborative editing

### Advanced Audio
- [ ] Background noise suppression
- [ ] Multiple microphone support
- [ ] Audio file import/transcription
- [ ] Batch file processing from GUI
- [ ] Audio quality indicator
- [ ] Noise gate settings

### Packaging & Distribution
- [ ] PyInstaller standalone .exe (Windows)
- [ ] .app bundle (macOS)
- [ ] .deb/.rpm packages (Linux)
- [ ] Installer wizard
- [ ] Auto-updater
- [ ] App icon and branding

---

## Parked Features (Good Ideas, Low Priority) 🅿️

### Advanced Punctuation - Deep Learning Model
**Status:** PARKED (Option 2)  
**Why:** Adds ~500MB model, most users don't need it  
**When:** After basic rules prove insufficient  
**How:** 
```python
from deepmultilingualpunctuation import PunctuationModel
model = PunctuationModel()  # Download on first use
corrected = model.restore_punctuation(text)
```
**Thread:** Separate PunctuationWorker (like VocabularyWorker)  
**Config:** Enable/disable in settings  

### Whisper Prompt Engineering
**Status:** PARKED  
**Why:** Inconsistent results, model-dependent  
**When:** If Whisper adds better prompt support  
**How:**
```python
prompt = "Transcribe with proper punctuation:"
result = model.transcribe(audio, prompt=prompt)
```

### Voice Commands
**Status:** PARKED  
**Why:** Scope creep, niche use case  
**When:** If users request it  
**Examples:**
- "New paragraph" → Insert paragraph break
- "Period" → Add punctuation
- "Delete that" → Remove last sentence
- "Save file" → Trigger save

### Plugins System
**Status:** PARKED  
**Why:** Complex, entry modes cover most needs  
**When:** If community wants to contribute  
**How:** Python plugin loader, API for extensions  

---

## Known Issues 🐛

### Current Bugs
- [x] Duplicate transcription (sometimes entire chunk retranscribed)
  - **Fix:** Track last transcription, deduplicate
- [ ] Interim text not always replaced by final
  - **Debug:** Check cursor positioning logic
- [ ] Occasional audio dropout on pause/resume
  - **Debug:** Buffer management issue

### Performance Issues
- [ ] Model loading takes 2-3 seconds (expected, but could improve)
- [ ] Large vocabulary slows down corrections
  - **Fix:** Index vocabulary, use trie structure
- [ ] Long transcriptions cause UI lag
  - **Fix:** Pagination or virtual scrolling

### Edge Cases
- [ ] What happens if disk full during save?
- [ ] What if vocabulary file is corrupt?
- [ ] What if model download fails?
- [ ] Handle very long recordings (>1 hour)

---

## Research Needed 🔬

### To Investigate
- [ ] Better VAD algorithms (current: silero-vad)
- [ ] Streaming Whisper alternatives (faster-whisper vs whisper.cpp)
- [ ] Real-time speaker diarization
- [ ] Noise reduction preprocessing
- [ ] Custom vocabulary training (fine-tuning Whisper)

### Benchmarking
- [ ] Memory usage over time
- [ ] CPU usage per model size
- [ ] Transcription accuracy by model
- [ ] Latency measurements (audio → display)

---

## Documentation Needed 📚

### User Guides
- [ ] Getting started guide
- [ ] Keyboard shortcuts reference
- [ ] Vocabulary guide (how to add terms)
- [ ] Entry modes tutorial
- [ ] Troubleshooting guide

### Developer Docs
- [ ] Architecture overview
- [ ] Threading model explanation
- [ ] Signal/slot communication map
- [ ] How to add new entry modes
- [ ] How to contribute

---

## Testing Needed 🧪

### Manual Testing
- [ ] Test all export formats
- [ ] Test with different microphones
- [ ] Test with different models (tiny → large)
- [ ] Test long recording sessions (1+ hour)
- [ ] Test with different accents/languages

### Automated Testing
- [ ] Unit tests for vocabulary correction
- [ ] Unit tests for deduplication
- [ ] Integration tests for full pipeline
- [ ] UI tests with pytest-qt
- [ ] Performance regression tests

---

## Community Feedback Needed 💬

### Questions for Users
- [ ] Do you need Pause button? Or just Start/Stop?
- [ ] Which entry modes would you use most?
- [ ] What keyboard shortcuts do you want?
- [ ] How important is deep learning punctuation?
- [ ] Would you use cloud sync?

---

## Version Planning 🎯

### v0.4.0 - GUI Foundation ✅
- [x] PyQt6 desktop GUI
- [x] Real-time transcription
- [x] Microphone selection
- [x] Basic controls

### v0.5.0 - Day 3 Features (Current)
- [ ] Export functionality
- [ ] Duplicate fix
- [ ] Vocab correction thread
- [ ] Blinking cursor + confidence colors
- [ ] Basic punctuation

### v0.6.0 - Entry Modes
- [ ] Plugin architecture
- [ ] 5 entry modes implemented
- [ ] Mode selector UI
- [ ] Per-mode settings

### v0.7.0 - Smart Features
- [ ] User corrections → vocabulary
- [ ] Settings dialog
- [ ] Vocabulary manager
- [ ] Auto-save

### v1.0.0 - Production Ready
- [ ] All major features stable
- [ ] Comprehensive testing
- [ ] User documentation
- [ ] Installers for all platforms

---

## Notes 📝

### Design Decisions
- **Threading:** GUI main thread + workers for audio/transcription/vocab/punctuation
- **Config:** YAML for settings, separate files for data (vocabulary)
- **Extensibility:** Plugin patterns for entry modes, matchers, formatters
- **UX:** Show interim results immediately, refine in background

### Constraints
- **Privacy:** Everything local, no cloud requirements
- **Performance:** Should work on modest hardware (CPU-only)
- **Dependencies:** Minimal required, optional for advanced features
- **Cross-platform:** Windows, Mac, Linux support

---

## How to Use This File

### Adding New TODOs
```markdown
- [ ] Your new task here
```

### Marking Complete
```markdown
- [x] Completed task
```

### Parking Features
Add to "Parked Features" section with:
- **Status:** PARKED
- **Why:** Reason for parking
- **When:** Conditions to unpark
- **How:** Implementation notes

### Moving Items
When priorities change, move between sections:
- Immediate → Short Term → Medium Term → Long Term → Parked

---

## Last Updated
**Date:** 2026-02-15  
**Version:** v0.5.0-dev (Day 3 in progress)  
**By:** Locivox Development Team
