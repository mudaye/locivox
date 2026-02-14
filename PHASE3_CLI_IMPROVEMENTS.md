# Phase 3 CLI Improvements - FIXED!

## What Was Missing (You Were Right!)

❌ No config sections for batch/watcher  
❌ No way to select model from CLI  
❌ No way to select device from CLI  
❌ No way to override format from CLI  
❌ No way to use custom vocabulary from CLI  

**Result:** Users stuck with config.yaml settings - not flexible!

---

## ✅ What's Fixed

### 1. Config Sections Added

**config.yaml now has:**

```yaml
# Batch Processing Settings (Phase 3)
batch:
  extensions: [".wav", ".mp3", ".flac", ".m4a", ".ogg", ".opus"]
  recursive: false
  overwrite: false
  show_progress: true
  save_report: false
  report_file: "./batch_report.json"

# Folder Watching Settings (Phase 3)
watcher:
  poll_interval: 2.0
  process_existing: false
  extensions: [".wav", ".mp3", ".flac", ".m4a", ".ogg", ".opus"]
```

---

### 2. CLI Arguments Added

**Batch CLI (`cli_batch.py`):**

```bash
python -m src.cli_batch [input] [options]

New options:
  --model SIZE            # tiny, base, small, medium, large
  --device DEVICE         # cpu or cuda
  --format FORMAT         # txt, json, srt
  --vocab FILE            # Custom vocabulary file
  --enable-vocab          # Enable vocabulary from config
```

**Watcher CLI (`watcher.py`):**

```bash
python -m src.watcher [directory] [options]

New options:
  --model SIZE            # tiny, base, small, medium, large
  --device DEVICE         # cpu or cuda
  --format FORMAT         # txt, json, srt
  --vocab FILE            # Custom vocabulary file
  --enable-vocab          # Enable vocabulary from config
```

---

## 🎯 Now You Can

### Use Tiny Model for Speed

```bash
# Batch
python -m src.cli_batch ./files/ --model tiny

# Watcher
python -m src.watcher ./notes/ --model tiny
```

### Use GPU if Available

```bash
# Batch
python -m src.cli_batch ./files/ --device cuda

# Watcher
python -m src.watcher ./notes/ --device cuda
```

### Override Output Format

```bash
# JSON output
python -m src.cli_batch ./files/ --format json

# SRT subtitles
python -m src.watcher ./videos/ --format srt
```

### Use Custom Vocabulary

```bash
# Batch with vocab
python -m src.cli_batch ./meetings/ --vocab work_terms.txt

# Watcher with vocab
python -m src.watcher ./notes/ --vocab my_terms.txt

# Or enable config vocab
python -m src.cli_batch ./files/ --enable-vocab
```

### Combine Everything

```bash
# Batch: tiny model, GPU, JSON, vocabulary
python -m src.cli_batch ./recordings/ \
  --model tiny \
  --device cuda \
  --format json \
  --vocab tech_terms.txt \
  --output ./transcripts/ \
  --recursive

# Watcher: small model, vocabulary, fast polling
python -m src.watcher ./inbox/ \
  --model small \
  --vocab work_terms.txt \
  --format txt \
  --interval 1.0 \
  --process-existing
```

---

## 📊 Complete CLI Options

### Batch Processing

```bash
python -m src.cli_batch INPUT [options]

Required:
  INPUT                   Directory or file(s) to process

Configuration:
  --config FILE           Config file (default: config.yaml)
  --model SIZE            Override model (tiny/base/small/medium/large)
  --device DEVICE         Override device (cpu/cuda)
  --format FORMAT         Override format (txt/json/srt)

Vocabulary:
  --vocab FILE            Use custom vocabulary file
  --enable-vocab          Enable vocabulary from config

Processing:
  --output, -o DIR        Output directory
  --recursive, -r         Process subdirectories
  --overwrite             Overwrite existing files
  --extensions EXT...     File extensions (e.g., .wav .mp3)
  --report FILE           Save processing report
```

### Folder Watching

```bash
python -m src.watcher DIRECTORY [options]

Required:
  DIRECTORY               Directory to watch

Configuration:
  --config FILE           Config file (default: config.yaml)
  --model SIZE            Override model (tiny/base/small/medium/large)
  --device DEVICE         Override device (cpu/cuda)
  --format FORMAT         Override format (txt/json/srt)

Vocabulary:
  --vocab FILE            Use custom vocabulary file
  --enable-vocab          Enable vocabulary from config

Watching:
  --output, -o DIR        Output directory
  --interval SECONDS      Poll interval (default: 2.0)
  --process-existing      Process files at startup
  --extensions EXT...     File extensions to watch
```

---

## 🎉 Much Better Now!

**Before:** Stuck with config.yaml  
**After:** Full CLI control!

All CLIs now consistent:
- ✅ `cli.py` - Model, device, format options
- ✅ `cli_streaming.py` - Model, device options
- ✅ `cli_batch.py` - Model, device, format, vocab options ← FIXED!
- ✅ `watcher.py` - Model, device, format, vocab options ← FIXED!

---

**Thanks for catching this!** 🙏
