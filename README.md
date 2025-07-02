# json-api-builder

**SQLModelベースの、シンプルで堅牢なREST API構築ライブラリ**

`json-api-builder` は、[SQLModel](https://sqlmodel.tiangolo.com/) と [FastCRUD](https://github.com/benavlabs/fastcrud) を活用し、最小限のコードで堅牢なREST APIを簡単に構築するためのPythonライブラリです。

## 設計思想

-   **究極のシンプルさ**: `SQLModel` でモデルを定義し、`AppBuilder` に渡すだけで、データベースとCRUD操作が可能なAPIエンドポイントが自動生成されます。
-   **ベストプラクティスの活用**: 実績のあるライブラリ群を内部で活用することで、利用者は定型コードを書くことなく、堅牢でモダンなアプリケーションを構築できます。

## 主な機能

-   **CRUD APIの自動生成**: `AppBuilder` にモデルを追加するだけで、CRUD操作が可能なエンドポイントが利用可能になります。
-   **JSONからDB生成**: 特定のディレクトリ構造を持つJSONファイル群から、データベースを生成するユーティリティ関数を提供します。
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

# 4. アプリケーションを取得する
app = builder.get_app()
```
**サーバーの起動:**
```bash
uvicorn main:app --reload
```

### JSONからのデータベース生成

`generate_db_from_directory` 関数は、特定のディレクトリ構造からデータベースを生成します。

#### 1. フォルダとファイルの準備

`input_dir` として指定するディレクトリ（例: `json_data`）の直下に、**テーブル名と同じ名前のサブディレクトリ**を作成します。その中に、JSONファイルを用意します。

**形式A: ファイル名がIDとなる個別のJSONファイル**

各JSONファイルには、`id` を除くレコードのデータを含めます。`id` はファイル名から自動的に割り当てられます。

```
json_data/
└── users/                <-- テーブル名 'users'
    ├── 1.json
    |   { "name": "Alice" }
    └── 2.json
        { "name": "Bob" }
└── posts/                <-- テーブル名 'posts'
    ├── 101.json
    |   { "title": "First Post", "user_id": 1 }
    └── 102.json
        { "title": "Second Post", "user_id": 1 }
```

**形式B: `all.json` に全データをまとめる**

`all.json` という名前のファイルに、`id` をキーとするオブジェクトとして全データを記述します。

```
json_data/
└── users/                <-- テーブル名 'users'
    └── all.json
        {
          "1": { "name": "Alice" },
          "2": { "name": "Bob" }
        }
```
*注意: `all.json` が存在する場合、同じディレクトリ内の他の `{id}.json` ファイルは無視されます。*

#### 2. 生成スクリプトの作成

```python
# generate_db.py
from sqlmodel import Field, SQLModel
from json_api_builder import generate_db_from_directory

# データベースに対応するモデルを定義
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    name: str

# 生成関数を呼び出す
generate_db_from_directory(
    models=[User],
    db_path="generated_database.db",
    input_dir="json_data", # 上で準備したディレクトリ
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
