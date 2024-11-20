# Version 1.0.0

import time
import traceback
import sys

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
    QApplication, 
    QMessageBox)
from ui import Ui_Logfilter
from functools import partial
from pathlib import Path
from file_processing import find_new_txt_files
from ecu_processing import  load_keywords_from_json
from real_time_monitoring import process_file
from check_errors_in_folder import check_errors_in_folder
from datetime import datetime
from functools import partial

version = "1.0.0"

# Crash log directory and file
CRASH_LOG_DIRECTORY = Path("CrashLogs")
CRASH_LOG_FILE = CRASH_LOG_DIRECTORY / "crash_report-log"

# Ensure the crash log directory exists
CRASH_LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

# Load keywords globally
json_file_path = Path('reference_list.json').resolve()
keywords = load_keywords_from_json(json_file_path)

class LogViewer(QMainWindow):
    closed = pyqtSignal()
    def __init__(self, log_content, file_name="", parent=None):
        super(LogViewer, self).__init__(parent)
        self.setWindowTitle(f"Log Viewer - {file_name}" if file_name else "Log Viewer")
        self.setWindowIcon(QIcon('AurobayLogo.png'))
        self.resize(800, 600)  # Set a default size

        #closed = pyqtSignal()

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
    
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

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

        # Determine the base path
        if getattr(sys, 'frozen', False):
            # Running in a PyInstaller bundle
            base_path = Path(sys._MEIPASS)
        else:
            # Running in a normal Python environment
            base_path = Path(__file__).parent

        # Construct the full path to the icon
        icon_path = base_path / 'AurobayLogo.png'

        # Set the window icon
        self.setWindowIcon(QIcon(str(icon_path)))

        self.settings = QSettings("Aurobay", "Logfilter")

        # Define log subfolder path
        self.LOG_SUBFOLDER = "Logs"

        # Load recent directories from external file
        self.recent_directories = self.load_recent_directories()

        # Initialize current_directory
        if self.recent_directories:
            self.current_directory = Path(self.recent_directories[0])
        else:
            self.current_directory = Path.home()  # Use the user's home directory

        # Define the log directory as a subfolder within the scanned directory
        self.log_directory = Path(self.current_directory) / self.LOG_SUBFOLDER

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

        # Ensure the Logs subfolder exists
        self.ensure_log_directory()

    def update_recent_logs_menu(self):
        """Updates the Recent Logs submenu with the latest log files."""
        # Clear the existing actions in the Recent Logs menu
        self.menuRecent_Logs.clear()
        # Iterate over the recent_logs list and add each as an action
        for log in self.recent_logs:
            action = QtWidgets.QAction(log, self)
            # Connect the action to the open_recent_log method with the file path
            action.triggered.connect(partial(self.open_recent_log, log))
            self.menuRecent_Logs.addAction(action)

    def ensure_log_directory(self):
        """Ensures that the Logs subfolder exists within the scanned directory; creates it if it doesn't."""
        # Ensure self.log_directory is a Path object
        log_directory_path = Path(self.log_directory)

        if not log_directory_path.exists():
            try:
                log_directory_path.mkdir(parents=True, exist_ok=True)
                print(f"Created log directory at: {log_directory_path}")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to create log directory at {log_directory_path}:\n{str(e)}"
                )
                self.label_status_value.setText("Failed to create log directory")
                self.label_status_value.setStyleSheet("color: red;")

    def combo_box_selection_changed(self, index):
        if index >= 0:
            directory = self.comboBox_directory.itemText(index)
            if directory:
                self.set_directory(directory)

    def update_window_title(self):
        self.setWindowTitle(f"Logfilter {version} - {self.current_directory}")

    def load_recent_directories(self):
        directories = self.settings.value("recent_directories")
        # Convert directories to Path objects
        if directories:
            return [Path(dir_str) for dir_str in directories]
        else:
            return []

    def save_recent_directories(self):
        # Convert Path objects to strings before saving
        directories_as_strings = [str(dir_path) for dir_path in self.recent_directories]
        self.settings.setValue("recent_directories", directories_as_strings)

    # def load_recent_directories(self):
    #     try:
    #         with open('recent_directories.txt', 'r') as file:
    #             directories = [line.strip() for line in file.readlines()]
    #         return directories
    #     except FileNotFoundError:
    #         return []

    # def save_recent_directories(self):
    #     with open('recent_directories.txt', 'w') as file:
    #         for directory in self.recent_directories:
    #             file.write(f"{directory}\n")

    def update_recent_directories_menu(self):
        self.menuRecent_Directories.clear()
        for directory in self.recent_directories:
            action = QtWidgets.QAction(str(directory), self)
            action.triggered.connect(partial(self.set_directory, directory))
            self.menuRecent_Directories.addAction(action)

    def add_to_recent_logs(self, file_path):
        """Adds a file path to the recent logs list and updates the menu."""
         # Ensure file_path is a Path object
        file_path = Path(file_path)
        # Remove the file_path if it's already in the list to avoid duplicates
        if file_path in self.recent_logs:
            self.recent_logs.remove(file_path)
        # Insert the file_path at the beginning of the list
        self.recent_logs.insert(0, file_path)
        # Keep only the 5 most recent logs
        if len(self.recent_logs) > 5:
            self.recent_logs = self.recent_logs[:5]
        # Save the updated recent_logs list to QSettings
        self.settings.setValue("recent_logs", self.recent_logs)
        # Update the Recent Logs menu to reflect the changes
        self.update_recent_logs_menu()

    def update_combo_box(self):
        # Block signals to prevent triggering currentIndexChanged
        self.comboBox_directory.blockSignals(True)
        self.comboBox_directory.clear()
        for directory in self.recent_directories:
            self.comboBox_directory.addItem(str(directory))
        # Set the current index to match current_directory
        if self.current_directory in self.recent_directories:
            index = self.recent_directories.index(self.current_directory)
            self.comboBox_directory.setCurrentIndex(index)
        else:
            self.comboBox_directory.setCurrentIndex(-1)
        # Unblock signals after updating
        self.comboBox_directory.blockSignals(False)

    def set_directory(self, directory):
        self.current_directory = Path(directory)

        # Update log_directory based on current_directory
        self.log_directory = Path(self.current_directory) / self.LOG_SUBFOLDER

        # Ensure Logs subfolder exists within the new scanned directory
        self.ensure_log_directory()

        # Update recent directories list
        if directory in self.recent_directories:
            self.recent_directories.remove(directory)
        self.recent_directories.insert(0, directory)
        if len(self.recent_directories) > 5:
            self.recent_directories = self.recent_directories[:5]

        # Save to external file
        self.save_recent_directories()

        # Update the menu and combo box
        self.update_recent_directories_menu()
        self.update_combo_box()

        # Update the window title
        self.update_window_title()

    def browse_directory(self):
        current_directory = Path(self.current_directory)
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", str(current_directory))
        if directory:
            self.set_directory(Path(directory))

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

        # Ensure log_directory_path is a Path object
        log_directory_path = Path(self.log_directory)

        # Create the default path for the save dialog
        default_path = log_directory_path / default_filename

        # Open a file dialog to choose where to save the log file with the default filename
        options = QFileDialog.Options()

        # options |= QFileDialog.DontUseNativeDialog

        fileName, _ = QFileDialog.getSaveFileName(
            self,
            "Save Log",
            str(default_path), 
            "Text Files (*.txt);;HTML Files (*.html);;All Files (*)", #Choice of .txt or .html
            options=options
        )

        if fileName:
            try:
                # Normalize paths for comparison
                normalized_log_dir = log_directory_path.resolve()
                normalized_file_path = Path(fileName).resolve()

                # Check if the file is within the Logs subfolder
                if not normalized_file_path.is_relative_to(normalized_log_dir):
                    # Warn the user and abort saving
                    QMessageBox.warning(
                        self,
                        "Save Location Warning",
                        f"Please save the log within the Logs directory:\n{self.log_directory}"
                    )
                    return  # Exit the method without saving

                # Determine the content format based on file extension
                if normalized_file_path.suffix == '.html':
                    content = self.textBrowser_log.toHtml()
                else:
                    content = self.textBrowser_log.toPlainText()

                # Write the content to the file
                with open(fileName, 'w', encoding='utf-8') as file:
                    file.write(content)

                # Update the status label
                self.label_status_value.setText(f"Log saved to: {normalized_file_path}")
                self.label_status_value.setStyleSheet("color: green;")

                # Save the last saved log path
                self.settings.setValue("last_saved_log", normalized_file_path)

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save log: {str(e)}"
                )
                self.label_status_value.setText("Failed to save log")
                self.label_status_value.setStyleSheet("color: red;")
        else:
            self.label_status_value.setText("Save log cancelled")
            self.label_status_value.setStyleSheet("color: orange;")

    def load_log(self):
        # Ensure self.log_directory is defined and points to the Logs directory
        if not hasattr(self, 'log_directory') or not self.log_directory:
            QMessageBox.critical(
                self,
                "Error",
                "Log directory is not defined. Please set self.log_directory."
            )
            self.label_status_value.setText("Load log failed: Log directory undefined")
            self.label_status_value.setStyleSheet("color: red;")
            return

        # Set initial directory to Logs subfolder
        initial_dir = self.log_directory

        # Open a file dialog to choose which log file to load
        options = QFileDialog.Options()

        # Convert Path to string for QFileDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Load Log",
            str(initial_dir),  # Convert Path to string
            "Text Files (*.txt);;HTML Files (*.html);;All Files (*)",
            options=options
        )

        if fileName:
            try:
                selected_file = Path(fileName).resolve()
                log_dir_resolved = self.log_directory.resolve()

                # Ensure the selected file is within the Logs subfolder
                try:
                    selected_file.relative_to(log_dir_resolved)
                except ValueError:
                    QMessageBox.warning(
                        self,
                        "Load Location Warning",
                        f"Please load the log from within the Logs directory:\n{self.log_directory}"
                    )
                    self.label_status_value.setText("Load log failed: Invalid directory")
                    self.label_status_value.setStyleSheet("color: red;")
                    return  # Exit the method without loading

                # Read the content based on file extension
                if selected_file.suffix.lower() == '.html':
                    content = selected_file.read_text(encoding='utf-8')
                    # Optionally, parse or process HTML as needed
                else:
                    content = selected_file.read_text(encoding='utf-8')

                # Create and show the LogViewer window
                log_viewer = LogViewer(log_content=content, file_name=selected_file.name)
                log_viewer.show()

                # Connect the closed signal to remove the reference
                log_viewer.closed.connect(lambda: self.log_viewers.remove(log_viewer))

                # Keep a reference to prevent garbage collection
                self.log_viewers.append(log_viewer)

                # Update the status label
                self.label_status_value.setText(f"Log loaded from: {selected_file}")
                self.label_status_value.setStyleSheet("color: green;")

                # Optional: Save the last loaded log path
                self.settings.setValue("last_loaded_log", str(selected_file))

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

def log_crash_to_file(exc_type, exc_value, exc_traceback):
    """Logs the uncaught exception details to a file."""
    with open(CRASH_LOG_FILE, "a") as crash_log:
        crash_log.write("----- Crash Report -----\n")
        crash_log.write(f"Exception Type: {exc_type.__name__}\n")
        crash_log.write(f"Exception Message: {exc_value}\n")
        crash_log.write("Traceback:\n")
        traceback.print_tb(exc_traceback, file=crash_log)
        crash_log.write("\n")

def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """Handles uncaught exceptions and logs them."""
    log_crash_to_file(exc_type, exc_value, exc_traceback)
    
    # Notify the user about the crash
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Application Crashed")
    msg.setText("The application encountered an error and needs to close.")
    msg.setInformativeText(f"A crash report has been saved to:\n{CRASH_LOG_FILE}")
    msg.exec_()

    # Call the default handler
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

# Set the global exception hook
sys.excepthook = handle_uncaught_exception

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    