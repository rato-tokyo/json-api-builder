#!/usr/bin/env python3
"""
データベースダウンロード機能のサンプル
"""

from pydantic import BaseModel, Field

from json_api_builder import APIBuilder


# データモデル
class Item(BaseModel):
    id: int | None = None
    name: str = Field(description="アイテム名")
    description: str = Field(description="説明")
    price: float = Field(description="価格", ge=0)


def main():
    # APIBuilder作成
    builder = APIBuilder(
        title="ダウンロード機能付きAPI",
        description="データベースダウンロード機能を持つAPI",
        version="1.0.0",
        db_path="download_test.db",
    )

    # リソース登録
    builder.resource("items", Item)

    # データベースダウンロード機能を追加
    # 認証なしバージョン
    builder.add_db_download_endpoint()

    # 認証ありバージョン（コメントアウト）
    # builder.add_db_download_endpoint(
    #     endpoint_path="/download/database-secure",
    #     require_auth=True,
    #     auth_token="my-secret-token-123"
    # )

    print("🚀 ダウンロード機能付きAPIサーバーを起動中...")
    print("📍 URL: http://127.0.0.1:8000")
    print("📚 ドキュメント: http://127.0.0.1:8000/docs")
    print()
    print("📥 ダウンロードエンドポイント:")
    print("  - http://127.0.0.1:8000/download/database")
    print("  - http://127.0.0.1:8000/download/info (情報表示)")
    print()
    print("💡 使用方法:")
    print("  1. まずアイテムを作成してください:")
    print("     curl -X POST http://127.0.0.1:8000/items/ \\")
    print('       -H "Content-Type: application/json" \\')
    print(
        '       -d \'{"name": "テストアイテム", "description": "テスト", "price": 100}\''
    )
    print()
    print("  2. ブラウザで以下にアクセスしてダウンロード:")
    print("     http://127.0.0.1:8000/download/database")

    # サーバー起動
    builder.run(host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
