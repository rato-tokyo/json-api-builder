# json-api-builder

**SQLModelベースの、シンプルで堅牢なREST API構築ライブラリ**

`json-api-builder` は、[SQLModel](https://sqlmodel.tiangolo.com/) と [FastCRUD](https://github.com/benavlabs/fastcrud) を活用し、最小限のコードで堅牢なREST APIを簡単に構築するためのPythonライブラリです。

## 設計思想

-   **究極のシンプルさ**: `SQLModel` でモデルを定義し、`AppBuilder` に渡すだけで、データベースとCRUD操作が可能なAPIエンドポイントが自動生成されます。
-   **ベストプラクティスの活用**: 実績のあるライブラリ群を内部で活用することで、利用者は定型コードを書くことなく、堅牢でモダンなアプリケーションを構築できます。

## 主な機能

-   **CRUD APIの自動生成**: `AppBuilder` にモデルを追加するだけで、CRUD操作が可能なエンドポイントが利用可能になります。
-   **JSONから���DB生成**: 特定のディレクトリ構造を持つJSONファイル群から、データベースを生成するユーティリティ関数を提供します。
-   **自動APIドキュメント**: `/docs` でSwagger UIが利用可能。

詳細は��以下のドキュメントを参照してください。
-   [**APIリファレンス**](./docs/api_reference.md)
-   [**データベース仕様**](./docs/database.md)

## 使い方

### APIサーバーの構築

`main.py` を作成し、以下のコードを記述します。

```python
# main.py
from sqlmodel import Field, SQLModel
from json_api_builder import AppBuilder

# 1. モデルを定義する
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

# 2. ビルダーを使ってアプリを構築する
builder = AppBuilder(
    db_path="sqlite+aiosqlite:///database.db",
    title="Hero API",
    version="1.0.0"
)

# 3. リソースを追加する
builder.add_resource(model=Hero, path="/heroes")

# 4. アプリケーションを���得する
app = builder.get_app()
```
**サーバーの起動:**
```bash
uvicorn main:app --reload
```

### JSONからのデータベース生成

`generate_db.py` を作成し、以下のコードを記述します。

```python
# generate_db.py
from sqlmodel import Field, SQLModel
from json_api_builder import generate_db_from_directory

# 1. データベースに対応するモデルを定義
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    name: str

# 2. 生成関数を呼���出す
generate_db_from_directory(
    models=[User],
    db_path="generated_database.db",
    input_dir="path/to/your/json_data",
    overwrite=True
)

print("✅ データベースの生成が完了しました。")
```
**実行:**
```bash
python generate_db.py
```

## Renderへのデプロイ

（...Renderへのデプロイガイドは変更なし...）

## テスト

```bash
pip install pytest httpx pytest-asyncio
pytest
```