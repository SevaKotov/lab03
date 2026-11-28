
import json

import pytest

from catalog.errors import CorruptedFile, InvalidEntity, UndefinedFormatVersion
from catalog.models import ClassData, Classroom
from catalog.storage import load_catalog, save_catalog


def test_json_round_trip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    catalog = ClassData()
    room = Classroom("101", "Лекционная", 2024, 50)

    catalog.add(room)
    save_catalog(catalog)

    new_catalog = ClassData()
    load_catalog(new_catalog)

    assert list(new_catalog) == [room]


def test_corrupted_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with open("catalog.json", "w") as file:
        file.write("wrong json")

    with pytest.raises(CorruptedFile):
        load_catalog(ClassData())


def test_unknown_version(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    data = {"format_version": 100, "catalog": {}}

    with open("catalog.json", "w") as file:
        json.dump(data, file)

    with pytest.raises(UndefinedFormatVersion):
        load_catalog(ClassData())


def test_no_changes_after_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    catalog = ClassData()
    room = Classroom("101", "Лекционная", 2024, 50)
    catalog.add(room)

    data = {
        "format_version": 2,
        "catalog": {
            "1": {
                "id": "1",
                "name": 123,
                "category": "Лекционная",
                "year": 2024,
                "capacity": 50,
                "equipment": None,
                "floor": None
            }
        }
    }

    with open("catalog.json", "w") as file:
        json.dump(data, file)

    with pytest.raises(InvalidEntity):
        load_catalog(catalog)

    assert list(catalog) == [room]
