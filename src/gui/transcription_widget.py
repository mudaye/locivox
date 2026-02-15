"""
Transcription display widget
Real-time text display with auto-scroll and formatting
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor, QFont
import logging


class TranscriptionWidget(QWidget):
    """Widget for displaying transcription text"""
    
    # Signals
    text_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('locivox.gui.transcription')
        self._interim_start = None  # Track interim text position
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Header label
        self.header = QLabel("Transcription")
        self.header.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                background-color: #f0f0f0;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.header)
        
        # Text display
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Arial", 11))
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 10px;
                background-color: white;
            }
        """)
        
        # Set placeholder text
        self.text_edit.setPlaceholderText(
            "Transcription will appear here...\n\n"
            "Click 'Start' to begin recording."
        )
        
        layout.addWidget(self.text_edit)
        
        # Stats label
        self.stats_label = QLabel("Words: 0 | Characters: 0")
        self.stats_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 10px;
                padding: 3px;
            }
        """)
        layout.addWidget(self.stats_label)
        
        self.setLayout(layout)
        
    def append_text(self, text: str, is_final: bool = False):
        """
        Append text to display
        
        Args:
            text: Text to append
            is_final: Whether this is final text (vs interim)
        """
        if not text:
            return
            
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Prepare text with spacing
        if not self.text_edit.toPlainText():
            display_text = text
        else:
            display_text = " " + text
        
        if is_final:
            # Final text - normal font, black
            cursor.insertText(display_text)
        else:
            # Interim text - italic, gray
            # Insert as HTML for styling
            html = f'<span style="color: #888; font-style: italic;">{display_text}</span>'
            cursor.insertHtml(html)
            
            # Store cursor position to replace interim text when final arrives
            self._interim_start = cursor.position() - len(display_text)
        
        # Auto-scroll to bottom
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()
        
        # Update stats
        self.update_stats()
        
        # Emit signal
        self.text_changed.emit()
        
    def clear(self):
        """Clear all text"""
        self.text_edit.clear()
        self.update_stats()
        self.logger.info("Transcription cleared")
        
    def get_text(self) -> str:
        """Get all transcription text"""
        return self.text_edit.toPlainText()
        
    def update_stats(self):
        """Update statistics label"""
        text = self.get_text()
        words = len(text.split()) if text else 0
        chars = len(text)
        
        self.stats_label.setText(f"Words: {words} | Characters: {chars}")
        
    def set_status(self, status: str):
        """Update header status"""
        if status:
            self.header.setText(f"Transcription - {status}")
        else:
            self.header.setText("Transcription")
