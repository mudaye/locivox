"""
Vocabulary Correction Worker
Background thread for applying vocabulary corrections without blocking UI
"""

from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
import logging
from typing import Optional

from src.vocabulary import VocabularyManager
from src.punctuation import improve_punctuation


class VocabularyWorker(QThread):
    """Worker thread for vocabulary corrections"""
    
    # Signals
    correction_ready = pyqtSignal(str, str)  # original_text, corrected_text
    error_occurred = pyqtSignal(str)
    
    def __init__(self, config: dict):
        super().__init__()
        self.logger = logging.getLogger('locivox.gui.vocab_worker')
        self.config = config
        self.vocab_manager: Optional[VocabularyManager] = None
        self.is_running = False
        self.pending_text = None
        
    def run(self):
        """Main worker thread execution"""
        try:
            self.logger.info("Vocabulary worker thread starting")
            
            # Initialize vocabulary manager if enabled
            if self.config.get('vocabulary', {}).get('enabled', False):
                self.logger.info("Initializing VocabularyManager")
                self.vocab_manager = VocabularyManager(self.config)
                self.logger.info(f"Loaded {len(self.vocab_manager.terms)} vocabulary terms")
            else:
                self.logger.info("Vocabulary corrections disabled in config")
            
            self.is_running = True
            
            # Keep thread alive while running
            while self.is_running:
                self.msleep(100)  # Sleep 100ms
                
        except Exception as e:
            self.logger.error(f"Vocabulary worker error: {e}", exc_info=True)
            self.error_occurred.emit(str(e))
            
    def process_text(self, text: str):
        """
        Process text with vocabulary corrections and punctuation
        
        Args:
            text: Text to correct
        """
        if not self.is_running:
            return
        
        try:
            original_text = text
            self.logger.debug(f"Processing text: '{text}'")
            
            # Apply vocabulary corrections if enabled
            vocab_corrected = False
            if self.vocab_manager:
                text = self.vocab_manager.apply_vocabulary(text)
                if text != original_text:
                    vocab_corrected = True
                    self.logger.info(f"Vocabulary changed text: '{original_text}' → '{text}'")
                    # Log ONLY real vocabulary corrections
                    from src.analytics import get_analytics
                    analytics = get_analytics()
                    if analytics:
                        analytics.log_vocabulary_correction(original_text, text, "vocabulary_match")
            
            # Apply punctuation improvements (track what changed)
            text_before_punctuation = text
            text = improve_punctuation(text)
            
            self.logger.debug(f"Punctuation: before='{text_before_punctuation}', after='{text}'")
            
            # Log punctuation changes to analytics (separately from vocab)
            if text != text_before_punctuation:
                from src.analytics import get_analytics
                analytics = get_analytics()
                if analytics:
                    rules_applied = []
                    if text[0].isupper() and not text_before_punctuation[0].isupper():
                        rules_applied.append("capitalize_first")
                    if text.count('.') > text_before_punctuation.count('.'):
                        rules_applied.append("add_periods")
                    if text != text_before_punctuation:
                        rules_applied.append("punctuation_cleanup")
                    
                    self.logger.info(f"Punctuation changed: rules={rules_applied}")
                    analytics.log_punctuation(text_before_punctuation, text, rules_applied)
            else:
                self.logger.debug("No punctuation changes")
            
            # Only emit if text changed from original
            if text != original_text:
                self.logger.info(f"Emitting correction: '{original_text}' → '{text}'")
                self.correction_ready.emit(original_text, text)
            else:
                self.logger.debug(f"No corrections needed for: '{text}'")
                
        except Exception as e:
            self.logger.error(f"Error processing text: {e}", exc_info=True)
            
    def stop(self):
        """Stop vocabulary worker"""
        self.logger.info("Stopping vocabulary worker")
        self.is_running = False
        
    def cleanup(self):
        """Clean up resources"""
        self.vocab_manager = None
