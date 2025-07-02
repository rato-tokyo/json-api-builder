## 開発環境
- **OS**: Windows 11
- **Shell**: PowerShell 7.5

---

## コード品質を維持するための推奨手順

コミットする前に、以下のコマンドをすべて実行し、エラーが発生しないことを確認してください。これにより、CIワークフローの失敗を防ぐことができます。

**注記**: コンテキストの消費を抑えるため、不要なログ出力を減らす`--quiet`フラグなどの使用を推奨します。

### 1. 自動修正とフォーマット
```shell
# ruffによるリントエラーの自動修正とコードフォーマット（静かに実行）
ruff check . --fix --quiet
ruff format . --quiet
```

### 2. Python構文のアップグレード
PowerShell環境では、以下のコマンドを実行してください。
```powershell
# Python 3.10以降の構文にアップグレード
Get-ChildItem -Recurse -Filter *.py | ForEach-Object { pyupgrade --py310-plus $_.FullName }
```

### 3. 品質チェック
```shell
# 未使用コードの検出
vulture . --min-confidence 80

# 型チェック
mypy json_api_builder/
```
---
## Gitのコミットについて

コミットメッセージは、シェルの解釈による予期せぬトラブルを避けるため、常に一文で完結させてください。

**良い例:**
```shell
git commit -m "feat: 新しい機能を追加"
```

---
### ライブラリ情報の収集について

ライブラリの情報を得るときは、mcpのcontext7を使って情報を集めることを優先してください。通常のネット検索よりも情報が最新で質が高いためです。
