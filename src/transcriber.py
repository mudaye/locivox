"""
Transcription module for Locivox
Model-agnostic wrapper for different STT engines
"""

import logging
import numpy as np
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod


class BaseTranscriber(ABC):
    """Abstract base class for transcription engines"""
    
    @abstractmethod
    def transcribe(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Transcribe audio data and return results"""
        pass
    
    @abstractmethod
    def load_model(self) -> None:
        """Load the transcription model"""
        pass


class FasterWhisperTranscriber(BaseTranscriber):
    """Faster-Whisper implementation"""
    
    def __init__(self, config: dict):
        self.logger = logging.getLogger('locivox.transcriber.faster_whisper')
        self.model_config = config.get('model', {})
        self.audio_config = config.get('audio', {})
        
        self.model_size = self.model_config.get('size', 'base')
        self.device = self.model_config.get('device', 'cpu')
        self.compute_type = self.model_config.get('compute_type', 'int8')
        self.language = self.model_config.get('language', 'en')
        
        self.model = None
        self.load_model()
    
    def load_model(self) -> None:
        """Load Faster-Whisper model"""
        try:
            from faster_whisper import WhisperModel
            
            self.logger.info(f"Loading Faster-Whisper model: {self.model_size}")
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            self.logger.info("Model loaded successfully")
        except ImportError:
            self.logger.error("faster-whisper not installed. Run: pip install faster-whisper")
            raise
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def transcribe(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Transcribe audio using Faster-Whisper"""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            # Convert to float32 if needed
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Flatten if stereo
            if len(audio_data.shape) > 1:
                audio_data = audio_data.flatten()
            
            # Detect language if set to auto
            language = None if self.language == "auto" else self.language
            
            # Transcribe
            segments, info = self.model.transcribe(
                audio_data,
                language=language,
                vad_filter=True,  # Voice activity detection
                beam_size=5
            )
            
            # Collect segments
            transcription_segments = []
            full_text = []
            
            for segment in segments:
                transcription_segments.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip()
                })
                full_text.append(segment.text.strip())
            
            result = {
                'text': ' '.join(full_text),
                'segments': transcription_segments,
                'language': info.language if hasattr(info, 'language') else self.language,
                'language_probability': info.language_probability if hasattr(info, 'language_probability') else None
            }
            
            self.logger.info(f"Transcription complete. Detected language: {result['language']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            raise


class OpenAIWhisperTranscriber(BaseTranscriber):
    """OpenAI Whisper implementation"""
    
    def __init__(self, config: dict):
        self.logger = logging.getLogger('locivox.transcriber.openai_whisper')
        self.model_config = config.get('model', {})
        self.audio_config = config.get('audio', {})
        
        self.model_size = self.model_config.get('size', 'base')
        self.device = self.model_config.get('device', 'cpu')
        self.language = self.model_config.get('language', 'en')
        
        self.model = None
        self.load_model()
    
    def load_model(self) -> None:
        """Load OpenAI Whisper model"""
        try:
            import whisper
            
            self.logger.info(f"Loading OpenAI Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size, device=self.device)
            self.logger.info("Model loaded successfully")
        except ImportError:
            self.logger.error("openai-whisper not installed. Run: pip install openai-whisper")
            raise
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def transcribe(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Transcribe audio using OpenAI Whisper"""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            # Convert to float32 if needed
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Flatten if stereo
            if len(audio_data.shape) > 1:
                audio_data = audio_data.flatten()
            
            # Transcribe
            language = None if self.language == "auto" else self.language
            result = self.model.transcribe(
                audio_data,
                language=language,
                fp16=False  # CPU doesn't support fp16
            )
            
            self.logger.info(f"Transcription complete. Language: {result.get('language', 'unknown')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            raise


class TranscriberFactory:
    """Factory to create appropriate transcriber based on config"""
    
    @staticmethod
    def create_transcriber(config: dict) -> BaseTranscriber:
        """Create and return appropriate transcriber"""
        engine = config.get('model', {}).get('engine', 'faster-whisper')
        
        if engine == 'faster-whisper':
            return FasterWhisperTranscriber(config)
        elif engine == 'openai-whisper':
            return OpenAIWhisperTranscriber(config)
        else:
            raise ValueError(f"Unknown transcription engine: {engine}")
