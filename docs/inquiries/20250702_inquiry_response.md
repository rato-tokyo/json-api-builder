# `json-api-builder` v0.1.1のテストに関するお問い合わせへの回答

**お問い合わせ日時:** 2025-07-02
**件名:** `db_engine`引数の挙動について

---

この度は、`json-api-builder`をご利用いただき、また、詳細なご報告をいただき誠にありがとうございます。
ドキュメントとライブラリの実際の挙動に差異があるとのこと、深くお詫び申し上げます。

ご指摘いただいた問題は、v0.1.1の開発過程で発生したリファクタリングに起因するものです。

### 1. `db_engine`引数の実装状況について

お問い合わせいただいた通り、`db_engine`引数は現在の`v0.1.1`には**実装されておりません。**

開発の初期段階では、`db_engine`引数をサポートする設計を検討していました。しかし、最終的なリファクタリングの過程で、「後方互換性を考慮せず、ラ���ブラリの責務をより明確にし、全体を簡素化する」という方針を優先することにいたしました。

その結果、`APIBuilder`の責務を「APIサーバーの構築と実行」に限定し、データベースエンジンの直接注入機能を削除して、ファイルベースの`db_path`のみをサポートする現在のシンプルな形に落ち着きました。

この設計変更が、ドキュメントの一部に反映されずに残ってしまったことが、今回の混乱の原因です。誠に申し訳ありません。

### 2. v0.1.1での推奨テスト方法について

`db_engine`引数がない現在のバージョンで、ファイルロックを回避しつつ安定したテストを行うための推奨方法は、**FastAPIの`TestClient`と`lifespan`イベントを活用すること**です。

`v0.1.1`の`APIBuilder`には、アプリケーションの起動・終了時にデータベース接続を適切に管理する`lifespan`イベントが組み込まれています。`pytest`のフィクスチャで`TestClient`をコンテキストマネージャ（`with`文）として使用することで、こ���`lifespan`が自動的に呼び出され、テスト終了後にデータベース接続が確実に破棄されるため、ファイルロック問題を防ぐことができます。

### 3. 動作するテストコード例

以下に、`v0.1.1`で動作する、ファイルベースの一時データベースを使用したテストの最小限のコード例を示します。この方法であれば、インメモリDBを使わずとも、ファイルロックを回避したクリーンなテストが可能です。

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
    """
    テスト用のAPIクライアントを生成するフィクスチャ。
    一時的なデータベースファイルを作成し、テスト終了後にクリーンアップします。
    """
    # 1. 一時的なDBファイルを作成
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    # 2. APIBuilderを初期化
    builder = APIBuilder(
        title="Test API",
        description="A temporary API for testing",
        version="0.1.1",
        db_path=db_path,
    )
    builder.resource("items", Item)

    # 3. TestClientをコンテキストマネージャとして使用
    #    これにより、テスト終了時にlifespanが呼び出され、DB接続が閉じる
    with TestClient(builder.get_app()) as test_client:
        yield test_client

    # 4. テスト終了後に一時ファイルを削除
    os.unlink(db_path)


# --- テスト関数の実装 ---
def test_create_and_get_item(client: TestClient):
    """
    アイテムを作成し、取得できることをテストします。
    """
    # アイテムを作成
    response = client.post("/items/", json={"name": "Test Item"})
    assert response.status_code == 200
    
    created_item = response.json()
    assert created_item["name"] == "Test Item"
    assert "id" in created_item

    # アイテムを取得
    item_id = created_item["id"]
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item"
```

この度は、ドキュメントの不備によりご不便をおかけしましたことを重ねてお詫び申し上げます。
ご指摘いただいたドキュメントの箇所は、直ちに修正いたします。

今後とも`json-api-builder`をよろしくお願いいたします。
