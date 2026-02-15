"""
Tests for phonetic matcher system
"""

import pytest
from unittest.mock import Mock, patch
from src.matchers import (
    PhoneticMatcher,
    FuzzyMatcher,
    JellyfishMatcher,
    AbydosMatcher,
    MatcherFactory
)


class TestFuzzyMatcher:
    """Tests for FuzzyMatcher"""
    
    def test_init(self):
        """Test fuzzy matcher initialization"""
        matcher = FuzzyMatcher(threshold=0.9)
        
        assert matcher.threshold == 0.9
    
    def test_init_default_threshold(self):
        """Test default threshold"""
        matcher = FuzzyMatcher()
        
        assert matcher.threshold == 0.85
    
    def test_match_identical(self):
        """Test matching identical words"""
        matcher = FuzzyMatcher()
        
        assert matcher.match("Python", "Python") is True
    
    def test_match_case_insensitive(self):
        """Test case-insensitive matching"""
        matcher = FuzzyMatcher()
        
        assert matcher.match("Python", "python") is True
        assert matcher.match("PYTHON", "python") is True
    
    def test_match_similar(self):
        """Test matching similar words"""
        matcher = FuzzyMatcher(threshold=0.85)
        
        # 83% similar (5/6 chars match)
        assert matcher.match("Pithon", "Python") is False  # Below 85%
        
        # 86% similar
        matcher2 = FuzzyMatcher(threshold=0.80)
        assert matcher2.match("Pithon", "Python") is True
    
    def test_match_different(self):
        """Test non-matching words"""
        matcher = FuzzyMatcher()
        
        assert matcher.match("Python", "JavaScript") is False
        assert matcher.match("hello", "world") is False
    
    def test_encode(self):
        """Test encoding (returns lowercase)"""
        matcher = FuzzyMatcher()
        
        assert matcher.encode("Python") == "python"
        assert matcher.encode("HELLO") == "hello"


class TestJellyfishMatcher:
    """Tests for JellyfishMatcher"""
    
    def test_init_missing_library(self):
        """Test initialization with missing library"""
        # Remove jellyfish from sys.modules to simulate not installed
        with patch.dict('sys.modules', {'jellyfish': None}):
            with pytest.raises(ImportError) as exc_info:
                JellyfishMatcher()
            
            assert "jellyfish" in str(exc_info.value).lower()
    
    def test_real_jellyfish_matcher(self):
        """Test with real jellyfish library (if installed)"""
        try:
            import jellyfish
        except ImportError:
            pytest.skip("jellyfish not installed")
        
        # If we get here, jellyfish is installed
        matcher = JellyfishMatcher()
        
        # Test real phonetic matching
        assert matcher.match("Pithon", "Python") is True
        assert matcher.match("Jython", "Python") is False
    
    def test_match_with_mock(self):
        """Test matching logic with mocked jellyfish"""
        mock_jellyfish = Mock()
        mock_jellyfish.metaphone = Mock(side_effect=lambda w: {
            'pithon': 'P0N',
            'python': 'P0N',
            'jython': 'J0N',
        }.get(w.lower(), w))
        
        with patch.dict('sys.modules', {'jellyfish': mock_jellyfish}):
            matcher = JellyfishMatcher()
            matcher.jellyfish = mock_jellyfish
            
            # Same phonetic code = match
            assert matcher.match("Pithon", "Python") is True
            
            # Different phonetic code = no match
            assert matcher.match("Jython", "Python") is False
    
    def test_encode_with_mock(self):
        """Test phonetic encoding with mocked jellyfish"""
        mock_jellyfish = Mock()
        mock_jellyfish.metaphone = Mock(return_value='KBRNTS')
        
        with patch.dict('sys.modules', {'jellyfish': mock_jellyfish}):
            matcher = JellyfishMatcher()
            matcher.jellyfish = mock_jellyfish
            
            code = matcher.encode("Kubernetes")
            
            assert code == 'KBRNTS'


class TestAbydosMatcher:
    """Tests for AbydosMatcher"""
    
    def test_init_missing_library(self):
        """Test initialization with missing library"""
        with patch.dict('sys.modules', {'abydos': None, 'abydos.phonetic': None}):
            with pytest.raises(ImportError) as exc_info:
                AbydosMatcher()
            
            assert "abydos" in str(exc_info.value).lower()
    
    def test_real_abydos_matcher(self):
        """Test with real abydos library (if installed)"""
        try:
            from abydos.phonetic import DoubleMetaphone
        except ImportError:
            pytest.skip("abydos not installed")
        
        # If we get here, abydos is installed
        matcher = AbydosMatcher()
        
        # Test real phonetic matching
        assert matcher.match("Python", "Pithon") is True
    
    def test_match_with_mock(self):
        """Test phonetic matching with mocked abydos"""
        mock_phonetic = Mock()
        mock_encoder = Mock()
        # Make encode() method return actual values
        mock_encoder.encode = Mock(side_effect=lambda w: {
            'python': 'P0N',
            'pithon': 'P0N',
            'jython': 'J0N',
        }.get(w.lower(), w))
        
        mock_phonetic.DoubleMetaphone = Mock(return_value=mock_encoder)
        
        with patch.dict('sys.modules', {'abydos': Mock(), 'abydos.phonetic': mock_phonetic}):
            matcher = AbydosMatcher()
            matcher.encoder = mock_encoder  # Inject the encoder
            
            assert matcher.match("Python", "Pithon") is True
            assert matcher.match("Python", "Jython") is False
    
    def test_encode_with_mock(self):
        """Test phonetic encoding with mocked abydos"""
        mock_phonetic = Mock()
        mock_encoder = Mock()
        mock_encoder.encode = Mock(return_value='KBRNTS')
        
        mock_phonetic.DoubleMetaphone = Mock(return_value=mock_encoder)
        
        with patch.dict('sys.modules', {'abydos': Mock(), 'abydos.phonetic': mock_phonetic}):
            matcher = AbydosMatcher()
            matcher.encoder = mock_encoder  # Inject the encoder
            
            code = matcher.encode("Kubernetes")
            
            assert code == 'KBRNTS'
    
    def test_custom_algorithm_with_mock(self):
        """Test custom algorithm selection with mocked abydos"""
        mock_phonetic = Mock()
        mock_encoder = Mock()
        mock_phonetic.Soundex = Mock(return_value=mock_encoder)
        
        with patch.dict('sys.modules', {'abydos': Mock(), 'abydos.phonetic': mock_phonetic}):
            matcher = AbydosMatcher(algorithm="Soundex")
            
            assert matcher.algorithm == "Soundex"


class TestMatcherFactory:
    """Tests for MatcherFactory"""
    
    def test_create_fuzzy(self):
        """Test creating fuzzy matcher"""
        matcher = MatcherFactory.create('fuzzy', threshold=0.9)
        
        assert isinstance(matcher, FuzzyMatcher)
        assert matcher.threshold == 0.9
    
    def test_create_jellyfish(self):
        """Test creating jellyfish matcher"""
        try:
            import jellyfish
        except ImportError:
            pytest.skip("jellyfish not installed")
        
        matcher = MatcherFactory.create('jellyfish')
        assert isinstance(matcher, JellyfishMatcher)
    
    def test_create_unknown(self):
        """Test creating unknown matcher"""
        with pytest.raises(ValueError) as exc_info:
            MatcherFactory.create('unknown')
        
        assert "unknown" in str(exc_info.value).lower()
    
    def test_create_with_fallback_success(self):
        """Test fallback creation with successful load"""
        matcher = MatcherFactory.create_with_fallback('fuzzy', threshold=0.9)
        
        assert isinstance(matcher, FuzzyMatcher)
    
    def test_create_with_fallback_import_error(self):
        """Test fallback to fuzzy on import error"""
        # Try to create jellyfish without it installed
        # Should fallback to fuzzy
        with patch.dict('sys.modules', {'jellyfish': None}):
            matcher = MatcherFactory.create_with_fallback('jellyfish', threshold=0.85)
            
            # Should have fallen back to fuzzy
            assert isinstance(matcher, FuzzyMatcher)
    
    def test_register_custom_matcher(self):
        """Test registering custom matcher"""
        class CustomMatcher(PhoneticMatcher):
            def match(self, word1, word2):
                return True
        
        MatcherFactory.register('custom', CustomMatcher)
        
        assert 'custom' in MatcherFactory._MATCHERS
        
        matcher = MatcherFactory.create('custom')
        assert isinstance(matcher, CustomMatcher)
        
        # Cleanup
        del MatcherFactory._MATCHERS['custom']
    
    def test_register_invalid_class(self):
        """Test registering non-matcher class"""
        class NotAMatcher:
            pass
        
        with pytest.raises(TypeError):
            MatcherFactory.register('invalid', NotAMatcher)
    
    def test_list_available(self):
        """Test listing available matchers"""
        matchers = MatcherFactory.list_available()
        
        assert 'fuzzy' in matchers
        assert 'jellyfish' in matchers
        assert 'abydos' in matchers


class TestPhoneticMatcherBase:
    """Tests for PhoneticMatcher base class"""
    
    def test_abstract_methods(self):
        """Test that base class can't be instantiated"""
        with pytest.raises(TypeError):
            PhoneticMatcher()
    
    def test_encode_default(self):
        """Test default encode implementation"""
        class TestMatcher(PhoneticMatcher):
            def match(self, word1, word2):
                return True
        
        matcher = TestMatcher()
        assert matcher.encode("Python") == "python"


class TestMatcherIntegration:
    """Integration tests for matcher system"""
    
    def test_fuzzy_real_world(self):
        """Test fuzzy matcher with real examples"""
        matcher = FuzzyMatcher(threshold=0.75)  # Lower threshold for real-world similarity
        
        # Should match similar words
        assert matcher.match("hello", "hallo") is True  # 80% similar
        assert matcher.match("color", "colour") is True  # 83% similar
        
        # Should not match different words
        assert matcher.match("hello", "world") is False
    
    def test_matcher_consistency(self):
        """Test that matchers produce consistent results"""
        fuzzy = FuzzyMatcher()
        
        # Same result when called multiple times
        result1 = fuzzy.match("Python", "Pithon")
        result2 = fuzzy.match("Python", "Pithon")
        
        assert result1 == result2
