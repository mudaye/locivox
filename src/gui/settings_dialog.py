"""
Settings Dialog
Comprehensive configuration interface for Locivox
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QComboBox, QSpinBox, QCheckBox, QPushButton,
    QGroupBox, QFormLayout, QMessageBox, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
import logging
import yaml


class SettingsDialog(QDialog):
    """Settings dialog for configuring Locivox"""
    
    # Signal emitted when settings are saved
    settings_changed = pyqtSignal()
    
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger('locivox.gui.settings')
        self.config = config.copy()  # Work on a copy
        self.original_config = config  # Keep reference to original
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout()
        
        # Tab widget for different setting categories
        self.tabs = QTabWidget()
        
        # Create tabs
        self.tabs.addTab(self.create_model_tab(), "Model")
        self.tabs.addTab(self.create_audio_tab(), "Audio")
        self.tabs.addTab(self.create_vocabulary_tab(), "Vocabulary")
        self.tabs.addTab(self.create_logging_tab(), "Logging")
        self.tabs.addTab(self.create_analytics_tab(), "Analytics")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.restore_btn = QPushButton("Restore Defaults")
        self.restore_btn.clicked.connect(self.restore_defaults)
        button_layout.addWidget(self.restore_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def create_model_tab(self) -> QWidget:
        """Create model settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Model group
        model_group = QGroupBox("Model Configuration")
        model_layout = QFormLayout()
        
        # Model size
        self.model_size = QComboBox()
        self.model_size.addItems(["tiny", "base", "small", "medium", "large"])
        self.model_size.setToolTip("Larger models are more accurate but slower")
        model_layout.addRow("Model Size:", self.model_size)
        
        # Device
        self.model_device = QComboBox()
        self.model_device.addItems(["cpu", "cuda"])
        self.model_device.setToolTip("Use CUDA for GPU acceleration (if available)")
        model_layout.addRow("Device:", self.model_device)
        
        # Compute type
        self.compute_type = QComboBox()
        self.compute_type.addItems(["int8", "float16", "float32"])
        self.compute_type.setToolTip("int8 is faster, float32 is more accurate")
        model_layout.addRow("Compute Type:", self.compute_type)
        
        # Language
        self.language = QLineEdit()
        self.language.setPlaceholderText("en (or 'auto' for detection)")
        self.language.setToolTip("ISO language code (en, es, fr, etc.) or 'auto'")
        model_layout.addRow("Language:", self.language)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_audio_tab(self) -> QWidget:
        """Create audio settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Audio group
        audio_group = QGroupBox("Audio Configuration")
        audio_layout = QFormLayout()
        
        # Sample rate
        self.sample_rate = QSpinBox()
        self.sample_rate.setRange(8000, 48000)
        self.sample_rate.setSingleStep(8000)
        self.sample_rate.setValue(16000)
        self.sample_rate.setToolTip("Whisper expects 16kHz")
        audio_layout.addRow("Sample Rate:", self.sample_rate)
        
        # Chunk duration
        self.chunk_duration = QSpinBox()
        self.chunk_duration.setRange(1, 10)
        self.chunk_duration.setSuffix(" seconds")
        self.chunk_duration.setToolTip("Duration of each processing chunk")
        audio_layout.addRow("Chunk Duration:", self.chunk_duration)
        
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        # VAD group
        vad_group = QGroupBox("Voice Activity Detection")
        vad_layout = QFormLayout()
        
        # VAD enabled
        self.vad_enabled = QCheckBox("Enable VAD")
        self.vad_enabled.setToolTip("Filter out silence and background noise")
        vad_layout.addRow("", self.vad_enabled)
        
        # VAD threshold
        self.vad_threshold_label = QLabel("Threshold:")
        self.vad_threshold = QComboBox()
        self.vad_threshold.addItems(["0.3 (lenient)", "0.5 (normal)", "0.7 (strict)"])
        self.vad_threshold.setToolTip("Lower = more sensitive, higher = stricter")
        vad_layout.addRow(self.vad_threshold_label, self.vad_threshold)
        
        # Connect VAD enabled to threshold visibility
        self.vad_enabled.toggled.connect(self.vad_threshold.setEnabled)
        self.vad_enabled.toggled.connect(self.vad_threshold_label.setEnabled)
        
        vad_group.setLayout(vad_layout)
        layout.addWidget(vad_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_vocabulary_tab(self) -> QWidget:
        """Create vocabulary settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Vocabulary group
        vocab_group = QGroupBox("Vocabulary Configuration")
        vocab_layout = QFormLayout()
        
        # Vocabulary enabled
        self.vocab_enabled = QCheckBox("Enable Custom Vocabulary")
        self.vocab_enabled.setToolTip("Apply vocabulary corrections to transcriptions")
        vocab_layout.addRow("", self.vocab_enabled)
        
        # Vocabulary file
        vocab_file_layout = QHBoxLayout()
        self.vocab_file = QLineEdit()
        self.vocab_file.setPlaceholderText("./vocabulary.txt")
        vocab_file_layout.addWidget(self.vocab_file)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_vocab_file)
        vocab_file_layout.addWidget(browse_btn)
        
        self.vocab_file_label = QLabel("Vocabulary File:")
        vocab_layout.addRow(self.vocab_file_label, vocab_file_layout)
        
        # Case sensitive
        self.vocab_case_sensitive = QCheckBox("Case Sensitive Matching")
        vocab_layout.addRow("", self.vocab_case_sensitive)
        
        vocab_group.setLayout(vocab_layout)
        layout.addWidget(vocab_group)
        
        # Matching group
        matching_group = QGroupBox("Phonetic Matching")
        matching_layout = QFormLayout()
        
        # Library
        self.matching_library_label = QLabel("Library:")
        self.matching_library = QComboBox()
        self.matching_library.addItems(["fuzzy", "jellyfish", "abydos"])
        self.matching_library.setToolTip("fuzzy = built-in, jellyfish = recommended, abydos = advanced")
        matching_layout.addRow(self.matching_library_label, self.matching_library)
        
        # Threshold
        self.matching_threshold_label = QLabel("Threshold:")
        self.matching_threshold = QComboBox()
        self.matching_threshold.addItems(["0.75 (strict)", "0.85 (normal)", "0.95 (lenient)"])
        matching_layout.addRow(self.matching_threshold_label, self.matching_threshold)
        
        matching_group.setLayout(matching_layout)
        layout.addWidget(matching_group)
        
        # Connect vocabulary enabled to other controls
        self.vocab_enabled.toggled.connect(self.vocab_file.setEnabled)
        self.vocab_enabled.toggled.connect(self.vocab_file_label.setEnabled)
        self.vocab_enabled.toggled.connect(self.vocab_case_sensitive.setEnabled)
        self.vocab_enabled.toggled.connect(self.matching_library.setEnabled)
        self.vocab_enabled.toggled.connect(self.matching_library_label.setEnabled)
        self.vocab_enabled.toggled.connect(self.matching_threshold.setEnabled)
        self.vocab_enabled.toggled.connect(self.matching_threshold_label.setEnabled)
        
        # Open vocabulary manager button
        vocab_btn = QPushButton("Open Vocabulary Manager...")
        vocab_btn.clicked.connect(self.open_vocabulary_manager)
        layout.addWidget(vocab_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_logging_tab(self) -> QWidget:
        """Create logging settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Logging group
        log_group = QGroupBox("Logging Configuration")
        log_layout = QFormLayout()
        
        # Log level
        self.log_level = QComboBox()
        self.log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level.setToolTip("DEBUG = verbose, INFO = normal, WARNING+ = minimal")
        log_layout.addRow("Log Level:", self.log_level)
        
        # Log file
        log_file_layout = QHBoxLayout()
        self.log_file = QLineEdit()
        self.log_file.setPlaceholderText("locivox_gui.log")
        log_file_layout.addWidget(self.log_file)
        
        browse_log_btn = QPushButton("Browse...")
        browse_log_btn.clicked.connect(self.browse_log_file)
        log_file_layout.addWidget(browse_log_btn)
        
        log_layout.addRow("Log File:", log_file_layout)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_analytics_tab(self) -> QWidget:
        """Create analytics settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Info label
        info = QLabel(
            "Locivox collects anonymous usage data to improve transcription quality.\n"
            "This data includes deduplication decisions, punctuation corrections,\n"
            "and vocabulary matches. No audio or personal information is collected."
        )
        info.setWordWrap(True)
        info.setStyleSheet("QLabel { color: #666; padding: 10px; }")
        layout.addWidget(info)
        
        # Analytics group
        analytics_group = QGroupBox("Analytics Configuration")
        analytics_layout = QFormLayout()
        
        # Auto export
        self.analytics_auto_export = QCheckBox("Auto-export on session end")
        self.analytics_auto_export.setChecked(True)
        self.analytics_auto_export.setToolTip("Automatically save analytics when you stop recording")
        analytics_layout.addRow("", self.analytics_auto_export)
        
        # Keep sessions
        self.analytics_keep_sessions = QSpinBox()
        self.analytics_keep_sessions.setRange(1, 100)
        self.analytics_keep_sessions.setValue(30)
        self.analytics_keep_sessions.setSuffix(" sessions")
        self.analytics_keep_sessions.setToolTip("Older sessions will be automatically deleted")
        analytics_layout.addRow("Keep Last:", self.analytics_keep_sessions)
        
        # Export directory
        export_dir_layout = QHBoxLayout()
        self.analytics_export_dir = QLineEdit()
        self.analytics_export_dir.setPlaceholderText("./analytics")
        export_dir_layout.addWidget(self.analytics_export_dir)
        
        browse_analytics_btn = QPushButton("Browse...")
        browse_analytics_btn.clicked.connect(self.browse_analytics_dir)
        export_dir_layout.addWidget(browse_analytics_btn)
        
        analytics_layout.addRow("Export Directory:", export_dir_layout)
        
        analytics_group.setLayout(analytics_layout)
        layout.addWidget(analytics_group)
        
        # Manual export button
        manual_export_btn = QPushButton("Export Analytics Now...")
        manual_export_btn.clicked.connect(self.manual_export_analytics)
        layout.addWidget(manual_export_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def load_settings(self):
        """Load settings from config"""
        # Model tab
        self.model_size.setCurrentText(self.config.get('model', {}).get('size', 'base'))
        self.model_device.setCurrentText(self.config.get('model', {}).get('device', 'cpu'))
        self.compute_type.setCurrentText(self.config.get('model', {}).get('compute_type', 'int8'))
        self.language.setText(self.config.get('model', {}).get('language', 'en'))
        
        # Audio tab
        self.sample_rate.setValue(self.config.get('audio', {}).get('sample_rate', 16000))
        self.chunk_duration.setValue(self.config.get('audio', {}).get('chunk_duration', 5))
        
        # VAD
        vad_config = self.config.get('vad', {})
        self.vad_enabled.setChecked(vad_config.get('enabled', False))
        
        threshold = vad_config.get('threshold', 0.5)
        if threshold <= 0.3:
            self.vad_threshold.setCurrentIndex(0)
        elif threshold <= 0.5:
            self.vad_threshold.setCurrentIndex(1)
        else:
            self.vad_threshold.setCurrentIndex(2)
        
        # Vocabulary tab
        vocab_config = self.config.get('vocabulary', {})
        self.vocab_enabled.setChecked(vocab_config.get('enabled', False))
        self.vocab_file.setText(vocab_config.get('file', './vocabulary.txt'))
        self.vocab_case_sensitive.setChecked(vocab_config.get('case_sensitive', False))
        
        matching_config = vocab_config.get('matching', {})
        self.matching_library.setCurrentText(matching_config.get('library', 'fuzzy'))
        
        threshold = matching_config.get('fuzzy_threshold', 0.85)
        if threshold <= 0.75:
            self.matching_threshold.setCurrentIndex(0)
        elif threshold <= 0.85:
            self.matching_threshold.setCurrentIndex(1)
        else:
            self.matching_threshold.setCurrentIndex(2)
        
        # Logging tab
        log_config = self.config.get('logging', {})
        self.log_level.setCurrentText(log_config.get('level', 'INFO'))
        self.log_file.setText(log_config.get('file', 'locivox_gui.log'))
        
        # Analytics tab
        analytics_config = self.config.get('analytics', {})
        self.analytics_auto_export.setChecked(analytics_config.get('auto_export', True))
        self.analytics_keep_sessions.setValue(analytics_config.get('keep_sessions', 30))
        self.analytics_export_dir.setText(analytics_config.get('export_dir', './analytics'))
        
    def save_settings(self):
        """Save settings to config"""
        try:
            # Model settings
            if 'model' not in self.config:
                self.config['model'] = {}
            self.config['model']['size'] = self.model_size.currentText()
            self.config['model']['device'] = self.model_device.currentText()
            self.config['model']['compute_type'] = self.compute_type.currentText()
            self.config['model']['language'] = self.language.text() or 'en'
            
            # Audio settings
            if 'audio' not in self.config:
                self.config['audio'] = {}
            self.config['audio']['sample_rate'] = self.sample_rate.value()
            self.config['audio']['chunk_duration'] = self.chunk_duration.value()
            
            # VAD settings
            if 'vad' not in self.config:
                self.config['vad'] = {}
            self.config['vad']['enabled'] = self.vad_enabled.isChecked()
            
            threshold_map = {0: 0.3, 1: 0.5, 2: 0.7}
            self.config['vad']['threshold'] = threshold_map[self.vad_threshold.currentIndex()]
            
            # Vocabulary settings
            if 'vocabulary' not in self.config:
                self.config['vocabulary'] = {}
            self.config['vocabulary']['enabled'] = self.vocab_enabled.isChecked()
            self.config['vocabulary']['file'] = self.vocab_file.text() or './vocabulary.txt'
            self.config['vocabulary']['case_sensitive'] = self.vocab_case_sensitive.isChecked()
            
            if 'matching' not in self.config['vocabulary']:
                self.config['vocabulary']['matching'] = {}
            self.config['vocabulary']['matching']['library'] = self.matching_library.currentText()
            
            threshold_map = {0: 0.75, 1: 0.85, 2: 0.95}
            self.config['vocabulary']['matching']['fuzzy_threshold'] = threshold_map[self.matching_threshold.currentIndex()]
            
            # Logging settings
            if 'logging' not in self.config:
                self.config['logging'] = {}
            self.config['logging']['level'] = self.log_level.currentText()
            self.config['logging']['file'] = self.log_file.text() or 'locivox_gui.log'
            
            # Analytics settings
            if 'analytics' not in self.config:
                self.config['analytics'] = {}
            self.config['analytics']['auto_export'] = self.analytics_auto_export.isChecked()
            self.config['analytics']['keep_sessions'] = self.analytics_keep_sessions.value()
            self.config['analytics']['export_dir'] = self.analytics_export_dir.text() or './analytics'
            
            # Save to file
            with open('config.yaml', 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            
            # Update original config
            self.original_config.clear()
            self.original_config.update(self.config)
            
            self.logger.info("Settings saved successfully")
            
            # Emit signal
            self.settings_changed.emit()
            
            # Show success message
            QMessageBox.information(
                self,
                "Settings Saved",
                "Settings have been saved successfully.\n\n"
                "Some changes (like model or device) will take effect\n"
                "when you start a new recording session."
            )
            
            self.accept()
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error Saving Settings",
                f"Failed to save settings:\n\n{e}"
            )
            
    def restore_defaults(self):
        """Restore default settings"""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore default settings?\n\n"
            "This will reset all settings to their default values.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Load defaults
            self.model_size.setCurrentText('base')
            self.model_device.setCurrentText('cpu')
            self.compute_type.setCurrentText('int8')
            self.language.setText('en')
            
            self.sample_rate.setValue(16000)
            self.chunk_duration.setValue(5)
            
            self.vad_enabled.setChecked(False)
            self.vad_threshold.setCurrentIndex(1)  # 0.5
            
            self.vocab_enabled.setChecked(False)
            self.vocab_file.setText('./vocabulary.txt')
            self.vocab_case_sensitive.setChecked(False)
            self.matching_library.setCurrentText('fuzzy')
            self.matching_threshold.setCurrentIndex(1)  # 0.85
            
            self.log_level.setCurrentText('INFO')
            self.log_file.setText('locivox_gui.log')
            
            self.analytics_auto_export.setChecked(True)
            self.analytics_keep_sessions.setValue(30)
            self.analytics_export_dir.setText('./analytics')
            
    def browse_vocab_file(self):
        """Browse for vocabulary file"""
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Vocabulary File",
            self.vocab_file.text(),
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if filename:
            self.vocab_file.setText(filename)
            
    def browse_log_file(self):
        """Browse for log file"""
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Select Log File",
            self.log_file.text(),
            "Log Files (*.log);;All Files (*.*)"
        )
        
        if filename:
            self.log_file.setText(filename)
            
    def browse_analytics_dir(self):
        """Browse for analytics directory"""
        from PyQt6.QtWidgets import QFileDialog
        
        dirname = QFileDialog.getExistingDirectory(
            self,
            "Select Analytics Directory",
            self.analytics_export_dir.text()
        )
        
        if dirname:
            self.analytics_export_dir.setText(dirname)
            
    def open_vocabulary_manager(self):
        """Open vocabulary manager dialog"""
        from src.gui.vocabulary_dialog import VocabularyDialog
        
        vocab_file = self.vocab_file.text() or './vocabulary.txt'
        dialog = VocabularyDialog(vocab_file, self)
        dialog.vocabulary_changed.connect(self.on_vocabulary_changed)
        dialog.exec()
    
    def on_vocabulary_changed(self):
        """Handle vocabulary changes"""
        self.logger.info("Vocabulary changed")
        # Signal will be emitted when settings are saved
        
    def manual_export_analytics(self):
        """Manually export analytics"""
        # This will be implemented when we add analytics
        QMessageBox.information(
            self,
            "Export Analytics",
            "Manual analytics export will be available soon!"
        )
