#!/usr/bin/env python3
"""
json-api-builder 動作確認用スクリプト（シンプル版）
"""

import json
import os
import tempfile

from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from json_api_builder import APIBuilder


# テスト用データモデル
class Item(BaseModel):
    id: int | None = None
    name: str = Field(description="アイテム名")
    description: str = Field(description="説明")
    price: float = Field(description="価格", ge=0)


def main():
    """メイン処理"""
    print("🚀 json-api-builder 動作確認開始")

    # 一時データベースファイル作成
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    try:
        # APIBuilder作成
        builder = APIBuilder(
            title="動作確認API",
            description="json-api-builderの動作確認用API",
            version="1.0.0",
            db_path=db_path,
        )

        # リソース登録
        builder.resource("items", Item)

        # ダウンロード機能を追加
        builder.add_db_download_endpoint()

        # TestClient作成
        client = TestClient(builder.get_app())

        print("✅ API初期化完了")

        # 1. アイテム作成
        item_data = {
            "name": "テストアイテム",
            "description": "これはテスト用のアイテムです",
            "price": 1000,
        }
        response = client.post("/items/", json=item_data)
        print(f"📝 アイテム作成: {response.status_code}")
        print(f"   データ: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

        item_id = response.json()["id"]

        # 2. アイテム取得
        response = client.get(f"/items/{item_id}")
        print(f"📖 アイテム取得: {response.status_code}")
        print(f"   データ: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

        # 3. アイテム一覧取得
        response = client.get("/items/")
        print(f"📋 アイテム一覧: {response.status_code}")
        print(f"   データ: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

        # 4. アイテム更新
        updated_data = {
            "name": "更新されたアイテム",
            "description": "更新されました",
            "price": 1500,
        }
        response = client.put(f"/items/{item_id}", json=updated_data)
        print(f"✏️ アイテム更新: {response.status_code}")
        print(f"   データ: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

        # 5. ダウンロード情報確認
        response = client.get("/download/info")
        print(f"📥 ダウンロード情報: {response.status_code}")
        print(f"   データ: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

        # 6. アイテム削除
        response = client.delete(f"/items/{item_id}")
        print(f"🗑️ アイテム削除: {response.status_code}")
        print(f"   データ: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

        print("✅ 動作確認完了！")
        print("💡 ダウンロードエンドポイント: /download/database")

    except Exception as e:
        print(f"❌ エラー: {e}")

    finally:
        # データベース接続をクローズ
        if "builder" in locals():
            builder.engine.dispose()

        # 一時ファイル削除
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except PermissionError:
            pass


if __name__ == "__main__":
    main()
