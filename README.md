# json-api-builder

JSONデータを使ったREST APIサーバーを簡単に構築できるPythonライブラリです。 

## 特徴

- 🚀 **簡単セットアップ**: 数行のコードでAPIサーバーを構築
- 📝 **Pydanticベース**: 型安全なPydanticモデルを使用
- 🗄️ **SQLite統合**: 軽量で高性能なSQLiteデータベース
- 📚 **自動ドキュメント**: FastAPIによる自動Swagger UI
- 📥 **データベースダウンロード**: ブラウザからDBファイルをダウンロード可能
- 🔧 **シンプル設計**: 必要最小限の機能で分かりやすい
- ✅ **型安全**: 完全な型ヒント対応

## インストール

```bash
pip install json-api-builder
```

## 基本的な使用方法

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
builder.run(host="127.0.0.1", port=8000)
```

これだけで以下のエンドポイントが自動生成されます：

- `POST /items/` - アイテム作成
- `GET /items/` - すべてのアイテム取得
- `GET /items/{id}` - 特定のアイテム取得
- `PUT /items/{id}` - アイテム更新
- `DELETE /items/{id}` - アイテム削除

## データベースダウンロード機能

データベースファイルをブラウザからダウンロードできる機能を提供します。

```python
from json_api_builder import APIBuilder
from pydantic import BaseModel, Field

class Item(BaseModel):
    id: int | None = None
    name: str = Field(description="アイテム名")
    price: float = Field(description="価格", ge=0)

builder = APIBuilder(
    title="ダウンロード機能付きAPI",
    description="データベースダウンロード機能を持つAPI",
    version="1.0.0",
    db_path="my_data.db"
)

builder.resource("items", Item)

# ダウンロード機能を追加
builder.add_db_download_endpoint()

# 認証付きダウンロード（オプション）
builder.add_db_download_endpoint(
    endpoint_path="/download/secure",
    require_auth=True,
    auth_token="your-secret-token"
)

builder.run()
```

### ダウンロードエンドポイント

- **`GET /download/database`** - データベースファイルをダウンロード
- **`GET /download/info`** - データベース情報を表示
- **`GET /download/secure?token=xxx`** - 認証付きダウンロード

### ブラウザでの使用

1. サーバーを起動
2. ブラウザで `http://localhost:8000/download/database` にアクセス
3. タイムスタンプ付きのファイル名でダウンロードされます

## API仕様

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

## 設定オプション

### APIBuilder初期化

```python
builder = APIBuilder(
    title="My API",                # APIタイトル（必須）
    description="API説明",          # API説明（必須）
    version="1.0.0",              # APIバージョン（必須）
    db_path="./data.db"           # データベースファイルパス（必須）
)
```

### サーバー起動

```python
builder.run(
    host="127.0.0.1",             # サーバーホスト（デフォルト: 127.0.0.1）
    port=8000,                    # サーバーポート（デフォルト: 8000）
    reload=True                   # 開発用自動リロード（デフォルト: False）
)
```

## 使用例

### 基本的なCRUD操作

```python
from json_api_builder import APIBuilder
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int | None = None
    name: str = Field(description="ユーザー名")
    email: str = Field(description="メールアドレス")
    age: int = Field(description="年齢", ge=0, le=150)

builder = APIBuilder(
    title="User Management API",
    description="ユーザー管理API",
    version="1.0.0",
    db_path="users.db"
)

builder.resource("users", User)
builder.run()
```

### 複数リソースの管理

```python
from json_api_builder import APIBuilder
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int | None = None
    name: str = Field(description="ユーザー名")
    email: str = Field(description="メールアドレス")

class Post(BaseModel):
    id: int | None = None
    title: str = Field(description="タイトル")
    content: str = Field(description="本文")
    user_id: int = Field(description="ユーザーID")

builder = APIBuilder(
    title="Blog API",
    description="ブログAPI",
    version="1.0.0",
    db_path="blog.db"
)

# 複数のリソースを登録
builder.resource("users", User)
builder.resource("posts", Post)

# ダウンロード機能も追加
builder.add_db_download_endpoint()

builder.run()
```

## プロジェクト構造

```
json-api-builder/
├── json_api_builder/          # メインパッケージ
│   ├── __init__.py
│   ├── api_builder.py         # メインクラス
│   └── db_download.py         # ダウンロード機能
├── examples/                  # 使用例
│   ├── basic_example.py
│   ├── simple_example.py
│   ├── render_example.py
│   └── download_example.py
├── tests/                     # テスト
├── main.py                    # 動作確認用
├── pyproject.toml            # プロジェクト設定
├── README.md
└── LICENSE
```

## 開発・テスト

### 開発用インストール

```bash
git clone https://github.com/yourusername/json-api-builder.git
cd json-api-builder
pip install -e .
```

### テスト実行

```bash
python -m pytest tests/
```

### コード品質チェック

```bash
ruff check .
ruff format .
```

### 使用例実行

```bash
# 基本例
python examples/basic_example.py

# シンプル例
python examples/simple_example.py

# ダウンロード機能例
python examples/download_example.py

# 動作確認
python main.py
```

## 技術仕様

### 依存関係

- **FastAPI**: 高性能なWeb APIフレームワーク
- **Pydantic**: データバリデーションと設定管理
- **SQLAlchemy**: SQLデータベースツールキット
- **Uvicorn**: ASGI サーバー
- **python-multipart**: フォームデータ処理

### データベース

- **SQLite**: ファイルベースの軽量データベース
- 自動テーブル作成
- 自動マイグレーション
- トランザクション対応

### セキュリティ

- Pydanticによる入力検証
- SQLインジェクション対策
- オプション認証機能（ダウンロード）

## よくある質問

### Q: メモリ内データベースは使用できますか？
A: 現在はファイルベースのSQLiteのみサポートしています。

### Q: 認証機能はありますか？
A: データベースダウンロード機能でのみ、シンプルなトークン認証を提供しています。

### Q: 本番環境で使用できますか？
A: 小規模なアプリケーションや開発環境での使用を想定しています。

## ライセンス

MIT License

## 貢献

プルリクエストやイシューの報告を歓迎します。

## サポート

- ドキュメント: [GitHub Repository](https://github.com/yourusername/json-api-builder)
- イシュー: [GitHub Issues](https://github.com/yourusername/json-api-builder/issues)