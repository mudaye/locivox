# Phase 3: Personal Assistant Foundation - COMPLETE! 🎉

## Overview

Phase 3 transforms Locivox into a powerful personal note-taking assistant with three major features:

1. **Custom Vocabulary** - Recognize your domain-specific terms
2. **Batch Processing** - Transcribe multiple files at once
3. **Folder Watching** - Auto-transcribe new audio files

Perfect for creating a personal knowledge base from voice notes!

---

## 🎯 Feature 1: Custom Vocabulary

### Quick Start

**Enable vocabulary:**
```yaml
# config.yaml
vocabulary:
  enabled: true
  file: "./vocabulary.txt"
```

**Add your terms:**
```
# vocabulary.txt
YourProjectName
Kubernetes: coober netes
PostgreSQL: postgres
```

**Use it:**
```bash
python -m src.cli_streaming
# Say: "Working on coober netes"
# Output: "Working on Kubernetes"
```

### Full Documentation
See `PHASE3_VOCABULARY.md` for complete guide.

---

## 📦 Feature 2: Batch Processing

### Configuration

```yaml
# config.yaml
batch:
  extensions: [".wav", ".mp3", ".flac", ".m4a", ".ogg", ".opus"]
  recursive: false          # Process subdirectories
  overwrite: false          # Overwrite existing transcriptions
  show_progress: true       # Show progress bar
  save_report: false        # Auto-save processing report
  report_file: "./batch_report.json"
```

### Process Directory

```bash
# Process all audio files in directory
python -m src.cli_batch ./meeting_recordings/

# With output directory
python -m src.cli_batch ./meetings/ --output ./transcripts/

# Recursive (include subdirectories)
python -m src.cli_batch ./recordings/ --recursive

# Overwrite existing transcriptions
python -m src.cli_batch ./files/ --overwrite
```

### Process Specific Files

```bash
# Transcribe specific files
python -m src.cli_batch file1.wav file2.mp3 file3.flac

# With custom output
python -m src.cli_batch *.wav --output ./done/
```

### Options

```bash
python -m src.cli_batch [input] [options]

Options:
  --output, -o DIR        Output directory
  --config FILE           Config file (default: config.yaml)
  --model SIZE            Model size (tiny, base, small, medium, large)
  --device DEVICE         Device (cpu or cuda)
  --format FORMAT         Output format (txt, json, srt)
  --vocab FILE            Custom vocabulary file
  --enable-vocab          Enable vocabulary (uses config or --vocab)
  --recursive, -r         Process subdirectories
  --overwrite             Overwrite existing files
  --extensions EXT...     File types (e.g., .wav .mp3)
  --report FILE           Save processing report
```

### Examples

```bash
# Use tiny model for speed
python -m src.cli_batch ./files/ --model tiny

# Use GPU
python -m src.cli_batch ./files/ --device cuda

# JSON output
python -m src.cli_batch ./files/ --format json

# With vocabulary
python -m src.cli_batch ./files/ --vocab my_terms.txt

# All together
python -m src.cli_batch ./recordings/ \
  --model small \
  --format json \
  --vocab tech_terms.txt \
  --output ./transcripts/ \
  --recursive
```

### Output

```
🎤 Processing 15 files...

Transcribing: 100%|████████████████| 15/15 [02:34<00:00, 10.27s/file]

============================================================
BATCH PROCESSING SUMMARY
============================================================
Total files: 15
Successful: 14 ✅
Failed: 1 ❌
Skipped: 0 ⏭️
Total duration: 1234.5s
Total words: 12,567
Average file duration: 88.2s
============================================================
```

### Save Report

```bash
python -m src.cli_batch ./files/ --report report.json
```

**Report contains:**
- Statistics
- Error details
- Processing timestamp
- Configuration used

---

## 👀 Feature 3: Folder Watching

### Configuration

```yaml
# config.yaml
watcher:
  poll_interval: 2.0        # Seconds between directory scans
  process_existing: false   # Process files that exist at startup
  extensions: [".wav", ".mp3", ".flac", ".m4a", ".ogg", ".opus"]
```

### Auto-Transcribe New Files

```bash
# Watch directory for new audio files
python -m src.watcher ./voice_notes/

# With custom output
python -m src.watcher ./notes/ --output ./transcripts/

# Process existing files at startup
python -m src.watcher ./inbox/ --process-existing

# Custom poll interval
python -m src.watcher ./dir/ --interval 5.0
```

### Options

```bash
python -m src.watcher DIRECTORY [options]

Options:
  --output, -o DIR         Output directory
  --config FILE            Config file
  --model SIZE             Model size (tiny, base, small, medium, large)
  --device DEVICE          Device (cpu or cuda)
  --format FORMAT          Output format (txt, json, srt)
  --vocab FILE             Custom vocabulary file
  --enable-vocab           Enable vocabulary (uses config or --vocab)
  --extensions EXT...      File types to watch
  --interval SECONDS       Poll interval (default: 2.0)
  --process-existing       Transcribe existing files
```

### Examples

```bash
# Use tiny model for speed
python -m src.watcher ./notes/ --model tiny

# Use GPU for faster processing
python -m src.watcher ./recordings/ --device cuda

# JSON output
python -m src.watcher ./voice_notes/ --format json

# With vocabulary
python -m src.watcher ./notes/ --vocab my_terms.txt

# Complete setup
python -m src.watcher ./inbox/ \
  --model base \
  --format txt \
  --vocab work_terms.txt \
  --output ./transcripts/ \
  --interval 1.0 \
  --process-existing
```

### How It Works

1. **Start watcher** - Monitors directory every 2 seconds
2. **Detect new file** - When audio file appears
3. **Wait for complete** - Ensures file fully written
4. **Auto-transcribe** - Processes automatically
5. **Save output** - Transcription saved to output dir

### Output

```
============================================================
👀 FOLDER WATCHER - Auto-Transcription Active
============================================================
Watching: ./voice_notes
Output: ./output
Extensions: .wav, .mp3, .flac, .m4a, .ogg, .opus
Poll interval: 2.0s

Waiting for new audio files... (Press Ctrl+C to stop)
============================================================

🎤 New file detected: note_001.wav
   Transcribing (45.2s)...
   ✅ Transcribed in 8.3s (5.4x speed)
   💾 Saved to: note_001.txt
   📝 Preview: Today I had a great meeting about the Kubernetes...

🎤 New file detected: idea_002.mp3
   Transcribing (23.1s)...
   ✅ Transcribed in 4.2s (5.5x speed)
   💾 Saved to: idea_002.txt
   📝 Preview: New feature idea for the FastAPI backend...
```

### Use Cases

**Personal Knowledge Base:**
```bash
# Watch your voice notes folder
python -m src.watcher ~/VoiceNotes/ --output ~/Transcripts/

# Record voice note → Auto-transcribed immediately
```

**Meeting Recordings:**
```bash
# Watch meeting recordings folder
python -m src.watcher ./Meetings/ --extensions .m4a --output ./MeetingNotes/
```

**Podcast/Interview Workflow:**
```bash
# Watch recordings, auto-process
python -m src.watcher ./Recordings/ --process-existing
```

---

## 🔄 Complete Workflow Examples

### Example 1: Daily Voice Notes

**Setup:**
```bash
# Start watcher in background
python -m src.watcher ~/VoiceNotes/ --output ~/KnowledgeBase/
```

**Usage:**
1. Record voice note on phone
2. Save to ~/VoiceNotes/
3. Auto-transcribed instantly
4. Text appears in ~/KnowledgeBase/

**With vocabulary:**
```yaml
# config.yaml
vocabulary:
  enabled: true
  terms:
    - correct: "ProjectAlpha"
    - correct: "ClientAcme"
```

### Example 2: Meeting Archive

**Process old meetings:**
```bash
# Batch process archive
python -m src.cli_batch ./MeetingArchive/ --recursive --output ./Transcripts/
```

**Watch for new meetings:**
```bash
# Auto-process new recordings
python -m src.watcher ./MeetingRecordings/ --output ./Transcripts/
```

### Example 3: Personal Assistant

**vocabulary.txt:**
```
# My life
ProjectWork: project work
GymSession: gym, workout
Meditation: meditate, meditation
Shopping: groceries, shop

# People
Alice
Bob
Charlie: charlie, charles

# Tech
Python
Kubernetes: k8s, coober netes
Docker
```

**Workflow:**
```bash
# Start watcher with vocabulary
python -m src.watcher ~/Notes/ --output ~/Knowledge/
```

**Say:** "Had gym session then worked on project work with charlie about coober netes"  
**Get:** "Had GymSession then worked on ProjectWork with Charlie about Kubernetes"

---

## 📊 Output Formats

All features support multiple output formats:

```yaml
# config.yaml
output:
  format: "txt"  # Options: txt, json, srt
```

### TXT (Plain Text)
```
This is the transcribed text.
Simple and readable.
```

### JSON (Structured)
```json
{
  "text": "Full transcription here",
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "First segment"
    }
  ],
  "language": "en"
}
```

### SRT (Subtitles)
```
1
00:00:00,000 --> 00:00:02,500
First segment

2
00:00:02,500 --> 00:00:05,000
Second segment
```

---

## 🎯 Performance Tips

### Batch Processing

**For large batches:**
- Use `--report` to track progress
- Process overnight if many files
- Use `--recursive` carefully (can be many files)

**For faster processing:**
```yaml
# Use smaller model
model:
  size: "tiny"  # Or "base"
```

### Folder Watching

**Poll interval:**
- `2.0s` (default) - Good balance
- `1.0s` - More responsive, more CPU
- `5.0s` - Less responsive, less CPU

**File readiness:**
- Watcher waits 0.5s to ensure file complete
- Checks file size stability
- Safe for files copied over network

---

## 🐛 Troubleshooting

### Batch Processing Issues

**"No files found"**
```bash
# Check extensions
python -m src.cli_batch ./dir/ --extensions .wav .mp3

# Check path
ls ./dir/  # Verify files exist
```

**"Permission denied"**
```bash
# Check write permissions on output directory
chmod 755 ./output/
```

### Folder Watching Issues

**Not detecting new files**
- Check poll interval (try lower value)
- Verify file extensions match
- Check directory path is correct

**Processing old files**
```bash
# Add --process-existing to transcribe files at startup
python -m src.watcher ./dir/ --process-existing
```

**Files transcribed multiple times**
- Watcher tracks processed files
- Restart watcher = processes new files only
- Use `--process-existing` only on first run

---

## 💡 Pro Tips

### 1. Combine Features

**Watch + Vocabulary:**
```bash
# Auto-transcribe with term correction
# Just enable vocabulary in config.yaml
python -m src.watcher ./notes/
```

### 2. Archive Strategy

**Daily:**
```bash
# Watch for new notes
python -m src.watcher ~/TodayNotes/
```

**Weekly:**
```bash
# Batch process week's notes
python -m src.cli_batch ~/ThisWeek/ --output ~/Archive/Week_$(date +%V)/
```

### 3. Multiple Watch Folders

**Terminal 1:**
```bash
python -m src.watcher ~/PersonalNotes/
```

**Terminal 2:**
```bash
python -m src.watcher ~/WorkNotes/ --output ~/WorkTranscripts/
```

### 4. Backup Original Audio

```bash
# Process but keep originals
python -m src.cli_batch ./audio/ --output ./transcripts/
# Audio files stay in ./audio/
# Transcripts go to ./transcripts/
```

---

## 🚀 Phase 3 Complete!

### What We Built

✅ **Custom Vocabulary** (Day 1-3)
- Domain-specific term recognition
- Fuzzy matching
- File or inline configuration

✅ **Batch Processing** (Day 4-5)
- Multi-file transcription
- Progress tracking
- Error handling and reports

✅ **Folder Watching** (Day 6-7)
- Auto-transcribe new files
- Continuous monitoring
- Real-time processing

---

## 📈 What's Next?

**Phase 4: GUI** (Optional)
- Visual interface
- Drag & drop
- Settings panel

**Phase 5: Smart Features** (Future)
- Auto-tagging
- Summarization
- Search & indexing
- AI integration

---

## 📚 All Commands Reference

```bash
# Phase 1: Basic transcription
python -m src.cli                              # Interactive recording
python -m src.cli file.wav                     # Transcribe file

# Phase 2: Real-time streaming
python -m src.cli_streaming                    # Stream transcription
python -m src.cli_streaming --model small      # With specific model

# Phase 3: Enhanced features
python -m src.cli_batch ./files/               # Batch processing
python -m src.cli_batch file1.wav file2.mp3    # Specific files
python -m src.watcher ./folder/                # Watch folder
python -m src.watcher ./notes/ --process-existing  # Process existing too
```

---

**Phase 3: Personal Assistant Foundation - COMPLETE! 🎊**

Your Locivox is now a powerful voice-to-text personal assistant!
