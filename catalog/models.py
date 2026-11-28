
from dataclasses import dataclass
from uuid import uuid4

from .errors import *

FORMAT_VERSION = 3
VERSION_FIELDS = {
    1: {"name", "category", "year", "capacity", "equipment", "id"},
    2: {"name", "category", "year", "capacity", "equipment", "id", "floor"},
    3: {"name", "category", "year", "capacity", "equipment", "id", "floor", "building"}
}


@dataclass(frozen=True)
class Classroom:
    name: str
    category: str
    year: int
    capacity: int
    equipment: str | None = None
    id: str = ""
    floor: str | None = None
    building: str | None = None

    def __post_init__(self):
        if not isinstance(self.name, str) or not isinstance(self.category, str):
            raise InvalidEntity("Incorrect name or category")

        if type(self.year) is not int or type(self.capacity) is not int:
            raise InvalidEntity("Year and capacity must be integers")

        if self.id == "":
            object.__setattr__(self, "id", str(uuid4()))

        if not isinstance(self.id, str):
            raise InvalidEntity("ID must be a string")

        if self.capacity < 0:
            raise InvalidEntity("Capacity of element below zero")

        if self.year < 0:
            raise InvalidEntity("Year is below zero")

        if self.equipment is not None and not isinstance(self.equipment, str):
            raise InvalidEntity("Incorrect equipment")

        if self.floor is not None and not isinstance(self.floor, str):
            raise InvalidEntity("Incorrect floor")

        if self.building is not None and not isinstance(self.building, str):
            raise InvalidEntity("Incorrect building")

    @classmethod
    def from_dict(cls, d: dict, version: int, preserve_id: bool = True):
        """Переводит словарь в объект classroom"""
        if type(version) is not int or version not in VERSION_FIELDS:
            raise UndefinedFormatVersion(f"Undefined format version {version}")

        if not isinstance(d, dict):
            raise InvalidEntity("Incorrect room structure")

        required_fields = {"name", "category", "year", "capacity", "equipment"}

        if preserve_id:
            required_fields.add("id")

        missing = required_fields - d.keys()

        if missing:
            raise InvalidEntity(f"Missing required fields: {missing}")

        if (
                not isinstance(d["name"], str)
                or not isinstance(d["category"], str)
                or type(d["year"]) is not int
                or type(d["capacity"]) is not int
                or (d["equipment"] is not None and not isinstance(d["equipment"], str))
        ):
            raise InvalidEntity("Incorrect fields")

        if preserve_id and not isinstance(d["id"], str):
            raise InvalidEntity("Incorrect ID")

        match version:
            case 1:
                return cls(
                    id=d["id"] if preserve_id else "",
                    name=d["name"],
                    category=d["category"],
                    year=d["year"],
                    capacity=d["capacity"],
                    equipment=d["equipment"]
                )

            case 2:
                if "floor" not in d:
                    raise InvalidEntity("Not enough fields. No floor")

                if d["floor"] is not None and not isinstance(d["floor"], str):
                    raise InvalidEntity("Incorrect floor")

                return cls(
                    id=d["id"] if preserve_id else "",
                    name=d["name"],
                    category=d["category"],
                    year=d["year"],
                    capacity=d["capacity"],
                    equipment=d["equipment"],
                    floor=d["floor"]
                )

            case 3:
                if "floor" not in d or "building" not in d:
                    raise InvalidEntity("Not enough fields. No floor or building")

                if (
                        (d["floor"] is not None and not isinstance(d["floor"], str))
                        or (d["building"] is not None and not isinstance(d["building"], str))
                ):
                    raise InvalidEntity("Incorrect floor or building")

                return cls(
                    id=d["id"] if preserve_id else "",
                    name=d["name"],
                    category=d["category"],
                    year=d["year"],
                    capacity=d["capacity"],
                    equipment=d["equipment"],
                    floor=d["floor"],
                    building=d["building"]
                )


class ClassData:
    def __init__(self):
        self._data = {"format_version": FORMAT_VERSION, "catalog": {}}
        self._category_index = {}

    def add(self, item: Classroom) -> None:
        """Добавляет объект в каталог"""
        if item in self:
            return
        while item.id in self._data["catalog"]:
            item = Classroom(
                name=item.name,
                category=item.category,
                year=item.year,
                capacity=item.capacity,
                equipment=item.equipment,
                floor=item.floor,
                building=item.building
            )
            #Либо просто raise DoubleID(...)
        self._data["catalog"][item.id] = item
        if item.category.lower() in self._category_index:
            self._category_index[item.category.lower()].append(item.id)
        else:
            self._category_index[item.category.lower()] = [item.id]

    def get(self, item_id: str) -> Classroom:
        """Выводит объект по его id"""
        try:
            return self._data["catalog"][item_id]
        except KeyError as e:
            raise UndefinedObject(f"There is no item with id {item_id} in catalog") from e

    def remove(self, item_id: str) -> None:
        """Удаляет объект по его id"""
        try:
            room = self._data["catalog"].pop(item_id)
        except KeyError as e:
            raise UndefinedObject(f"There is no element with id {item_id}") from e

        category = room.category.lower()

        if category in self._category_index:
            self._category_index[category].remove(item_id)

            if not self._category_index[category]:
                del self._category_index[category]

    def find_by_category(self, category: str) -> list:
        """Ищет объекты с заданной категорией"""
        ids = self._category_index.get(category.lower(), [])
        return [self._data["catalog"][item_id] for item_id in ids]

    def find_by_name(self, query: str) -> list:
        """Ищет объект по имени"""
        result = []
        for c in self._data["catalog"].values():
            if query.lower() in c.name.lower():
                result.append(c)

        return result

    def __len__(self) -> int:
        """Возвращает длинну каталога"""
        return len(self._data["catalog"])

    def __iter__(self):
        """Возвращает аудитории в порядке их добавления в каталог"""
        return iter(self._data["catalog"].values())

    def __contains__(self, item) -> bool:
        """Проверяет наличие аудитории или ее ID в каталоге"""
        if isinstance(item, Classroom):
            return any(
                room.name == item.name
                and room.category == item.category
                and room.year == item.year
                and room.capacity == item.capacity
                and room.equipment == item.equipment
                and room.floor == item.floor
                and room.building == item.building
                for room in self._data["catalog"].values()
            )

        return item in self._data["catalog"]
