"""
Locivox GUI Package
PyQt6-based desktop interface for real-time transcription
"""

from .main_window import MainWindow
from .transcription_widget import TranscriptionWidget
from .controls_widget import ControlsWidget

__all__ = ['MainWindow', 'TranscriptionWidget', 'ControlsWidget']
