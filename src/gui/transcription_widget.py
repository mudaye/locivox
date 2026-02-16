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
        self._cursor_visible = False
        self._cursor_timer = None
        
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
        
        from PyQt6.QtGui import QTextCharFormat, QColor, QFont
        
        # Get current text (without cursor)
        current_text = self.text_edit.toPlainText()
        
        # Remove cursor if present
        while " █" in current_text:
            current_text = current_text.replace(" █", "")
        while "█" in current_text:
            current_text = current_text.replace("█", "")
        
        # Determine spacing
        if not current_text:
            # First text - no spacing needed
            display_text = text
        else:
            # Add spacing between chunks
            if current_text and not current_text.endswith(' '):
                display_text = " " + text
            else:
                display_text = text
        
        # Get cursor
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        
        # Set text format based on final/interim
        fmt = QTextCharFormat()
        if is_final:
            # Final text - black, normal
            fmt.setForeground(QColor(0, 0, 0))  # Black
            fmt.setFontItalic(False)
        else:
            # Interim text - gray, italic
            fmt.setForeground(QColor(136, 136, 136))  # Gray
            fmt.setFontItalic(True)
        
        # Insert text with formatting
        cursor.setCharFormat(fmt)
        cursor.insertText(display_text)
        
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
    
    def replace_text(self, original: str, corrected: str):
        """
        Replace text in display (for vocabulary corrections)
        
        Args:
            original: Text to find and replace
            corrected: Replacement text
        """
        if not original or not corrected or original == corrected:
            return
        
        # Get current text (without cursor)
        current_text = self.text_edit.toPlainText()
        
        # Remove cursor if present
        if current_text.endswith(" █"):
            current_text = current_text[:-2]
        elif current_text.endswith("█"):
            current_text = current_text[:-1]
        
        # Try to find and replace the text
        if original in current_text:
            new_text = current_text.replace(original, corrected)
            
            # Update display
            self.text_edit.setPlainText(new_text)
            
            # Move cursor to end
            cursor = self.text_edit.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.text_edit.setTextCursor(cursor)
            self.text_edit.ensureCursorVisible()
            
            # Update stats
            self.update_stats()
            
            self.logger.info(f"Replaced in display: '{original}' → '{corrected}'")
        else:
            self.logger.warning(f"Could not find text to replace: '{original}'")
    
    def start_cursor_blink(self):
        """Start blinking cursor to indicate active recording"""
        from PyQt6.QtCore import QTimer
        
        if self._cursor_timer is None:
            self._cursor_timer = QTimer()
            self._cursor_timer.timeout.connect(self._toggle_cursor)
        
        self._cursor_visible = True
        self._cursor_timer.start(500)  # Blink every 500ms
        self._update_cursor()
        
    def stop_cursor_blink(self):
        """Stop blinking cursor"""
        if self._cursor_timer:
            self._cursor_timer.stop()
        
        # Remove cursor if present
        if self._cursor_visible:
            self._cursor_visible = False
            self._update_cursor()
    
    def _toggle_cursor(self):
        """Toggle cursor visibility"""
        self._cursor_visible = not self._cursor_visible
        self._update_cursor()
    
    def _update_cursor(self):
        """Update cursor display"""
        # Get current text
        text = self.text_edit.toPlainText()
        
        # Remove ALL existing cursors (there might be multiple)
        while " █" in text:
            text = text.replace(" █", "")
        while "█" in text:
            text = text.replace("█", "")
        
        # Add cursor if visible and we have text
        if self._cursor_visible and text:
            text = text.rstrip() + " █"
        
        # Update display
        self.text_edit.setPlainText(text)
        
        # Move cursor to end
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()
