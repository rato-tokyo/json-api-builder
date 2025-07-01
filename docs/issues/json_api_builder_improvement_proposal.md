### `json-api-builder`のテスト容易性向上のための改善提案

#### 1. 概要

`json-api-builder`は非常に便利なライブラリですが、FastAPIの`TestClient`などを用いて自動テストを実装する際に、いくつかの課題に直面することがあります。
このドキュメントでは、テストの安定性と信頼性を向上させるための具体的な改善策を提案します。

#### 2. 現状の課題

##### 課題1: ファイルベースDB利用時のファイルロック問題

テスト実行時にSQLiteなどのファイルベースのデータベースを使用すると、テストプロセス終了後もデータベースファイルがロックされたままになることがあります。これにより、テスト後のクリーンアップ処理（例: `os.remove(test_db_file)`）が`PermissionError`で失敗し、テストが不安定になる原因となります。

これは、データベース接続が適切にクローズされていないことに起因する典型的な問題です。

##### 課題2: インメモリDB利用時のテーブル自動生成の問題

ファイルロック問題を回避するためにインメモリデータベース（例: `sqlite:///:memory:`）を利用すると、今度は`sqlalchemy.exc.OperationalError: no such table: generic_data`というエラーが発生することがあります。

これは、`APIBuilder`の初期化プロセスにおいて、テーブルスキーマ（`CREATE TABLE`文）が実行されるタイミングが、インメモリDBのライフサイクルと合っていないためだと考えられます。インメモリDBは接続が閉じるたびにデータが消滅するため、テストのセットアップ時に毎回テーブルを確実に作成する仕組みが必要です。

#### 3. 改善提案

上記の課題を解決し、ライブラリのテスト容易性を向上させるために、以下の改善を提案します。

##### 提案1: FastAPIの`lifespan`によるデータベース接続管理

FastAPIの`lifespan`コンテキストマネージャを`APIBuilder`に導入し、アプリケーションの起動時と終了時にデータベース接続の初期化とクローズ処理を明示的に行うようにします。

**期待される効果:**
*   アプリケーション終了時にDB接続が確実にクローズされるため、ファイルロック問題が解消されます。
*   リソース管理がより堅牢になります。

**実装イメージ:**
`APIBuilder`の内部で、FastAPIアプリの`lifespan`を管理します。

```python
# json_api_builder/builder.py (修正イメージ)

from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # アプリケーション起動時の処理
    # (例: DB接続プールの初期化)
    app.state.db_engine = self.engine  # selfはAPIBuilderインスタンス
    yield
    # アプリケーション終了時の処理
    # (例: DB接続プールのクローズ)
    app.state.db_engine.dispose()

class APIBuilder:
    def __init__(self, ..., db_path: str):
        # ...
        self.app = FastAPI(
            title=self.title,
            description=self.description,
            version=self.version,
            lifespan=lifespan  # lifespanを登録
        )
        # ...
```

##### 提案2: `db_engine`引数のサポートとテーブル作成処理の明確化

`APIBuilder`のコンストラクタで、`db_path`文字列の代わりに`sqlalchemy.engine.Engine`のインスタンスを直接受け取れるようにします。

さらに、エンジンが渡された際に、テーブル作成処理（`Base.metadata.create_all(bind=engine)`）が必ず実行されることを保証します。

**期待される効果:**
*   **DI (Dependency Injection) の実現**: 利用者がデータベースエンジンを外部で作成し、`APIBuilder`に注入できるようになります。これにより、テスト時にインメモリDB用のエンジンを簡単に設定できます。
*   **テーブル作成の信頼性向上**: `APIBuilder`の初期化時にテーブルが確実に作成されるため、インメモリDB利用時の`no such table`エラーが解消されます。

**実装イメージ:**

```python
# json_api_builder/builder.py (修正イメージ)
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from typing import Optional

class APIBuilder:
    def __init__(
        self,
        ...,
        db_path: Optional[str] = None,
        db_engine: Optional[Engine] = None
    ):
        if db_engine:
            self.engine = db_engine
        elif db_path:
            self.engine = create_engine(db_path)
        else:
            raise ValueError("Either 'db_path' or 'db_engine' must be provided.")

        # エンジンが設定された直後にテーブルを作成
        self._create_tables_if_not_exist()
        # ...

    def _create_tables_if_not_exist(self):
        # ここでBase.metadata.create_all(self.engine)などを実行する
        pass
```

#### 4. まとめ

これらの改善により、`json-api-builder`利用者は、よりクリーンで安定した自動テストを容易に記述できるようになります。特にインメモリデータベースへの完全な対応は、高速で信頼性の高いテスト環境の構築に不可欠です。
