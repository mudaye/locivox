"""
GUI Controller
Bridges PyQt6 GUI with Locivox backend
Handles threading and signal/slot communication
"""

import logging
import numpy as np
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from typing import Optional

from src.streaming import StreamingTranscriber
from src.utils import load_config


class TranscriptionWorker(QThread):
    """Worker thread for audio processing"""
    
    # Signals
    transcription_ready = pyqtSignal(str, bool)  # text, is_final
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    started = pyqtSignal()  # Emitted when transcriber is ready
    
    def __init__(self, config: dict):
        super().__init__()
        self.logger = logging.getLogger('locivox.gui.worker')
        self.config = config
        self.transcriber: Optional[StreamingTranscriber] = None
        self.is_running = False
        self._audio_queue = []
        self._last_final_text = ""  # Track last finalized transcription
        self._last_interim_text = ""  # Track last interim transcription
        
    def run(self):
        """Main worker thread execution"""
        try:
            self.logger.info("Transcription worker thread starting")
            self.status_changed.emit("Loading model...")
            
            # Create transcriber with callback
            self.logger.info("Creating StreamingTranscriber")
            self.transcriber = StreamingTranscriber(
                self.config,
                callback=self.on_transcription
            )
            
            self.logger.info("Starting transcriber")
            # Start transcription
            self.transcriber.start()
            self.is_running = True
            
            self.logger.info("Transcriber started successfully")
            self.status_changed.emit("Ready")
            self.started.emit()
            
            # Keep thread alive while recording
            while self.is_running:
                self.msleep(100)  # Sleep 100ms
                
        except Exception as e:
            self.logger.error(f"Worker thread error: {e}", exc_info=True)
            self.error_occurred.emit(str(e))
            self.status_changed.emit(f"Error: {e}")
        finally:
            self.cleanup()
            
    def on_transcription(self, text: str, is_final: bool):
        """Callback for transcription results"""
        try:
            self.logger.info(f"=== TRANSCRIPTION CALLBACK ===")
            self.logger.info(f"Text: '{text}'")
            self.logger.info(f"Is final: {is_final}")
            self.logger.info(f"Text length: {len(text) if text else 0}")
            
            if not text or not text.strip():
                self.logger.debug("Skipping empty transcription")
                return
            
            # Deduplicate text
            deduplicated_text = self._deduplicate_text(text, is_final)
            
            if deduplicated_text and deduplicated_text.strip():
                self.logger.info(f"Emitting transcription: {deduplicated_text}")
                self.transcription_ready.emit(deduplicated_text, is_final)
            else:
                self.logger.debug("Skipping duplicate transcription")
                
        except Exception as e:
            self.logger.error(f"Error in transcription callback: {e}", exc_info=True)
    
    def _deduplicate_text(self, text: str, is_final: bool) -> str:
        """
        Remove duplicate text from transcription
        
        Args:
            text: New transcription text
            is_final: Whether this is final or interim
            
        Returns:
            Deduplicated text (only new portion)
        """
        # Compare with last transcription
        last_text = self._last_final_text if is_final else self._last_interim_text
        
        # If new text starts with last text, extract only the new part
        if text.startswith(last_text):
            new_text = text[len(last_text):].strip()
            self.logger.debug(f"Deduplicated: '{last_text}...' → '{new_text}'")
        else:
            # Completely new text (or different enough)
            new_text = text
        
        # Update tracking
        if is_final:
            self._last_final_text = text
            self._last_interim_text = ""  # Reset interim
        else:
            self._last_interim_text = text
        
        return new_text
            
    def add_audio(self, audio_data: np.ndarray):
        """Add audio data to transcriber"""
        if self.transcriber and self.is_running:
            try:
                self.transcriber.add_audio(audio_data)
            except Exception as e:
                self.logger.error(f"Error adding audio to transcriber: {e}", exc_info=True)
                # Don't crash - just log and continue
                
    def stop(self):
        """Stop transcription"""
        self.logger.info("Stopping transcription worker")
        self.is_running = False
        
    def cleanup(self):
        """Clean up resources"""
        if self.transcriber:
            try:
                self.logger.info("Stopping transcriber")
                self.transcriber.stop()
            except Exception as e:
                self.logger.error(f"Error stopping transcriber: {e}")
            finally:
                self.transcriber = None
        self.status_changed.emit("Stopped")


class AudioCaptureWorker(QThread):
    """Worker thread for audio capture"""
    
    # Signals
    audio_ready = pyqtSignal(np.ndarray)  # audio_data
    error_occurred = pyqtSignal(str)
    started = pyqtSignal()  # Emitted when actually capturing
    
    def __init__(self, config: dict, device_index: Optional[int] = None):
        super().__init__()
        self.logger = logging.getLogger('locivox.gui.audio_capture')
        self.config = config
        self.device_index = device_index
        self.is_running = False
        self.stream = None
        
    def run(self):
        """Main audio capture loop"""
        try:
            import sounddevice as sd
            
            self.logger.info("Audio capture thread starting")
            
            # Get audio config
            sample_rate = self.config.get('audio', {}).get('sample_rate', 16000)
            chunk_duration = 0.1  # 100ms chunks
            chunk_size = int(sample_rate * chunk_duration)
            
            self.logger.info(f"Opening audio stream: device={self.device_index}, sr={sample_rate}")
            
            # Callback for audio chunks
            def audio_callback(indata, frames, time, status):
                try:
                    if status:
                        self.logger.warning(f"Audio status: {status}")
                    
                    if self.is_running:
                        # Convert to float32 and emit
                        audio_data = indata.copy().flatten().astype(np.float32)
                        self.audio_ready.emit(audio_data)
                except Exception as e:
                    self.logger.error(f"Error in audio callback: {e}", exc_info=True)
            
            # Open stream
            self.stream = sd.InputStream(
                device=self.device_index,
                channels=1,
                samplerate=sample_rate,
                blocksize=chunk_size,
                dtype=np.float32,
                callback=audio_callback
            )
            
            self.is_running = True
            self.stream.start()
            
            self.logger.info("Audio stream started successfully")
            self.started.emit()
            
            # Keep thread alive while recording
            while self.is_running:
                self.msleep(100)
                
        except Exception as e:
            self.logger.error(f"Audio capture error: {e}", exc_info=True)
            self.error_occurred.emit(f"Audio capture failed: {e}")
        finally:
            self.cleanup()
            
    def stop(self):
        """Stop audio capture"""
        self.logger.info("Stopping audio capture")
        self.is_running = False
        
    def cleanup(self):
        """Clean up resources"""
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
                self.logger.info("Audio stream closed")
            except Exception as e:
                self.logger.error(f"Error closing audio stream: {e}")
            finally:
                self.stream = None


class GUIController(QObject):
    """
    Main controller for GUI application
    Manages communication between GUI and backend
    """
    
    # Signals
    transcription_ready = pyqtSignal(str, bool)
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    recording_actually_started = pyqtSignal()  # When backend is truly ready
    start_failed = pyqtSignal()  # When start fails
    
    def __init__(self, config_path: str = "config.yaml"):
        super().__init__()
        self.logger = logging.getLogger('locivox.gui.controller')
        
        # Load configuration
        self.config = load_config(config_path)
        
        # Workers
        self.transcription_worker: Optional[TranscriptionWorker] = None
        self.audio_worker: Optional[AudioCaptureWorker] = None
        
        # State
        self.is_recording = False
        self.selected_mic_device = None  # Selected microphone device index
        
        self.logger.info("GUI Controller initialized")
        
    def start_recording(self):
        """Start recording and transcription"""
        if self.is_recording:
            self.logger.warning("Already recording")
            return
            
        try:
            self.logger.info("=== Starting recording ===")
            self.status_changed.emit("Initializing...")
            
            # Create and start transcription worker
            self.logger.info("Creating transcription worker")
            self.transcription_worker = TranscriptionWorker(self.config)
            
            # Connect signals
            self.transcription_worker.transcription_ready.connect(
                self.on_transcription_ready
            )
            self.transcription_worker.error_occurred.connect(
                self.on_worker_error
            )
            self.transcription_worker.status_changed.connect(
                self.on_status_changed
            )
            self.transcription_worker.started.connect(
                self.on_transcription_started
            )
            
            # Start transcription worker
            self.logger.info("Starting transcription worker thread")
            self.transcription_worker.start()
            
            # Note: Audio worker will be started when transcription worker is ready
            
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}", exc_info=True)
            self.error_occurred.emit(f"Failed to start: {e}")
            self.status_changed.emit("Failed to start")
            self.start_failed.emit()
    
    def on_transcription_started(self):
        """Called when transcription worker is ready"""
        try:
            self.logger.info("Transcription worker ready, starting audio capture")
            self.status_changed.emit("Starting audio capture...")
            
            # Create and start audio capture worker
            self.audio_worker = AudioCaptureWorker(
                self.config,
                device_index=self.selected_mic_device
            )
            
            # Connect signals
            self.audio_worker.audio_ready.connect(
                self.on_audio_ready
            )
            self.audio_worker.error_occurred.connect(
                self.on_error
            )
            self.audio_worker.started.connect(
                self.on_audio_started
            )
            
            # Start audio worker
            self.logger.info("Starting audio capture worker thread")
            self.audio_worker.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start audio capture: {e}", exc_info=True)
            self.error_occurred.emit(f"Failed to start audio: {e}")
    
    def on_audio_started(self):
        """Called when audio capture is ready"""
        self.logger.info("=== Recording started successfully ===")
        self.is_recording = True
        self.status_changed.emit("🔴 Recording")
        self.recording_actually_started.emit()  # Tell GUI to start timer
    
    @pyqtSlot(np.ndarray)
    def on_audio_ready(self, audio_data: np.ndarray):
        """Handle audio data from capture worker"""
        self.logger.debug(f"Audio chunk received: {len(audio_data)} samples")
        
        if self.transcription_worker:
            self.logger.debug(f"Adding audio to transcriber")
            self.transcription_worker.add_audio(audio_data)
        else:
            self.logger.warning("No transcription worker - dropping audio")
    
    @pyqtSlot(str)
    def on_status_changed(self, status: str):
        """Handle status change from workers"""
        self.logger.info(f"Status: {status}")
        self.status_changed.emit(status)
            
    def stop_recording(self):
        """Stop recording and transcription"""
        if not self.is_recording:
            return
            
        try:
            self.logger.info("Stopping recording")
            
            # Stop workers
            if self.transcription_worker:
                self.transcription_worker.stop()
                self.transcription_worker.wait(2000)  # Wait up to 2 seconds
                if self.transcription_worker.isRunning():
                    self.transcription_worker.terminate()
                self.transcription_worker = None
                
            if self.audio_worker:
                self.audio_worker.stop()
                self.audio_worker.wait(2000)
                if self.audio_worker.isRunning():
                    self.audio_worker.terminate()
                self.audio_worker = None
                
            self.is_recording = False
            self.status_changed.emit("Recording stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}", exc_info=True)
    
    def set_microphone_device(self, device_index: int):
        """Set the microphone device to use for recording"""
        self.logger.info(f"Setting microphone device to index: {device_index}")
        self.selected_mic_device = device_index
        
        # Update config
        if 'audio' not in self.config:
            self.config['audio'] = {}
        self.config['audio']['device_index'] = device_index
            
    def update_config(self, key: str, value):
        """Update configuration"""
        try:
            # Parse nested keys (e.g., "model.size")
            keys = key.split('.')
            config = self.config
            
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
                
            config[keys[-1]] = value
            
            self.logger.info(f"Config updated: {key} = {value}")
            
        except Exception as e:
            self.logger.error(f"Error updating config: {e}")
            
    @pyqtSlot(str, bool)
    def on_transcription_ready(self, text: str, is_final: bool):
        """Handle transcription result from worker"""
        self.transcription_ready.emit(text, is_final)
            
    @pyqtSlot(str)
    def on_error(self, error: str):
        """Handle error from worker"""
        self.logger.error(f"Worker error: {error}")
        self.error_occurred.emit(error)
    
    @pyqtSlot(str)
    def on_worker_error(self, error: str):
        """Handle error from worker during startup"""
        self.logger.error(f"Worker error: {error}")
        self.error_occurred.emit(error)
        
        # If we haven't started recording yet, this is a startup failure
        if not self.is_recording:
            self.start_failed.emit()
        
    def cleanup(self):
        """Clean up resources"""
        self.logger.info("Cleaning up controller")
        self.stop_recording()
