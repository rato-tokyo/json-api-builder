# json-api-builder

**SQLModelベースの、シンプルで堅牢なREST API構築ライブラリ**

`json-api-builder` は、[SQLModel](https://sqlmodel.tiangolo.com/) と [FastCRUD](https://github.com/benavlabs/fastcrud) を活用し、最小限のコードで堅牢なREST APIを簡単に構築するためのPythonライブラリです。

## 設計思想

-   **究極のシンプルさ**: `SQLModel` でモデルを定義し、`AppBuilder` に渡すだけで、データベースとCRUD操作が可能なAPIエンドポイントが自動生成されます。
-   **ベストプラクティスの活用**: 実績のあるライブラリ群を内部で活用することで、利用者は定型コードを書くことなく、堅牢でモダンなアプリケーションを構築できます。

## 主な機能

-   **CRUD APIの自動生成**: `AppBuilder` にモデルを追加するだけで、CRUD操作が可能なエンドポイントが利用可能になります。
-   **柔軟な���キーマ設定**: 作成時と更新時で異なるバリデーションスキーマを適用できます。
-   **JSONからDB生成**: 特定のディレクトリ構造を持つJSONファイル群から、データベースを生成するユーティリティ関数を提供します。
-   **自動APIドキュメント**: `/docs` でSwagger UIが利用可能。

詳細は以下のドキュメントを参照してください。
-   [**APIリファレンス**](./docs/api_reference.md)
-   [**データベース仕様**](./docs/database.md)

## 使い方

### APIサーバーの構築

`AppBuilder` を使って、モデルからAPIを構築します。

```python
# main.py
from sqlmodel import Field, SQLModel
from json_api_builder import AppBuilder

# 1. モデルを定義する
class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

# 作成時用のスキーマ（idは不要）
class HeroCreate(HeroBase):
    pass

# 2. ビルダーを使ってアプリを構築する
builder = AppBuilder(
    db_path="sqlite+aiosqlite:///database.db",
    title="Hero API",
    version="1.0.0"
)

# 3. リソースを追加する
# pathを省略すると、テーブル名から自動的に "/heroes" が設定されます。
builder.add_resource(
    model=Hero,
    create_schema=HeroCreate,
    path="/heroes"
)

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

**IDの決定**:
レコードの `id` は、まずJSONファイル内の `id` フィールドが使われます。もし存在しない場合は、ファイル名（拡張子を除く）が `id` として扱われます。

**形式A: 個別のJSONファイル**
```
json_data/
└── users/                <-- テーブル名 'users'
    ├── 1.json            <-- id: 1
    |   { "name": "Alice" }
    └── 2.json            <-- id: 2
        { "name": "Bob" }
└── posts/
    ├── 101.json
    |   { "title": "First Post", "user_id": 1 }
    └── post_with_id.json <-- id: post_with_id (非推奨)
        { "id": 102, "title": "Second Post", "user_id": 1 }
```

**形式B: `all.json` に全データをまとめる**
`all.json` という名前のファイルに、`id` をキーとするオブジェクトとして全データを記述します。
*注意: `all.json` が存在する場合、同じディレクトリ内の他の `{id}.json` ファイルは無視されます。*
```
json_data/
└── users/
    └── all.json
        {
          "1": { "name": "Alice" },
          "2": { "id": 99, "name": "Bob" }  // "id": 99 が優先される
        }
```

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
    input_dir="json_data",
    overwrite=True  # Trueにすると、実行時に既存のDBファイルを削除
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