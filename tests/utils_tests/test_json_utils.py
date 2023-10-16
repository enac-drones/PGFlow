import os
from src.utils import json_utils
import json


def test_load_existing_json(tmpdir):
    data = {"name": "John", "age": 30}
    file_path = tmpdir.join("data.json")
    with open(file_path, "w") as f:
        json.dump(data, f)

    loaded_data = json_utils.load_from_json(file_path.strpath)

    assert loaded_data == data


def test_load_nonexistent_json(tmpdir):
    file_path = tmpdir.join("nonexistent.json")
    loaded_data = json_utils.load_from_json(file_path.strpath)

    assert loaded_data == {}
    with open(file_path, "r") as f:
        contents = json.load(f)
    assert contents == {}


def test_dump_to_json(tmpdir):
    data = {"name": "Alice", "age": 25}
    file_path = tmpdir.join("output.json")
    json_utils.dump_to_json(file_path.strpath, data)

    with open(file_path, "r") as f:
        written_data = json.load(f)

    assert written_data == data


def test_dump_to_json_directory_creation(tmpdir):
    data = {"name": "Bob", "age": 40}
    directory_path = tmpdir.join("some", "nested", "directory")
    file_path = directory_path.join("output.json")
    json_utils.dump_to_json(file_path.strpath, data)

    assert os.path.exists(directory_path)
    with open(file_path, "r") as f:
        written_data = json.load(f)

    assert written_data == data
