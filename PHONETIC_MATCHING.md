# Phonetic Matching System 🔊

## Overview

Locivox uses phonetic matching to correct speech recognition errors in vocabulary terms. The system supports multiple matching strategies through a plugin architecture.

---

## Why Phonetic Matching?

**The Problem with String Similarity:**
```python
"Pithon" vs "Python":  83% similar ✓ (1 char different)
"Jython" vs "Python":  83% similar ✓ (1 char different)
# Both match equally, but only one sounds like Python!

"coober netes" vs "Kubernetes": 30% similar ✗
# Doesn't match, but sounds identical!
```

**Phonetic matching solves this** by comparing how words SOUND, not how they're spelled.

---

## Available Matchers

### 1. Fuzzy (Default - No Dependencies) ⚡

**Uses:** Edit distance (string similarity)

**Best for:**
- Testing/development
- No additional dependencies needed
- Simple vocabulary

**Limitations:**
- Can't distinguish sound-alikes (Pithon/Jython)
- Misses phonetically similar words (coober netes/Kubernetes)

**Configuration:**
```yaml
vocabulary:
  matching:
    library: "fuzzy"
    fuzzy_threshold: 0.85
```

**Install:** Nothing (built-in)

---

### 2. Jellyfish (Recommended) ⭐

**Uses:** Double Metaphone phonetic algorithm

**Best for:**
- Most users
- Speech-to-text corrections
- Real-world usage

**Why it's better:**
```python
"Pithon"     → "P0N"  = "Python"    ✓
"Jython"     → "J0N"  ≠ "Python"    ✓ (correctly doesn't match)
"coobernetes" → "KBRNTS" = "Kubernetes" ✓
"postgre"    → "PSTK" = "PostgreSQL"  ✓
```

**Configuration:**
```yaml
vocabulary:
  matching:
    library: "jellyfish"
```

**Install:**
```bash
pip install jellyfish
# or
pip install -r requirements-optional.txt
```

---

### 3. Abydos (Advanced) 🔬

**Uses:** 20+ phonetic algorithms (DoubleMetaphone, Soundex, NYSIIS, etc.)

**Best for:**
- Researchers
- Contributors experimenting with algorithms
- Specialized use cases

**Configuration:**
```yaml
vocabulary:
  matching:
    library: "abydos"
    abydos_algorithm: "DoubleMetaphone"  # or Soundex, NYSIIS, etc.
```

**Install:**
```bash
pip install abydos
```

**Available algorithms:** See [Abydos Documentation](https://abydos.readthedocs.io/en/latest/abydos.phonetic.html)

---

## Quick Start

### Default (No Installation)

Works out of the box with fuzzy matching:
```yaml
# config.yaml
vocabulary:
  enabled: true
  file: "./vocabulary.txt"
  matching:
    library: "fuzzy"
    fuzzy_threshold: 0.85
```

### Recommended Setup (Jellyfish)

1. **Install jellyfish:**
   ```bash
   pip install jellyfish
   ```

2. **Update config:**
   ```yaml
   vocabulary:
     enabled: true
     file: "./vocabulary.txt"
     matching:
       library: "jellyfish"  # ← Change this
   ```

3. **Done!** Phonetic matching is now active.

---

## Configuration Reference

```yaml
vocabulary:
  enabled: true
  file: "./vocabulary.txt"
  case_sensitive: false
  
  matching:
    # Matcher library
    library: "jellyfish"  # Options: "fuzzy", "jellyfish", "abydos"
    
    # Fuzzy matching threshold (used by fuzzy matcher or as fallback)
    fuzzy_threshold: 0.85  # 0.0-1.0
    
    # Abydos algorithm (only used if library="abydos")
    abydos_algorithm: "DoubleMetaphone"
  
  terms:
    - correct: "Kubernetes"
      variations: ["coober netes", "kube ernetes"]
```

---

## Testing Different Matchers

### Compare Performance

```python
from src.matchers import MatcherFactory

# Test fuzzy
fuzzy = MatcherFactory.create('fuzzy', threshold=0.85)
print(fuzzy.match("Pithon", "Python"))   # True
print(fuzzy.match("Jython", "Python"))   # True (WRONG!)

# Test jellyfish
jellyfish = MatcherFactory.create('jellyfish')
print(jellyfish.match("Pithon", "Python"))   # True ✓
print(jellyfish.match("Jython", "Python"))   # False ✓ (CORRECT!)

# Test encoding
print(jellyfish.encode("coober netes"))  # ('KBRNTS', None)
print(jellyfish.encode("Kubernetes"))    # ('KBRNTS', None)
```

---

## Adding Custom Matchers

### For Contributors

You can add your own matching algorithm:

```python
from src.matchers import PhoneticMatcher, MatcherFactory

class MyCustomMatcher(PhoneticMatcher):
    """My custom phonetic matching algorithm"""
    
    def __init__(self, my_param: str = "default"):
        super().__init__()
        self.my_param = my_param
    
    def match(self, word1: str, word2: str) -> bool:
        """Implement your matching logic"""
        # Your algorithm here
        return your_logic(word1, word2)

# Register it
MatcherFactory.register('custom', MyCustomMatcher)

# Use it
matcher = MatcherFactory.create('custom', my_param="value")
```

Then update config:
```yaml
vocabulary:
  matching:
    library: "custom"
```

---

## Automatic Fallback

If a matcher library isn't installed, Locivox automatically falls back to fuzzy matching:

```python
# config.yaml says jellyfish
# but jellyfish not installed

# Result: Falls back to fuzzy with a warning
# No crashes, always works
```

**Log output:**
```
WARNING: Failed to load jellyfish matcher: jellyfish library not installed.
         Falling back to fuzzy matcher.
INFO: Fuzzy matcher initialized (threshold=0.85)
```

---

## Performance Comparison

| Matcher | Speed | Accuracy | Dependencies |
|---------|-------|----------|--------------|
| Fuzzy | Fast | Fair | None |
| Jellyfish | Fast | Excellent | jellyfish (~200KB) |
| Abydos | Medium | Varies | abydos (~2MB) |

**Recommendation:** Use jellyfish for best balance of speed and accuracy.

---

## Real-World Examples

### Speech Recognition Errors → Corrections

**With Fuzzy (Default):**
```
"coober netes" → No match ✗
"post gres" → No match ✗
"Pithon" → "Python" ✓
"Jython" → "Python" ✗ (incorrect match)
```

**With Jellyfish (Recommended):**
```
"coober netes" → "Kubernetes" ✓
"post gres" → "PostgreSQL" ✓
"Pithon" → "Python" ✓
"Jython" → No match ✓ (correctly no match)
```

---

## Troubleshooting

### Matcher not loading

**Error:**
```
ImportError: jellyfish library not installed
```

**Solution:**
```bash
pip install jellyfish
```

### Too many false matches

**Issue:** Words matching that shouldn't

**Solution:** Try different matchers:
```yaml
# More strict
library: "fuzzy"
fuzzy_threshold: 0.90  # Higher = more strict
```

### Not enough matches

**Issue:** Words not matching that should

**Solution:**
```yaml
# More lenient
library: "jellyfish"  # Better for phonetic similarity
```

---

## Migration Guide

### From Old Config (Phase 3 Release)

**Old:**
```yaml
vocabulary:
  fuzzy_threshold: 0.85
```

**New:**
```yaml
vocabulary:
  matching:
    library: "fuzzy"
    fuzzy_threshold: 0.85
```

**Backward compatibility:** Old configs still work (fuzzy_threshold at root level is supported).

---

## Summary

✅ **Default:** Fuzzy matching (no dependencies)  
⭐ **Recommended:** Jellyfish (best for speech-to-text)  
🔬 **Advanced:** Abydos (for researchers)  
🔧 **Extensible:** Add your own matcher  
🛡️ **Safe:** Auto-fallback if library missing  

**For 90% of users:** Install jellyfish and update config. Done.

---

## References

- [Jellyfish Documentation](https://github.com/jamesturk/jellyfish)
- [Abydos Documentation](https://abydos.readthedocs.io/)
- [Double Metaphone Algorithm](https://en.wikipedia.org/wiki/Metaphone)
- [Soundex Algorithm](https://en.wikipedia.org/wiki/Soundex)
