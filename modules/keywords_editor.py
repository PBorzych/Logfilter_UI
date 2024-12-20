from PyQt5.QtWidgets import (QDialog, 
                            QVBoxLayout, 
                            QHBoxLayout, 
                            QTableWidget, 
                            QTableWidgetItem, 
                            QPushButton, 
                            QMessageBox)

import json
import os
from constants import KEYWORD_LIST_FILE


class KeywordsEditorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.json_file = KEYWORD_LIST_FILE 
        self.setup_ui()
        self.load_keywords()

    def setup_ui(self):
        self.setWindowTitle("Keywords Editor")
        self.setMinimumSize(500, 400)

        # Main layout
        layout = QVBoxLayout(self)

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Category", "Keywords"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Buttons layout
        button_layout = QHBoxLayout()

        # Add buttons
        self.add_button = QPushButton("Add Row")
        self.delete_button = QPushButton("Delete Row")
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # Connect signals
        self.add_button.clicked.connect(self.add_row)
        self.delete_button.clicked.connect(self.delete_row)
        self.save_button.clicked.connect(self.save_keywords)
        self.cancel_button.clicked.connect(self.reject)

    def load_keywords(self):
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r') as f:
                    keywords_dict = json.load(f)
            else:
                keywords_dict = {"errors": ["error", "warning", "fatal"],
                               "success": ["completed", "successful"]}

            # Populate table
            self.table.setRowCount(len(keywords_dict))
            for row, (category, keywords) in enumerate(keywords_dict.items()):
                category_item = QTableWidgetItem(category)
                keywords_item = QTableWidgetItem(", ".join(keywords))
                self.table.setItem(row, 0, category_item)
                self.table.setItem(row, 1, keywords_item)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load keywords: {str(e)}")

    def add_row(self):
        current_row = self.table.rowCount()
        self.table.insertRow(current_row)
        self.table.setItem(current_row, 0, QTableWidgetItem(""))
        self.table.setItem(current_row, 1, QTableWidgetItem(""))

    def delete_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)

    def save_keywords(self):
        try:
            keywords_dict = {}
            for row in range(self.table.rowCount()):
                category = self.table.item(row, 0).text().strip()
                keywords_text = self.table.item(row, 1).text().strip()

                if category and keywords_text:  # Only save non-empty rows
                    keywords = [k.strip() for k in keywords_text.split(",")]
                    keywords_dict[category] = keywords

            with open(self.json_file, 'w') as f:
                json.dump(keywords_dict, f, indent=4)

            QMessageBox.information(self, "Success", "Keywords saved successfully!")
            self.accept()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save keywords: {str(e)}")