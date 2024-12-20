Logfilter 1.0.2

TODO:
    o/ CLR Screen when changing vehicle and /clr button. 
    o Organize the functions in to diff. files 
    o Add/Remove Keywords in the json list
    o Show MIL on/off in folder check
    o Pending/Confirmed in relation to IGNCNTR
    o Pending/Confirmed to check to only if same DTC and not the whole filename
    o selection for mismatch in pending/confirmed
    o selection of specific node
    o export folder check report to excel file
    o Refactor
    o Clean up commented code
    
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
