# json_api_builder/db_generator.py
import json
import os
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine


def generate_db_from_directory(
    models: list[type[SQLModel]],
    db_path: str,
    input_dir: str,
    overwrite: bool = False,
) -> None:
    """
    Scans a directory and populates the database from JSON files.

    Args:
        models: A list of SQLModel classes to be included in the database.
        db_path: The path to the output SQLite database file.
        input_dir: The root directory containing the JSON data.
        overwrite: If True, the existing database file will be deleted before generation.
    """
    # Use a synchronous engine for this standalone script
    engine = create_engine(f"sqlite:///{db_path}")

    if overwrite and engine.url.database and os.path.exists(engine.url.database):
        os.remove(engine.url.database)

    SQLModel.metadata.create_all(engine)
    model_map = {model.__tablename__: model for model in models}

    with Session(engine) as session:
        for table_name, model in model_map.items():
            table_path = Path(input_dir) / str(table_name)
            if not table_path.is_dir():
                continue

            all_json_path = table_path / "all.json"
            if all_json_path.exists():
                with open(all_json_path, encoding="utf-8") as f:
                    data = json.load(f)
                    for item_id, item_data in data.items():
                        item_data["id"] = item_data.get("id", int(item_id))
                        db_item = model.model_validate(item_data)
                        session.add(db_item)
            else:
                for json_file in table_path.glob("*.json"):
                    with open(json_file, encoding="utf-8") as f:
                        item_data = json.load(f)
                        item_id = json_file.stem
                        item_data["id"] = item_data.get("id", int(item_id))
                        db_item = model.model_validate(item_data)
                        session.add(db_item)

        session.commit()

    engine.dispose()
