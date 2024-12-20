import json
import re

def load_keywords_from_json(json_file_path):
    try:
        with open(json_file_path) as json_file:
            data = json.load(json_file)
            if 'keywords' not in data:
                raise KeyError("The key 'keywords' is missing from the JSON data.")
            
            keywords = data['keywords']
            ignore_keywords = data.get('ignore_keywords', [])
            return keywords, ignore_keywords
        
    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
        return [], []
    except json.JSONDecodeError:
        print(f"Error: The file '{json_file_path}' is not a valid JSON file.")
        return [], []
    except KeyError as e:
        print(f"Error: {e}")
        return [], []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return [], []

def load_ecu_reference(json_file_path):
    try:
        with open(json_file_path) as json_file:
            data = json.load(json_file)
            flattened_reference = {
            ecu.split()[1] for key, sublist in data.items()
            if key != 'keywords'
            for ecu in sublist
        }
        return flattened_reference
    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{json_file_path}' is not a valid JSON file.")
    except KeyError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def count_ecus_in_modes(content, flattened_reference):
    """
    Counts ECUs in different modes and finds fault codes.
    
    Args:
    - content (str): The content of the file being processed.
    - flattened_reference (dict): The reference data for ECUs.
    
    Returns:
    - ecu_counts (dict): The count of ECUs in different modes.
    - mode_faults (dict): The detailed fault codes for specified modes.
    - warning (str): A warning if ECU counts are not the same in all modes.
    """
    # Initializing dictionaries to keep track of ECU counts and specific mode faults.
    sections = content.split("Scan-Tool Mode")
    ecu_counts = {}
    mode_faults = {"1": [], 
                   "2": [], 
                   "3": [],
                   "6": [], 
                   "7": [],
                   "9": [], 
                   "A": []}  # Focusing on these modes
    

    # Processing each section corresponding to a different mode in the scan-tool data.
    for section in sections[1:]:
        lines = section.split("\n")
        mode_line = lines[0].split("-")
        mode_name = mode_line[0].strip()
        ecu_list = [line.strip() for line in lines[2:] if line.strip() != ""]
        
        # Only process specified modes to avoid KeyError
        if mode_name in mode_faults:
            current_ecu_name = ""
            for line in ecu_list:
                # Check if the line is an ECU identifier
                if len(line.split()) > 1 and line.split()[1] in flattened_reference:
                    current_ecu_name = line
                    mode_faults[mode_name].append(current_ecu_name)
                else:
                    if ("fault code entries" in line or line.startswith("P") or line.startswith("U") or line.startswith("C") or line.startswith("B")) and not line.startswith("PID"):
                        if not re.search(r"\d+\s+fault code entries", line):
                            mode_faults[mode_name].append(line)

        # Filtering ECU list to count only those that are in the flattened reference.
        filtered_ecu_list = [ecu for ecu in ecu_list if len(ecu.split()) > 1 and ecu.split()[1] in flattened_reference]
        ecu_counts[mode_name] = len(set(filtered_ecu_list))

    # Comparing ECU counts across modes and generating a warning if necessary
    modes_to_check = ["1", "2", "3", "6", "7", "9", "A"]
    reference_count = ecu_counts.get(modes_to_check[0], 0)
    all_counts_match = True

    for mode in modes_to_check:
        if ecu_counts.get(mode, 0) != reference_count:
            all_counts_match = False
            break

    warning = ""
    if not all_counts_match:
        warning = "Warning: ECU counts are not the same in all modes."
    
    return ecu_counts, mode_faults, warning

# def determine_version(ecu_counts):
#     version_reference = {
#         "US MP/HP version": 8,
#         "CH MP/HP version": 2,
#         "CH/US PHEV version": 8
#     }

#     mode_ecu_count = next(iter(ecu_counts.values()))

#     for version, expected_count in version_reference.items():
#         if mode_ecu_count == expected_count:
#             return version
#     return "Unknown version"

def find_fail_keywords(file_content, keywords, ignore_keywords):
    sections = file_content.split("Scan-Tool Mode")
    fail_details = []

    # Iterate through sections with enumeration to keep track of section index
    for index, section in enumerate(sections):
        lines = section.split('\n')
        
        for line in lines:
            line_lower = line.lower()

            should_ignore = False
            for ignore_keyword in ignore_keywords:
                if ignore_keyword.lower() in line_lower:
                    should_ignore = True
                    break
            if not should_ignore:
                for keyword in keywords:
                    if keyword.lower() in line_lower:
                        # Append a tuple containing the section index and the line
                        fail_details.append((f"Mode {index}", line.strip()))
                        break

    return fail_details

def find_recent_fueled_ignition_data(log_content):
    # Identifying the start of the relevant section for "INFOTYPE 08"
    start_phase = "INFOTYPE 08\tIn-use Performance Tracking for Spark Ignition Engines"
    start_index = log_content.find(start_phase)
    
    if start_index == -1:
        return None  # Indicate that the section was not found

    # Extracting the content starting from the identified index
    relevant_content = log_content[start_index:]

    # Find the line containing "Ignition Cycle Counter"
    lines = relevant_content.split('\n')
    for line in lines:
        if 'Ignition Cycle Counter' in line:
            return line.strip()  # Return the entire line

    return None

