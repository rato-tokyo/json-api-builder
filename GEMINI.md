対象python3.10以上

## コード品質の維持について

プロジェクトのコード品質を保つために、コミット前に以下のコマンドを順に実行することを推奨します。
CIでも同様のチェックが実行されます。

### 1. 自動修正とフォーマット

```shell
# ruffによるリントエラーの自動修正
ruff check . --fix

# ruffによるコードフォーマット
ruff format .
```

### 2. Python構文のアップグレード

```shell
# Python 3.10以降の構文にアップグレード
pyupgrade --py310-plus json_api_builder/ tests/ examples/ main.py
```

### 3. 品質チェック

```shell
# 未使用コードの検出
vulture . --min-confidence 80

# 型チェック
mypy json_api_builder/
```
---
### ライブラリ情報の収集について

ライブラリの情報を得るときは、mcpのcontext7を使って情報を集めることを優先してください。通常のネット検索よりも情報が最新で質が高いためです。