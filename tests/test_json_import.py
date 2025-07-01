"""
Tests for JSON import functionality.
"""

import os
import tempfile
import time

import pytest

from json_api_builder import (
    APIBuilder,
    JSONExporter,
    JSONImporter,
    import_database_from_json,
)
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

            assert result["total_records"] == 5
            with db.get_db() as session:
                from json_api_builder.models import GenericTable

                items_count = (
                    session.query(GenericTable).filter_by(resource_type="items").count()
                )
                assert items_count == 3
        finally:
            db.engine.dispose()
            if os.path.exists(new_db_path):
                os.unlink(new_db_path)

    def test_import_with_overwrite(self, exported_json_dir):
        """Test importing with overwrite=True."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        db = Database(db_path)
        importer = JSONImporter(db)
        try:
            importer.import_from_json(exported_json_dir)
            result = importer.import_from_json(exported_json_dir, overwrite=True)
            assert result["total_records"] == 5

            with db.get_db() as session:
                from json_api_builder.models import GenericTable

                items_count = (
                    session.query(GenericTable).filter_by(resource_type="items").count()
                )
                assert items_count == 3
        finally:
            db.engine.dispose()
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_import_from_nonexistent_directory(self):
        """Test importing from a nonexistent directory."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        db = Database(db_path)
        try:
            importer = JSONImporter(db)
            with pytest.raises(NotADirectoryError):
                importer.import_from_json("/path/to/nonexistent/dir")
        finally:
            db.engine.dispose()
            os.unlink(db_path)


class TestFunctionAPIImport:
    """Tests for the standalone import functions."""

    def test_import_database_from_json_function(self, exported_json_dir):
        """Test the import_database_from_json function."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            new_db_path = tmp_file.name

        try:
            result = import_database_from_json(new_db_path, exported_json_dir)
            assert result["total_records"] == 5
        finally:
            time.sleep(0.1)
            if os.path.exists(new_db_path):
                os.unlink(new_db_path)
