Logfilter 1.0.2

TODO:
    o/ CLR Screen when changing vehicle and /clr button. 
    o Organize the functions in to diff. files 
    o Show MIL on/off in folder check
    o Pending/Confirmed in relation to IGNCNTR
    o Pending/Confirmed to check to only if same DTC and not the whole filename
    o selection for mismatch in pending/confirmed
    o selection of specific node
    o export folder check report to excel file
    o Refactor
    o Clean up commented code
    
    / Add/Remove Keywords in the json list
    / Ignore the word error in when it is "EGR ERROR"
    / Fix loading problem!
    / Browse function and recent function           
    / Save log file function 
    / Status info, "ready for live monitoring", "finished reading whole path" etc. 
    / Folder check
    / Live monitoring
    / confirm and confirmed as keywords
    / logo not shown after compilation
    / Unify path handling with pathlib 22/11 2024

Compile with this command prompt:
pyinstaller main.spec


Suggestion for structure:

├── modules/
│   ├── __init__.py
│   ├── check_errors_in_folder.py
│   ├── directory_handler.py
│   ├── ecu_processing.py
│   ├── file_processing.py
│   ├── keywords_editor.py
│   ├── log_handler.py
│   ├── ui_handler.py
│   ├── monitoring_handler.py
│   ├── keywords_editor.py
│   └── real_time_monitoring.py
├── constants.py
├── exceptions_handler.py
├── main.py
├── threads.py
├── ui.py
├── readme.md
└── reference_list.json

modules/directory_handler.py: 
from pathlib import Path
from PyQt5.QtCore import QSettings

class DirectoryHandler:
    def load_recent_directories(self, settings):
        # Directory-related methods...
        pass

    def save_recent_directories(self, settings, directories):
        pass

    def update_recent_directories_menu(self, menu, directories):
        pass

    def set_directory(self, directory):
        pass

    def ensure_log_directory(self, log_directory):
        pass


modules/log_handler.py:
class LogHandler:
    def save_log(self, log_directory, content):
        # Log saving/loading methods...
        pass

    def load_log(self, log_directory):
        pass

    def append_log(self, text):
        pass

    def set_full_log(self, html_text):
        pass

modules/ui_handler.py:
class UIHandler:
    def update_window_title(self, window, version, directory):
        # UI-related methods...
        pass

    def update_combo_box(self, combo_box, directories):
        pass

    def update_status(self, label, text, color):
        pass

modules/monitoring_handler.py
class MonitoringHandler:
    def start_monitoring(self, mode, directory):
        # Monitoring-related methods...
        pass

    def stop_monitoring(self):
        pass

    def monitoring_finished(self):
        pass