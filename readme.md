Logfilter 1.0.2

TODO:
    o/ CLR Screen when changing vehicle and /clr button. 
    o Organize the functions in to diff. files 
    o Show MIL on/off in folder check
    o Pending/Confirmed in relation to IGNCNTR
    o Pending/Confirmed to check to only if same DTC and not the whole filename
    o selection for mismatch in pending/confirmed
    o selection of specific node
        - add some more options maybe in a setup menu? 
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

03-01-2025
Attempted to divide the PyQT functions (which include data processing, file handling, and log filtering functions) into separate classes and organize them across different files to improve modularity and maintainability. However, this approach introduced unnecessary complexity for the current scope of the project. As a result, decided to keep all functions in the main.py file for simplicity and ease of understanding. This structure can be revisited and refactored in the future if the project grows in complexity. 