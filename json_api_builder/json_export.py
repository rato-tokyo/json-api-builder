"""
Database to JSON export functionality.
"""

import json
import os
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import GenericTable


def export_database_to_json(
    db_path: str, output_dir: str, pretty: bool = True
) -> dict[str, Any]:
    """
    Exports all data from the database to JSON files.
    This is a standalone function, independent of the APIBuilder.
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")

    engine = create_engine(f"sqlite:///{db_path}")
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_local()

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    export_info: dict[str, Any] = {
        "database_path": db_path,
        "output_directory": str(output_path.absolute()),
        "exported_files": [],
        "resource_counts": {},
        "total_records": 0,
    }

    try:
        all_items = session.query(GenericTable).all()
        resources_data: dict[str, list[dict[str, Any]]] = {}

        for item in all_items:
            resource_type = item.resource_type
            if resource_type not in resources_data:
                resources_data[resource_type] = []

            data = json.loads(item.data)
            data["id"] = item.id
            data["created_at"] = (
                item.created_at.isoformat() if item.created_at else None
            )
            data["updated_at"] = (
                item.updated_at.isoformat() if item.updated_at else None
            )
            resources_data[resource_type].append(data)

        for resource_type, items in resources_data.items():
            filename = f"{resource_type}.json"
            file_path = output_path / filename
            with open(file_path, "w", encoding="utf-8") as f:
                indent = 2 if pretty else None
                json.dump(items, f, ensure_ascii=False, indent=indent, default=str)

            export_info["exported_files"].append(filename)
            export_info["resource_counts"][resource_type] = len(items)
            export_info["total_records"] += len(items)
    finally:
        session.close()
        engine.dispose()

    return export_info
