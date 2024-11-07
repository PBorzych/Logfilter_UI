from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMainWindow, QApplication
from ui import Ui_Logfilter

class MainWindow(QMainWindow, Ui_Logfilter):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # Initialize QSettings
        self.settings = QSettings('YourCompany', 'YourApp')

        # Load recent directories
        self.recent_directories = self.settings.value('recent_directories', [], type=list)

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


    def update_recent_directories_menu(self):
        self.menuRecent_Directories.clear()
        for directory in self.recent_directories:
            action = QtWidgets.QAction(directory, self)
            action.triggered.connect(lambda checked, dir=directory: self.set_directory(dir))
            self.menuRecent_Directories.addAction(action)

    def set_directory(self, directory):
        self.Directory_adress.setText(directory)
    
        self.comboBox.addItem(directory)
    
    def browse_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.Directory_adress.setText(directory)
            self.comboBox.addItem(directory)

        # Add to recent directories
        if directory in self.recent_directories:
            self.recent_directories.remove(directory)
        self.recent_directories.insert(0, directory)
        if len(self.recent_directories) > 10:  # Limit to 5 recent directories
            self.recent_directories = self.recent_directories[:10]

        # Save to settings
        self.settings.setValue('recent_directories', self.recent_directories)

        # Update the menu
        self.update_recent_directories_menu()
    
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
        pass

    def close_application(self):
        self.close()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    