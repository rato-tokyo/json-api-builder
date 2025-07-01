# json-api-builder

JSONデータを使ったREST APIサーバーを簡単に構築できるPythonライブラリです。

## 特徴

- 🚀 **簡単セットアップ**: 数行のコードでAPIサーバーを構築
- 📝 **Pydanticベース**: 型安全なPydanticモデルを使用
- 🗄️ **SQLite統合**: 軽量で高性能なSQLiteデータベース
- 📚 **自動ドキュメント**: FastAPIによる自動Swagger UI
- 📥 **データベースダウンロード**: ブラウザからDBファイルをダウンロード可能
- 🔄 **JSONインポート/エクスポート**: データベースとJSONファイル間でデータを相互に変換

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

# APIBuilder作成
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

## 機能

### JSONエクスポート

データベースの内容をJSONファイルとしてエクスポートします。

**APIBuilderインスタンスを使用する方法:**
```python
# 全リソースをディレクトリにエクスポート
builder.export_to_json(output_dir="exported_data")

# 特定のリソースをファイルにエクスポート
builder.export_resource_to_json(resource_type="items", output_file="items.json")
```

**関数を直接使用する方法:**
```python
from json_api_builder import export_database_to_json

export_database_to_json(db_path="data.db", output_dir="exported_data")
```

### JSONインポート

JSONファイル（またはそれらを含むディレクトリ）からデータベースを構築します。

```python
from json_api_builder import import_database_from_json

# ディレクトリ内の全JSONファイルをインポート
# overwrite=True にすると、既存のデータベースはクリアされます
import_database_from_json(
    db_path="new_data.db",
    input_dir="exported_data",
    overwrite=True
)
```

### データベースダウンロード

APIサーバー起動後、以下のエンドポイントにアクセスすることでデータベースに関する情報を取得したり、ファイルをダウンロードしたりできます。

- **`GET /download/info`**: データベースのファイルパス、サイズ、最終更新日時などの情報をJSON形式で返します。
- **`GET /download/database`**: データベースファイル（SQLite）を直接ダウンロードします。

## 設計方針と妥当性

本ライブラリは、シンプルさと安定性を最優先に設計されています。過去のバージョンで発生した問題を解決し、より堅牢なアーキテクチャを採用する��めに、以下の設計方針を確立しました。

1.  **明確な責務の分離 (Separation of Concerns)**
    - **方針**: `APIBuilder` はAPIの構築、`JSONExporter`/`Importer` はデータの入出力、`Database` は接続管理、というように各コンポーネントの責務を明確に分けています。
    - **妥当性**: これにより、各機能が独立して動作し、変更やデバッグが容易になります。例えば、データベースの接続方法を変更する場合、`Database` クラスのみを修正すればよく、他の部分への影響を最小限に抑えられます。

2.  **依存性の注入 (Dependency Injection)**
    - **方針**: `JSONExporter` や `JSONImporter` のようなクラスは、データベースのパス（文字列）を直接受け取るのではなく、初期化済みの `Database` オブジェクトを外部から受け取ります。
    - **妥当性**: これにより、データベース接続の生成と破棄のライフサイクル管理が、呼び出し元（アプリケーションのメインロジックやテストコード）に一元化されます。結果として、リ��ースの競合による `PermissionError` のような実行時エラーを防ぎ、安定性が大幅に向上しました。また、テスト時にモックオブジェクトを注入しやすくなり、テストの信頼性と保守性が高まります。

3.  **一貫したAPI設計**
    - **方針**: データベースセッションを取得する `Database.get_db()` は、Pythonで標準的なコンテキストマネージャ（`with`文で使う形式）として統一されています。
    - **妥当性**: これにより、ライブラリ全体でデータベースセッションの扱い方が一貫し、開発者が使い方を推測しやすくなりました。FastAPIのDI（依存性注入）で必要なジェネレータ形式への変換は、`router.py` 内部でアダプタパターンを用いて吸収しており、ライブラリの利用者や他のコンポーネントに複雑さを感じさせないように配慮しています。

これらの設計方針は、過去のイテレーションで発生した「ファイルがロックされる」「APIの挙動が不安定になる」といった問題を根本的に解決するためのものです。一度はこの方針から外れたことで問題が再発しましたが、最終的にこの堅牢な設計に戻すことで、現在の安定したバージョンが実現されています。

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

## ライセンス

MIT License