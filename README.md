# json-api-builder

JSONデータを使ったREST APIサーバーを簡単に構築できるPythonライブラリです。

## 特徴

- 🚀 **簡単セットアップ**: 数行のコードでAPIサーバーを構築
- 📝 **Pydanticベース**: 型安全なPydanticモデルを使用
- 🗄️ **SQLite統合**: 軽量で高性能なSQLiteデータベース
- 📚 **自動ドキュメント**: FastAPIによる自動Swagger UI
- 📥 **データベースダウンロード**: ブラウザからDBファイルをダウンロード可能
- 📤 **JSONエクスポート**: データベースの内容をJSONファイルにエクスポート
- 🔧 **シンプル設計**: 必要最小限の機能で分かりやすい
- ✅ **型安全**: 完全な型ヒント対応
- 🛠️ **ruff統合**: 統一されたコード品質管理

## インストール

```bash
pip install json-api-builder
```

## クイックスタート

```python
from json_api_builder import APIBuilder
from pydantic import BaseModel, Field

class Item(BaseModel):
    id: int | None = None
    name: str = Field(description="アイテム名")
    description: str = Field(description="説明")
    price: float = Field(description="価格", ge=0)

# APIBuilder作成（全パラメータ必須）
builder = APIBuilder(
    title="My API",
    description="シンプルなAPI",
    version="1.0.0",
    db_path="data.db"
)

# リソース登録
builder.resource("items", Item)

# サーバー起動
# ターミナルで `python your_script_name.py` を実行し、
# ブラウザで http://127.0.0.1:8000/docs を開くとAPIドキュメントが確認できます。
if __name__ == "__main__":
    builder.run(host="127.0.0.1", port=8000)
```

これだけで以下のエンドポイントが自動生成されます：

- `POST /items/` - アイテム作成
- `GET /items/` - すべてのアイテム取得
- `GET /items/{id}` - 特定のアイテム取得
- `PUT /items/{id}` - アイテム更新
- `DELETE /items/{id}` - アイテム削除

## 機能

### データベースダウンロード

APIサーバー起動後、以下のエンドポイントにアクセスすることでデータベースに関する情報を取得したり、ファイルをダウンロードしたりできます。

- **`GET /download/info`**: データベースのファイルパス、サイズ、最終更新日時などの情報をJSON形式で返します。
- **`GET /download/database`**: データベースファイル（SQLite）を直接ダウンロードします。

### JSONエクスポート

データベースの内容をJSONファイルとしてエクスポートする機能を提供します。

#### APIBuilderインスタンスを使用する方法

```python
# APIBuilderのインスタンスを作成した後
builder.export_to_json(output_dir="exported_data")
builder.export_resource_to_json(resource_type="items", output_file="exported_data/items.json")
```

#### 関数を直接使用する方法

```python
from json_api_builder import export_database_to_json, export_resource_to_json

# データベース全体をエクスポート
export_database_to_json(db_path="data.db", output_dir="exported_data")

# 特定のリソースをエクスポート
export_resource_to_json(db_path="data.db", resource_type="items", output_file="exported_data/items.json")
```

## API���様

### 自動生成されるエンドポイント

各リソースに対して以下のエンドポイントが自動生成されます：

#### POST /{resource_name}/
- **説明**: 新しいアイテムを作成
- **リクエストボディ**: Pydanticモデルに基づくJSON
- **レスポンス**: 作成されたアイテム（IDを含む）

#### GET /{resource_name}/
- **説明**: すべてのアイテムを取得
- **レスポンス**: アイテムリスト

#### GET /{resource_name}/{id}
- **説明**: 特定のアイテムを取得
- **パスパラメータ**: `id` - アイテムID
- **レスポンス**: アイテムデータまたは404エラー

#### PUT /{resource_name}/{id}
- **説明**: アイテムを更新
- **パスパラメータ**: `id` - アイテムID
- **リクエストボディ**: Pydanticモデルに基づくJSON
- **レスポンス**: 更新されたアイテムまたは404エラー

#### DELETE /{resource_name}/{id}
- **説明**: アイテムを削除
- **パスパラメータ**: `id` - アイテムID
- **レスポンス**: 削除確認メッセージまたは404エラー

### 自動ドキュメント

- **`GET /docs`** - Swagger UI（FastAPI自動生成）
- **`GET /redoc`** - ReDoc（FastAPI自動生成）

## プロジェクト構造

```
json-api-builder/
├── json_api_builder/          # メインパッケージ
│   ├── __init__.py
│   ├── api_builder.py         # APIBuilderクラス
│   ├── crud.py                # CRUD操作
│   ├── database.py            # データベース設定
│   ├── db_download.py         # ダウンロード機能
│   ├── json_export.py         # JSONエクスポート機能
│   ├── models.py              # SQLAlchemyモデル
│   └── router.py              # APIルーター生成
├── examples/                  # 使用例
├── tests/                     # テスト
├── main.py                    # 動作確認用
├── pyproject.toml             # プロジェクト設定・依存関係
├── README.md
└── LICENSE
```

## 開発・テスト

### 開発用インストール

```bash
git clone https://github.com/yourusername/json-api-builder.git
cd json-api-builder
pip install -e .[dev]
```

### テスト実行

```bash
pytest
```

### コード品質チェック

プロジェクトはruffを使用してコード品質を管理しています：

```bash
# リンティングとフォーマットチェック
ruff check .
ruff format . --check

# 自動修正
ruff check . --fix
ruff format .
```

## ライセンス

MIT License
