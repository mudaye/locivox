# Phase 3: Personal Assistant Foundation 🎯

## New Features

### ✨ Custom Vocabulary (Day 1-3)
- Domain-specific term recognition
- Fuzzy matching for common mishearings
- Case-sensitive or insensitive matching
- Inline or file-based vocabulary

### 🚀 Batch Processing (Day 4-5) - COMING SOON
- Process multiple files at once
- Progress tracking
- Error handling and retry

### 👀 Folder Watching (Day 6-7) - COMING SOON
- Auto-transcribe new files
- Watch mode for continuous processing
- File pattern matching

---

## Custom Vocabulary Usage

### Quick Start

**1. Enable in config.yaml:**
```yaml
vocabulary:
  enabled: true
  file: "./vocabulary.txt"
```

**2. Add your terms to vocabulary.txt:**
```
# Your terms
Kubernetes: coober netes, kube ernetes
PostgreSQL: postgres, postgre
YourProjectName
```

**3. Run streaming:**
```bash
python -m src.cli_streaming
```

Now when you say "coober netes", it automatically corrects to "Kubernetes"!

---

## Vocabulary File Format

```
# Comments start with #

# Simple term (exact match)
Python

# Term with variations (common mishearings)
FastAPI: fast api, fast a p i

# Multiple variations
Kubernetes: coober netes, kube ernetes, k8s, k 8 s

# Case matters if case_sensitive: true
PostgreSQL: postgres, postgre, post gres
```

---

## Configuration Options

```yaml
vocabulary:
  enabled: true             # Turn on/off
  file: "./vocabulary.txt"  # Path to vocab file
  case_sensitive: false     # Match case exactly?
  fuzzy_threshold: 0.85     # Similarity threshold (0.0-1.0)
  
  # Inline terms (optional, instead of file)
  terms:
    - correct: "Kubernetes"
      variations: ["coober netes", "kube ernetes"]
    - correct: "FastAPI"
      variations: ["fast api"]
```

### Parameters Explained:

**case_sensitive:**
- `false` (default): "kubernetes" → "Kubernetes"
- `true`: Only exact case matches

**fuzzy_threshold:**
- `0.85` (default): Pretty strict
- `0.7`: More lenient (more corrections)
- `1.0`: Exact matches only (no fuzzy)

**How fuzzy matching works:**
- "coobernetes" → "Kubernetes" (85% similar)
- "post gres" → "PostgreSQL" (fuzzy match)

---

## Examples

### For Software Development

```
# Languages
Python
JavaScript: java script
TypeScript: type script
Go: golang

# Frameworks
React
Vue.js: view, view js
Django
FastAPI: fast api
```

### For Medical/Healthcare

```
# Medical terms
hypertension: high blood pressure
diabetes: diabeetus
pneumonia: new monia
```

### For Your Personal Assistant

```
# Your project names
ProjectAlpha: project alpha
ClientXYZ: client x y z

# People you talk about
JohnDoe: john, doe
TeamMemberName

# Your domain terms
YourCompanyName
YourProductName
```

---

## Testing Vocabulary

**Test with streaming:**
```bash
python -m src.cli_streaming
```

Say: "I'm working with coober netes and fast api"  
Output: "I'm working with Kubernetes and FastAPI"

**Check what was replaced:**
Look in logs for:
```
[DEBUG] Applied 2 replacements: ['coober netes → Kubernetes (1x)', 'fast api → FastAPI (1x)']
```

---

## Tips & Tricks

### 1. Start Small
Add just the terms YOU use most:
```
# Just my current projects
CurrentProject
ClientName
TechStackTerm: common mistake
```

### 2. Add as You Go
Hear a mistake? Add it immediately:
```
# Heard today: "reactor" instead of "React"
React: reactor
```

### 3. Use Fuzzy Matching for Flexible Names
```
# Catches: "kube ernetes", "coobernetes", etc.
Kubernetes: coober netes, kube ernetes
# Fuzzy will catch similar variations automatically
```

### 4. Technical Acronyms
```
# Spell-outs
API: a p i, ay pee eye
REST: r e s t
JWT: j w t, jay double u tee
AWS: a w s
```

### 5. Brand Names
```
# Common mishearings
PostgreSQL: postgres, post gres, postgre s q l
MongoDB: mongo, mongo db
Redis: reddis, redis
```

---

## Performance Impact

**Minimal!**
- Direct replacements: < 1ms per transcription
- Fuzzy matching: ~5-10ms per transcription
- No noticeable lag

---

## Troubleshooting

### Corrections not working?

**1. Check vocabulary is enabled:**
```yaml
vocabulary:
  enabled: true  # ← Make sure this is true
```

**2. Check file path:**
```yaml
file: "./vocabulary.txt"  # ← File exists?
```

**3. Check file format:**
```
# ✅ Correct
Kubernetes: coober netes

# ❌ Wrong (no colon)
Kubernetes coober netes
```

**4. Enable debug logging:**
```yaml
logging:
  level: "DEBUG"  # See what's being replaced
```

### Too many false corrections?

**Increase fuzzy threshold:**
```yaml
fuzzy_threshold: 0.90  # More strict (fewer corrections)
```

**Or disable fuzzy entirely:**
```yaml
fuzzy_threshold: 1.0  # Exact matches only
```

### Corrections changing wrong words?

**Use case-sensitive matching:**
```yaml
case_sensitive: true
```

**Or be more specific in variations:**
```
# Instead of just "go"
Go: golang, go lang
```

---

## Coming Soon (Days 4-7)

### Batch Processing
```bash
# Transcribe folder of recordings
locivox batch ./meeting_recordings/

# With vocabulary
locivox batch ./notes/ --vocab my_terms.txt
```

### Folder Watching
```bash
# Auto-transcribe new files
locivox watch ./voice_notes/

# Watch with vocabulary
locivox watch ./notes/ --vocab tech_terms.txt
```

---

## Integration with Future Features

**Phase 4 (GUI):**
- Visual vocabulary editor
- Test vocabulary in real-time
- Import/export vocab files

**Phase 5 (Smart Features):**
- Auto-learn new terms from corrections
- Suggest vocabulary from your notes
- Context-aware replacements

---

## Example: Complete Personal Assistant Setup

**vocabulary.txt:**
```
# My Projects
ProjectAlpha
ProjectBeta: beta project
ClientAcme: acme, a c m e

# My Team
AliceSmith: alice
BobJones: bob

# Tech Stack
Python
FastAPI: fast api
PostgreSQL: postgres
Docker
Kubernetes: coober netes

# My Notes Categories  
meeting: meating
todo: to do
idea: idear
```

**config.yaml:**
```yaml
vocabulary:
  enabled: true
  file: "./vocabulary.txt"
  case_sensitive: false
  fuzzy_threshold: 0.85
```

**Usage:**
```bash
# Real-time note taking
python -m src.cli_streaming

# Say: "Meeting with alice about project beta and fast api"
# Output: "Meeting with AliceSmith about ProjectBeta and FastAPI"
```

---

**Phase 3 Day 1-3: Custom Vocabulary COMPLETE!** ✅

Next up: Batch Processing (Day 4-5) 🚀
