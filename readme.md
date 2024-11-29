Logfilter 1.0.0

TODO:
    o CLR Screen when changing vehicle and clr button. 
    o Organize the functions in to diff. files 
    o Add/Remove Keywords in the program
    o Ignore the word error in when it is "EGR ERROR"
    o Pending/Confirmed in relation to IGNCNTR
    o Pending/Confirmed to check to only if same DTC and not the whole filename
    o selection for mismatch in pending/confirmed
    o Refactor
    o Clean up commented code
    
    / Fix loading problem!
    / Browse function and recent function           
    / Save log file function 
    / Status info, "ready for live monitoring", "finished reading whole path" etc. 
    / Folder check
    / Live monitoring
    / confirm and confirmed as keywords
    / logo not shown after compilation
    / Unify path handling with pathlib 22/11 2024

Compile with this:
pyinstaller --onefile --windowed --add-data "AurobayLogo.png;." main.py
