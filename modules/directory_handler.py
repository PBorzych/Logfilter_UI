from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from functools import partial
from constants import LOG_SUBFOLDER

class DirectoryHandler:
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

    def update_recent_directories_menu(self):
        self.menuRecent_Directories.clear()
        for directory in self.recent_directories:
            action = QtWidgets.QAction(str(directory), self)
            action.triggered.connect(partial(self.set_directory, directory))
            self.menuRecent_Directories.addAction(action)

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