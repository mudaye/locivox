"""
Custom Vocabulary module for Locivox Phase 3
Handles domain-specific term recognition and replacement
"""

import logging
import re
from typing import List, Dict, Optional
from difflib import SequenceMatcher


class VocabularyManager:
    """Manages custom vocabulary and term replacement"""
    
    def __init__(self, config: dict):
        self.logger = logging.getLogger('locivox.vocabulary')
        
        # Vocabulary settings
        vocab_config = config.get('vocabulary', {})
        self.enabled = vocab_config.get('enabled', False)
        self.case_sensitive = vocab_config.get('case_sensitive', False)
        self.fuzzy_threshold = vocab_config.get('fuzzy_threshold', 0.85)
        
        # Term storage
        self.terms = {}  # {correct_term: [variations]}
        self.replacements = {}  # {incorrect -> correct}
        
        # Load terms from config
        self._load_vocabulary(vocab_config)
        
        if self.enabled:
            self.logger.info(f"Vocabulary manager initialized with {len(self.terms)} terms")
    
    def _load_vocabulary(self, config: dict) -> None:
        """Load vocabulary from configuration"""
        # Load from inline terms
        terms_list = config.get('terms', [])
        for term_config in terms_list:
            if isinstance(term_config, str):
                # Simple string term
                self.add_term(term_config)
            elif isinstance(term_config, dict):
                # Term with variations
                correct = term_config.get('correct')
                variations = term_config.get('variations', [])
                if correct:
                    self.add_term(correct, variations)
        
        # Load from file if specified
        vocab_file = config.get('file')
        if vocab_file:
            self.load_from_file(vocab_file)
    
    def add_term(self, correct_term: str, variations: Optional[List[str]] = None) -> None:
        """
        Add a term to vocabulary
        
        Args:
            correct_term: The correct form of the term
            variations: List of common incorrect variations
        """
        if variations is None:
            variations = []
        
        self.terms[correct_term] = variations
        
        # Build replacement map
        for variation in variations:
            if not self.case_sensitive:
                self.replacements[variation.lower()] = correct_term
            else:
                self.replacements[variation] = correct_term
        
        self.logger.debug(f"Added term: {correct_term} with {len(variations)} variations")
    
    def load_from_file(self, filepath: str) -> None:
        """
        Load vocabulary from file
        
        File format:
        correct_term
        correct_term: variation1, variation2, variation3
        # Comments
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse line
                    if ':' in line:
                        # Term with variations
                        correct, variations_str = line.split(':', 1)
                        correct = correct.strip()
                        variations = [v.strip() for v in variations_str.split(',')]
                        self.add_term(correct, variations)
                    else:
                        # Just a term
                        self.add_term(line)
            
            self.logger.info(f"Loaded vocabulary from {filepath}")
        
        except FileNotFoundError:
            self.logger.warning(f"Vocabulary file not found: {filepath}")
        except Exception as e:
            self.logger.error(f"Error loading vocabulary file: {e}")
    
    def apply_vocabulary(self, text: str) -> str:
        """
        Apply vocabulary replacements to text
        
        Args:
            text: Input text
            
        Returns:
            Text with vocabulary corrections applied
        """
        if not self.enabled or not text:
            return text
        
        # Track replacements made
        replacements_made = []
        
        # Direct replacements (exact matches)
        result = self._apply_direct_replacements(text, replacements_made)
        
        # Fuzzy replacements (similarity matching)
        result = self._apply_fuzzy_replacements(result, replacements_made)
        
        # Log replacements
        if replacements_made:
            self.logger.debug(f"Applied {len(replacements_made)} replacements: {replacements_made}")
        
        return result
    
    def _apply_direct_replacements(self, text: str, tracking: List) -> str:
        """Apply exact match replacements"""
        result = text
        
        # Build regex pattern for all variations
        for incorrect, correct in self.replacements.items():
            # Word boundary matching
            if self.case_sensitive:
                pattern = r'\b' + re.escape(incorrect) + r'\b'
                flags = 0
            else:
                pattern = r'\b' + re.escape(incorrect) + r'\b'
                flags = re.IGNORECASE
            
            # Count replacements
            matches = re.findall(pattern, result, flags=flags)
            if matches:
                result = re.sub(pattern, correct, result, flags=flags)
                tracking.append(f"{incorrect} → {correct} ({len(matches)}x)")
        
        return result
    
    def _apply_fuzzy_replacements(self, text: str, tracking: List) -> str:
        """Apply fuzzy matching for similar terms"""
        if self.fuzzy_threshold >= 1.0:
            return text  # Fuzzy matching disabled
        
        words = text.split()
        result_words = []
        
        for word in words:
            # Clean word for comparison
            clean_word = re.sub(r'[^\w\s]', '', word)
            if not clean_word:
                result_words.append(word)
                continue
            
            # Try fuzzy matching against known terms
            best_match = None
            best_score = 0.0
            
            for correct_term in self.terms.keys():
                # Compare
                score = self._similarity(clean_word, correct_term)
                
                if score >= self.fuzzy_threshold and score > best_score:
                    best_score = score
                    best_match = correct_term
            
            if best_match:
                # Preserve case and punctuation
                replacement = self._preserve_case(word, clean_word, best_match)
                result_words.append(replacement)
                if clean_word.lower() != best_match.lower():
                    tracking.append(f"{clean_word} → {best_match} (fuzzy: {best_score:.2f})")
            else:
                result_words.append(word)
        
        return ' '.join(result_words)
    
    def _similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings"""
        if not self.case_sensitive:
            a = a.lower()
            b = b.lower()
        
        return SequenceMatcher(None, a, b).ratio()
    
    def _preserve_case(self, original: str, clean: str, replacement: str) -> str:
        """Preserve punctuation and case from original word"""
        # Get punctuation
        prefix = original[:len(original) - len(original.lstrip())]
        suffix = original[len(original.rstrip()):]
        
        # Match case
        if clean.isupper():
            replacement = replacement.upper()
        elif clean[0].isupper() if clean else False:
            replacement = replacement.capitalize()
        else:
            replacement = replacement.lower()
        
        return prefix + replacement + suffix
    
    def get_stats(self) -> dict:
        """Get vocabulary statistics"""
        return {
            'enabled': self.enabled,
            'num_terms': len(self.terms),
            'num_variations': len(self.replacements),
            'case_sensitive': self.case_sensitive,
            'fuzzy_threshold': self.fuzzy_threshold
        }
