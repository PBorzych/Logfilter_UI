from pathlib import Path
from modules.ecu_processing import load_ecu_reference, count_ecus_in_modes, load_keywords_from_json, find_fail_keywords
import winsound
import re

def format_detail(detail):
    if isinstance(detail, tuple):
        return ' - '.join(str(item) for item in detail)
    else:
        return str(detail)

def check_file_pairs_and_duplicates(directory):
    file_pairs = {}
    file_names = set()
    duplicates = []
    missing_pairs = []

    for file_path in directory.glob('*.txt'):
        file_name = file_path.stem

        # Check for duplicates
        if file_name in file_names:
            duplicates.append(file_name)
        file_names.add(file_name)

        # Remove any substring containing "confirm" (which will catch both confirm and confirmed)
        # or "pending" (case-insensitive)        
        lower_file_name = file_name.lower()
        pair_name = re.sub(r'_?(pending|confirm)[a-z]*', '', lower_file_name)

        # Remove any trailing underscores or special characters left after replacement
        pair_name = re.sub(r'[_&]+$', '', pair_name)

        if pair_name in file_pairs:
            file_pairs[pair_name].append(file_name)
        else:
            file_pairs[pair_name] = [file_name]

    # Identify missing pairs
    for pair_name, files in file_pairs.items():
        if len(files) == 1:
            missing_pairs.append(files[0])

    # Return only three values
    return file_pairs, duplicates, missing_pairs

def check_errors_in_folder(folder_path, json_file_path, is_running=lambda: True):
    """
    Scans through all files in the given folder, processes each file, and checks for errors.
    Summarizes which files have errors based on specified keywords. Additionally, checks for duplicate files
    and ensures there is a corresponding "pending" logfile for every "confirmed" logfile and vice versa.
    """
    # Load ECU reference data and error keywords
    keywords, ignore_keywords = load_keywords_from_json(json_file_path)
    flattened_reference = load_ecu_reference(json_file_path)

    # Initialize the output string with CSS styles
    output = """
    <style>
        body { font-family: Arial, sans-serif; }
        h2 { color: #2E8B57; } /* Green headings */
        h3 { color: #4682B4; } /* Blue subheadings */
        ul { margin-left: 20px; }
        li { margin-bottom: 5px; }
        .error { color: red; }
        .warning { color: red; }
    </style>
    """

    # Get file pairs, duplicates, and missing pairs
    directory = Path(folder_path)
    file_pairs, duplicates, missing_pairs = check_file_pairs_and_duplicates(directory)

    # Handle duplicates
    if duplicates:
        output += "<h2>Duplicate Files Found:</h2><ul>"
        for duplicate in duplicates:
            output += f"<li>{duplicate}</li>"
        output += "</ul>"

    # Handle missing pairs
    if missing_pairs:
        output += "<h2 class='error'>Files with Missing Pairs:</h2><ul>"
        for missing_pair in missing_pairs:
            output += f"<li>{missing_pair}</li>"
        output += "</ul>"

    # Store errors found for final summary
    error_summary = {}

    # Iterate over all text files in the folder
    for file_path in directory.glob('*.txt'):
        if not is_running():
            return output + "<p>Process was stopped by the user.</p>"
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        # Process the file content to find ECUs, faults, and generate any warnings
        ecu_counts, detailed_faults, warning = count_ecus_in_modes(file_content, flattened_reference)

        # Check for specific failures or keywords
        fail_details = find_fail_keywords(file_content, keywords, ignore_keywords)

        # Aggregate error information
        if warning or fail_details:
            error_summary[file_path.name] = {"warning": warning, "fail_details": fail_details}

    # Build summary of errors across all files
    if error_summary:
        output += "<h2>Summary of Errors:</h2>"
        for file_name, errors in error_summary.items():
            output += f"<h3>{file_name}:</h3><ul>"
            if errors["warning"]:
                formatted_warning = format_detail(errors["warning"])
                output += f"<li class='warning'>{formatted_warning}</li>"
            if errors["fail_details"]:
                for detail in errors["fail_details"]:
                    formatted_detail = format_detail(detail)
                    output += f"<li>{formatted_detail}</li>"
            output += "</ul>"
    else:
        output += "<p>No errors found across all files.</p>"

    return output