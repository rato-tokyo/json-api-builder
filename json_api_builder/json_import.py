"""
JSON to database import functionality.
"""

import json
import os
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, GenericTable


def import_database_from_json(
    db_path: str, input_dir: str, overwrite: bool = False
) -> dict[str, Any]:
    """
    Imports data from JSON files into the database.
    This is a standalone function, independent of the APIBuilder.
    """
    if overwrite and os.path.exists(db_path):
        os.remove(db_path)

    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = session_local()

    import_info: dict[str, Any] = {
        "database_path": db_path,
        "input_directory": input_dir,
        "imported_files": [],
        "resource_counts": {},
        "total_records": 0,
    }

    try:
        input_path = Path(input_dir)
        for json_file in input_path.glob("*.json"):
            resource_type = json_file.stem
            with open(json_file, encoding="utf-8") as f:
                items = json.load(f)

            count = 0
            for item_data in items:
                if isinstance(item_data, dict):
                    item_data.pop("id", None)
                    item_data.pop("created_at", None)
                    item_data.pop("updated_at", None)
                    db_item = GenericTable(
                        resource_type=resource_type,
                        data=json.dumps(item_data, default=str, ensure_ascii=False),
                    )
                    db.add(db_item)
                    count += 1

            db.commit()
            if count > 0:
                import_info["imported_files"].append(json_file.name)
                import_info["resource_counts"][resource_type] = count
                import_info["total_records"] += count
    finally:
        db.close()
        engine.dispose()

    return import_info
