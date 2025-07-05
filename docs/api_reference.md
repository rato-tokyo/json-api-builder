# APIリファレンス

`json-api-builder` は、`AppBuilder` クラスを通じてAPIを構築します。

---

## CRUDリソースの登録 `add_resource`

`builder.add_resource()` メソッドでリソースを登録すると、標準的なCRUD操作のためのエンドポイントが自動的に作成されます。

```python
builder.add_resource(
    model: type[SQLModel],
    create_schema: type[SQLModel] | None = None,
    update_schema: type[SQLModel] | None = None,
    path: str | None = None,
)
```

-   **`model`**: データベースとAPIの基本となる `SQLModel` クラス。
-   **`create_schema`**: (任意) アイテム作成時に使用するバリデーションスキーマ。
-   **`update_schema`**: (任意) アイテム更新時に使用するバリデーションスキーマ。
-   **`path`**: (任意) エンドポイントのURLパス。デフォルトはモデルのテーブル名から自動生成されます。

---

## カスタムルートの登録 `add_custom_route`

`builder.add_custom_route()` を使うと、CRUD以外の独自のAPIエンドポイントを自由に追加できます。

```python
builder.add_custom_route(
    path: str,
    endpoint: Callable[..., Any],
    methods: list[str] | None = None,
    **kwargs: Any,
)
```

-   **`path`**: エンドポイントのURLパス（例: `/my-custom-action`）。
-   **`endpoint`**: リクエストを処理する非同期関数。
-   **`methods`**: HTTPメソッドのリスト（例: `["POST"]`）。
-   **`**kwargs`**: FastAPIの `add_api_route` に渡す追加の引数（例: `tags=["Custom"]`）。

---

## 自動生成されるCRUDエンドポイント

`builder.add_resource(model=Hero, path="/heroes")` のようにリソースを登録した場合の例です。

### `POST /heroes/`

新しいアイテムを作成します。

-   **リクエストボディ**: `create_schema` に基づくJSONオブジェクト。
-   **成功レスポンス (`200 OK`)**: 作成されたアイテムのデータ。

---

### `GET /heroes/`

アイテムのリストを取得します。フィルタリングとページネーションに対応しています。

-   **クエリパラメータ**:
    -   **フィルタリング**: モデルのフィールド名（例: `?age=30`）。
    -   **ページネーション**: `limit` と `offset`。
-   **成功レスポンス (`200 OK`)**: `data`（アイテムリスト）と `total`（総件数）を含むオブジェクト。

---

### `GET /heroes/{item_id}`

指定されたIDのアイテムを1件取得します。

-   **成功レスポンス (`200 OK`)**: 対応するアイテムのデータ。
-   **エラーレスポンス (`404 Not Found`)**: アイテムが存在しない場合。

---

### `PATCH /heroes/{item_id}`

指定されたIDのアイテムを部分的に更新します。

-   **リクエストボディ**: `update_schema` に基づくJSONオブジェクト。
-   **成功レスポンス (`200 OK`)**: 更新後のアイテムデータ。

---

### `DELETE /heroes/{item_id}`

指定されたIDのアイテムを削除します。

-   **成功レスポンス (`200 OK`)**: 削除されたアイテムのデータ。
