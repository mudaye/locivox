"""
Phonetic matching strategies for vocabulary correction
Supports multiple algorithms: fuzzy, jellyfish, abydos
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional
from difflib import SequenceMatcher


class PhoneticMatcher(ABC):
    """Base class for phonetic matching strategies"""
    
    def __init__(self):
        self.logger = logging.getLogger('locivox.vocabulary.matcher')
    
    @abstractmethod
    def match(self, word1: str, word2: str) -> bool:
        """
        Check if two words match phonetically
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            True if words match, False otherwise
        """
        pass
    
    def encode(self, word: str) -> str:
        """
        Encode word to phonetic representation (optional)
        
        Args:
            word: Word to encode
            
        Returns:
            Phonetic encoding
        """
        return word.lower()


class FuzzyMatcher(PhoneticMatcher):
    """
    Built-in fuzzy string matching (no dependencies)
    Uses edit distance similarity
    """
    
    def __init__(self, threshold: float = 0.85):
        super().__init__()
        self.threshold = threshold
        self.logger.info(f"Fuzzy matcher initialized (threshold={threshold})")
    
    def match(self, word1: str, word2: str) -> bool:
        """Check if words are similar based on edit distance"""
        similarity = SequenceMatcher(None, word1.lower(), word2.lower()).ratio()
        return similarity >= self.threshold
    
    def encode(self, word: str) -> str:
        """No encoding for fuzzy matcher"""
        return word.lower()


class JellyfishMatcher(PhoneticMatcher):
    """
    Jellyfish Metaphone matcher
    Requires: pip install jellyfish
    """
    
    def __init__(self):
        super().__init__()
        try:
            import jellyfish
            self.jellyfish = jellyfish
            self.logger.info("Jellyfish matcher initialized (Metaphone)")
        except ImportError:
            raise ImportError(
                "jellyfish library not installed. "
                "Install with: pip install jellyfish"
            )
    
    def encode(self, word: str) -> str:
        """Encode word using Metaphone"""
        return self.jellyfish.metaphone(word.lower())
    
    def match(self, word1: str, word2: str) -> bool:
        """Check if words sound similar using Metaphone"""
        code1 = self.encode(word1)
        code2 = self.encode(word2)
        
        # Match if phonetic codes are identical
        return code1 == code2


class AbydosMatcher(PhoneticMatcher):
    """
    Abydos phonetic matcher (for contributors/researchers)
    Requires: pip install abydos
    Supports multiple algorithms: DoubleMetaphone, Soundex, NYSIIS, etc.
    """
    
    def __init__(self, algorithm: str = "DoubleMetaphone"):
        super().__init__()
        try:
            from abydos import phonetic
            algo_class = getattr(phonetic, algorithm)
            self.encoder = algo_class()
            self.algorithm = algorithm
            self.logger.info(f"Abydos matcher initialized ({algorithm})")
        except ImportError:
            raise ImportError(
                "abydos library not installed. "
                "Install with: pip install abydos"
            )
        except AttributeError:
            raise ValueError(
                f"Unknown abydos algorithm: {algorithm}. "
                f"See https://abydos.readthedocs.io/en/latest/abydos.phonetic.html"
            )
    
    def encode(self, word: str) -> str:
        """Encode word using configured algorithm"""
        return self.encoder.encode(word.lower())
    
    def match(self, word1: str, word2: str) -> bool:
        """Check if words sound similar using configured algorithm"""
        return self.encode(word1) == self.encode(word2)


class MatcherFactory:
    """Factory for creating phonetic matchers"""
    
    # Registry of available matchers
    _MATCHERS = {
        'fuzzy': FuzzyMatcher,
        'jellyfish': JellyfishMatcher,
        'abydos': AbydosMatcher,
    }
    
    @classmethod
    def create(cls, library: str, **kwargs) -> PhoneticMatcher:
        """
        Create phonetic matcher instance
        
        Args:
            library: Matcher type ('fuzzy', 'jellyfish', 'abydos')
            **kwargs: Additional arguments for matcher
                - threshold: For fuzzy matcher (default: 0.85)
                - algorithm: For abydos matcher (default: 'DoubleMetaphone')
        
        Returns:
            PhoneticMatcher instance
            
        Raises:
            ValueError: If library is unknown
            ImportError: If required library not installed
        """
        if library not in cls._MATCHERS:
            raise ValueError(
                f"Unknown matcher library: {library}. "
                f"Available: {list(cls._MATCHERS.keys())}"
            )
        
        matcher_class = cls._MATCHERS[library]
        
        try:
            return matcher_class(**kwargs)
        except TypeError:
            # No kwargs supported, try without
            return matcher_class()
    
    @classmethod
    def create_with_fallback(cls, library: str, **kwargs) -> PhoneticMatcher:
        """
        Create matcher with automatic fallback to fuzzy if library unavailable
        
        Args:
            library: Preferred matcher type
            **kwargs: Additional arguments
            
        Returns:
            PhoneticMatcher instance (preferred or fallback)
        """
        logger = logging.getLogger('locivox.vocabulary.matcher')
        
        try:
            return cls.create(library, **kwargs)
        except ImportError as e:
            logger.warning(
                f"Failed to load {library} matcher: {e}. "
                f"Falling back to fuzzy matcher."
            )
            # Fallback to fuzzy with threshold from kwargs or default
            threshold = kwargs.get('threshold', 0.85)
            return cls.create('fuzzy', threshold=threshold)
    
    @classmethod
    def register(cls, name: str, matcher_class: type):
        """
        Register custom matcher (for contributors)
        
        Args:
            name: Matcher name (e.g., 'custom')
            matcher_class: Matcher class (must inherit from PhoneticMatcher)
        
        Example:
            class MyMatcher(PhoneticMatcher):
                def match(self, word1, word2):
                    # Custom logic
                    pass
            
            MatcherFactory.register('mymatcher', MyMatcher)
        """
        if not issubclass(matcher_class, PhoneticMatcher):
            raise TypeError(
                f"Matcher class must inherit from PhoneticMatcher, "
                f"got {matcher_class}"
            )
        
        cls._MATCHERS[name] = matcher_class
        logging.getLogger('locivox.vocabulary.matcher').info(
            f"Registered custom matcher: {name}"
        )
    
    @classmethod
    def list_available(cls) -> list:
        """Get list of available matchers"""
        return list(cls._MATCHERS.keys())
