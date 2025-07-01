"""
Tests for JSON export functionality.
"""

import json
import tempfile
from pathlib import Path

import pytest
from json_api_builder import (
    APIBuilder,
    JSONExporter,
    export_database_to_json,
    export_resource_to_json,
)
from json_api_builder.database import Database


class TestJSONExporter:
    """Tests for the JSONExporter class."""

    def test_export_to_json_all_resources(self, sample_app_builder: APIBuilder):
        """Tests exporting all resources to JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = JSONExporter(sample_app_builder.db)
            result = exporter.export_to_json(temp_dir)
            assert result["total_records"] == 2
            assert len(result["exported_files"]) == 2

    def test_export_resource_to_json(self, sample_app_builder: APIBuilder):
        """Tests exporting a single resource to JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "items.json"
            exporter = JSONExporter(sample_app_builder.db)
            result = exporter.export_resource_to_json("items", str(output_file))
            assert result["record_count"] == 1


class TestFunctionAPI:
    """Tests for the standalone export functions."""

    def test_export_database_to_json_function(self, sample_app_builder: APIBuilder):
        """Tests the export_database_to_json function."""
        db_path = sample_app_builder.db.get_db_file_path()
        with tempfile.TemporaryDirectory() as temp_dir:
            result = export_database_to_json(db_path, temp_dir)
            assert result["total_records"] == 2
