# file to store useful json utilities
import json


def load_from_json(file_path: str) -> dict:
    with open(file_path, "r") as f:
        file_contents = json.load(f)
        return file_contents


def dump_to_json(file_path: str, data: dict) -> dict:
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
        return None
