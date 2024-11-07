# Version 1.0

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from ui import Ui_Logfilter
from functools import partial
import os

version = "1.0.0"

class MainWindow(QMainWindow, Ui_Logfilter):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

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
        self.pushButton.clicked.connect(self.browse_directory)
        self.pushButton_2.clicked.connect(self.start_monitoring)
        self.pushButton_3.clicked.connect(self.stop_monitoring)
        self.actionOpen_Directory.triggered.connect(self.browse_directory)
        self.actionExit.triggered.connect(self.close_application)
        self.actionSave_Log.triggered.connect(self.save_log)
        self.actionLocal_Check.triggered.connect(self.local_check)
        self.actionSharepoint_Check_N_A.triggered.connect(self.sharepoint_check)
        self.actionabout.triggered.connect(self.about)

        # Connect the comboBox currentIndexChanged signal to the method
        self.comboBox.currentIndexChanged.connect(self.combo_box_selection_changed)

    def combo_box_selection_changed(self, index):
        if index >= 0:
            directory = self.comboBox.itemText(index)
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
        self.comboBox.blockSignals(True)
        self.comboBox.clear()
        for directory in self.recent_directories:
            self.comboBox.addItem(directory)
        # Set the current index to match current_directory
        index = self.recent_directories.index(self.current_directory)
        self.comboBox.setCurrentIndex(index)
        # Unblock signals after updating
        self.comboBox.blockSignals(False)

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
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", self.current_directory)
        if directory:
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
    
    def start_monitoring(self):
        pass

    def stop_monitoring(self):
        pass

    def save_log(self):
        pass

    def local_check(self):
        pass

    def sharepoint_check(self):
        pass

    def about(self):
        QMessageBox.about(
        self,
        "About Logfilter",
        f"<b>Logfilter</b><br>Version {version}<br><br>"
        "This application is designed to filter logs from Silver Scan-Tool and perform live monitoring."
        )

    def close_application(self):
        self.close()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    