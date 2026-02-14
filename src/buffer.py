"""
Audio buffer module for streaming transcription
Manages circular buffer with overlap for continuous processing
"""

import logging
import numpy as np
from collections import deque
from threading import Lock
from typing import Optional, Tuple


class AudioBuffer:
    """Circular audio buffer with overlap for streaming transcription"""
    
    def __init__(self, config: dict):
        self.logger = logging.getLogger('locivox.buffer')
        
        # Configuration
        audio_config = config.get('audio', {})
        streaming_config = config.get('streaming', {})
        
        self.sample_rate = audio_config.get('sample_rate', 16000)
        self.chunk_duration = streaming_config.get('chunk_size', 5.0)
        self.overlap_duration = streaming_config.get('chunk_overlap', 1.0)
        self.max_chunks = streaming_config.get('buffer_size', 10)
        
        # Calculate sizes in samples
        self.chunk_samples = int(self.chunk_duration * self.sample_rate)
        self.overlap_samples = int(self.overlap_duration * self.sample_rate)
        self.step_samples = self.chunk_samples - self.overlap_samples
        
        # Buffer storage
        self.buffer = np.array([], dtype=np.float32)
        self.chunks_queue = deque(maxlen=self.max_chunks)
        self.lock = Lock()
        
        self.logger.info(f"Audio buffer initialized: "
                        f"chunk={self.chunk_duration}s, "
                        f"overlap={self.overlap_duration}s, "
                        f"max_chunks={self.max_chunks}")
    
    def add_audio(self, audio_data: np.ndarray) -> None:
        """
        Add new audio data to buffer
        
        Args:
            audio_data: New audio samples to add
        """
        with self.lock:
            # Ensure float32
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Flatten if stereo
            if len(audio_data.shape) > 1:
                audio_data = audio_data.flatten()
            
            # Append to buffer
            self.buffer = np.concatenate([self.buffer, audio_data])
            
            # Extract complete chunks
            while len(self.buffer) >= self.chunk_samples:
                chunk = self.buffer[:self.chunk_samples].copy()
                self.chunks_queue.append(chunk)
                
                # Move forward by step size (chunk - overlap)
                self.buffer = self.buffer[self.step_samples:]
                
                self.logger.debug(f"Chunk added to queue. "
                                f"Queue size: {len(self.chunks_queue)}, "
                                f"Buffer remaining: {len(self.buffer)} samples")
    
    def get_chunk(self) -> Optional[np.ndarray]:
        """
        Get next chunk from queue
        
        Returns:
            Audio chunk or None if queue is empty
        """
        with self.lock:
            if self.chunks_queue:
                return self.chunks_queue.popleft()
            return None
    
    def has_chunks(self) -> bool:
        """Check if chunks are available"""
        with self.lock:
            return len(self.chunks_queue) > 0
    
    def get_queue_size(self) -> int:
        """Get number of chunks in queue"""
        with self.lock:
            return len(self.chunks_queue)
    
    def flush(self) -> Optional[np.ndarray]:
        """
        Flush remaining buffer as final chunk
        
        Returns:
            Remaining audio or None if buffer is empty
        """
        with self.lock:
            if len(self.buffer) > 0:
                final_chunk = self.buffer.copy()
                self.buffer = np.array([], dtype=np.float32)
                self.logger.info(f"Flushed final chunk: {len(final_chunk)} samples")
                return final_chunk
            return None
    
    def clear(self) -> None:
        """Clear buffer and queue"""
        with self.lock:
            self.buffer = np.array([], dtype=np.float32)
            self.chunks_queue.clear()
            self.logger.info("Buffer cleared")
    
    def get_stats(self) -> dict:
        """Get buffer statistics"""
        with self.lock:
            return {
                'buffer_samples': len(self.buffer),
                'buffer_seconds': len(self.buffer) / self.sample_rate,
                'chunks_queued': len(self.chunks_queue),
                'chunk_duration': self.chunk_duration,
                'overlap_duration': self.overlap_duration
            }
