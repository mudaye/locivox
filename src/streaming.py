"""
Streaming transcription module for Locivox Phase 2
Transcribes audio chunks in background thread with real-time output
"""

import logging
import time
import threading
import queue
from typing import Optional, Callable
import numpy as np

from src.buffer import AudioBuffer
from src.vad import VoiceActivityDetector
from src.transcriber import TranscriberFactory
from src.vocabulary import VocabularyManager


class StreamingTranscriber:
    """Real-time streaming transcriber with background processing"""
    
    def __init__(self, config: dict, callback: Optional[Callable] = None):
        """
        Initialize streaming transcriber
        
        Args:
            config: Configuration dictionary
            callback: Optional callback function(text, is_final) for results
        """
        self.logger = logging.getLogger('locivox.streaming')
        self.config = config
        self.callback = callback
        
        # Streaming settings
        streaming_config = config.get('streaming', {})
        self.min_speech_duration = streaming_config.get('min_speech_duration', 0.5)
        self.vad_enabled = streaming_config.get('vad_enabled', True)
        
        # Components
        self.buffer = AudioBuffer(config)
        self.vad = VoiceActivityDetector(config) if self.vad_enabled else None
        self.transcriber = TranscriberFactory.create_transcriber(config)
        self.vocabulary = VocabularyManager(config)
        
        # Threading
        self.processing_thread = None
        self.stop_event = threading.Event()
        self.is_running = False
        
        # Results
        self.transcription_results = []
        self.result_lock = threading.Lock()
        
        # Timestamp-based deduplication
        self.last_emitted_timestamp = 0.0  # Track last word timestamp we emitted
        self.absolute_start_time = None  # Start time of recording session
        self.chunk_start_offset = 0.0  # Offset for current chunk in absolute time
        self.all_words_with_timestamps = []  # Store all words for SRT export
        
        self.logger.info("Streaming transcriber initialized")
    
    def start(self) -> None:
        """Start background processing thread"""
        if self.is_running:
            self.logger.warning("Streaming already running")
            return
        
        # Reset timestamp tracking
        self.absolute_start_time = time.time()
        self.last_emitted_timestamp = 0.0
        self.chunk_start_offset = 0.0
        self.all_words_with_timestamps = []
        
        self.stop_event.clear()
        self.is_running = True
        self.processing_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True,
            name="TranscriptionThread"
        )
        self.processing_thread.start()
        self.logger.info("Streaming transcription started")
    
    def stop(self) -> None:
        """Stop background processing thread"""
        if not self.is_running:
            return
        
        self.logger.info("Stopping streaming transcription...")
        
        # Signal thread to stop
        self.stop_event.set()
        self.is_running = False
        
        # DON'T join the thread - it's a daemon, let it die naturally
        # If it's mid-transcription, joining would block and cause hanging
        
        # Process final chunk if buffer has remaining audio
        final_chunk = self.buffer.flush()
        if final_chunk is not None and len(final_chunk) > 0:
            try:
                self._process_chunk(final_chunk, is_final=True)
            except Exception as e:
                self.logger.warning(f"Could not process final chunk: {e}")
        
        self.logger.info("Streaming transcription stopped")
    
    def add_audio(self, audio_data: np.ndarray) -> None:
        """
        Add audio data for processing
        
        Args:
            audio_data: Audio samples to process
        """
        if not self.is_running:
            self.logger.warning("Cannot add audio - streaming not running")
            return
        
        self.buffer.add_audio(audio_data)
    
    def _processing_loop(self) -> None:
        """Background thread for processing audio chunks"""
        self.logger.info("Processing loop started")
        
        while not self.stop_event.is_set():
            try:
                # Check if chunks available
                if self.buffer.has_chunks():
                    chunk = self.buffer.get_chunk()
                    
                    if chunk is not None:
                        self._process_chunk(chunk, is_final=False)
                else:
                    # No chunks, sleep briefly
                    time.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}", exc_info=True)
                time.sleep(0.5)  # Avoid tight loop on repeated errors
        
        self.logger.info("Processing loop ended")
    
    def _process_chunk(self, audio_chunk: np.ndarray, is_final: bool = False) -> None:
        """
        Process a single audio chunk with timestamp-based deduplication
        
        Args:
            audio_chunk: Audio data to transcribe
            is_final: Whether this is the final chunk
        """
        try:
            # Check minimum duration
            duration = len(audio_chunk) / self.config['audio']['sample_rate']
            if duration < self.min_speech_duration:
                self.logger.debug(f"Chunk too short ({duration:.2f}s), skipping")
                return
            
            # VAD check
            if self.vad and not self.vad.is_speech(audio_chunk):
                self.logger.debug("No speech detected in chunk, skipping")
                return
            
            # Transcribe
            self.logger.debug(f"Transcribing chunk ({duration:.2f}s) starting at offset {self.chunk_start_offset:.2f}s...")
            start_time = time.time()
            
            result = self.transcriber.transcribe(audio_chunk)
            
            elapsed = time.time() - start_time
            speed_factor = duration / elapsed if elapsed > 0 else 0
            
            # Check if model supports word timestamps
            has_word_timestamps = result.get('has_word_timestamps', False)
            words = result.get('words', [])
            
            self.logger.info(f"Transcription result: has_timestamps={has_word_timestamps}, words={len(words)}")
            
            if has_word_timestamps and words:
                # TIMESTAMP-BASED DEDUPLICATION (preferred)
                self.logger.debug(f"Using timestamp-based deduplication ({len(words)} words)")
                
                new_words = []
                new_words_data = []
                
                for word_data in words:
                    # Calculate absolute timestamp
                    absolute_timestamp = self.chunk_start_offset + word_data['start']
                    
                    # Only include words AFTER last emitted timestamp
                    if absolute_timestamp > self.last_emitted_timestamp:
                        new_words.append(word_data['word'])
                        
                        # Store word with absolute timestamp for SRT export
                        word_with_abs_time = word_data.copy()
                        word_with_abs_time['absolute_start'] = absolute_timestamp
                        word_with_abs_time['absolute_end'] = self.chunk_start_offset + word_data['end']
                        new_words_data.append(word_with_abs_time)
                        
                        # Update last emitted timestamp
                        self.last_emitted_timestamp = absolute_timestamp
                
                text = ' '.join(new_words)
                
                # Store words for SRT export
                with self.result_lock:
                    self.all_words_with_timestamps.extend(new_words_data)
                
                self.logger.debug(f"Filtered by timestamp: {len(words)} → {len(new_words)} words")
                
            else:
                # FALLBACK: No word timestamps available (use full text)
                self.logger.warning("Word timestamps not available - using full text (duplicates may occur)")
                text = result.get('text', '').strip()
            
            # Apply custom vocabulary corrections
            if text:
                text = self.vocabulary.apply_vocabulary(text)
            
            # Update chunk offset for next chunk
            self.chunk_start_offset += duration
            
            if text:
                self.logger.info(f"Transcribed ({speed_factor:.1f}x): {text}")
                
                # Store result
                with self.result_lock:
                    self.transcription_results.append({
                        'text': text,
                        'duration': duration,
                        'is_final': is_final,
                        'timestamp': time.time(),
                        'has_word_timestamps': has_word_timestamps
                    })
                
                # Call callback
                if self.callback:
                    try:
                        self.callback(text, is_final)
                    except Exception as e:
                        self.logger.error(f"Callback error: {e}")
            else:
                self.logger.debug("No new text after deduplication")
                
        except Exception as e:
            self.logger.error(f"Error processing chunk: {e}", exc_info=True)
    
    def get_results(self) -> list:
        """Get all transcription results"""
        with self.result_lock:
            return self.transcription_results.copy()
    
    def get_full_text(self) -> str:
        """Get concatenated full transcription"""
        with self.result_lock:
            return self._get_full_text_internal()
    
    def get_words_with_timestamps(self) -> list:
        """
        Get all words with absolute timestamps for SRT export
        
        Returns:
            List of word dictionaries with absolute_start and absolute_end timestamps
        """
        with self.result_lock:
            return self.all_words_with_timestamps.copy()
    
    def _get_full_text_internal(self) -> str:
        """Internal helper - assumes lock is already held"""
        return ' '.join([r['text'] for r in self.transcription_results])
    
    def clear_results(self) -> None:
        """Clear stored results"""
        with self.result_lock:
            self.transcription_results.clear()
        self.logger.info("Results cleared")
    
    def get_stats(self) -> dict:
        """Get streaming statistics"""
        buffer_stats = self.buffer.get_stats()
        
        with self.result_lock:
            num_results = len(self.transcription_results)
            # Use internal helper to avoid double-locking
            total_text = self._get_full_text_internal()
        
        return {
            'is_running': self.is_running,
            'buffer_stats': buffer_stats,
            'num_transcriptions': num_results,
            'total_words': len(total_text.split()) if total_text else 0,
            'total_chars': len(total_text)
        }
