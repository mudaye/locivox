"""
Main application window for Locivox GUI
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence
import logging

from .transcription_widget import TranscriptionWidget
from .controls_widget import ControlsWidget


class MainWindow(QMainWindow):
    """Main application window"""
    
    # Signals
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    vocabulary_requested = pyqtSignal()
    export_requested = pyqtSignal()
    mic_changed = pyqtSignal(int)  # microphone device index
    
    def __init__(self, config: dict, controller=None):
        super().__init__()
        self.logger = logging.getLogger('locivox.gui')
        self.logger.info("Initializing main window")
        self.config = config  # Store config reference
        self.controller = controller  # Store controller reference
        
        self.init_ui()
        self.create_menu_bar()
        self.create_status_bar()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Locivox - Local Voice Transcription")
        self.setMinimumSize(800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Controls at top
        self.controls = ControlsWidget()
        main_layout.addWidget(self.controls)
        
        # Transcription display (takes most space)
        self.transcription = TranscriptionWidget()
        main_layout.addWidget(self.transcription, stretch=1)
        
        central_widget.setLayout(main_layout)
        
        # Connect control signals
        self.controls.start_clicked.connect(self.on_start)
        self.controls.stop_clicked.connect(self.on_stop)
        self.controls.clear_clicked.connect(self.transcription.clear)
        self.controls.copy_clicked.connect(self.on_copy)
        self.controls.mic_changed.connect(self.on_mic_changed)
        
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        export_action = QAction("&Export...", self)
        export_action.setShortcut(QKeySequence.StandardKey.Save)
        export_action.triggered.connect(self.on_export)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        clear_action = QAction("&Clear Transcription", self)
        clear_action.setShortcut(QKeySequence("Ctrl+L"))
        clear_action.triggered.connect(self.transcription.clear)
        edit_menu.addAction(clear_action)
        
        edit_menu.addSeparator()
        
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut(QKeySequence.StandardKey.Preferences)
        settings_action.triggered.connect(self.on_settings)
        edit_menu.addAction(settings_action)
        
        vocab_action = QAction("&Vocabulary...", self)
        vocab_action.setShortcut(QKeySequence("Ctrl+V"))
        vocab_action.triggered.connect(self.on_vocabulary)
        edit_menu.addAction(vocab_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About Locivox", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    # Slot methods
    def on_start(self):
        """Handle start button"""
        self.logger.info("Start requested")
        self.start_requested.emit()
        self.update_status("Recording...")
        
    def on_stop(self):
        """Handle stop button"""
        self.logger.info("Stop requested")
        self.stop_requested.emit()
        self.update_status("Stopped")
    
    def on_mic_changed(self, device_index: int):
        """Handle microphone selection change"""
        self.logger.info(f"Microphone changed to device index: {device_index}")
        self.mic_changed.emit(device_index)
    
    def on_copy(self):
        """Handle copy button - copy transcription to clipboard"""
        from PyQt6.QtWidgets import QApplication
        
        text = self.transcription.get_text()
        
        if not text:
            self.update_status("Nothing to copy")
            return
        
        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        self.update_status(f"Copied {len(text)} characters to clipboard")
        self.logger.info(f"Copied {len(text)} characters to clipboard")
        
    def on_settings(self):
        """Handle settings menu"""
        self.logger.info("Settings requested")
        
        # Import here to avoid circular dependency
        from src.gui.settings_dialog import SettingsDialog
        
        # Create and show settings dialog
        dialog = SettingsDialog(self.config, self)
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.exec()
    
    def on_settings_changed(self):
        """Handle settings changed"""
        self.logger.info("Settings changed - will take effect on next recording session")
        self.update_status("Settings saved")
        
    def on_vocabulary(self):
        """Handle vocabulary menu"""
        self.logger.info("Vocabulary manager requested")
        
        # Import here to avoid circular dependency
        from src.gui.vocabulary_dialog import VocabularyDialog
        
        # Get vocabulary file from config
        vocab_file = self.config.get('vocabulary', {}).get('file', './vocabulary.txt')
        
        # Create and show vocabulary dialog
        dialog = VocabularyDialog(vocab_file, self)
        dialog.vocabulary_changed.connect(self.on_vocabulary_changed)
        dialog.exec()
    
    def on_vocabulary_changed(self):
        """Handle vocabulary changes"""
        self.logger.info("Vocabulary changed - will take effect on next recording session")
        self.update_status("Vocabulary updated")
        
    def on_export(self):
        """Handle export menu"""
        self.logger.info("Export requested")
        
        # Get transcription text
        text = self.transcription.get_text()
        
        if not text:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "No Content",
                "There is no transcription to export."
            )
            return
        
        # Show export dialog
        self._show_export_dialog(text)
        
    def on_about(self):
        """Handle about menu"""
        from PyQt6.QtWidgets import QMessageBox
        
        QMessageBox.about(
            self,
            "About Locivox",
            "<h2>Locivox</h2>"
            "<p>Privacy-first local speech-to-text transcription</p>"
            "<p>Version 1.0</p>"
            "<p>Built with Faster-Whisper and PyQt6</p>"
        )
        
    # Public methods
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_bar.showMessage(message)
        
    def append_transcription(self, text: str, is_final: bool = False):
        """Add transcription text"""
        self.transcription.append_text(text, is_final)
        
    def set_controls_enabled(self, start: bool = True, stop: bool = False):
        """Enable/disable control buttons"""
        self.controls.set_buttons_enabled(start, stop)
        
    def closeEvent(self, event):
        """Handle window close"""
        self.logger.info("Main window closing")
        # Emit stop signal to ensure cleanup
        self.stop_requested.emit()
        event.accept()
    
    def _show_export_dialog(self, text: str):
        """Show export options dialog"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from datetime import datetime
        import json
        
        # Ask user for format and filename
        filename, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Transcription",
            f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text File (*.txt);;JSON File (*.json);;SRT Subtitle (*.srt);;All Files (*.*)"
        )
        
        if not filename:
            return  # User cancelled
        
        try:
            # Determine format from filename
            if filename.endswith('.json'):
                self._export_json(filename, text)
            elif filename.endswith('.srt'):
                self._export_srt(filename, text)
            else:
                self._export_txt(filename, text)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Transcription exported to:\n{filename}"
            )
            self.logger.info(f"Exported to: {filename}")
            
        except Exception as e:
            self.logger.error(f"Export failed: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export transcription:\n{e}"
            )
    
    def _export_txt(self, filename: str, text: str):
        """Export as plain text"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)
    
    def _export_json(self, filename: str, text: str):
        """Export as JSON with word-level timestamps and metadata"""
        from datetime import datetime
        import json
        
        # Get word-level timestamps if available
        words_with_timestamps = []
        if self.controller:
            words_with_timestamps = self.controller.get_words_with_timestamps()
        
        # Build structured JSON
        data = {
            'metadata': {
                'exported_at': datetime.now().isoformat(),
                'word_count': len(text.split()) if text else 0,
                'character_count': len(text),
                'model': self.controls.get_selected_model(),
                'device': self.controls.get_selected_device(),
                'has_word_timestamps': len(words_with_timestamps) > 0
            },
            'text': text,
            'words': [],
            'segments': []
        }
        
        # Add word-level data if available
        if words_with_timestamps:
            data['words'] = [
                {
                    'word': w['word'],
                    'start': round(w['absolute_start'], 3),
                    'end': round(w['absolute_end'], 3),
                    'duration': round(w['absolute_end'] - w['absolute_start'], 3)
                }
                for w in words_with_timestamps
            ]
            
            # Create segments (similar to SRT chunks: max 10 words or 5 seconds)
            current_segment = []
            current_start = None
            
            for word_data in words_with_timestamps:
                if not current_segment:
                    current_start = word_data['absolute_start']
                
                current_segment.append(word_data['word'])
                
                # Create segment if we have 10 words or 5 seconds elapsed
                segment_duration = word_data['absolute_end'] - current_start
                if len(current_segment) >= 10 or segment_duration >= 5.0:
                    data['segments'].append({
                        'text': ' '.join(current_segment),
                        'start': round(current_start, 3),
                        'end': round(word_data['absolute_end'], 3),
                        'duration': round(word_data['absolute_end'] - current_start, 3),
                        'word_count': len(current_segment)
                    })
                    current_segment = []
                    current_start = None
            
            # Add remaining words
            if current_segment and words_with_timestamps:
                data['segments'].append({
                    'text': ' '.join(current_segment),
                    'start': round(current_start, 3),
                    'end': round(words_with_timestamps[-1]['absolute_end'], 3),
                    'duration': round(words_with_timestamps[-1]['absolute_end'] - current_start, 3),
                    'word_count': len(current_segment)
                })
        
        # Write JSON file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _export_srt(self, filename: str, text: str):
        """Export as SRT subtitle format with real word-level timestamps"""
        # Try to get word-level timestamps
        words_with_timestamps = []
        if self.controller:
            words_with_timestamps = self.controller.get_words_with_timestamps()
        
        if words_with_timestamps:
            self.logger.info(f"Exporting SRT with {len(words_with_timestamps)} word timestamps")
            
            # Group words into subtitle chunks (max 10 words or 5 seconds per subtitle)
            subtitle_chunks = []
            current_chunk = []
            current_start = None
            
            for word_data in words_with_timestamps:
                if not current_chunk:
                    current_start = word_data['absolute_start']
                
                current_chunk.append(word_data['word'])
                
                # Create subtitle if we have 10 words or 5 seconds elapsed
                chunk_duration = word_data['absolute_end'] - current_start
                if len(current_chunk) >= 10 or chunk_duration >= 5.0:
                    subtitle_chunks.append({
                        'text': ' '.join(current_chunk),
                        'start': current_start,
                        'end': word_data['absolute_end']
                    })
                    current_chunk = []
                    current_start = None
            
            # Add remaining words
            if current_chunk and words_with_timestamps:
                subtitle_chunks.append({
                    'text': ' '.join(current_chunk),
                    'start': current_start,
                    'end': words_with_timestamps[-1]['absolute_end']
                })
            
            # Write SRT file
            with open(filename, 'w', encoding='utf-8') as f:
                for i, chunk in enumerate(subtitle_chunks, 1):
                    start_time = self._format_srt_time(chunk['start'])
                    end_time = self._format_srt_time(chunk['end'])
                    
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{chunk['text']}\n")
                    f.write("\n")
            
        else:
            # Fallback: Use sentence-based timing (old behavior)
            self.logger.warning("No word timestamps available - using sentence-based timing")
            
            sentences = text.replace('! ', '!|').replace('? ', '?|').replace('. ', '.|').split('|')
            sentences = [s.strip() for s in sentences if s.strip()]
            
            with open(filename, 'w', encoding='utf-8') as f:
                for i, sentence in enumerate(sentences, 1):
                    # Estimate timestamps (5 seconds per sentence)
                    start_time = self._format_srt_time(i * 5)
                    end_time = self._format_srt_time((i + 1) * 5)
                    
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{sentence}\n")
                    f.write("\n")
    
    def _format_srt_time(self, seconds: float) -> str:
        """Format seconds as SRT timestamp (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
