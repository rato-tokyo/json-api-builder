# json-api-builder

JSONデータ保存に特化したFastAPI サーバーを簡単に構築できるPythonライブラリです。

## 特徴

- 🚀 **簡単セットアップ**: 数行のコードでAPIサーバーを構築
- 📝 **Pydanticベース**: 事前定義されたPydanticモデルを使用
- 🗄️ **SQLite統合**: 軽量で高性能なSQLiteデータベース
- 🔧 **カスタマイズ可能**: バリデーター、トランスフォーマー、カスタムエンドポイント
- 📚 **自動ドキュメント**: FastAPIによる自動Swagger UI
- 🌐 **Render対応**: 本番環境デプロイ対応
- ✅ **型安全**: 完全な型ヒント対応

## インストール

```bash
pip install json-api-builder
```

## 基本的な使用方法

```python
from json_api_builder import APIBuilder
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str

builder = APIBuilder()
builder.resource('items', model=Item)
builder.serve()
```

これだけで以下のエンドポイントが自動生成されます：

- `POST /items` - アイテム作成
- `GET /items` - すべてのアイテム取得
- `GET /items/{id}` - 特定のアイテム取得
- `PUT /items/{id}` - アイテム更新
- `DELETE /items/{id}` - アイテム削除
- `GET /health` - ヘルスチェック

## 詳細な使用例

### カスタムバリデーターとトランスフォーマー

```python
from json_api_builder import APIBuilder
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    age: int
    created_at: Optional[datetime] = None

builder = APIBuilder(db_path="./data.db")
builder.resource('users', model=User)

# カスタムバリデーター
@builder.validator('users')
def validate_user(user: User):
    if user.age < 0:
        raise ValueError('年齢は0以上である必要があります')
    return True

# カスタムトランスフォーマー
@builder.transformer('users')
def transform_user(user: User):
    user.created_at = datetime.now()
    user.email = user.email.lower()
    return user

# カスタムエンドポイント
@builder.route('/stats', methods=['GET'])
def get_stats():
    return {'total_users': 100, 'timestamp': datetime.now().isoformat()}

builder.serve(host='0.0.0.0', port=8000)
```

### Renderデプロイ用設定

```python
from json_api_builder import APIBuilder
from pydantic import BaseModel
import os

class Item(BaseModel):
    name: str
    description: str
    price: float

builder = APIBuilder(
    db_path=os.getenv("DATABASE_URL", "./data.db"),
    host="0.0.0.0",
    port=int(os.getenv("PORT", 10000))
)

builder.resource('items', model=Item)

# Renderで起動するためのapp取得
app = builder.get_app()

if __name__ == '__main__':
    builder.serve()
```

## API仕様

### 自動生成されるエンドポイント

各リソースに対して以下のエンドポイントが自動生成されます：

#### POST /{resource_name}
- **説明**: 新しいアイテムを作成
- **リクエストボディ**: Pydanticモデルに基づくJSON
- **レスポンス**: 作成されたアイテム（IDとタイムスタンプを含む）

#### GET /{resource_name}
- **説明**: すべてのアイテムを取得
- **クエリパラメータ**:
  - `skip`: スキップする件数（デフォルト: 0）
  - `limit`: 取得する最大件数（デフォルト: 100、最大: 1000）
- **レスポンス**: アイテムリスト、総数、ページネーション情報

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

### 標準エンドポイント

#### GET /health
- **説明**: ヘルスチェック
- **レスポンス**: サーバーとデータベースの状態

#### GET /docs
- **説明**: Swagger UI（FastAPI自動生成）
- **レスポンス**: インタラクティブなAPIドキュメント

## カスタマイズ機能

### バリデーター

```python
@builder.validator('resource_name')
def custom_validator(item: YourModel):
    # カスタムバリデーションロジック
    if some_condition:
        raise ValueError('エラーメッセージ')
    return True
```

### トランスフォーマー

```python
@builder.transformer('resource_name')
def custom_transformer(item: YourModel):
    # データ変換ロジック
    item.field = transform_value(item.field)
    return item
```

### カスタムエンドポイント

```python
@builder.route('/custom-endpoint', methods=['GET', 'POST'])
def custom_endpoint():
    return {'message': 'カスタムエンドポイント'}
```

## 設定オプション

```python
builder = APIBuilder(
    db_path="./data.db",           # データベースファイルパス
    title="My API",                # APIタイトル
    description="API説明",          # API説明
    version="1.0.0",              # APIバージョン
    host="127.0.0.1",             # サーバーホスト
    port=8000                     # サーバーポート
)
```

## エラーハンドリング

ライブラリは以下のエラーを適切にハンドリングします：

- **バリデーションエラー** (400): 入力データの検証失敗
- **リソース未発見** (404): 指定されたリソースが存在しない
- **データ変換エラー** (500): トランスフォーマーでのエラー
- **データベースエラー** (500): データベース操作でのエラー

## 開発・テスト

### 開発用インストール

```bash
git clone https://github.com/yourusername/json-api-builder.git
cd json-api-builder
pip install -e .
pip install -e ".[dev]"
```

### テスト実行

```bash
pytest tests/
```

### 使用例実行

```bash
# 基本例
python examples/basic_example.py

# シンプル例
python examples/simple_example.py

# Render例
python examples/render_example.py
```

## ライセンス

MIT License

## 貢献

プルリクエストやイシューの報告を歓迎します。

## サポート

- ドキュメント: [GitHub Wiki](https://github.com/yourusername/json-api-builder/wiki)
- イシュー: [GitHub Issues](https://github.com/yourusername/json-api-builder/issues)
- ディスカッション: [GitHub Discussions](https://github.com/yourusername/json-api-builder/discussions)