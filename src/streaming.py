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


class StreamingTranscriber:
    """Real-time streaming transcriber with background processing"""
    
    def __init__(self, config: dict, callback: Optional[Callable] = None, transcriber_factory = None):
        """
        Initialize streaming transcriber
        
        Args:
            config: Configuration dictionary
            callback: Optional callback function(text, is_final) for results
            transcriber_factory: Optional factory for dependency injection (Testing)
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
        
        # Use injected factory if provided, otherwise default to the imported class
        factory = transcriber_factory or TranscriberFactory
        self.transcriber = factory.create_transcriber(config)
        
        # Threading
        self.processing_thread = None
        self.stop_event = threading.Event()
        self.is_running = False
        
        # Results
        self.transcription_results = []
        self.result_lock = threading.Lock()
        
        self.logger.info("Streaming transcriber initialized")
    
    def start(self) -> None:
        """Start background processing thread"""
        if self.is_running:
            self.logger.warning("Streaming already running")
            return
        
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
        self.logger.info("Wait for the processing thread to end")
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join()
        
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
        Process a single audio chunk
        
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
            self.logger.debug(f"Transcribing chunk ({duration:.2f}s)...")
            start_time = time.time()
            
            result = self.transcriber.transcribe(audio_chunk)
            
            elapsed = time.time() - start_time
            speed_factor = duration / elapsed if elapsed > 0 else 0
            
            text = result.get('text', '').strip()
            
            if text:
                self.logger.info(f"Transcribed ({speed_factor:.1f}x): {text}")
                
                # Store result
                with self.result_lock:
                    self.transcription_results.append({
                        'text': text,
                        'duration': duration,
                        'is_final': is_final,
                        'timestamp': time.time()
                    })
                
                # Call callback
                if self.callback:
                    try:
                        self.callback(text, is_final)
                    except Exception as e:
                        self.logger.error(f"Callback error: {e}")
            else:
                self.logger.debug("Empty transcription result")
                
        except Exception as e:
            self.logger.error(f"Error processing chunk: {e}", exc_info=True)
    
    def get_results(self) -> list:
        """Get all transcription results"""
        with self.result_lock:
            return self.transcription_results.copy()
    
    def get_full_text(self) -> str:
        """Get concatenated full transcription"""
        with self.result_lock:
            return self._get_full_text_internal() # Helper does the work

    def _get_full_text_internal(self) -> str:
        # Logic only, no locking
        return ' '.join([r['text'] for r in self.transcription_results])
    
    def clear_results(self) -> None:
        """Clear stored results"""
        with self.result_lock:
            self.transcription_results.clear()
        self.logger.info("Results cleared")
    
    def get_stats(self) -> dict:
        """Get streaming statistics"""
        buffer_stats = self.buffer.get_stats()
        self.logger.debug(f"Buffer stats: {buffer_stats}")
        
        with self.result_lock:
            num_results = len(self.transcription_results)
            total_text = self._get_full_text_internal()
            
        self.logger.debug(f"num_results = {num_results}")
        self.logger.debug(f"total_text = {total_text}")
        
        return {
            'is_running': self.is_running,
            'buffer_stats': buffer_stats,
            'num_transcriptions': num_results,
            'total_words': len(total_text.split()) if total_text else 0,
            'total_chars': len(total_text)
        }
