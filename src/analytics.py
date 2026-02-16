"""
Analytics Module
Collect usage data to improve transcription quality
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class TranscriptionAnalytics:
    """Collect and export transcription analytics"""
    
    def __init__(self, config: dict):
        self.logger = logging.getLogger('locivox.analytics')
        self.config = config
        
        # Get analytics config
        analytics_config = config.get('analytics', {})
        self.auto_export = analytics_config.get('auto_export', True)
        self.keep_sessions = analytics_config.get('keep_sessions', 30)
        self.export_dir = analytics_config.get('export_dir', './analytics')
        
        # Session data
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.session_start = datetime.now()
        self.session_data = {
            'session_id': self.session_id,
            'start_time': self.session_start.isoformat(),
            'end_time': None,
            'duration_seconds': 0,
            'total_words': 0,
            'total_characters': 0,
            'model': config.get('model', {}).get('size', 'unknown'),
            'device': config.get('model', {}).get('device', 'unknown'),
            'vocabulary_enabled': config.get('vocabulary', {}).get('enabled', False),
            'deduplication_events': [],
            'punctuation_events': [],
            'vocabulary_events': [],
            'transcription_events': [],
            'errors': []
        }
        
        self.logger.info(f"Analytics session started: {self.session_id}")
    
    def log_deduplication(self, original: str, deduplicated: str, overlap_words: int):
        """
        Log a deduplication event
        
        Args:
            original: Original transcription text
            deduplicated: Deduplicated text (only new portion)
            overlap_words: Number of overlapping words
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'original_text': original,
            'deduplicated_text': deduplicated,
            'overlap_words': overlap_words,
            'original_word_count': len(original.split()),
            'new_word_count': len(deduplicated.split()) if deduplicated else 0
        }
        
        self.session_data['deduplication_events'].append(event)
        self.logger.debug(f"Dedup event: {overlap_words} words overlap")
    
    def log_punctuation(self, before: str, after: str, rules_applied: List[str]):
        """
        Log a punctuation correction event
        
        Args:
            before: Text before punctuation correction
            after: Text after punctuation correction
            rules_applied: List of rule names that were applied
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'before': before,
            'after': after,
            'rules_applied': rules_applied,
            'changed': before != after
        }
        
        self.session_data['punctuation_events'].append(event)
        
        if before != after:
            self.logger.debug(f"Punctuation changed: {len(rules_applied)} rules applied")
    
    def log_vocabulary_correction(self, original: str, corrected: str, term_used: str):
        """
        Log a vocabulary correction event
        
        Args:
            original: Original text
            corrected: Corrected text
            term_used: The vocabulary term that was matched
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'original': original,
            'corrected': corrected,
            'term_used': term_used
        }
        
        self.session_data['vocabulary_events'].append(event)
        self.logger.debug(f"Vocab correction: '{original}' → '{corrected}'")
    
    def log_transcription(self, text: str, is_final: bool, confidence: Optional[float] = None):
        """
        Log a transcription event
        
        Args:
            text: Transcribed text
            is_final: Whether this is final transcription
            confidence: Optional confidence score
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'text': text,
            'is_final': is_final,
            'confidence': confidence,
            'word_count': len(text.split()) if text else 0
        }
        
        self.session_data['transcription_events'].append(event)
        
        # In streaming mode, count all transcriptions since "final" might never come
        # Note: This may overcount during interim updates, but gives us data
        if text:
            words = text.split()
            # Only add to total if this seems like new text (simple heuristic)
            # A better approach would be to track what we've counted
            if is_final or len(words) > 0:
                self.session_data['total_words'] += len(words)
                self.session_data['total_characters'] += len(text)
    
    def log_error(self, error_type: str, error_message: str, details: Optional[Dict] = None):
        """
        Log an error event
        
        Args:
            error_type: Type of error (e.g., 'transcription', 'audio_capture')
            error_message: Error message
            details: Optional additional details
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': error_message,
            'details': details or {}
        }
        
        self.session_data['errors'].append(event)
        self.logger.warning(f"Error logged: {error_type} - {error_message}")
    
    def end_session(self):
        """End the current session"""
        self.session_data['end_time'] = datetime.now().isoformat()
        
        duration = datetime.now() - self.session_start
        self.session_data['duration_seconds'] = int(duration.total_seconds())
        
        self.logger.info(
            f"Session ended: {self.session_id} "
            f"({self.session_data['duration_seconds']}s, "
            f"{self.session_data['total_words']} words)"
        )
        
        # Auto-export if enabled
        if self.auto_export:
            self.export_session()
    
    def export_session(self, filename: Optional[str] = None) -> str:
        """
        Export session data to file
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        # Create export directory
        os.makedirs(self.export_dir, exist_ok=True)
        
        # Generate filename if not provided
        if filename is None:
            filename = f"session_{self.session_id}.json"
        
        filepath = os.path.join(self.export_dir, filename)
        
        # Export to JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Session exported to: {filepath}")
        
        # Clean up old sessions
        self._cleanup_old_sessions()
        
        return filepath
    
    def _cleanup_old_sessions(self):
        """Remove old session files beyond keep_sessions limit"""
        try:
            # Get all session files
            session_files = sorted(
                Path(self.export_dir).glob('session_*.json'),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            # Remove old files
            if len(session_files) > self.keep_sessions:
                for old_file in session_files[self.keep_sessions:]:
                    old_file.unlink()
                    self.logger.info(f"Removed old session: {old_file.name}")
        
        except Exception as e:
            self.logger.error(f"Error cleaning up old sessions: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for current session
        
        Returns:
            Dictionary with summary statistics
        """
        return {
            'session_id': self.session_id,
            'duration_seconds': self.session_data['duration_seconds'],
            'total_words': self.session_data['total_words'],
            'total_characters': self.session_data['total_characters'],
            'deduplication_count': len(self.session_data['deduplication_events']),
            'punctuation_count': len(self.session_data['punctuation_events']),
            'vocabulary_corrections': len(self.session_data['vocabulary_events']),
            'transcription_events': len(self.session_data['transcription_events']),
            'errors': len(self.session_data['errors'])
        }
    
    def export_summary(self, filename: Optional[str] = None) -> str:
        """
        Export summary to text file
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        os.makedirs(self.export_dir, exist_ok=True)
        
        if filename is None:
            filename = f"summary_{self.session_id}.txt"
        
        filepath = os.path.join(self.export_dir, filename)
        
        summary = self.get_summary()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Locivox Session Summary\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"Session ID: {summary['session_id']}\n")
            f.write(f"Duration: {summary['duration_seconds']} seconds\n")
            f.write(f"Total Words: {summary['total_words']}\n")
            f.write(f"Total Characters: {summary['total_characters']}\n")
            f.write(f"\nEvents:\n")
            f.write(f"  Deduplication: {summary['deduplication_count']}\n")
            f.write(f"  Punctuation: {summary['punctuation_count']}\n")
            f.write(f"  Vocabulary: {summary['vocabulary_corrections']}\n")
            f.write(f"  Transcriptions: {summary['transcription_events']}\n")
            f.write(f"  Errors: {summary['errors']}\n")
        
        self.logger.info(f"Summary exported to: {filepath}")
        
        return filepath


# Global analytics instance
_analytics: Optional[TranscriptionAnalytics] = None


def get_analytics(config: Optional[dict] = None) -> Optional[TranscriptionAnalytics]:
    """
    Get or create analytics instance
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Analytics instance or None if not initialized
    """
    global _analytics
    
    if _analytics is None and config is not None:
        _analytics = TranscriptionAnalytics(config)
    
    return _analytics


def reset_analytics():
    """Reset analytics instance (for testing or new session)"""
    global _analytics
    _analytics = None
