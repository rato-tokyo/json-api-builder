"""
Database to JSON export functionality.
"""

import json
import os
from pathlib import Path
from typing import Any

from .database import Database
from .models import GenericTable


class JSONExporter:
    """Exports the database content to JSON files."""

    def __init__(self, db_path: str):
        """Initializes the JSONExporter."""
        self.db_path = db_path

    def export_to_json(self, output_dir: str, pretty: bool = True) -> dict[str, Any]:
        """Exports all data from the database to JSON files."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        db = Database(self.db_path)
        session = next(db.get_db())
        try:
            export_info = {
                "database_path": self.db_path,
                "output_directory": str(output_path.absolute()),
                "exported_files": [],
                "resource_counts": {},
                "total_records": 0,
            }

            all_items = session.query(GenericTable).all()
            resources_data: dict[str, list[dict]] = {}

            for item in all_items:
                if item.resource_type not in resources_data:
                    resources_data[item.resource_type] = []

                data = json.loads(item.data)
                data["id"] = item.id
                data["created_at"] = (
                    item.created_at.isoformat() if item.created_at else None
                )
                data["updated_at"] = (
                    item.updated_at.isoformat() if item.updated_at else None
                )
                resources_data[item.resource_type].append(data)

            for resource_type, items in resources_data.items():
                filename = f"{resource_type}.json"
                file_path = output_path / filename
                with open(file_path, "w", encoding="utf-8") as f:
                    indent = 2 if pretty else None
                    json.dump(items, f, ensure_ascii=False, indent=indent, default=str)

                export_info["exported_files"].append(filename)
                export_info["resource_counts"][resource_type] = len(items)
                export_info["total_records"] += len(items)

            return export_info
        finally:
            session.close()
            db.engine.dispose()

    def export_resource_to_json(
        self, resource_type: str, output_file: str, pretty: bool = True
    ) -> dict[str, Any]:
        """Exports a specific resource type to a JSON file."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        db = Database(self.db_path)
        session = next(db.get_db())
        try:
            export_info = {
                "database_path": self.db_path,
                "resource_type": resource_type,
                "output_file": str(output_path.absolute()),
                "record_count": 0,
            }

            items = (
                session.query(GenericTable)
                .filter_by(resource_type=resource_type)
                .all()
            )
            if not items:
                raise ValueError(f"No data found for resource type: {resource_type}")

            export_data = []
            for item in items:
                data = json.loads(item.data)
                data["id"] = item.id
                data["created_at"] = (
                    item.created_at.isoformat() if item.created_at else None
                )
                data["updated_at"] = (
                    item.updated_at.isoformat() if item.updated_at else None
                )
                export_data.append(data)

            with open(output_path, "w", encoding="utf-8") as f:
                indent = 2 if pretty else None
                json.dump(
                    export_data, f, ensure_ascii=False, indent=indent, default=str
                )

            export_info["record_count"] = len(export_data)
            return export_info
        finally:
            session.close()
            db.engine.dispose()


def export_database_to_json(
    db_path: str, output_dir: str, pretty: bool = True
) -> dict[str, Any]:
    """Function to export the entire database to JSON files."""
    exporter = JSONExporter(db_path)
    return exporter.export_to_json(output_dir, pretty)


def export_resource_to_json(
    db_path: str, resource_type: str, output_file: str, pretty: bool = True
) -> dict[str, Any]:
    """Function to export a specific resource type to a JSON file."""
    exporter = JSONExporter(db_path)
    return exporter.export_resource_to_json(resource_type, output_file, pretty)