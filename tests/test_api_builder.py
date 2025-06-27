"""
APIBuilderの簡素化されたテスト
"""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from json_api_builder import APIBuilder


# テスト用モデル
class Item(BaseModel):
    id: int | None = None
    name: str
    description: str
    price: float


def test_basic_functionality():
    """基本機能のテスト"""
    # 一時データベースファイル作成
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    builder = None
    try:
        # APIBuilder作成
        builder = APIBuilder(
            title="Test API", description="Test API", version="1.0.0", db_path=db_path
        )

        # リソース登録
        builder.resource("items", Item)

        # TestClient作成
        client = TestClient(builder.get_app())

        # アイテム作成
        item_data = {"name": "test", "description": "test item", "price": 100.0}
        response = client.post("/items/", json=item_data)
        assert response.status_code == 200
        created_item = response.json()
        assert created_item["name"] == "test"
        assert "id" in created_item

        # アイテム取得
        item_id = created_item["id"]
        response = client.get(f"/items/{item_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "test"

        # アイテム一覧
        response = client.get("/items/")
        assert response.status_code == 200
        assert len(response.json()) == 1

        # アイテム更新
        update_data = {"name": "updated", "description": "updated item", "price": 200.0}
        response = client.put(f"/items/{item_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["name"] == "updated"

        # アイテム削除
        response = client.delete(f"/items/{item_id}")
        assert response.status_code == 200

        # 削除確認
        response = client.get(f"/items/{item_id}")
        assert response.status_code == 404

    finally:
        # データベース接続をクローズ
        if builder:
            builder.engine.dispose()
        # 一時ファイル削除
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except PermissionError:
            pass  # Windowsでファイルが使用中の場合は無視


def test_model_validation():
    """モデル検証のテスト"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    builder = None
    try:
        builder = APIBuilder(
            title="Test API", description="Test API", version="1.0.0", db_path=db_path
        )

        # 無効なモデル
        class InvalidModel:
            pass

        with pytest.raises(
            ValueError, match="Model must be a Pydantic BaseModel subclass"
        ):
            builder.resource("invalid", InvalidModel)

    finally:
        if builder:
            builder.engine.dispose()
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except PermissionError:
            pass


def test_multiple_resources():
    """複数リソースのテスト"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    builder = None
    try:
        builder = APIBuilder(
            title="Test API", description="Test API", version="1.0.0", db_path=db_path
        )

        # ユーザーモデル
        class User(BaseModel):
            id: int | None = None
            name: str
            email: str

        # 両方のリソース登録
        builder.resource("items", Item)
        builder.resource("users", User)

        client = TestClient(builder.get_app())

        # アイテム作成
        item_data = {"name": "test", "description": "test item", "price": 100.0}
        response = client.post("/items/", json=item_data)
        assert response.status_code == 200

        # ユーザー作成
        user_data = {"name": "John", "email": "john@example.com"}
        response = client.post("/users/", json=user_data)
        assert response.status_code == 200

        # 両方のリソースが独立して動作することを確認
        response = client.get("/items/")
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.get("/users/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    finally:
        if builder:
            builder.engine.dispose()
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except PermissionError:
            pass
