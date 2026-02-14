"""
Voice Activity Detection module for Locivox Phase 2
Uses Silero VAD for detecting speech in audio streams
"""

import os
import logging
import numpy as np
import torch
from typing import Optional

# Disable HuggingFace telemetry to avoid auth issues
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
os.environ['HF_HUB_OFFLINE'] = '0'  # Allow downloads but no telemetry


class VoiceActivityDetector:
    """Voice Activity Detection using Silero VAD"""
    
    def __init__(self, config: dict):
        self.logger = logging.getLogger('locivox.vad')
        self.streaming_config = config.get('streaming', {})
        
        # VAD settings
        self.threshold = self.streaming_config.get('vad_threshold', 0.5)
        self.sample_rate = config.get('audio', {}).get('sample_rate', 16000)
        
        # Model
        self.model = None
        self.load_model()
        
        self.logger.info(f"VAD initialized (threshold: {self.threshold})")
    
    def load_model(self) -> None:
        """Load Silero VAD model"""
        try:
            # Load Silero VAD model
            self.model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            
            # Extract utility functions
            (self.get_speech_timestamps,
             self.save_audio,
             self.read_audio,
             self.VADIterator,
             self.collect_chunks) = utils
            
            self.logger.info("Silero VAD model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load VAD model: {e}")
            self.logger.warning("VAD will be disabled")
            self.model = None
    
    def is_speech(self, audio_chunk: np.ndarray) -> bool:
        """
        Detect if audio chunk contains speech
        
        Args:
            audio_chunk: Audio data as numpy array (float32, 16kHz)
            
        Returns:
            True if speech detected, False otherwise
        """
        if self.model is None:
            # VAD disabled, assume all audio is speech
            return True
        
        try:
            # Convert to torch tensor
            if audio_chunk.dtype != np.float32:
                audio_chunk = audio_chunk.astype(np.float32)
            
            # Ensure 1D
            if len(audio_chunk.shape) > 1:
                audio_chunk = audio_chunk.flatten()
            
            # Convert to tensor
            audio_tensor = torch.from_numpy(audio_chunk)
            
            # Use get_speech_timestamps for large chunks (handles chunking internally)
            speech_timestamps = self.get_speech_timestamps(
                audio_tensor,
                self.model,
                sampling_rate=self.sample_rate,
                threshold=self.threshold,
                return_seconds=False  # Return in samples
            )
            
            # If any speech detected, return True
            is_speech = len(speech_timestamps) > 0
            
            # Calculate speech ratio for logging
            if is_speech and speech_timestamps:
                total_speech_samples = sum(
                    segment['end'] - segment['start'] 
                    for segment in speech_timestamps
                )
                speech_ratio = total_speech_samples / len(audio_chunk)
                self.logger.debug(f"VAD: speech_ratio={speech_ratio:.2f}, is_speech={is_speech}")
            else:
                self.logger.debug(f"VAD: no speech detected")
            
            return is_speech
            
        except Exception as e:
            self.logger.error(f"VAD detection error: {e}")
            # On error, assume speech to avoid dropping audio
            return True
    
    def get_speech_segments(self, audio: np.ndarray) -> list:
        """
        Get timestamps of speech segments in audio
        
        Args:
            audio: Full audio array
            
        Returns:
            List of dicts with 'start' and 'end' timestamps in seconds
        """
        if self.model is None:
            # Return entire audio as one segment
            duration = len(audio) / self.sample_rate
            return [{'start': 0.0, 'end': duration}]
        
        try:
            # Convert to tensor
            audio_tensor = torch.from_numpy(audio.astype(np.float32))
            
            # Get speech timestamps
            speech_timestamps = self.get_speech_timestamps(
                audio_tensor,
                self.model,
                sampling_rate=self.sample_rate,
                threshold=self.threshold,
                return_seconds=True
            )
            
            return speech_timestamps
            
        except Exception as e:
            self.logger.error(f"Error getting speech segments: {e}")
            duration = len(audio) / self.sample_rate
            return [{'start': 0.0, 'end': duration}]
    
    def filter_silence(self, audio: np.ndarray) -> np.ndarray:
        """
        Remove silence from audio, keeping only speech
        
        Args:
            audio: Audio data
            
        Returns:
            Audio with silence removed
        """
        speech_segments = self.get_speech_segments(audio)
        
        if not speech_segments:
            return np.array([], dtype=audio.dtype)
        
        # Extract speech segments
        speech_chunks = []
        for segment in speech_segments:
            start_sample = int(segment['start'] * self.sample_rate)
            end_sample = int(segment['end'] * self.sample_rate)
            speech_chunks.append(audio[start_sample:end_sample])
        
        # Concatenate all speech
        if speech_chunks:
            return np.concatenate(speech_chunks)
        else:
            return np.array([], dtype=audio.dtype)
