from dataclasses import asdict
from json import JSONDecodeError, dump, load
from pathlib import Path

from .errors import CorruptedFile, Invalid_Path, InvalidEntity, UndefinedFormatVersion
from .models import FORMAT_VERSION, VERSION_FIELDS, ClassData, Classroom


def json_parser(path: Path) -> dict:
    """Читает JSON-файл и возвращает данные каталога"""
    try:
        with path.open(encoding="utf-8") as file:
            try:
                rooms = load(file)
                if isinstance(rooms, dict):
                    return rooms
                else:
                    raise CorruptedFile(f"Invalid file: {path}")
            except JSONDecodeError as e:
                raise CorruptedFile(f"{path}: {e}") from e

    except FileNotFoundError as e:
        raise Invalid_Path(f"Invalid path: {path}") from e
    except PermissionError as e:
        raise Invalid_Path(f"No access to file: {path}") from e
    except OSError as e:
        raise Invalid_Path(f"Can't open {path}: {e}") from e


def save_by_json(path: Path, cat: ClassData) -> None:
    """Сохраняет данные в каталог полученные из json"""
    d = json_parser(path)
    try:
        version = d["format_version"]
        if type(version) is not int or version not in VERSION_FIELDS:
            raise UndefinedFormatVersion(f"Undefined format version: {version}")
        if not isinstance(d["catalog"], dict):
            raise InvalidEntity("Irrcoret structure of file")
    except KeyError as e:
        raise Invalid_Path(f"Invalid json: {path}") from e
    temp_catalog = ClassData()
    temp_catalog._data = {
        "format_version": cat._data["format_version"],
        "catalog": cat._data["catalog"].copy()
    }
    for key, value in d["catalog"].items():
        if not isinstance(value, dict):
            raise InvalidEntity("Incorrect room structure")
        room = Classroom.from_dict(value, version)
        temp_catalog.add(room)
    catalog = {}
    for key, room in temp_catalog._data["catalog"].items():
        room_dict = asdict(room)
        catalog[key] = {
            field: value
            for field, value in room_dict.items()
            if field in VERSION_FIELDS[FORMAT_VERSION]
        }
    with open("catalog.json", "w", encoding="utf-8") as file:
        dump({
            "format_version": FORMAT_VERSION,
            "catalog": catalog
        }, file, ensure_ascii=False, indent=4)

def save_catalog(cat: ClassData) -> None:
    """Сохраняет аудиторию введенную через add"""
    catalog = {}
    rooms = []
    for key, room in cat._data["catalog"].items():
        if room in rooms:
            continue
        rooms.append(room)
        room_dict = asdict(room)
        catalog[key] = {
            field: value
            for field, value in room_dict.items()
            if field in VERSION_FIELDS[FORMAT_VERSION]
        }
    with open("catalog.json", "w", encoding="utf-8") as file:
        dump({
            "format_version": FORMAT_VERSION,
            "catalog": catalog
        }, file, ensure_ascii=False, indent=4)

def load_catalog(cat: ClassData) -> ClassData:
    """Загружает catalog.json в переменную cat"""
    path = Path("catalog.json")
    d = json_parser(path)
    try:
        version = d["format_version"]
        data = d["catalog"]
        if not isinstance(data, dict):
            raise InvalidEntity("Incorrect catalog structure")
    except KeyError as e:
        raise CorruptedFile(f"Missing field in JSON: {e}") from e
    if type(version) is not int or version not in VERSION_FIELDS:
        raise UndefinedFormatVersion(f"Undefined format version: {version}")
    temp_catalog = ClassData()
    for key, value in data.items():
        if not isinstance(value, dict):
            raise InvalidEntity("Incorrect room structure")
        room = Classroom.from_dict(value, version)
        if key != room.id:
            raise InvalidEntity(f"ID mismatch: {key} != {room.id}")
        temp_catalog.add(room)
    cat._data = temp_catalog._data
    return cat
