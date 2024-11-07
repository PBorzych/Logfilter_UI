from pathlib import Path
# from window_management import bring_window_to_front

def read_file_contents(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print("The file does not exist")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def find_new_txt_files(directory_path, processed_files):
    new_files = []
    directory = Path(directory_path)
    for file in directory.glob('*.txt'):
        if file.name not in processed_files:  
            print(f"Detected a new logfile: {file.name}\n")
            processed_files.add(file.name)
            new_files.append(file)
            #bring_window_to_front()
    return new_files