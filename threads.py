import time

from PyQt5.QtCore import QThread, pyqtSignal
from pathlib import Path
from modules.file_processing import find_new_txt_files
from modules.real_time_monitoring import process_file
from modules.check_errors_in_folder import check_errors_in_folder

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