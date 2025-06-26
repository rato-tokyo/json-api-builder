"""
APIBuilderの簡素化されたテスト
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Optional

from json_api_builder import APIBuilder


# テスト用モデル
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    price: float


def test_basic_functionality():
    """基本機能のテスト"""
    # APIBuilder作成
    builder = APIBuilder(db_path=":memory:")
    
    # リソース登録
    builder.resource("items", Item)
    
    # TestClient作成
    client = TestClient(builder.get_app())
    
    # ヘルスチェック
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    
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


def test_model_validation():
    """モデル検証のテスト"""
    builder = APIBuilder(db_path=":memory:")
    
    # 無効なモデル
    class InvalidModel:
        pass
    
    with pytest.raises(ValueError, match="Model must be a Pydantic BaseModel subclass"):
        builder.resource("invalid", InvalidModel)


def test_custom_prefix():
    """カスタムプレフィックスのテスト"""
    builder = APIBuilder(db_path=":memory:")
    builder.resource("items", Item, prefix="/api/v1/items")
    
    client = TestClient(builder.get_app())
    
    item_data = {"name": "test", "description": "test item", "price": 100.0}
    response = client.post("/api/v1/items/", json=item_data)
    assert response.status_code == 200


def test_cors_configuration():
    """CORS設定のテスト"""
    builder = APIBuilder(
        db_path=":memory:",
        cors_origins=["http://localhost:3000"]
    )
    builder.resource("items", Item)
    
    client = TestClient(builder.get_app())
    
    # プリフライトリクエストのテスト
    response = client.options("/items/", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST"
    })
    assert response.status_code == 200 