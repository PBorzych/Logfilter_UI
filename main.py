# Version 1.0

import os
import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import (
    QMainWindow,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMainWindow, 
    QMessageBox, 
    QFileDialog)
from ui import Ui_Logfilter
from functools import partial
from pathlib import Path
from file_processing import find_new_txt_files
from ecu_processing import  load_keywords_from_json
from real_time_monitoring import process_file
from check_errors_in_folder import check_errors_in_folder
from datetime import datetime

version = "1.0.0"

# Load keywords globally
json_file_path = os.path.abspath('reference_list.json')
keywords = load_keywords_from_json(json_file_path)

class LogViewer(QMainWindow):
    def __init__(self, log_content, file_name="", parent=None):
        super(LogViewer, self).__init__(parent)
        self.setWindowTitle(f"Log Viewer - {file_name}" if file_name else "Log Viewer")
        self.setWindowIcon(QIcon('logo.webp'))  # Optional: Set an icon if desired
        self.resize(800, 600)  # Set a default size; adjust as needed

        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # QTextBrowser to display the log content
        self.text_browser = QTextBrowser()
        self.text_browser.setReadOnly(True)
        self.text_browser.setOpenExternalLinks(True)  # Allow opening links if any
        layout.addWidget(self.text_browser)

        # Set the log content
        if file_name.endswith('.html'):
            self.text_browser.setHtml(log_content)
        else:
            self.text_browser.setPlainText(log_content)

class MonitoringThread(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, directory, json_file_path):
        super().__init__()
        self.directory = directory
        self.json_file_path = json_file_path
        self._is_running = True

    def run(self):
        processed_files = set()

        # Populate initial set of processed files to avoid re-processing
        directory = Path(self.directory)
        for file in directory.glob('*.txt'):
            processed_files.add(file.name)

        # Continuous monitoring loop
        while self._is_running:
            new_files = find_new_txt_files(self.directory, processed_files)
            for file in new_files:
                output = process_file(file, self.json_file_path)
                self.output_signal.emit(output)
                processed_files.add(file.name)
            time.sleep(5)
        self.finished_signal.emit()

    def stop(self):
        self._is_running = False

class FullFolderCheckThread(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, directory, json_file_path):
        super().__init__()
        self.directory = directory
        self.json_file_path = json_file_path
        self._is_running = True

    def run(self):
        if self._is_running:
            # Pass the is_running function to check_errors_in_folder
            output = check_errors_in_folder(self.directory, self.json_file_path, is_running=lambda: self._is_running)
            self.output_signal.emit(output)
        self.finished_signal.emit()

    def stop(self):
        self._is_running = False

class MainWindow(QMainWindow, Ui_Logfilter):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # Set the window icon
        self.setWindowIcon(QIcon('logo.webp'))

        self.settings = QSettings("Aurobay", "Logfilter")

        # Load recent directories from external file
        self.recent_directories = self.load_recent_directories()

        # Initialize current_directory
        if self.recent_directories:
            self.current_directory = self.recent_directories[0]
        else:
            self.current_directory = os.path.expanduser("~")  # Set to user's home directory

        # Clear and populate the comboBox with all recent directories
        self.update_combo_box()

        # Update the window title
        self.update_window_title()

        # Update the Recent Directories menu
        self.update_recent_directories_menu()

        # Connect buttons to methods
        self.pushButton_browse.clicked.connect(self.browse_directory)
        self.pushButton_start.clicked.connect(self.start_monitoring)
        self.pushButton_stop.clicked.connect(self.stop_monitoring)
        self.actionOpen_Directory.triggered.connect(self.browse_directory)
        self.actionExit.triggered.connect(self.close_application)
        self.actionSave_Log.triggered.connect(self.save_log)
        self.actionLoad_Log.triggered.connect(self.load_log)
        self.actionSharepoint_Check_N_A.triggered.connect(self.sharepoint_check)
        self.actionAbout.triggered.connect(self.about)

        # Connect the comboBox currentIndexChanged signal to the method
        self.comboBox_directory.currentIndexChanged.connect(self.combo_box_selection_changed)

        # Disable Stop button initially
        self.pushButton_stop.setEnabled(False)

        # Connect mode selection radio buttons if needed
        self.radioButton_real_time.toggled.connect(self.mode_changed)
        self.radioButton_full_folder_check.toggled.connect(self.mode_changed)

        # List to keep references to open LogViewer windows
        self.log_viewers = []

    def combo_box_selection_changed(self, index):
        if index >= 0:
            directory = self.comboBox_directory.itemText(index)
            if directory:
                self.set_directory(directory)

    def update_window_title(self):
        self.setWindowTitle(f"Logfilter {version} - {self.current_directory}")    

    def load_recent_directories(self):
        try:
            with open('recent_directories.txt', 'r') as file:
                directories = [line.strip() for line in file.readlines()]
            return directories
        except FileNotFoundError:
            return []

    def save_recent_directories(self):
        with open('recent_directories.txt', 'w') as file:
            for directory in self.recent_directories:
                file.write(f"{directory}\n")

    def update_recent_directories_menu(self):
        self.menuRecent_Directories.clear()
        for directory in self.recent_directories:
            action = QtWidgets.QAction(directory, self)
            action.triggered.connect(partial(self.set_directory, directory))
            self.menuRecent_Directories.addAction(action)

    def update_combo_box(self):
        # Block signals to prevent triggering currentIndexChanged
        self.comboBox_directory.blockSignals(True)
        self.comboBox_directory.clear()
        for directory in self.recent_directories:
            self.comboBox_directory.addItem(directory)
        # Set the current index to match current_directory
        if self.current_directory in self.recent_directories:
            index = self.recent_directories.index(self.current_directory)
            self.comboBox_directory.setCurrentIndex(index)
        else:
            self.comboBox_directory.setCurrentIndex(-1)
        # Unblock signals after updating
        self.comboBox_directory.blockSignals(False)

    def set_directory(self, directory):
        self.current_directory = directory

        # Update recent directories list
        if directory in self.recent_directories:
            self.recent_directories.remove(directory)
        self.recent_directories.insert(0, directory)
        if len(self.recent_directories) > 5:  # Limit to 5 recent directories
            self.recent_directories = self.recent_directories[:5]

        # Save to external file
        self.save_recent_directories()

        # Update the menu and combo box
        self.update_recent_directories_menu()
        self.update_combo_box()

        # Update the window title
        self.update_window_title()

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", self.current_directory)
        if directory:
            self.set_directory(directory)

    def start_monitoring(self):
        if not hasattr(self, 'current_directory') or not self.current_directory:
            QMessageBox.warning(self, "Warning", "Please select a directory before starting monitoring.")
            return

        if self.radioButton_real_time.isChecked():
            # Start real-time monitoring
            self.monitoring_thread = MonitoringThread(self.current_directory, json_file_path)
            self.monitoring_thread.output_signal.connect(self.update_output)
            self.monitoring_thread.finished_signal.connect(self.monitoring_finished)
            self.monitoring_thread.start()
            self.pushButton_start.setEnabled(False)
            self.pushButton_stop.setEnabled(True)
            self.label_status_value.setText("Monitoring...")
            self.label_status_value.setStyleSheet("color: green;")
        elif self.radioButton_full_folder_check.isChecked():
            # Start full folder error check
            self.full_folder_thread = FullFolderCheckThread(self.current_directory, json_file_path)
            self.full_folder_thread.output_signal.connect(self.update_full_folder_output)
            self.full_folder_thread.finished_signal.connect(self.full_folder_finished)
            self.full_folder_thread.start()
            self.pushButton_start.setEnabled(False)
            self.pushButton_stop.setEnabled(True)
            self.label_status_value.setText("Processing...")
            self.label_status_value.setStyleSheet("color: green;")
        else:
            QMessageBox.warning(self, "Warning", "Please select a mode before starting.")

    def stop_monitoring(self):
        if hasattr(self, 'monitoring_thread') and self.monitoring_thread.isRunning():
            self.monitoring_thread.stop()
            self.monitoring_thread.wait()
        if hasattr(self, 'full_folder_thread') and self.full_folder_thread.isRunning():
            self.full_folder_thread.stop()
            self.full_folder_thread.wait()
        self.pushButton_start.setEnabled(True)
        self.pushButton_stop.setEnabled(False)
        self.label_status_value.setText("Stopped")
        self.label_status_value.setStyleSheet("color: red;")

    def append_log(self, text):
        #Appends text to the log and scrolls to the bottom.
        existing_text = self.textBrowser_log.toPlainText()
        if text not in existing_text:
            self.textBrowser_log.append(text)
            self.textBrowser_log.moveCursor(QTextCursor.End)

    def set_full_log(self, html_text):
        #Sets the entire log with HTML content and scrolls to the bottom.
        self.textBrowser_log.clear()
        self.textBrowser_log.setHtml(html_text)
        self.textBrowser_log.moveCursor(QTextCursor.End)

    def update_output(self, text):
        self.append_log(text)

    def update_full_folder_output(self, text):
        self.set_full_log(text)

    def full_folder_finished(self):
        QMessageBox.information(self, "Info", "Full folder error check has finished.")
        self.pushButton_start.setEnabled(True)
        self.pushButton_stop.setEnabled(False)
        self.label_status_value.setText("Completed")
        self.label_status_value.setStyleSheet("color: blue;")

    def monitoring_finished(self):
        QMessageBox.information(self, "Info", "Monitoring has finished.")
        self.pushButton_start.setEnabled(True)
        self.pushButton_stop.setEnabled(False)
        self.label_status_value.setText("Completed")
        self.label_status_value.setStyleSheet("color: blue;")

    def save_log(self):
        # Generate a timestamped default filename
        current_time = datetime.now()
        timestamp = current_time.strftime("%Y%m%d-%H%M%S")  # Format: YYYYMMDD-HHMMSS
        default_filename = f"log-{timestamp}.txt"

        # Set the default directory to the user's Documents folder
        default_directory = os.path.expanduser(self.current_directory)
        default_path = os.path.join(default_directory, default_filename)

        # Open a file dialog to choose where to save the log file with the default filename
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            "Save Log",
            default_path, 
            "Text Files (*.txt);;HTML Files (*.html);;All Files (*)", #Choice of .txt or .html
            options=options
        )

        if fileName:
            try:
                # Determine the encoding based on file extension
                if fileName.endswith('.html'):
                    content = self.textBrowser_log.toHtml()
                else:
                    content = self.textBrowser_log.toPlainText()

                # Write the content to the file
                with open(fileName, 'w', encoding='utf-8') as file:
                    file.write(content)

                # Update the status label
                self.label_status_value.setText(f"Log saved to: {fileName}")
                self.label_status_value.setStyleSheet("color: green;")

                # Save the last saved log path
                self.settings.setValue("last_saved_log", fileName)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save log: {str(e)}")
                self.label_status_value.setText("Failed to save log")
                self.label_status_value.setStyleSheet("color: red;")
        else:
            self.label_status_value.setText("Save log cancelled")
            self.label_status_value.setStyleSheet("color: orange;")

    def load_log(self):
        # Retrieve the last saved log path from QSettings
        last_log = self.settings.value("last_saved_log", "")

        # Open a file dialog to choose which log file to load
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        initial_dir = os.path.dirname(last_log) if os.path.exists(last_log) else os.path.expanduser(self.current_directory)
        initial_file = last_log if os.path.exists(last_log) else ""
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Load Log",
            initial_file,
            "Text Files (*.txt);;HTML Files (*.html);;All Files (*)",
            options=options
        )

        if fileName:
            try:
                # Read the content based on file extension
                if fileName.endswith('.html'):
                    with open(fileName, 'r', encoding='utf-8') as file:
                        content = file.read()
                else:
                    with open(fileName, 'r', encoding='utf-8') as file:
                        content = file.read()

                # Create and show the LogViewer window
                log_viewer = LogViewer(log_content=content, file_name=os.path.basename(fileName))
                log_viewer.show()

                # Keep a reference to prevent garbage collection
                self.log_viewers.append(log_viewer)

                # Update the status label
                self.label_status_value.setText(f"Log loaded from: {fileName}")
                self.label_status_value.setStyleSheet("color: green;")

                # Save the last loaded log path
                self.settings.setValue("last_loaded_log", fileName)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load log: {str(e)}")
                self.label_status_value.setText("Failed to load log")
                self.label_status_value.setStyleSheet("color: red;")
        else:
            self.label_status_value.setText("Load log cancelled")
            self.label_status_value.setStyleSheet("color: orange;")

    def sharepoint_check(self):
        # Implement your sharepoint_check method here
        QMessageBox.information(self, "Info", "Sharepoint Check is not available (N/A).")

    def about(self):
        QMessageBox.about(
            self,
            "About Logfilter",
            f"<b>Logfilter</b><br>Version {version}<br><br>"
            "This application is designed to filter logs from Silver Scan-Tool and perform live monitoring."
        )

    def close_application(self):
        reply = QMessageBox.question(
            self,
            'Confirm Exit',
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()

    def mode_changed(self):
        if self.radioButton_real_time.isChecked():
            self.label_status_value.setText("Mode set to Real-time Monitoring")
            self.label_status_value.setStyleSheet("color: blue;")
        elif self.radioButton_full_folder_check.isChecked():
            self.label_status_value.setText("Mode set to Full Folder Error Check")
            self.label_status_value.setStyleSheet("color: blue;")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    