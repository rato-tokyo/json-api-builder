対象python3.10以上

適宜下記コマンドを実施してコード品質を保ってください。
# 自動整形コマンド
pyupgrade --py310-plus **/*.py
ruff format . --check --quiet
vulture . --min-confidence 80

# コード品質確認コマンド
ruff check --fix . --quiet
Get-ChildItem -Recurse -Filter *.py | ForEach-Object { pyupgrade --py310-plus $_.FullName }
vulture . --min-confidence 80
mypy json_api_builder/ --no-error-summary

ライブラリの情報を得るときは、mcpのcontext7を使って情報を集めることを優先してください。通常のネット検索よりも情報が最新で質が高いためです。






