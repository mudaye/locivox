"""
Audio capture module for Locivox
Handles microphone input and recording
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
import logging
from typing import Optional, Tuple
from queue import Queue
import threading


class AudioCapture:
    """Handle audio recording from microphone"""
    
    def __init__(self, config: dict):
        self.logger = logging.getLogger('locivox.audio')
        self.audio_config = config.get('audio', {})
        self.recording_config = config.get('recording', {})
        
        # Audio parameters
        self.sample_rate = self.audio_config.get('sample_rate', 16000)
        self.channels = self.audio_config.get('channels', 1)
        self.chunk_duration = self.audio_config.get('chunk_duration', 5)
        
        # Recording state
        self.is_recording = False
        self.audio_queue = Queue()
        self.recorded_frames = []
        
    def list_devices(self) -> None:
        """List available audio input devices"""
        print("\n🎤 Available Audio Input Devices:")
        print("=" * 60)
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                default_marker = " [DEFAULT]" if i == sd.default.device[0] else ""
                print(f"{i}: {device['name']}{default_marker}")
                print(f"   Channels: {device['max_input_channels']}, "
                      f"Sample Rate: {device['default_samplerate']:.0f} Hz")
        print("=" * 60 + "\n")
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream"""
        if status:
            self.logger.warning(f"Audio callback status: {status}")
        if self.is_recording:
            self.audio_queue.put(indata.copy())
    
    def start_recording(self, device: Optional[int] = None) -> None:
        """Start recording audio from microphone"""
        self.logger.info("Starting audio recording...")
        self.is_recording = True
        self.recorded_frames = []
        
        try:
            self.stream = sd.InputStream(
                device=device,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self._audio_callback
            )
            self.stream.start()
            self.logger.info(f"Recording started (Sample rate: {self.sample_rate} Hz)")
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            raise
    
    def stop_recording(self) -> np.ndarray:
        """Stop recording and return audio data"""
        self.logger.info("Stopping audio recording...")
        self.is_recording = False
        
        # Wait for any remaining audio in the queue
        while not self.audio_queue.empty():
            self.recorded_frames.append(self.audio_queue.get())
        
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        # Concatenate all recorded frames
        if self.recorded_frames:
            audio_data = np.concatenate(self.recorded_frames, axis=0)
            self.logger.info(f"Recording stopped. Duration: {len(audio_data) / self.sample_rate:.2f}s")
            return audio_data
        else:
            self.logger.warning("No audio data recorded")
            return np.array([])
    
    def record_audio(self) -> None:
        """Continuously record audio while is_recording is True"""
        while self.is_recording:
            if not self.audio_queue.empty():
                self.recorded_frames.append(self.audio_queue.get())
    
    def save_audio(self, audio_data: np.ndarray, filepath: str) -> None:
        """Save audio data to file"""
        try:
            sf.write(filepath, audio_data, self.sample_rate)
            self.logger.info(f"Audio saved to: {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save audio: {e}")
            raise
    
    def get_recording_level(self) -> float:
        """Get current RMS level of recording (for VU meter)"""
        if not self.audio_queue.empty():
            recent_data = self.audio_queue.queue[-1]
            rms = np.sqrt(np.mean(recent_data**2))
            return float(rms)
        return 0.0
    
    def detect_silence(self, audio_data: np.ndarray, 
                      threshold: Optional[float] = None) -> bool:
        """Detect if audio contains silence"""
        if threshold is None:
            threshold = self.audio_config.get('silence_threshold', 0.01)
        
        rms = np.sqrt(np.mean(audio_data**2))
        return rms < threshold
