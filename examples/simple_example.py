#!/usr/bin/env python3
"""
json-api-builder シンプルサンプル
"""

from pydantic import BaseModel, Field
from typing import Optional

from json_api_builder import APIBuilder


# データモデル定義
class Item(BaseModel):
    id: Optional[int] = None
    name: str = Field(description="アイテム名")
    description: str = Field(description="アイテムの説明")
    price: float = Field(description="価格")


def main():
    # APIBuilder作成
    builder = APIBuilder(
        title="シンプルAPI",
        description="PydanticベースのシンプルなAPI",
        db_path="simple.db"
    )
    
    # リソース登録
    builder.resource("items", Item)
    
    print("🚀 シンプルAPIサーバーを起動中...")
    print("📍 URL: http://127.0.0.1:8000")
    print("📚 ドキュメント: http://127.0.0.1:8000/docs")
    
    # サーバー起動
    builder.run(reload=True)


if __name__ == "__main__":
    main() 