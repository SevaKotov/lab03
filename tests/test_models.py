
import pytest

from catalog.errors import InvalidEntity
from catalog.models import ClassData, Classroom


def make_classroom(name="101", category="Лекционная", id=""):
    return Classroom(
        name=name,
        category=category,
        year=2024,
        capacity=50
    )


def test_create_classroom():
    room = make_classroom()

    assert room.name == "101"
    assert room.capacity == 50
    assert room.id != ""


def test_invalid_classroom():
    with pytest.raises(InvalidEntity):
        Classroom("101", "Лекционная", 2024, -1)


def test_add_and_get():
    catalog = ClassData()
    room = make_classroom()

    catalog.add(room)

    assert catalog.get(room.id) == room


def test_remove():
    catalog = ClassData()
    room = make_classroom()

    catalog.add(room)
    catalog.remove(room.id)

    assert len(catalog) == 0


def test_duplicate_id():
    catalog = ClassData()

    room1 = make_classroom("101", id="1")
    room2 = make_classroom("102", id="1")

    catalog.add(room1)
    catalog.add(room2)

    assert len(catalog) == 2


def test_find_by_category():
    catalog = ClassData()

    room1 = make_classroom("101", "Лекционная")
    room2 = make_classroom("102", "Лабораторная")

    catalog.add(room1)
    catalog.add(room2)

    assert catalog.find_by_category("Лекционная") == [room1]


def test_find_by_name():
    catalog = ClassData()

    room1 = make_classroom("101")
    room2 = make_classroom("201")

    catalog.add(room1)
    catalog.add(room2)

    assert catalog.find_by_name("10") == [room1]


def test_iteration():
    catalog = ClassData()

    room1 = make_classroom("101")
    room2 = make_classroom("102")

    catalog.add(room1)
    catalog.add(room2)

    assert [room.name for room in catalog] == ["101", "102"]
