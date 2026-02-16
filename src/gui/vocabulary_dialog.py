"""
Vocabulary Manager Dialog
Manage custom vocabulary terms for transcription correction
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLabel, QLineEdit, QTextEdit, QGroupBox, QFormLayout,
    QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
import logging
import os


class VocabularyDialog(QDialog):
    """Dialog for managing vocabulary terms"""
    
    # Signal emitted when vocabulary is modified
    vocabulary_changed = pyqtSignal()
    
    def __init__(self, vocab_file: str, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger('locivox.gui.vocabulary')
        self.vocab_file = vocab_file
        self.terms = []  # List of {correct: str, variations: [str]}
        
        self.init_ui()
        self.load_vocabulary()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Vocabulary Manager")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Info label
        info = QLabel(
            f"Managing vocabulary file: {os.path.basename(self.vocab_file)}\n"
            "Add custom terms and their variations to improve transcription accuracy."
        )
        info.setWordWrap(True)
        info.setStyleSheet("QLabel { color: #666; padding: 10px; background: #f0f0f0; border-radius: 5px; }")
        layout.addWidget(info)
        
        # Table for displaying terms
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Correct Form", "Variations", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.on_edit_term)
        layout.addWidget(self.table)
        
        # Add/Edit form (initially hidden)
        self.form_group = QGroupBox("Add/Edit Term")
        self.form_group.setVisible(False)
        form_layout = QFormLayout()
        
        self.correct_input = QLineEdit()
        self.correct_input.setPlaceholderText("e.g., Kubernetes")
        form_layout.addRow("Correct Form:", self.correct_input)
        
        self.variations_input = QTextEdit()
        self.variations_input.setPlaceholderText(
            "Enter variations, one per line:\n"
            "kubernetes\n"
            "coober netes\n"
            "kube ernetes"
        )
        self.variations_input.setMaximumHeight(100)
        form_layout.addRow("Variations:", self.variations_input)
        
        form_buttons = QHBoxLayout()
        form_buttons.addStretch()
        
        self.save_term_btn = QPushButton("Save Term")
        self.save_term_btn.clicked.connect(self.save_current_term)
        form_buttons.addWidget(self.save_term_btn)
        
        self.cancel_edit_btn = QPushButton("Cancel")
        self.cancel_edit_btn.clicked.connect(self.cancel_edit)
        form_buttons.addWidget(self.cancel_edit_btn)
        
        form_layout.addRow("", form_buttons)
        self.form_group.setLayout(form_layout)
        layout.addWidget(self.form_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Term")
        self.add_btn.clicked.connect(self.add_term)
        button_layout.addWidget(self.add_btn)
        
        self.import_btn = QPushButton("Import...")
        self.import_btn.clicked.connect(self.import_vocabulary)
        button_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("Export...")
        self.export_btn.clicked.connect(self.export_vocabulary)
        button_layout.addWidget(self.export_btn)
        
        self.test_btn = QPushButton("Test Matcher...")
        self.test_btn.clicked.connect(self.test_matcher)
        button_layout.addWidget(self.test_btn)
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Track if we're editing
        self.editing_index = -1
        
    def load_vocabulary(self):
        """Load vocabulary from file"""
        self.terms = []
        
        if not os.path.exists(self.vocab_file):
            self.logger.info(f"Vocabulary file not found: {self.vocab_file}")
            self.refresh_table()
            return
        
        try:
            with open(self.vocab_file, 'r', encoding='utf-8') as f:
                current_term = None
                
                for line in f:
                    line = line.strip()
                    
                    if not line or line.startswith('#'):
                        continue
                    
                    if line.startswith('correct:'):
                        # Save previous term if exists
                        if current_term:
                            self.terms.append(current_term)
                        
                        # Start new term
                        correct = line.split(':', 1)[1].strip()
                        current_term = {'correct': correct, 'variations': []}
                        
                    elif line.startswith('-') and current_term:
                        # Add variation
                        variation = line[1:].strip()
                        if variation:
                            current_term['variations'].append(variation)
                
                # Save last term
                if current_term:
                    self.terms.append(current_term)
            
            self.logger.info(f"Loaded {len(self.terms)} vocabulary terms")
            self.refresh_table()
            
        except Exception as e:
            self.logger.error(f"Error loading vocabulary: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error Loading Vocabulary",
                f"Failed to load vocabulary file:\n\n{e}"
            )
    
    def save_vocabulary(self):
        """Save vocabulary to file"""
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(self.vocab_file) or '.', exist_ok=True)
            
            with open(self.vocab_file, 'w', encoding='utf-8') as f:
                f.write("# Locivox Custom Vocabulary\n")
                f.write("# Format:\n")
                f.write("# correct: Correct Form\n")
                f.write("# - variation 1\n")
                f.write("# - variation 2\n")
                f.write("\n")
                
                for term in self.terms:
                    f.write(f"correct: {term['correct']}\n")
                    for variation in term['variations']:
                        f.write(f"- {variation}\n")
                    f.write("\n")
            
            self.logger.info(f"Saved {len(self.terms)} vocabulary terms")
            self.vocabulary_changed.emit()
            
        except Exception as e:
            self.logger.error(f"Error saving vocabulary: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error Saving Vocabulary",
                f"Failed to save vocabulary file:\n\n{e}"
            )
            raise
    
    def refresh_table(self):
        """Refresh the table display"""
        self.table.setRowCount(0)
        
        for i, term in enumerate(self.terms):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Correct form
            self.table.setItem(row, 0, QTableWidgetItem(term['correct']))
            
            # Variations (comma-separated)
            variations_text = ", ".join(term['variations'][:3])
            if len(term['variations']) > 3:
                variations_text += f" ... (+{len(term['variations']) - 3} more)"
            self.table.setItem(row, 1, QTableWidgetItem(variations_text))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(4, 4, 4, 4)
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, idx=i: self.edit_term(idx))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, idx=i: self.delete_term(idx))
            actions_layout.addWidget(delete_btn)
            
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 2, actions_widget)
    
    def add_term(self):
        """Start adding a new term"""
        self.editing_index = -1
        self.correct_input.clear()
        self.variations_input.clear()
        self.form_group.setTitle("Add Term")
        self.form_group.setVisible(True)
        self.correct_input.setFocus()
        
        # Disable table actions while editing
        self.add_btn.setEnabled(False)
        self.table.setEnabled(False)
    
    def edit_term(self, index: int):
        """Edit an existing term"""
        if index < 0 or index >= len(self.terms):
            return
        
        term = self.terms[index]
        self.editing_index = index
        
        self.correct_input.setText(term['correct'])
        self.variations_input.setPlainText("\n".join(term['variations']))
        
        self.form_group.setTitle("Edit Term")
        self.form_group.setVisible(True)
        self.correct_input.setFocus()
        
        # Disable table actions while editing
        self.add_btn.setEnabled(False)
        self.table.setEnabled(False)
    
    def on_edit_term(self, item):
        """Handle double-click on table item"""
        row = item.row()
        if 0 <= row < len(self.terms):
            self.edit_term(row)
    
    def save_current_term(self):
        """Save the currently edited term"""
        correct = self.correct_input.text().strip()
        variations_text = self.variations_input.toPlainText()
        
        # Validate
        if not correct:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter a correct form."
            )
            return
        
        # Parse variations
        variations = [v.strip() for v in variations_text.split('\n') if v.strip()]
        
        if not variations:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter at least one variation."
            )
            return
        
        # Create term
        term = {'correct': correct, 'variations': variations}
        
        # Add or update
        if self.editing_index == -1:
            # Adding new
            self.terms.append(term)
        else:
            # Updating existing
            self.terms[self.editing_index] = term
        
        # Save to file
        try:
            self.save_vocabulary()
            self.refresh_table()
            self.cancel_edit()
            
            action = "added" if self.editing_index == -1 else "updated"
            QMessageBox.information(
                self,
                "Success",
                f"Term '{correct}' {action} successfully!"
            )
            
        except Exception as e:
            # Error already shown by save_vocabulary
            pass
    
    def cancel_edit(self):
        """Cancel editing"""
        self.editing_index = -1
        self.form_group.setVisible(False)
        self.add_btn.setEnabled(True)
        self.table.setEnabled(True)
    
    def delete_term(self, index: int):
        """Delete a term"""
        if index < 0 or index >= len(self.terms):
            return
        
        term = self.terms[index]
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the term '{term['correct']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.terms.pop(index)
            
            try:
                self.save_vocabulary()
                self.refresh_table()
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Term '{term['correct']}' deleted successfully!"
                )
            except Exception as e:
                # Error already shown
                pass
    
    def import_vocabulary(self):
        """Import vocabulary from another file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import Vocabulary",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if not filename:
            return
        
        try:
            # Load from selected file
            imported_terms = []
            with open(filename, 'r', encoding='utf-8') as f:
                current_term = None
                
                for line in f:
                    line = line.strip()
                    
                    if not line or line.startswith('#'):
                        continue
                    
                    if line.startswith('correct:'):
                        if current_term:
                            imported_terms.append(current_term)
                        
                        correct = line.split(':', 1)[1].strip()
                        current_term = {'correct': correct, 'variations': []}
                        
                    elif line.startswith('-') and current_term:
                        variation = line[1:].strip()
                        if variation:
                            current_term['variations'].append(variation)
                
                if current_term:
                    imported_terms.append(current_term)
            
            if not imported_terms:
                QMessageBox.information(
                    self,
                    "No Terms Found",
                    "No vocabulary terms found in the selected file."
                )
                return
            
            # Ask to merge or replace
            reply = QMessageBox.question(
                self,
                "Import Mode",
                f"Found {len(imported_terms)} terms in the file.\n\n"
                "Do you want to MERGE with existing terms?\n"
                "(Select 'No' to REPLACE all existing terms)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return
            
            if reply == QMessageBox.StandardButton.Yes:
                # Merge
                self.terms.extend(imported_terms)
            else:
                # Replace
                self.terms = imported_terms
            
            self.save_vocabulary()
            self.refresh_table()
            
            QMessageBox.information(
                self,
                "Import Successful",
                f"Imported {len(imported_terms)} terms successfully!"
            )
            
        except Exception as e:
            self.logger.error(f"Error importing vocabulary: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Failed to import vocabulary:\n\n{e}"
            )
    
    def export_vocabulary(self):
        """Export vocabulary to another file"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Vocabulary",
            "vocabulary_export.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# Locivox Custom Vocabulary Export\n\n")
                
                for term in self.terms:
                    f.write(f"correct: {term['correct']}\n")
                    for variation in term['variations']:
                        f.write(f"- {variation}\n")
                    f.write("\n")
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Vocabulary exported to:\n{filename}"
            )
            
        except Exception as e:
            self.logger.error(f"Error exporting vocabulary: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export vocabulary:\n\n{e}"
            )
    
    def test_matcher(self):
        """Test the matcher with sample input"""
        from .vocabulary_test_dialog import VocabularyTestDialog
        
        dialog = VocabularyTestDialog(self.vocab_file, self)
        dialog.exec()
