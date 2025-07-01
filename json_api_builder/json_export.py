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

    def __init__(self, db: Database):
        """Initializes the JSONExporter."""
        self.db = db

    def export_to_json(self, output_dir: str, pretty: bool = True) -> dict[str, Any]:
        """Exports all data from the database to JSON files."""
        db_path = self.db.get_db_file_path()
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found: {db_path}")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        with self.db.get_db() as session:
            export_info: dict[str, Any] = {
                "database_path": db_path,
                "output_directory": str(output_path.absolute()),
                "exported_files": [],
                "resource_counts": {},
                "total_records": 0,
            }

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

            return export_info

    def export_resource_to_json(
        self, resource_type: str, output_file: str, pretty: bool = True
    ) -> dict[str, Any]:
        """Exports a specific resource type to a JSON file."""
        db_path = self.db.get_db_file_path()
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found: {db_path}")

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with self.db.get_db() as session:
            export_info = {
                "database_path": db_path,
                "resource_type": resource_type,
                "output_file": str(output_path.absolute()),
                "record_count": 0,
            }

            items = (
                session.query(GenericTable).filter_by(resource_type=resource_type).all()
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


def export_database_to_json(
    db_path: str, output_dir: str, pretty: bool = True
) -> dict[str, Any]:
    """Function to export the entire database to JSON files."""
    db = Database(db_path)
    try:
        exporter = JSONExporter(db)
        return exporter.export_to_json(output_dir, pretty)
    finally:
        db.engine.dispose()


def export_resource_to_json(
    db_path: str, resource_type: str, output_file: str, pretty: bool = True
) -> dict[str, Any]:
    """Function to export a specific resource type to a JSON file."""
    db = Database(db_path)
    try:
        exporter = JSONExporter(db)
        return exporter.export_resource_to_json(resource_type, output_file, pretty)
    finally:
        db.engine.dispose()
