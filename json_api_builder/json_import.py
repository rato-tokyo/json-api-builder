"""
JSON to database import functionality.
"""

import json
import os
from pathlib import Path
from typing import Any

from . import crud
from .database import Database
from .models import GenericTable


class JSONImporter:
    """Imports data from JSON files into the database."""

    def __init__(self, db: Database):
        """Initializes the JSONImporter."""
        self.db = db
        self.db.create_tables()

    def import_from_json(
        self, input_dir: str, overwrite: bool = False
    ) -> dict[str, Any]:
        """Imports all JSON files from a directory into the database."""
        input_path = Path(input_dir)
        if not input_path.is_dir():
            raise NotADirectoryError(f"Input directory not found: {input_dir}")

        db_path = self.db.get_db_file_path()
        if overwrite and os.path.exists(db_path):
            with self.db.get_db() as session:
                session.query(GenericTable).delete()
                session.commit()

        import_info: dict[str, Any] = {
            "database_path": db_path,
            "input_directory": str(input_path.absolute()),
            "imported_files": [],
            "resource_counts": {},
            "total_records": 0,
        }

        with self.db.get_db() as session:
            for json_file in input_path.glob("*.json"):
                resource_type = json_file.stem
                with open(json_file, encoding="utf-8") as f:
                    try:
                        items = json.load(f)
                    except json.JSONDecodeError:
                        continue  # Skip invalid JSON files

                if not isinstance(items, list):
                    continue  # Skip files that do not contain a list of items

                count = 0
                for item_data in items:
                    if isinstance(item_data, dict):
                        crud.create_item_from_dict(session, resource_type, item_data)
                        count += 1

                if count > 0:
                    import_info["imported_files"].append(json_file.name)
                    import_info["resource_counts"][resource_type] = count
                    import_info["total_records"] += count

        return import_info


def import_database_from_json(
    db_path: str, input_dir: str, overwrite: bool = False
) -> dict[str, Any]:
    """Function to import database content from JSON files."""
    db = Database(db_path)
    # The main importer will dispose the engine if overwriting.
    # If not, we need to dispose it here.
    try:
        importer = JSONImporter(db)
        return importer.import_from_json(input_dir, overwrite)
    finally:
        if not overwrite:
            db.engine.dispose()
