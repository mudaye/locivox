"""
Vocabulary Test Dialog
Test vocabulary matcher with sample inputs
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt
import logging


class VocabularyTestDialog(QDialog):
    """Dialog for testing vocabulary matcher"""
    
    def __init__(self, vocab_file: str, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger('locivox.gui.vocab_test')
        self.vocab_file = vocab_file
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Test Vocabulary Matcher")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        # Info
        info = QLabel(
            "Test how the vocabulary matcher will correct your transcriptions.\n"
            "Enter text below and click 'Test' to see the corrections."
        )
        info.setWordWrap(True)
        info.setStyleSheet("QLabel { color: #666; padding: 10px; }")
        layout.addWidget(info)
        
        # Input group
        input_group = QGroupBox("Input Text")
        input_layout = QVBoxLayout()
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText(
            "Enter test text here...\n\n"
            "Example:\n"
            "I use coober netes to deploy my applications.\n"
            "Postgre is great for databases."
        )
        input_layout.addWidget(self.input_text)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Test button
        test_btn_layout = QHBoxLayout()
        test_btn_layout.addStretch()
        
        self.test_btn = QPushButton("Test Corrections")
        self.test_btn.setMinimumWidth(150)
        self.test_btn.clicked.connect(self.run_test)
        test_btn_layout.addWidget(self.test_btn)
        
        layout.addLayout(test_btn_layout)
        
        # Output group
        output_group = QGroupBox("Corrected Text")
        output_layout = QVBoxLayout()
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Corrections will appear here...")
        output_layout.addWidget(self.output_text)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        close_layout.addWidget(self.close_btn)
        
        layout.addLayout(close_layout)
        
        self.setLayout(layout)
    
    def run_test(self):
        """Run the vocabulary matcher test"""
        input_text = self.input_text.toPlainText().strip()
        
        if not input_text:
            self.output_text.setPlainText("Please enter some text to test.")
            return
        
        try:
            # Import and create vocabulary manager
            from src.vocabulary import VocabularyManager
            from src.utils import load_config
            
            config = load_config()
            config['vocabulary']['file'] = self.vocab_file
            config['vocabulary']['enabled'] = True
            
            vocab_manager = VocabularyManager(config)
            
            # Apply corrections
            corrected_text = vocab_manager.apply_vocabulary(input_text)
            
            # Show results
            if corrected_text == input_text:
                self.output_text.setPlainText(
                    "No corrections made.\n\n"
                    "Original text:\n" + input_text
                )
            else:
                # Show before and after
                result = "=== CORRECTIONS MADE ===\n\n"
                result += "BEFORE:\n" + input_text + "\n\n"
                result += "AFTER:\n" + corrected_text + "\n\n"
                result += "=== CHANGES ===\n"
                
                # Show what changed
                original_words = input_text.split()
                corrected_words = corrected_text.split()
                
                for i, (orig, corr) in enumerate(zip(original_words, corrected_words)):
                    if orig != corr:
                        result += f"• '{orig}' → '{corr}'\n"
                
                self.output_text.setPlainText(result)
            
            self.logger.info("Vocabulary test completed")
            
        except Exception as e:
            self.logger.error(f"Error testing vocabulary: {e}", exc_info=True)
            self.output_text.setPlainText(
                f"Error testing vocabulary:\n\n{e}\n\n"
                "Make sure vocabulary terms are properly configured."
            )
