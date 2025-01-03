from PyQt5.QtCore import  pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
    QMainWindow)

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