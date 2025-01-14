import time
import os
import winsound

from pathlib import Path
from modules.file_processing import read_file_contents, find_new_txt_files
from modules.ecu_processing import load_ecu_reference, count_ecus_in_modes, load_keywords_from_json, find_fail_keywords, find_recent_fueled_ignition_data


json_file_path = os.path.abspath('reference_list.json')
#csv_file_path = r'fail_keywords.csv'
keywords, ignore_keywords = load_keywords_from_json(json_file_path)
#flattened_reference = load_ecu_reference(json_file_path)

def beep_sound(duration=1000, frequency=440):
    """Plays a beep sound with the given duration and frequency."""
    winsound.Beep(duration, frequency)

def handle_failures(file_content):
    """Handles and reports failures detected in the log content."""
    fail_details = find_fail_keywords(file_content, keywords, ignore_keywords)
    if fail_details:
        return f"<span style='color:red;'>Fail details found: {fail_details}</span><br>"
    return ""

def display_faults(detailed_faults):
    """Returns detailed fault information for specific modes as a string."""
    output = ""
    for mode in ["3", "7"]:
        if mode in detailed_faults and detailed_faults[mode]:
            output += f"<b>Faults and Data for Mode {mode}</b><br>"
            for fault in detailed_faults[mode]:
                fault_parts = fault.split(" ", 1)
                fault_code = fault_parts[0]
                fault_description = fault_parts[1] if len(fault_parts) > 1 else ""
                output += f"{fault_code} {fault_description}<br>"
            output += "<br>"
        elif mode in detailed_faults:
            output += f"No Faults Detected in Mode {mode}<br><br>"
    return output
    

def display_ecu_counts(ecu_counts):
    """Returns ECU counts per mode as a string."""
    output = ""
    for mode in ["1", "2", "3", "6", "7", "9", "A"]:
        count = ecu_counts.get(mode, "No data available")
        output += f"Nodes in mode {mode}: {count}<br>"
    return output

# def check_and_print_pending_confirmed_status(detailed_faults):
#     """Checks for errors and prints 'Pending' if an error is only present in mode 7,
#     or 'Confirmed' if the same error is present in both mode 3 and 7."""
    
#     mode_3_codes = set()
#     mode_7_codes = set()

#     # Extract error codes from mode 3
#     if "3" in detailed_faults:
#         for fault in detailed_faults["3"]:
#             fault_parts = fault.split(" ", 1)
#             mode_3_codes.add(fault_parts[0])
    
#     # Extract error codes from mode 7
#     if "7" in detailed_faults:
#         for fault in detailed_faults["7"]:
#             fault_parts = fault.split(" ", 1)
#             mode_7_codes.add(fault_parts[0])
    
#     # Check for pending status
#     for code in mode_7_codes:
#         if code not in mode_3_codes:
#             print("Pending")
#             return  

#     # Check for confirmed status
#     for code in mode_7_codes:
#         if code in mode_3_codes:
#             print("Confirmed")
#             return  
        
def compare_status_with_logfile(logfile_name, detailed_faults, mode_3_cycles, mode_7_cycles):
    """Compares the status derived from error codes with the status in the logfile name and returns the result as a string."""
    output = ""
    # Extract status from the logfile name
    parts = logfile_name.split('_')
    if len(parts) < 3:
        output += "Logfile name format is incorrect.<br>"
        return output

    # The status in the logfile name should be the third part
    logfile_status = parts[2].lower()

    # Determine the status based on detailed_faults
    mode_3_codes = set()
    mode_7_codes = set()

    # Extract error codes from mode 3
    if "3" in detailed_faults:
        for fault in detailed_faults["3"]:
            fault_parts = fault.split(" ", 1)
            mode_3_codes.add(fault_parts[0])

    # Extract error codes from mode 7
    if "7" in detailed_faults:
        for fault in detailed_faults["7"]:
            fault_parts = fault.split(" ", 1)
            mode_7_codes.add(fault_parts[0])

    # Check for pending status
    determined_status = "confirmed"
    for code in mode_7_codes:
        if code not in mode_3_codes:
            determined_status = "pending"
            break
    
    # Compare statuses
    if logfile_status == determined_status:
        output += f"<br>Status matches: {logfile_status.capitalize()}<br>"
    else:
        output += f"<span style='color:red;'>Status mismatch! Logfile: {logfile_status.capitalize()}, Determined: {determined_status.capitalize()}</span><br>"

    # # Compare ignition cycle counters
    # if mode_3_cycles is not None and mode_7_cycles is not None:
    #     expected_mode_7_cycles = mode_3_cycles + 1
    #     if mode_7_cycles == expected_mode_7_cycles:
    #         output += f"Ignition cycle counter check passed: Mode 3 ({mode_3_cycles}) + 1 = Mode 7 ({mode_7_cycles})<br>"
    #     else:
    #         output += f"<span style='color:red;'>Ignition cycle counter mismatch! Mode 3 ({mode_3_cycles}) + 1 ≠ Mode 7 ({mode_7_cycles})</span><br>"
    # else:
    #     output += "<span style='color:red;'>Unable to compare ignition cycle counters - missing data</span><br>"

    return output
        
def process_file(file, json_file_path):
    """Processes a single log file for ECU data, faults, and warnings, and returns the output as a string."""
    outputs = []
    file_content = read_file_contents(file)
    if file_content is None:
        return ""
    
    # Load reference data for ECU identifiers from the JSON file.
    flattened_reference = load_ecu_reference(json_file_path)
    ecu_counts, detailed_faults, warning = count_ecus_in_modes(file_content, flattened_reference)

   # Create variables to store the ignition cycle counters for modes 3 and 7
    mode_3_cycles = None
    mode_7_cycles = None
 
    # Compare ignition cycle counters
    mode_3_cycles = find_recent_fueled_ignition_data(file_content)
    mode_7_cycles = find_recent_fueled_ignition_data(file_content)
    if mode_3_cycles is not None and mode_7_cycles is not None:
        if mode_3_cycles == mode_7_cycles:
            outputs.append(f"<span style='color:red;'>Ignition cycle counter error! Mode 3 ({mode_3_cycles}) equals Mode 7 ({mode_7_cycles})</span><br>")
        elif mode_7_cycles == mode_3_cycles + 1:
                outputs.append(f"Ignition cycle counter check passed: Mode 3 ({mode_3_cycles}) + 1 = Mode 7 ({mode_7_cycles})<br>")
        else:
            outputs.append(f"<span style='color:red;'>Ignition cycle counter mismatch! Mode 3 ({mode_3_cycles}) + 1 != Mode 7 ({mode_7_cycles})</span><br>")
    
    # Reporting the processing of the new file
    outputs.append(f"<b>Processing new file:</b> {file.name}<br>")
    
    # Identifying and reporting on failures or lack of response in the log data.
    fail_output = handle_failures(file_content)
    if fail_output:
        outputs.append(fail_output)
    
    # Displaying detailed fault information for specific modes.
    fault_output = display_faults(detailed_faults)
    if fault_output:
        outputs.append(fault_output)
    
    # Displaying ECU counts per mode
    ecu_output = display_ecu_counts(ecu_counts)
    if ecu_output:
        outputs.append(ecu_output)
    
    # Comparing status with logfile
    status_output = compare_status_with_logfile(file.name, detailed_faults)
    if status_output:
        outputs.append(status_output)
    
    # Displaying warning messages
    if warning:
        outputs.append(f"<span style='color:red;'>{warning}</span><br>")
    
    # Retrieving and displaying data for fueled ignition cycles.
    fueled_ignition_cycle_counter = find_recent_fueled_ignition_data(file_content)
    if fueled_ignition_cycle_counter:
        outputs.append(f"<br>Ignition Cycle Counter: {fueled_ignition_cycle_counter}<br>")
    
    return ''.join(outputs)



# Continuously checking for new txt files
def continuous_file_check(logfile_directory, json_file_path):
    """
    Continuously monitors a directory for new txt files, processes them,
    and checks for errors or specific keywords like 'fail' or 'No response'.
    
    Args:
    - logfile_directory (str): Directory path where log files are located.
    - json_file_path (str): Path to the JSON file with ECU reference data.
    """
    processed_files = set()

    # Populate initial set of processed files to avoid re-processing
    directory = Path(logfile_directory)
    for file in directory.glob('*.txt'):
        processed_files.add(file.name)

    # Continuous monitoring loop
    while True:
        new_files = find_new_txt_files(logfile_directory, processed_files)
        for file in new_files:
            process_file(file, json_file_path)
            processed_files.add(file.name)

        # Configurable delay to avoid excessive frequency of directory checks
        time.sleep(3)