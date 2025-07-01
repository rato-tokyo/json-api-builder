# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-07-01

### Added
- JSONファイルからデータベースを構築するインポート機能 (`JSONImporter`, `import_database_from_json`) を追加。
- PyPI公開用のGitHub Actionsワークフロー (`python-publish.yml`) を追加。
- `pyupgrade`, `vulture` を導入し、CIにコード品質チェックを統合。
- APIの仕様を記述した `docs/api_reference.md` を作成。
- プロジェクトの設計方針を記述した `README.md` のセクションを追加。

### Changed
- データベース接続のライフサイクル管理を改善し、テストの安定性を向上。
- 依存性の注入（DI）の原則に基づき、`JSONExporter` と `JSONImporter` が `Database` オブジェクトを受け取るようにリファクタリング。
- テストフィク���チャを全面的に見直し、クリーンで管理しやすい構造に改善。
- `mypy` の型チェックエラーを、`# type: ignore` を限定的に使用することで解決。

### Removed
- 古いCIワークフロー (`ci.yml`) を削除し、リリース用のワークフローに一本化。
