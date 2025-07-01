"""
JSON展開機能のテスト
"""

import json
import os
import tempfile
from pathlib import Path

import pytest
from pydantic import BaseModel, Field

from json_api_builder import APIBuilder, JSONExporter, export_database_to_json, export_resource_to_json


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


@pytest.fixture
def sample_db():
    """サンプルデータベースを作成"""
    # 一時データベースファイル作成
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    try:
        # APIBuilder作成
        builder = APIBuilder(
            title="テストAPI",
            description="JSON展開テスト用API",
            version="1.0.0",
            db_path=db_path,
        )

        # リソース登録
        builder.resource("items", ItemModel)
        builder.resource("users", UserModel)

        # サンプルデータを追加
        from sqlalchemy.orm import Session
        from json_api_builder.api_builder import GenericTable

        db = builder.SessionLocal()
        try:
            # アイテムデータ
            item_data = [
                {"name": "商品1", "description": "最初の商品", "price": 1000.0},
                {"name": "商品2", "description": "二番目の商品", "price": 2000.0},
                {"name": "商品3", "description": "三番目の商品", "price": 1500.0},
            ]

            for data in item_data:
                db_item = GenericTable(
                    resource_type="items",
                    data=json.dumps(data, ensure_ascii=False),
                )
                db.add(db_item)

            # ユーザーデータ
            user_data = [
                {"username": "user1", "email": "user1@example.com", "age": 25},
                {"username": "user2", "email": "user2@example.com", "age": 30},
            ]

            for data in user_data:
                db_user = GenericTable(
                    resource_type="users",
                    data=json.dumps(data, ensure_ascii=False),
                )
                db.add(db_user)

            db.commit()

        finally:
            db.close()
            builder.engine.dispose()

        yield db_path

    finally:
        # クリーンアップ
        if os.path.exists(db_path):
            os.unlink(db_path)


class TestJSONExporter:
    """JSONExporterクラスのテスト"""

    def test_export_to_json_all_resources(self, sample_db):
        """全リソースのJSON展開テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = JSONExporter(sample_db)
            result = exporter.export_to_json(temp_dir)

            # 結果の検証
            assert result["database_path"] == sample_db
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
            with open(items_file, "r", encoding="utf-8") as f:
                items_data = json.load(f)
            assert len(items_data) == 3
            assert items_data[0]["name"] == "商品1"
            assert "id" in items_data[0]
            assert "created_at" in items_data[0]
            assert "updated_at" in items_data[0]

            with open(users_file, "r", encoding="utf-8") as f:
                users_data = json.load(f)
            assert len(users_data) == 2
            assert users_data[0]["username"] == "user1"
            assert "id" in users_data[0]

    def test_export_to_json_pretty_false(self, sample_db):
        """整形なしJSON展開テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = JSONExporter(sample_db)
            result = exporter.export_to_json(temp_dir, pretty=False)

            # ファイル内容が整形されていないことを確認
            items_file = Path(temp_dir) / "items.json"
            with open(items_file, "r", encoding="utf-8") as f:
                content = f.read()
            # 改行がないことを確認（整形されていない）
            assert "\n" not in content

    def test_export_resource_to_json(self, sample_db):
        """特定リソースのJSON展開テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "exported_items.json"
            
            exporter = JSONExporter(sample_db)
            result = exporter.export_resource_to_json("items", str(output_file))

            # 結果の検証
            assert result["database_path"] == sample_db
            assert result["resource_type"] == "items"
            assert result["output_file"] == str(output_file.absolute())
            assert result["record_count"] == 3

            # ファイルの存在確認
            assert output_file.exists()

            # ファイル内容の確認
            with open(output_file, "r", encoding="utf-8") as f:
                items_data = json.load(f)
            assert len(items_data) == 3
            assert items_data[0]["name"] == "商品1"
            assert items_data[1]["name"] == "商品2"
            assert items_data[2]["name"] == "商品3"

    def test_export_nonexistent_resource(self, sample_db):
        """存在しないリソースタイプの展開テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "nonexistent.json"
            
            exporter = JSONExporter(sample_db)
            with pytest.raises(ValueError, match="No data found for resource type: nonexistent"):
                exporter.export_resource_to_json("nonexistent", str(output_file))

    def test_export_nonexistent_database(self):
        """存在しないデータベースファイルのテスト"""
        nonexistent_db = "/path/to/nonexistent.db"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = JSONExporter(nonexistent_db)
            
            with pytest.raises(FileNotFoundError, match="Database file not found"):
                exporter.export_to_json(temp_dir)

            with pytest.raises(FileNotFoundError, match="Database file not found"):
                exporter.export_resource_to_json("items", str(Path(temp_dir) / "test.json"))


class TestFunctionAPI:
    """関数APIのテスト"""

    def test_export_database_to_json_function(self, sample_db):
        """export_database_to_json関数のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = export_database_to_json(sample_db, temp_dir)

            # 結果の検証
            assert result["total_records"] == 5
            assert len(result["exported_files"]) == 2
            assert "items.json" in result["exported_files"]
            assert "users.json" in result["exported_files"]

    def test_export_resource_to_json_function(self, sample_db):
        """export_resource_to_json関数のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_items.json"
            
            result = export_resource_to_json(sample_db, "items", str(output_file))

            # 結果の検証
            assert result["record_count"] == 3
            assert result["resource_type"] == "items"
            assert output_file.exists()


class TestAPIBuilderIntegration:
    """APIBuilderとの統合テスト"""

    def test_api_builder_export_methods(self, sample_db):
        """APIBuilderのexportメソッドテスト"""
        builder = APIBuilder(
            title="テストAPI",
            description="統合テスト用API",
            version="1.0.0",
            db_path=sample_db,
        )

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # 全データ展開
                result = builder.export_to_json(temp_dir)
                assert result["total_records"] == 5

                # 特定リソース展開
                output_file = Path(temp_dir) / "api_items.json"
                result = builder.export_resource_to_json("items", str(output_file))
                assert result["record_count"] == 3
                assert output_file.exists()

        finally:
            builder.engine.dispose()


class TestDirectoryCreation:
    """ディレクトリ作成のテスト"""

    def test_create_nested_output_directory(self, sample_db):
        """ネストしたディレクトリの作成テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_dir = Path(temp_dir) / "level1" / "level2" / "output"
            
            exporter = JSONExporter(sample_db)
            result = exporter.export_to_json(str(nested_dir))

            # ディレクトリが作成されていることを確認
            assert nested_dir.exists()
            assert nested_dir.is_dir()
            assert result["total_records"] == 5

    def test_create_nested_output_file_directory(self, sample_db):
        """ネストしたファイルパスのディレクトリ作成テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_file = Path(temp_dir) / "level1" / "level2" / "items.json"
            
            exporter = JSONExporter(sample_db)
            result = exporter.export_resource_to_json("items", str(nested_file))

            # ディレクトリとファイルが作成されていることを確認
            assert nested_file.parent.exists()
            assert nested_file.parent.is_dir()
            assert nested_file.exists()
            assert result["record_count"] == 3 