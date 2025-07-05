# データベース仕様

`json-api-builder` は、データベースのテーブルスキーマを、利用者が定義する **`SQLModel`** から動的に生成します。

## 動的なテーブル生成

`AppBuilder` に `add_resource` メソッドでモデルを追加すると、アプリケーションの起動時に、そのモデル定義に基づいてデータベース内にテーブルが自動的に作成されます。

### 例

以下のような `SQLModel` を定義して `builder.add_resource(model=Hero)` のように登録すると、`hero` テーブルが自動生成されます。

```python
from sqlmodel import SQLModel, Field

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
```

| カラム名      | データ型     | 制約・属性         |
|---------------|--------------|--------------------|
| `id`          | `INTEGER`    | プライマリキー, 自動採番 |
| `name`        | `VARCHAR`    | インデックス付き   |
| `secret_name` | `VARCHAR`    |                    |

このアプローチにより、モデル定義が単一の信頼できる情報源となり、開発者はSQLを意識することなく直感的に開発を進められます。

---

## JSONからのデータベース生成

### (推奨) API経由での非同期インポート

イベントループの衝突を避け、安全にデータをインポートするために、APIエンドポイント経由での実行を強く推奨します。

ライブラリは非同期ヘルパー関数 `import_from_json_async` を提供します。これを利用して、カスタムルートを作成できます。

```python
# main.py
from json_api_builder import AppBuilder, import_from_json_async
from pydantic import BaseModel

# ... builderの初期化 ...

class ImportRequest(BaseModel):
    json_path: str

async def import_data_endpoint(request: ImportRequest):
    await import_from_json_async(
        model=Hero, # 対象のモデル
        json_path=request.json_path,
        engine=builder.engine # builderインスタンスのエンジンを渡す
    )
    return {"message": "Data import successful."}

builder.add_custom_route(
    path="/import-data",
    endpoint=import_data_endpoint,
    methods=["POST"],
)
```

この方法では、`import_from_json_async` が以下の処理を行います。
1.  JSONファイル内の各オブジェクトを読み込みます。
2.  オブジェクト内の `id` フィールドは**完全に無視**されます。
3.  `SQLModel` を使ってデータをバリデーションし、インスタンス化します。
4.  インスタンスをデータベースセッションに追加します。このとき、プライマリキーである `id` はデータベースによって**自動的に採番**されます。
5.  すべてのレコードが処理された後、トランザクションがコミットされ、データが永続化されます。

### (非推奨) 同期関数 `generate_db_from_json_file`

この関数は、既存のイベントループと衝突してデッドロックを引き起こす可能性があるため、**非推奨**です。将来のバージョンで削除される予定です。特別な理由がない限り、API経由での非同期インポートを利用してください。