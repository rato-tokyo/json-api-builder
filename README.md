# json-api-builder

JSONデータを使ったREST APIサーバーの構築と、関連データ操作を簡単に行うためのPythonライブラリです。

## 設計思想と主な特徴

本ライブラリは、**シンプルさと責務の分離**を重視しています。

1.  **`APIBuilder`**: FastAPIサーバーの構築と実行、データベース接続管理に専念します。
2.  **独立したデータ操作関数**: サーバーを起動することなく、データベースのJSONへのエクスポートや、JSONからのインポートといった操作を行える関数群を提供します。

これにより、利用者は目的に応じて必要な機能だけをシンプルに使用できます。

### 主な特徴
- 🚀 **簡単セットアップ**: 数行のコードでAPIサーバーを構築
- 🔧 **独立したデータ操作**: サーバー不要でDBのインポート/エクスポートが可能
- 📝 **Pydanticベース**: 型安全なPydanticモデルを使用
- 🗄️ **SQLite統合**: 軽量で高性能なSQLite���ータベース
- 📚 **自動ドキュメント**: FastAPIによる自動Swagger UI

## インストール

```bash
pip install json-api-builder
```

## 使い方

### APIサーバーの構築

```python
from json_api_builder import APIBuilder
from pydantic import BaseModel

class Item(BaseModel):
    id: int | None = None
    name: str
    price: float

# APIサーバーを構築
builder = APIBuilder(
    title="My API",
    description="シンプルなAPI",
    version="1.0.0",
    db_path="my_data.db"
)

# "items"リソースを登録
builder.resource("items", Item)

# サーバーを起動
if __name__ == "__main__":
    builder.run(host="127.0.0.1", port=8000)
```

### データ操作（サーバー不要）

`APIBuilder`とは独立して、データベースのデータを操作できます。

```python
from json_api_builder import export_database_to_json, import_database_from_json

# データベースをJSONファイル群にエクスポート
export_database_to_json(db_path="my_data.db", output_dir="exported_data")

# JSONファイル群から新しいデータベースを構築
import_database_from_json(
    db_path="new_database.db",
    input_dir="exported_data",
    overwrite=True  # 既存のDBファイルを上書き
)
```

## APIリファレンス

詳細は `docs/api_reference.md` を参照してください。

## 開発・テスト

### 開発用インストール

```bash
pip install -e .[dev]
```

### テスト実行

```bash
pytest
```

### テストの実装について

本ライブラリを使用したアプリケーションのテストを`pytest`で実装する場合、`TestClient`と一時的なデータベースファイルを組み合わせることで、ファイルロックを回避した安定したテストが可能です。

`APIBuilder`に組み込まれた`lifespan`イベントにより、`TestClient`のコンテキスト（`with`文）が終了する際にデータベース接続が自動的にクローズされます。

**テストコードの例:**
```python
import os
import tempfile
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel
from json_api_builder import APIBuilder

# テスト対象のモデル
class Item(BaseModel):
    id: int | None = None
    name: str

# pytestフィクスチャ
@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name
    
    builder = APIBuilder("Test API", "Test", "1.0", db_path)
    builder.resource("items", Item)

    with TestClient(builder.get_app()) as test_client:
        yield test_client
    
    os.unlink(db_path)

# テスト関数
def test_create_item(client: TestClient):
    response = client.post("/items/", json={"name": "Test Item"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item"
```

## ライセンス

MIT License