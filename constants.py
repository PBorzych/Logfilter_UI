from pathlib import Path

version = "1.0.2"

# Crash log directory and file
CRASH_LOG_DIRECTORY = Path("CrashLogs")
CRASH_LOG_FILE = CRASH_LOG_DIRECTORY / "crash_report-log"

# Ensure the crash log directory exists
CRASH_LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

# Reference list file path
KEYWORD_LIST_FILE = 'reference_list.json'