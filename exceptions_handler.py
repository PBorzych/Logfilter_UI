
import traceback
import sys

from PyQt5.QtWidgets import QMessageBox
from constants import CRASH_LOG_FILE

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