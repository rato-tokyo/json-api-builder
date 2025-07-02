### `json-api-builder` v0.1.1のテストに関する問い合わせ

#### 1. 背景

`json-api-builder`を利用するアプリケーションで、`pytest`とインメモリデータベース（`sqlite://`）を使用した自動テストの構築を目指しています。

#### 2. 確認したドキュメント

`json-api-builder` v0.1.1に同梱されている`docs/json-api-builder/api_reference.md`を確認しました。
このドキュメントのセクション4「テストの容易性のための改善」には、`APIBuilder`のコンストラクタが`db_engine`というキーワード引数をサポートし、インメモリDBでのテストが容易になったと記載されています。

**ドキュメント記載のコード例:**
```python
engine = create_engine("sqlite:///:memory:")
builder = APIBuilder(
    ...,
    db_engine=engine  # ドキュメントで示されている利用方法
)
```

#### 3. 直面している問題

実際に`json-api-builder==0.1.1`をインストールした環境で上記のコードを実行す���と、以下の`TypeError`が発生します。

```
TypeError: APIBuilder.__init__() got an unexpected keyword argument 'db_engine'
```

`help(APIBuilder)`で確認したところ、v0.1.1の`APIBuilder`のコンストラクタシグネチャは `__init__(self, title: str, description: str, version: str, db_path: str)` であり、`db_engine`引数が存在しないことが分かりました。

#### 4. 開発者様への質問・提供依頼情報

ドキュメントと実際の挙動に差異があるようですので、以下の情報をご提供いただけますでしょうか。

1.  **`db_engine`引数の実装状況について**:
    *   この機能はv0.1.1で意図されたものでしょうか？それとも、将来のバージョンで実装予定の機能がドキュメントに先行して記載されているのでしょうか？

2.  **v0.1.1での推奨テスト方法について**:
    *   `db_engine`引数が利用できない場合、v0.1.1でインメモリデータベースを使用したテストを実装するための、現在の推奨方法はありますでしょうか？

3.  **動作するテストコード例**:
    *   もし可能であれば、`json-api-builder==0.1.1`と`pytest`を使用して、インメモリデータベースで動作する最小限のテストフィクスチャのコード例をご教示いただけると大変助かります。

この`db_engine`機能は、ファイルロックを回避し、高速で安定したテストを実現するために不可欠だと考えております。
お忙しいところ恐縮ですが、ご確認いただけますと幸いです。
