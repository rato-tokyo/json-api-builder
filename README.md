# json-api-builder

**SQLModelベースの、シンプルで堅牢なREST API構築ライブラリ**

`json-api-builder` は、[SQLModel](https://sqlmodel.tiangolo.com/) と [FastCRUD](https://github.com/benavlabs/fastcrud) を活用し、最小限のコードで堅牢なREST APIとカスタムエンドポイントを簡単に構築するためのPythonライブラリです。

## 設計思想

-   **究極のシンプルさ**: `SQLModel` でモデルを定義し、`AppBuilder` に渡すだけで、データベースとCRUD操作が可能なAPIエンドポイントが自動生成されます。
-   **高い拡張性**: `add_custom_route` メソッドにより、独自のビジネスロジックや非同期タスクを持つエンドポイントを簡単に追加できます。
-   **ベストプラクティスの活用**: 実績のあるライブラリ群を内部で活用することで、利用者は定型コードを書くことなく、堅牢でモダンなアプリケーションを構築できます。

## 主な機能

-   **CRUD APIの自動生成**: `add_resource` でモデルを追加するだけで、CRUD操作が可能なエンドポイントが利用可能になります。
-   **カスタムルートの追加**: `add_custom_route` で、任意の非同期処理を実行するカスタムAPIエンドポイントを簡単に追加できます。
-   **非同期JSONインポート**: API経由でJSONファイルから非同期にデータをインポートするヘルパー関数 `import_from_json_async` を提供。
-   **自動APIドキュメント**: `/docs` でSwagger UIが利用可能。

詳細は以下のドキュメントを参照してください。
-   [**APIリファレンス**](./docs/api_reference.md)
-   [**データベース��様**](./docs/database.md)

## 使い方

### 1. 基本的なAPIサーバーの構築

`AppBuilder` を使って、モデルからCRUD APIを構築します。

```python
# main.py
from sqlmodel import Field, SQLModel
from json_api_builder import AppBuilder

# モデルを定義
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str

# ビルダーを使ってアプリを構築
builder = AppBuilder(db_path="sqlite+aiosqlite:///database.db")

# CRUDリソースを追加
builder.add_resource(model=Hero, path="/heroes")

# アプリケーションを取得
app = builder.get_app()
```
**サーバーの起動:**
```bash
uvicorn main:app --reload
```

### 2. カスタムエンドポイントの追加

`add_custom_route` を使って、独自のロジックを持つエンドポイントを追加します。例えば、AIへの問い合わせや、特定のバッチ処理を実行するAPIなどを実装できます。

```python
# main.py (続き)
from pydantic import BaseModel

class MyRequest(BaseModel):
    prompt: str

# AIに問い合わせる非同期処理を���義
async def ask_ai(request: MyRequest):
    # ここにLangChainなどのAIライブラリを使った処理を記述
    response_text = f"AI response to '{request.prompt}'"
    # 必要であればDBに結果を保存
    # async with builder.get_session() as session:
    #     ...
    return {"response": response_text}

# カスタムルートとして登録
builder.add_custom_route(
    path="/ask-ai",
    endpoint=ask_ai,
    methods=["POST"],
    tags=["AI"],
)

app = builder.get_app() # 更新されたアプリケーションを取得
```

### 3. (推奨) API経由でのJSONインポート

`import_from_json_async` ヘルパー関数を使い、APIエンドポイント経由で安全にJSONからデータをインポートします。

```python
# main.py (さらに続き)
from json_api_builder import import_from_json_async
from pydantic import BaseModel

class ImportRequest(BaseModel):
    json_path: str

# JSONインポートを実行するエンドポイント
async def import_data(request: ImportRequest):
    # AppBuilderから非同期エンジンを取得してヘルパー関数に渡す
    await import_from_json_async(
        model=Hero, 
        json_path=request.json_path, 
        engine=builder.engine
    )
    return {"message": "Data import started successfully."}

builder.add_custom_route(
    path="/import-from-json",
    endpoint=import_data,
    methods=["POST"],
    tags=["Admin"],
)

app = builder.get_app()
```

### (非推奨) スクリプトからのデータベース生成

`generate_db_from_json_file` は、イベントループの衝突を避けるため、将来のバージョンで削除される予定です。API経由でのインポート（上記参照）を強く推奨します。

```python
# generate_db.py (非推奨)
# ... 以前のコード ...
# この方法は、asyncioのイベントループが既に実行中の環境では
# デッドロックを引き起こす可能性があります。
```

## テスト

```bash
pip install pytest httpx pytest-asyncio
pytest
```
