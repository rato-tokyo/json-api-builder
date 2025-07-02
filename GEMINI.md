対象python3.10以上

## コード品質の維持について

プロジェクトのコード品質を保つために、コミット前に以下のコマンドを順に実行することを推奨します。
CIでも同様のチェックが実行されます。

### 1. 自動修正とフォーマット

```shell
ruff format . --quiet
pyupgrade --py310-plus **/*.py
vulture . --min-confidence 100
```

### 2. 品質チェック

```shell
ruff check . --fix --quiet
mypy . --no-error-summary
vulture . --min-confidence 100
```

---
### ライブラリ情報の収集について

ライブラリの情報を得るときは、mcpのcontext7を使って情報を集めることを優先してください。通常のネット検索よりも情報が最新で質が高いためです。