"""
Tests for vocabulary module (Phase 3)
"""

import pytest
import tempfile
from pathlib import Path
from src.vocabulary import VocabularyManager


class TestVocabularyManager:
    """Tests for VocabularyManager"""
    
    @pytest.fixture
    def basic_config(self):
        """Basic configuration with vocabulary disabled"""
        return {
            'vocabulary': {
                'enabled': False,
                'case_sensitive': False,
                'fuzzy_threshold': 0.85,
                'terms': []
            }
        }
    
    @pytest.fixture
    def enabled_config(self):
        """Configuration with vocabulary enabled"""
        return {
            'vocabulary': {
                'enabled': True,
                'case_sensitive': False,
                'fuzzy_threshold': 0.85,
                'terms': [
                    {'correct': 'Kubernetes', 'variations': ['coober netes', 'kube ernetes']},
                    {'correct': 'PostgreSQL', 'variations': ['postgres', 'postgre']}
                ]
            }
        }
    
    def test_init_disabled(self, basic_config):
        """Test initialization with vocabulary disabled"""
        vocab = VocabularyManager(basic_config)
        
        assert vocab.enabled is False
        assert len(vocab.terms) == 0
        assert len(vocab.replacements) == 0
    
    def test_init_enabled(self, enabled_config):
        """Test initialization with vocabulary enabled"""
        vocab = VocabularyManager(enabled_config)
        
        assert vocab.enabled is True
        assert len(vocab.terms) == 2
        assert 'Kubernetes' in vocab.terms
        assert 'PostgreSQL' in vocab.terms
    
    def test_add_term_simple(self, basic_config):
        """Test adding a simple term without variations"""
        vocab = VocabularyManager(basic_config)
        vocab.add_term('Python')
        
        assert 'Python' in vocab.terms
        assert len(vocab.terms['Python']) == 0
    
    def test_add_term_with_variations(self, basic_config):
        """Test adding term with variations"""
        vocab = VocabularyManager(basic_config)
        vocab.add_term('FastAPI', ['fast api', 'fast a p i'])
        
        assert 'FastAPI' in vocab.terms
        assert len(vocab.terms['FastAPI']) == 2
        assert 'fast api' in vocab.replacements
        assert vocab.replacements['fast api'] == 'FastAPI'
    
    def test_apply_vocabulary_disabled(self, basic_config):
        """Test that vocabulary does nothing when disabled"""
        vocab = VocabularyManager(basic_config)
        vocab.add_term('Kubernetes', ['coober netes'])
        
        text = "I'm working with coober netes"
        result = vocab.apply_vocabulary(text)
        
        assert result == text  # No changes when disabled
    
    def test_apply_vocabulary_direct_replacement(self, enabled_config):
        """Test direct exact match replacement"""
        vocab = VocabularyManager(enabled_config)
        
        text = "I'm working with coober netes"
        result = vocab.apply_vocabulary(text)
        
        assert 'Kubernetes' in result
        assert 'coober netes' not in result
    
    def test_apply_vocabulary_multiple_replacements(self, enabled_config):
        """Test multiple replacements in one text"""
        vocab = VocabularyManager(enabled_config)
        
        text = "Using postgres and coober netes together"
        result = vocab.apply_vocabulary(text)
        
        assert 'PostgreSQL' in result
        assert 'Kubernetes' in result
        assert 'postgres' not in result
        assert 'coober netes' not in result
    
    def test_apply_vocabulary_case_insensitive(self, enabled_config):
        """Test case-insensitive matching"""
        vocab = VocabularyManager(enabled_config)
        
        text = "Working with POSTGRES and Coober Netes"
        result = vocab.apply_vocabulary(text)
        
        assert 'PostgreSQL' in result
        assert 'Kubernetes' in result
    
    def test_apply_vocabulary_case_sensitive(self):
        """Test case-sensitive matching"""
        config = {
            'vocabulary': {
                'enabled': True,
                'case_sensitive': True,
                'fuzzy_threshold': 0.85,
                'terms': [
                    {'correct': 'Python', 'variations': ['python']}
                ]
            }
        }
        vocab = VocabularyManager(config)
        
        # Exact case should match
        result1 = vocab.apply_vocabulary("I use python")
        assert 'Python' in result1
        
        # Different case should NOT match
        result2 = vocab.apply_vocabulary("I use PYTHON")
        assert 'PYTHON' in result2  # Unchanged
    
    def test_apply_vocabulary_preserve_punctuation(self, enabled_config):
        """Test that punctuation is preserved"""
        vocab = VocabularyManager(enabled_config)
        
        text = "Using postgres, coober netes, and more!"
        result = vocab.apply_vocabulary(text)
        
        assert 'PostgreSQL,' in result
        assert 'Kubernetes,' in result
        assert result.endswith('!')
    
    def test_apply_vocabulary_word_boundaries(self, enabled_config):
        """Test that only whole words are replaced"""
        vocab = VocabularyManager(enabled_config)
        vocab.add_term('API', ['api'])
        
        # Should replace 'api' but not 'rapid'
        text = "The api is rapid"
        result = vocab.apply_vocabulary(text)
        
        assert 'API' in result
        assert 'rapid' in result  # Should not become 'rAPId'
    
    def test_fuzzy_matching_similar_word(self):
        """Test fuzzy matching for similar words"""
        config = {
            'vocabulary': {
                'enabled': True,
                'case_sensitive': False,
                'matching': {
                    'library': 'fuzzy',
                    'fuzzy_threshold': 0.80  # Lower threshold for testing
                },
                'terms': [
                    {'correct': 'Kubernetes', 'variations': []}
                ]
            }
        }
        vocab = VocabularyManager(config)
        
        # Very similar word should match with lower threshold
        text = "Working with Kubeernetes"
        result = vocab.apply_vocabulary(text)
        
        # Should be corrected to Kubernetes
        assert 'Kubernetes' in result
    
    def test_fuzzy_matching_threshold(self):
        """Test different fuzzy matching thresholds"""
        config = {
            'vocabulary': {
                'enabled': True,
                'case_sensitive': False,
                'matching': {
                    'library': 'fuzzy',
                    'fuzzy_threshold': 0.70  # Lenient for testing
                },
                'terms': [
                    {'correct': 'Python', 'variations': []}
                ]
            }
        }
        vocab = VocabularyManager(config)
        
        # Very similar should match with lenient threshold
        result1 = vocab.apply_vocabulary("Using Pithon")
        assert 'Python' in result1
    
    def test_load_from_file(self, basic_config):
        """Test loading vocabulary from file"""
        # Create temporary vocabulary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# Comment line\n")
            f.write("Python\n")
            f.write("Kubernetes: coober netes, kube ernetes\n")
            f.write("\n")  # Empty line
            f.write("FastAPI: fast api\n")
            temp_file = f.name
        
        try:
            vocab = VocabularyManager(basic_config)
            vocab.load_from_file(temp_file)
            
            assert len(vocab.terms) == 3
            assert 'Python' in vocab.terms
            assert 'Kubernetes' in vocab.terms
            assert 'FastAPI' in vocab.terms
            
            # Check variations
            assert 'coober netes' in vocab.replacements
            assert vocab.replacements['fast api'] == 'FastAPI'
        finally:
            Path(temp_file).unlink()
    
    def test_load_from_file_not_found(self, basic_config):
        """Test loading from non-existent file"""
        vocab = VocabularyManager(basic_config)
        
        # Should not raise exception, just log warning
        vocab.load_from_file('/nonexistent/file.txt')
        
        assert len(vocab.terms) == 0
    
    def test_empty_text(self, enabled_config):
        """Test handling empty text"""
        vocab = VocabularyManager(enabled_config)
        
        result = vocab.apply_vocabulary("")
        assert result == ""
        
        result = vocab.apply_vocabulary(None)
        assert result is None
    
    def test_text_with_no_matches(self, enabled_config):
        """Test text with no vocabulary matches"""
        vocab = VocabularyManager(enabled_config)
        
        text = "This is just regular text with no special terms"
        result = vocab.apply_vocabulary(text)
        
        assert result == text
    
    def test_multiple_occurrences(self, enabled_config):
        """Test replacing multiple occurrences of same term"""
        vocab = VocabularyManager(enabled_config)
        
        text = "Using postgres, then more postgres, and finally postgres again"
        result = vocab.apply_vocabulary(text)
        
        # All occurrences should be replaced
        assert result.count('PostgreSQL') == 3
        assert 'postgres' not in result.lower() or 'PostgreSQL' in result
    
    def test_get_stats(self, enabled_config):
        """Test getting vocabulary statistics"""
        vocab = VocabularyManager(enabled_config)
        
        stats = vocab.get_stats()
        
        assert stats['enabled'] is True
        assert stats['num_terms'] == 2
        assert stats['num_variations'] > 0
        assert stats['case_sensitive'] is False
        assert stats['fuzzy_threshold'] == 0.85
    
    def test_inline_terms_from_config(self):
        """Test loading inline terms from config"""
        config = {
            'vocabulary': {
                'enabled': True,
                'case_sensitive': False,
                'fuzzy_threshold': 0.85,
                'terms': [
                    'Python',  # Simple string
                    {'correct': 'FastAPI', 'variations': ['fast api']},  # With variations
                ]
            }
        }
        vocab = VocabularyManager(config)
        
        assert 'Python' in vocab.terms
        assert 'FastAPI' in vocab.terms
        assert 'fast api' in vocab.replacements
    
    def test_special_characters_in_terms(self, basic_config):
        """Test terms with special characters"""
        vocab = VocabularyManager(basic_config)
        vocab.enabled = True
        vocab.add_term('C++', ['c plus plus', 'c plus'])
        
        text = "I program in c plus plus"
        result = vocab.apply_vocabulary(text)
        
        assert 'C++' in result
    
    def test_numbers_in_terms(self, basic_config):
        """Test terms with numbers"""
        vocab = VocabularyManager(basic_config)
        vocab.enabled = True
        vocab.add_term('Python3', ['python 3', 'python three'])
        
        text = "Using python 3 for development"
        result = vocab.apply_vocabulary(text)
        
        assert 'Python3' in result


class TestVocabularyEdgeCases:
    """Edge case tests for vocabulary"""
    
    def test_overlapping_terms(self):
        """Test handling overlapping term variations"""
        config = {
            'vocabulary': {
                'enabled': True,
                'case_sensitive': False,
                'fuzzy_threshold': 0.85,
                'terms': [
                    {'correct': 'FastAPI', 'variations': ['fast api']},
                    {'correct': 'API', 'variations': ['api']}
                ]
            }
        }
        vocab = VocabularyManager(config)
        
        text = "Using fast api for the api"
        result = vocab.apply_vocabulary(text)
        
        # Should handle both replacements
        assert 'FastAPI' in result
        assert 'API' in result
    
    def test_very_long_text(self):
        """Test performance with very long text"""
        config = {
            'vocabulary': {
                'enabled': True,
                'case_sensitive': False,
                'fuzzy_threshold': 0.85,
                'terms': [
                    {'correct': 'Kubernetes', 'variations': ['coober netes']}
                ]
            }
        }
        vocab = VocabularyManager(config)
        
        # Create long text with many replacements
        text = " ".join(["Working with coober netes"] * 100)
        result = vocab.apply_vocabulary(text)
        
        # Should handle efficiently
        assert result.count('Kubernetes') == 100
    
    def test_unicode_characters(self):
        """Test handling unicode characters"""
        config = {
            'vocabulary': {
                'enabled': True,
                'case_sensitive': False,
                'fuzzy_threshold': 0.85,
                'terms': [
                    {'correct': 'Café', 'variations': ['cafe']}
                ]
            }
        }
        vocab = VocabularyManager(config)
        
        text = "Meeting at the cafe"
        result = vocab.apply_vocabulary(text)
        
        assert 'Café' in result
