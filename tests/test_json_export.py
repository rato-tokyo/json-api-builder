"""
JSON展開機能のテスト
"""

import json
import tempfile
from pathlib import Path

import pytest
from pydantic import BaseModel, Field

from json_api_builder import (
    APIBuilder,
    JSONExporter,
    export_database_to_json,
    export_resource_to_json,
)
from json_api_builder.database import Database


class ItemModel(BaseModel):
    """テスト用アイテムモデル"""

    id: int | None = None
    name: str = Field(description="アイテム名")
    description: str = Field(description="説明")
    price: float = Field(description="価格", ge=0)


class UserModel(BaseModel):
    """テスト用ユーザーモデル"""

    id: int | None = None
    username: str = Field(description="ユーザー名")
    email: str = Field(description="メールアドレス")
    age: int = Field(description="年齢", ge=0)


class TestJSONExporter:
    """Tests for the JSONExporter class."""

    def test_export_to_json_all_resources(self, sample_app_builder: APIBuilder):
        """Tests exporting all resources to JSON."""
        db_path = sample_app_builder.db.get_db_file_path()
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = JSONExporter(sample_app_builder.db)
            result = exporter.export_to_json(temp_dir)

            assert result["database_path"] == db_path
            assert result["output_directory"] == str(Path(temp_dir).absolute())
            assert len(result["exported_files"]) == 2
            assert "items.json" in result["exported_files"]
            assert "users.json" in result["exported_files"]
            assert result["resource_counts"]["items"] == 3
            assert result["resource_counts"]["users"] == 2
            assert result["total_records"] == 5

            # ファイルの存在確認
            items_file = Path(temp_dir) / "items.json"
            users_file = Path(temp_dir) / "users.json"
            assert items_file.exists()
            assert users_file.exists()

            # ファイル内容の確認
            with open(items_file, encoding="utf-8") as f:
                items_data = json.load(f)
            assert len(items_data) == 3
            assert items_data[0]["name"] == "Item 1"
            assert "id" in items_data[0]
            assert "created_at" in items_data[0]
            assert "updated_at" in items_data[0]

            with open(users_file, encoding="utf-8") as f:
                users_data = json.load(f)
            assert len(users_data) == 2
            assert users_data[0]["username"] == "user1"
            assert "id" in users_data[0]
        # db.engine.dispose() # No longer needed with APIBuilder fixture

    def test_export_to_json_pretty_false(self, sample_app_builder: APIBuilder):
        """Tests exporting without pretty printing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = JSONExporter(sample_app_builder.db)
            exporter.export_to_json(temp_dir, pretty=False)
            items_file = Path(temp_dir) / "items.json"
            with open(items_file, encoding="utf-8") as f:
                content = f.read()
            assert "\n" not in content
        # db.engine.dispose() # No longer needed with APIBuilder fixture

    def test_export_resource_to_json(self, sample_app_builder: APIBuilder):
        """Tests exporting a single resource to JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "exported_items.json"
            exporter = JSONExporter(sample_app_builder.db)
            result = exporter.export_resource_to_json("items", str(output_file))
            assert result["database_path"] == sample_app_builder.db.get_db_file_path()
            assert result["resource_type"] == "items"
            assert result["output_file"] == str(output_file.absolute())
            assert result["record_count"] == 3

            # ファイルの存在確認
            assert output_file.exists()

            # ファイル内容の確認
            with open(output_file, encoding="utf-8") as f:
                items_data = json.load(f)
            assert len(items_data) == 3
            assert items_data[0]["name"] == "Item 1"
            assert items_data[1]["name"] == "Item 2"
            assert items_data[2]["name"] == "Item 3"
        # db.engine.dispose() # No longer needed with APIBuilder fixture

    def test_export_nonexistent_resource(self, sample_app_builder: APIBuilder):
        """Tests exporting a nonexistent resource type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "nonexistent.json"
            exporter = JSONExporter(sample_app_builder.db)
            with pytest.raises(
                ValueError, match="No data found for resource type: nonexistent"
            ):
                exporter.export_resource_to_json("nonexistent", str(output_file))
        # db.engine.dispose() # No longer needed with APIBuilder fixture

    def test_export_nonexistent_database(self):
        """Tests exporting from a nonexistent database file."""
        nonexistent_db_path = "/path/to/nonexistent.db"
        db = Database(nonexistent_db_path)

        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = JSONExporter(db)

            with pytest.raises(FileNotFoundError, match="Database file not found"):
                exporter.export_to_json(temp_dir)

            with pytest.raises(FileNotFoundError, match="Database file not found"):
                exporter.export_resource_to_json(
                    "items", str(Path(temp_dir) / "test.json")
                )
        # No need to dispose, as the connection was never made


class TestFunctionAPI:
    """Tests for the standalone export functions."""

    def test_export_database_to_json_function(self, sample_app_builder: APIBuilder):
        """Tests the export_database_to_json function."""
        db_path = sample_app_builder.db.get_db_file_path()
        with tempfile.TemporaryDirectory() as temp_dir:
            result = export_database_to_json(db_path, temp_dir)

            # 結果の検証
            assert result["total_records"] == 5
            assert len(result["exported_files"]) == 2
            assert "items.json" in result["exported_files"]
            assert "users.json" in result["exported_files"]

    def test_export_resource_to_json_function(self, sample_app_builder: APIBuilder):
        """Tests the export_resource_to_json function."""
        db_path = sample_app_builder.db.get_db_file_path()
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_items.json"

            result = export_resource_to_json(db_path, "items", str(output_file))

            # 結果の検証
            assert result["record_count"] == 3
            assert result["resource_type"] == "items"
            assert output_file.exists()


class TestAPIBuilderIntegration:
    """Tests integration with the APIBuilder class."""

    def test_api_builder_export_methods(self, sample_app_builder: APIBuilder):
        """Tests the export methods on the APIBuilder instance."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # 全データ展開
                result = sample_app_builder.export_to_json(temp_dir)
                assert result["total_records"] == 5

                # 特定リソース展開
                output_file = Path(temp_dir) / "api_items.json"
                result = sample_app_builder.export_resource_to_json(
                    "items", str(output_file)
                )
                assert result["record_count"] == 3
                assert output_file.exists()

        finally:
            sample_app_builder.engine.dispose()


class TestDirectoryCreation:
    """Tests for directory creation during export."""

    def test_create_nested_output_directory(self, sample_app_builder: APIBuilder):
        """Tests creation of nested output directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_dir = Path(temp_dir) / "level1" / "level2" / "output"

            exporter = JSONExporter(sample_app_builder.db)
            result = exporter.export_to_json(str(nested_dir))

            # ディレクトリが作成されていることを確認
            assert nested_dir.exists()
            assert nested_dir.is_dir()
            assert result["total_records"] == 5

    def test_create_nested_output_file_directory(self, sample_app_builder: APIBuilder):
        """Tests creation of directories for nested file paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_file = Path(temp_dir) / "level1" / "level2" / "items.json"

            exporter = JSONExporter(sample_app_builder.db)
            result = exporter.export_resource_to_json("items", str(nested_file))

            # ディレクトリとファイルが作成されていることを確認
            assert nested_file.parent.exists()
            assert nested_file.parent.is_dir()
            assert nested_file.exists()
            assert result["record_count"] == 3
