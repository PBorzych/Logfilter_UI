from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication
from ui import Ui_Logfilter

#import

class MainWindow(QMainWindow, Ui_Logfilter):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        #Connect buttons to methods
        self.pushButton.clicked.connect(self.browse_directory)
        #self.pushButton_2.clicked.connect(self.start_monitoring)
        #self.pushButton_3.clicked.connect(self.stop_monitoring)
        self.actionOpen_Directory.triggered.connect(self.browse_directory)
        self.actionExit.triggered.connect(self.close_application)
        #self.actionSave_Log.triggered.connect(self.save_log)
        #self.actionRecent_Directories.triggered.connect(self.open_recent_directories)
        #self.actionLocal_Check.triggered.connect(self.local_check)
        #self.actionSharepoint_Check_N_A.triggered.connect(self.sharepoint_check)
        #self.actionabout.triggered.connect(self.about)


    def browse_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.Directory_adress.setText(directory)
            self.comboBox.addItem(directory)
    
    #def start_monitoring(self):

    #def stop_monitoring(self):

    #def save_log(self):

    #def open_recent_directories(self):

    #def local_check(self):

    #def sharepoint_check(self):

    #def about(self):

    def close_application(self):
        self.close()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    