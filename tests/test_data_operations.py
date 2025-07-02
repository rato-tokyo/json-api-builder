"""
Tests for standalone data operations (import/export).
"""

import json
import os
import tempfile
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from json_api_builder import export_database_to_json, import_database_from_json
from json_api_builder.models import Base, GenericTable


def setup_test_db(db_path: str):
    """Helper function to create and populate a test database."""
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)
    session_cls = sessionmaker(bind=engine)
    session = session_cls()
    session.add(
        GenericTable(resource_type="items", data='{"name": "Item 1", "price": 100}')
    )
    session.add(
        GenericTable(resource_type="users", data='{"username": "user1", "age": 25}')
    )
    session.commit()
    session.close()
    engine.dispose()


def test_export_import_cycle():
    """
    Tests a full cycle of creating a DB, exporting it to JSON,
    and importing it back to a new DB.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Setup initial database
        db_path_source = os.path.join(temp_dir, "source.db")
        setup_test_db(db_path_source)

        # 2. Export to JSON
        json_dir = os.path.join(temp_dir, "json_data")
        export_result = export_database_to_json(db_path_source, json_dir)
        assert export_result["total_records"] == 2
        assert len(export_result["exported_files"]) == 2
        assert Path(json_dir, "items.json").exists()
        assert Path(json_dir, "users.json").exists()

        # 3. Import from JSON to a new database
        db_path_dest = os.path.join(temp_dir, "dest.db")
        import_result = import_database_from_json(db_path_dest, json_dir)
        assert import_result["total_records"] == 2

        # 4. Verify the content of the new database
        engine_dest = create_engine(f"sqlite:///{db_path_dest}")
        session_dest_cls = sessionmaker(bind=engine_dest)
        session_dest = session_dest_cls()
        items = session_dest.query(GenericTable).filter_by(resource_type="items").all()
        users = session_dest.query(GenericTable).filter_by(resource_type="users").all()
        assert len(items) == 1
        assert len(users) == 1
        assert json.loads(items[0].data)["name"] == "Item 1"
        session_dest.close()
        engine_dest.dispose()
