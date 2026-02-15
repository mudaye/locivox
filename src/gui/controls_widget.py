"""
Control buttons widget
Start/Stop/Pause/Clear controls for transcription
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon
import logging


class ControlsWidget(QWidget):
    """Widget containing control buttons"""
    
    # Signals
    start_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    clear_clicked = pyqtSignal()
    model_changed = pyqtSignal(str)
    device_changed = pyqtSignal(str)
    mic_changed = pyqtSignal(int)  # device index
    recording_started = pyqtSignal()  # Emitted when actually recording
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('locivox.gui.controls')
        
        self.is_recording = False
        self.is_paused = False
        self.recording_time = 0
        
        self.init_ui()
        
        # Timer for recording duration
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Control buttons
        self.start_btn = QPushButton("Start")
        self.start_btn.setMinimumWidth(100)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.start_btn.clicked.connect(self.on_start)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setMinimumWidth(100)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.stop_btn.clicked.connect(self.on_stop)
        layout.addWidget(self.stop_btn)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setMinimumWidth(100)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.pause_btn.clicked.connect(self.on_pause)
        layout.addWidget(self.pause_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setMinimumWidth(100)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
        """)
        self.clear_btn.clicked.connect(self.on_clear)
        layout.addWidget(self.clear_btn)
        
        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Status indicator
        self.status_label = QLabel("⚫ Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Timer display
        self.timer_label = QLabel("00:00")
        self.timer_label.setStyleSheet("""
            QLabel {
                font-family: monospace;
                font-size: 14px;
                font-weight: bold;
                color: #333;
                padding: 5px;
            }
        """)
        layout.addWidget(self.timer_label)
        
        # Model selection
        layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large"])
        self.model_combo.setCurrentText("base")
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        layout.addWidget(self.model_combo)
        
        # Device selection
        layout.addWidget(QLabel("Device:"))
        self.device_combo = QComboBox()
        self.device_combo.addItems(["cpu", "cuda"])
        self.device_combo.setCurrentText("cpu")
        self.device_combo.currentTextChanged.connect(self.on_device_changed)
        layout.addWidget(self.device_combo)
        
        # Microphone selection
        layout.addWidget(QLabel("Microphone:"))
        self.mic_combo = QComboBox()
        self.mic_combo.setMinimumWidth(200)
        self.mic_combo.setToolTip("Select audio input device")
        self.populate_audio_devices()
        self.mic_combo.currentIndexChanged.connect(self.on_mic_changed)
        layout.addWidget(self.mic_combo)
        
        self.setLayout(layout)
        
    def on_start(self):
        """Handle start button click"""
        # Disable ALL buttons while initializing
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)  # Can't stop yet
        self.pause_btn.setEnabled(False)  # Can't pause yet
        self.clear_btn.setEnabled(False)  # Prevent clear during init
        self.model_combo.setEnabled(False)
        self.device_combo.setEnabled(False)
        self.mic_combo.setEnabled(False)
        
        self.update_status("⏳ Initializing...")
        
        # Don't start timer yet - wait for backend to be ready
        
        self.start_clicked.emit()
    
    def start_recording(self):
        """Called when recording actually starts (from backend)"""
        self.is_recording = True
        self.is_paused = False
        self.recording_time = 0
        
        # NOW enable stop and pause
        self.stop_btn.setEnabled(True)
        self.pause_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)  # Can clear while recording
        
        self.update_status("🔴 Recording")
        
        self.timer.start(1000)  # Start timer now
        self.recording_started.emit()
        
    def on_stop(self):
        """Handle stop button click"""
        self.is_recording = False
        self.is_paused = False
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("Pause")
        self.model_combo.setEnabled(True)
        self.device_combo.setEnabled(True)
        self.mic_combo.setEnabled(True)
        
        self.update_status("⚫ Stopped")
        
        self.timer.stop()
        self.recording_time = 0
        self.timer_label.setText("00:00")
        
        self.stop_clicked.emit()
        
    def on_pause(self):
        """Handle pause button click"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.pause_btn.setText("Resume")
            self.update_status("⏸️ Paused")
            self.timer.stop()
        else:
            self.pause_btn.setText("Pause")
            self.update_status("🔴 Recording")
            self.timer.start(1000)
        
        self.pause_clicked.emit()
        
    def on_clear(self):
        """Handle clear button click"""
        self.clear_clicked.emit()
        
    def on_model_changed(self, model: str):
        """Handle model selection change"""
        self.logger.info(f"Model changed to: {model}")
        self.model_changed.emit(model)
        
    def on_device_changed(self, device: str):
        """Handle device selection change"""
        self.logger.info(f"Device changed to: {device}")
        self.device_changed.emit(device)
    
    def on_mic_changed(self, index: int):
        """Handle microphone selection change"""
        if index >= 0:
            device_name = self.mic_combo.currentText()
            self.logger.info(f"Microphone changed to: {device_name} (index: {index})")
            # Get the actual device index from the item data
            device_index = self.mic_combo.itemData(index)
            if device_index is not None:
                self.mic_changed.emit(device_index)
    
    def populate_audio_devices(self):
        """Populate microphone dropdown with available audio input devices"""
        try:
            import sounddevice as sd
            
            # Get list of devices
            devices = sd.query_devices()
            
            # Find input devices
            default_input = sd.default.device[0]  # Default input device index
            
            for i, device in enumerate(devices):
                # Only add input devices (max_input_channels > 0)
                if device['max_input_channels'] > 0:
                    device_name = device['name']
                    
                    # Mark default device
                    if i == default_input:
                        device_name = f"🎤 {device_name} (Default)"
                    
                    # Add to combo box with device index as data
                    self.mic_combo.addItem(device_name, i)
                    
                    # Select default
                    if i == default_input:
                        self.mic_combo.setCurrentIndex(self.mic_combo.count() - 1)
            
            if self.mic_combo.count() == 0:
                self.mic_combo.addItem("No input devices found", None)
                self.mic_combo.setEnabled(False)
                self.logger.warning("No audio input devices found")
            else:
                self.logger.info(f"Found {self.mic_combo.count()} input devices")
                
        except Exception as e:
            self.logger.error(f"Error listing audio devices: {e}")
            self.mic_combo.addItem("Error detecting devices", None)
            self.mic_combo.setEnabled(False)
        
    def update_timer(self):
        """Update recording timer"""
        if self.is_recording and not self.is_paused:
            self.recording_time += 1
            
            minutes = self.recording_time // 60
            seconds = self.recording_time % 60
            
            self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
            
    def update_status(self, status: str):
        """Update status indicator"""
        self.status_label.setText(status)
    
    def on_start_failed(self):
        """Handle failed start - reset UI to initial state"""
        self.is_recording = False
        self.is_paused = False
        
        # Re-enable start button
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.clear_btn.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.device_combo.setEnabled(True)
        self.mic_combo.setEnabled(True)
        
        self.update_status("❌ Failed to start")
        
        self.timer.stop()
        self.recording_time = 0
        self.timer_label.setText("00:00")
        
    def set_buttons_enabled(self, start: bool = True, stop: bool = False, pause: bool = False):
        """Enable/disable buttons programmatically"""
        self.start_btn.setEnabled(start)
        self.stop_btn.setEnabled(stop)
        self.pause_btn.setEnabled(pause)
        
    def get_selected_model(self) -> str:
        """Get currently selected model"""
        return self.model_combo.currentText()
        
    def get_selected_device(self) -> str:
        """Get currently selected device"""
        return self.device_combo.currentText()
    
    def get_selected_mic_index(self) -> int:
        """Get currently selected microphone device index"""
        index = self.mic_combo.currentIndex()
        if index >= 0:
            device_index = self.mic_combo.itemData(index)
            return device_index if device_index is not None else None
        return None
