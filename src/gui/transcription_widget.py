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
        
        # Enable context menu
        self.text_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.text_edit.customContextMenuRequested.connect(self.show_context_menu)
        
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
    
    def show_context_menu(self, position):
        """Show context menu for word correction"""
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        
        # Get cursor at position
        cursor = self.text_edit.cursorForPosition(position)
        
        # Select word under cursor
        cursor.select(cursor.SelectionType.WordUnderCursor)
        selected_text = cursor.selectedText().strip()
        
        if not selected_text:
            return
        
        # Create context menu
        menu = QMenu(self.text_edit)
        
        # Add "Correct..." action
        correct_action = QAction(f"Correct '{selected_text}'...", self.text_edit)
        correct_action.triggered.connect(lambda: self.correct_word(selected_text))
        menu.addAction(correct_action)
        
        menu.addSeparator()
        
        # Add standard actions
        copy_action = QAction("Copy", self.text_edit)
        copy_action.triggered.connect(self.text_edit.copy)
        copy_action.setEnabled(self.text_edit.textCursor().hasSelection())
        menu.addAction(copy_action)
        
        select_all_action = QAction("Select All", self.text_edit)
        select_all_action.triggered.connect(self.text_edit.selectAll)
        menu.addAction(select_all_action)
        
        # Show menu
        menu.exec(self.text_edit.mapToGlobal(position))
    
    def correct_word(self, word: str):
        """Open correction dialog for a word"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Correct Word")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Info
        info = QLabel(f"Correct '{word}' to:")
        layout.addWidget(info)
        
        # Input
        input_field = QLineEdit()
        input_field.setPlaceholderText("Enter correct form")
        input_field.setText(word)
        input_field.selectAll()
        layout.addWidget(input_field)
        
        # Checkbox to add to vocabulary
        from PyQt6.QtWidgets import QCheckBox
        add_to_vocab = QCheckBox("Add to vocabulary for future corrections")
        add_to_vocab.setChecked(True)
        layout.addWidget(add_to_vocab)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("Correct")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            corrected = input_field.text().strip()
            
            if corrected and corrected != word:
                # Replace in display
                self.replace_text(word, corrected)
                
                # Add to vocabulary if checked
                if add_to_vocab.isChecked():
                    self.add_to_vocabulary(word, corrected)
                
                self.logger.info(f"Corrected '{word}' → '{corrected}' (vocab: {add_to_vocab.isChecked()})")
    
    def add_to_vocabulary(self, variation: str, correct: str):
        """Add a word to vocabulary file"""
        try:
            # Get vocabulary file from parent window config
            parent_window = self.window()
            vocab_file = parent_window.config.get('vocabulary', {}).get('file', './vocabulary.txt')
            
            import os
            
            # Read existing vocabulary
            terms = []
            if os.path.exists(vocab_file):
                with open(vocab_file, 'r', encoding='utf-8') as f:
                    current_term = None
                    
                    for line in f:
                        line = line.strip()
                        
                        if not line or line.startswith('#'):
                            continue
                        
                        if line.startswith('correct:'):
                            if current_term:
                                terms.append(current_term)
                            
                            correct_form = line.split(':', 1)[1].strip()
                            current_term = {'correct': correct_form, 'variations': []}
                            
                        elif line.startswith('-') and current_term:
                            var = line[1:].strip()
                            if var:
                                current_term['variations'].append(var)
                    
                    if current_term:
                        terms.append(current_term)
            
            # Check if correct form already exists
            existing_term = None
            for term in terms:
                if term['correct'].lower() == correct.lower():
                    existing_term = term
                    break
            
            if existing_term:
                # Add variation if not already present
                if variation.lower() not in [v.lower() for v in existing_term['variations']]:
                    existing_term['variations'].append(variation)
                    self.logger.info(f"Added variation '{variation}' to existing term '{correct}'")
            else:
                # Create new term
                terms.append({'correct': correct, 'variations': [variation]})
                self.logger.info(f"Created new vocabulary term '{correct}' with variation '{variation}'")
            
            # Save vocabulary
            os.makedirs(os.path.dirname(vocab_file) or '.', exist_ok=True)
            
            with open(vocab_file, 'w', encoding='utf-8') as f:
                f.write("# Locivox Custom Vocabulary\n\n")
                
                for term in terms:
                    f.write(f"correct: {term['correct']}\n")
                    for var in term['variations']:
                        f.write(f"- {var}\n")
                    f.write("\n")
            
            # Show confirmation
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Added to Vocabulary",
                f"Added '{variation}' → '{correct}' to vocabulary.\n\n"
                "This correction will be applied automatically in future recordings."
            )
            
        except Exception as e:
            self.logger.error(f"Error adding to vocabulary: {e}", exc_info=True)
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to add to vocabulary:\n{e}"
            )
