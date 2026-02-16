"""
Punctuation Improvement
Basic rules-based punctuation correction
"""

import re
import logging


class PunctuationImprover:
    """Apply basic punctuation rules to improve transcription"""
    
    def __init__(self):
        self.logger = logging.getLogger('locivox.punctuation')
        
    def improve(self, text: str) -> str:
        """
        Apply punctuation improvements to text
        
        Args:
            text: Raw transcription text
            
        Returns:
            Text with improved punctuation
        """
        if not text:
            return text
        
        # Apply rules in order
        text = self._remove_whisper_artifacts(text)  # Clean Whisper's artifacts first
        text = self._fix_spacing(text)
        text = self._capitalize_first_word(text)
        text = self._fix_common_issues(text)
        text = self._add_missing_punctuation(text)
        text = self._capitalize_after_punctuation(text)
        text = self._final_cleanup(text)
        
        return text
    
    def _remove_whisper_artifacts(self, text: str) -> str:
        """Remove artifacts that Whisper adds"""
        # Remove ellipses that Whisper adds for pauses/uncertainty
        text = text.replace('...', '')
        text = text.replace('..', '')
        
        # Remove multiple spaces that might result
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _add_missing_punctuation(self, text: str) -> str:
        """Add missing periods between sentences"""
        # Pattern 1: lowercase word followed by uppercase word
        text = re.sub(r'([a-z])\s+([A-Z])', r'\1. \2', text)
        
        # Pattern 2: number/digit followed by uppercase word (like "3 Once")
        text = re.sub(r'(\d)\s+([A-Z])', r'\1. \2', text)
        
        # Pattern 3: lowercase word followed by number at start of sentence
        text = re.sub(r'([a-z])\s+(\d+\s+[A-Z])', r'\1. \2', text)
        
        # Add period at end if missing
        text = text.strip()
        if text and text[-1] not in '.!?':
            # Check if it's a complete statement
            ending_words = ['yes', 'no', 'okay', 'ok', 'sure', 'done', 'thanks', 
                          'thank you', 'right', 'correct', 'exactly', 'definitely']
            last_words = ' '.join(text.lower().split()[-2:])  # Last two words
            
            if any(last_words.endswith(word) for word in ending_words):
                text += '.'
            elif len(text.split()) > 3:  # Longer sentences get periods
                text += '.'
        
        return text
    
    def _capitalize_first_word(self, text: str) -> str:
        """Capitalize the first word"""
        if text:
            return text[0].upper() + text[1:]
        return text
    
    def _capitalize_after_punctuation(self, text: str) -> str:
        """Capitalize words after sentence-ending punctuation"""
        # First ensure there's space after punctuation
        text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
        
        # Split by sentence endings
        sentences = re.split(r'([.!?]\s+)', text)
        
        result = []
        capitalize_next = True  # Capitalize first word
        
        for part in sentences:
            if part.strip() in ['.', '!', '?'] or re.match(r'^[.!?]\s+$', part):
                # Punctuation part
                result.append(part)
                capitalize_next = True
            elif part and capitalize_next:
                # Capitalize first character of this part
                part = part[0].upper() + part[1:] if len(part) > 1 else part.upper()
                result.append(part)
                capitalize_next = False
            else:
                result.append(part)
        
        return ''.join(result)
    
    def _fix_spacing(self, text: str) -> str:
        """Fix spacing issues"""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,!?])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([.,!?])([A-Za-z])', r'\1 \2', text)  # Add space after punctuation
        
        # Fix common number/punctuation issues
        text = re.sub(r'(\d)\s*,\s*(\d)', r'\1, \2', text)  # "1,2,3" → "1, 2, 3"
        
        return text.strip()
    
    def _final_cleanup(self, text: str) -> str:
        """Final cleanup pass"""
        # Remove duplicate punctuation
        text = re.sub(r'\.+', '.', text)  # Multiple periods → one
        text = re.sub(r'\?+', '?', text)
        text = re.sub(r'!+', '!', text)
        
        # Fix sentence spacing
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
        
        # Ensure proper spacing after punctuation
        text = re.sub(r'([.!?,])\s+', r'\1 ', text)
        
        return text.strip()
    
    def _fix_common_issues(self, text: str) -> str:
        """Fix common transcription issues"""
        replacements = {
            ' i ': ' I ',  # Capitalize standalone I
            " i'": " I'",  # I'm, I'll, etc.
            "i ": "I ",    # I at start
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Capitalize I at the beginning
        if text.startswith('i '):
            text = 'I' + text[1:]
        
        return text


# Global instance
_improver = None


def get_improver() -> PunctuationImprover:
    """Get or create punctuation improver instance"""
    global _improver
    if _improver is None:
        _improver = PunctuationImprover()
    return _improver


def improve_punctuation(text: str) -> str:
    """
    Convenience function to improve punctuation
    
    Args:
        text: Raw text
        
    Returns:
        Text with improved punctuation
    """
    return get_improver().improve(text)
