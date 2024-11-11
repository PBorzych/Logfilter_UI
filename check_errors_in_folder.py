from pathlib import Path
from ecu_processing import load_ecu_reference, count_ecus_in_modes, load_keywords_from_json, find_fail_keywords
import winsound

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

        # Remove the word "confirmed" or "pending" from the -lowercase- file_name
        lower_file_name = file_name.lower()
        pair_name = lower_file_name.replace("_confirmed", "").replace("_pending", "")

        if pair_name in file_pairs:
            file_pairs[pair_name].append(file_name)
        else:
            file_pairs[pair_name] = [file_name]

    # Identify missing pairs
    for pair_name, files in file_pairs.items():
        if len(files) == 1:
            missing_pairs.append(files[0])

    return file_pairs, duplicates, missing_pairs

def check_errors_in_folder(folder_path, json_file_path):
    """
    Scans through all files in the given folder, processes each file, and checks for errors.
    Summarizes which files have errors based on specified keywords. Additionally, checks for duplicate files
    and ensures there is a corresponding "pending" logfile for every "confirmed" logfile and vice versa.
    """
    # Load ECU reference data and error keywords
    keywords = load_keywords_from_json(json_file_path)
    flattened_reference = load_ecu_reference(json_file_path)

    # Store errors found for final summary
    error_summary = {}

    # Get file pairs, duplicates, and missing pairs
    directory = Path(folder_path)
    file_pairs, duplicates, missing_pairs = check_file_pairs_and_duplicates(directory)

    # Handle duplicates
    if duplicates:
        print(f"\nDuplicate files found:")
        for duplicate in duplicates:
            print(f" - {duplicate}")

    # Handle missing pairs
    if missing_pairs:
        print(f"\n\033[1;31;40m Files with missing pairs: \033[0m")
        for missing_pair in missing_pairs:
            print(f" - {missing_pair}")

    # Iterate over all text files in the folder
    for file_path in directory.glob('*.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        # Process the file content to find ECUs, faults, and generate any warnings
        ecu_counts, detailed_faults, warning = count_ecus_in_modes(file_content, flattened_reference)

        # Check for specific failures or keywords
        fail_details = find_fail_keywords(file_content, keywords)

        # Aggregate error information
        if warning or fail_details:
            error_summary[file_path.name] = {"warning": warning, "fail_details": fail_details}

    # Print summary of errors across all files
    if error_summary:
        print("\n\033[1;32;40m Summary of Errors:   \033[0m")
        for file_name, errors in error_summary.items():
            print(f"\n\033[1;37;40m{file_name}:  \033[0m")
            if errors["warning"]:
                print(f" {errors['warning']}")
            if errors["fail_details"]:
                for detail in errors["fail_details"]:
                    print(f"  - {detail}")
    else:
        print("\nNo errors found across all files.")