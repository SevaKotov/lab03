import argparse
from pathlib import Path

from .errors import CatalogError
from .models import ClassData, Classroom
from .storage import load_catalog, save_by_json, save_catalog


def create_parser():
    parser = argparse.ArgumentParser(
        description="Каталог учебных аудиторий"
    )

    commands = parser.add_subparsers(
        dest="command",
        required=True
    )

    add_parser = commands.add_parser("add")
    add_parser.add_argument("name")
    add_parser.add_argument("category")
    add_parser.add_argument("year", type=int)
    add_parser.add_argument("capacity", type=int)
    add_parser.add_argument("--equipment", default=None)
    add_parser.add_argument("--floor", default=None)
    add_parser.add_argument("--building", default=None)

    get_parser = commands.add_parser("get")
    get_parser.add_argument("item_id")

    remove_parser = commands.add_parser("remove")
    remove_parser.add_argument("item_id")

    find_parser = commands.add_parser("find")
    find_commands = find_parser.add_subparsers(
        dest="find_type",
        required=True
    )

    category_parser = find_commands.add_parser("category")
    category_parser.add_argument("category")

    name_parser = find_commands.add_parser("name")
    name_parser.add_argument("query")

    import_parser = commands.add_parser("import")
    import_parser.add_argument("path")

    commands.add_parser("list")
    commands.add_parser("count")
    commands.add_parser("iter")

    contains_parser = commands.add_parser("contains")
    contains_parser.add_argument("item_id")

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    try:
        catalog = ClassData()
        catalog = load_catalog(catalog)

        if args.command == "add":
            room = Classroom(
                name=args.name,
                category=args.category,
                year=args.year,
                capacity=args.capacity,
                equipment=args.equipment,
                floor=args.floor,
                building=args.building
            )

            catalog.add(room)
            save_catalog(catalog)
            print("Audience added successfully")

        elif args.command == "get":
            room = catalog.get(args.item_id)
            print(room)

        elif args.command == "remove":
            catalog.remove(args.item_id)
            save_catalog(catalog)
            print("Audience removed successfully")

        elif args.command == "find":
            if args.find_type == "category":
                result = catalog.find_by_category(args.category)
            else:
                result = catalog.find_by_name(args.query)
            if result:
                for room in result:
                    print(room)
            else:
                print("Nothing found")

        elif args.command == "import":
            save_by_json(Path(args.path), catalog)
            print("Catalog imported successfully")

        elif args.command == "count":
            print(f"Amount of audiences: {len(catalog)}")

        elif args.command == "contains":
            if args.item_id in catalog:
                print("Audience exists")
            else:
                print("Audience does not exist")

        elif args.command == "iter":
            iterator = iter(catalog)

            for room in iterator:
                print(room)


    except CatalogError as error:
        print(f"Catalog error: {error}")


if __name__ == "__main__":
    main()
