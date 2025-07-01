"""
Tests for JSON import functionality.
"""

import os
import tempfile

import pytest
from json_api_builder import APIBuilder, JSONExporter, JSONImporter
from json_api_builder.database import Database


@pytest.fixture(scope="function")
def exported_json_dir(sample_app_builder: APIBuilder):
    """Creates a directory with exported JSON files for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        exporter = JSONExporter(sample_app_builder.db)
        exporter.export_to_json(temp_dir)
        yield temp_dir


class TestJSONImporter:
    """Tests for the JSONImporter class."""

    def test_import_from_json(self, exported_json_dir):
        """Test importing all resources from a JSON directory."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            new_db_path = tmp_file.name
        
        db = Database(new_db_path)
        try:
            importer = JSONImporter(db)
            result = importer.import_from_json(exported_json_dir)
            assert result["total_records"] == 2
        finally:
            db.engine.dispose()
            if os.path.exists(new_db_path):
                os.unlink(new_db_path)
