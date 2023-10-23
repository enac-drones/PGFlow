# file to store useful json utilities
import json, os


def load_from_json(file_path: str) -> dict:
    try:
        with open(file_path, "r") as f:
            file_contents = json.load(f)
            return file_contents
    except FileNotFoundError:
        # Create a new file if it doesn't exist
        with open(file_path, "x") as f:
            # Optionally, you can write some initial content to the file
            initial_data = {}
            json.dump(initial_data, f)
            return initial_data


def dump_to_json(file_path: str, data: dict) -> dict:
    # ensure the directory exists
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
        return None
