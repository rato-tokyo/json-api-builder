#!/usr/bin/env python3
"""
Renderデプロイ用サンプル
"""

import os
from pydantic import BaseModel, Field
from typing import Optional

from json_api_builder import APIBuilder


# データモデル
class Todo(BaseModel):
    id: Optional[int] = None
    title: str = Field(description="タスク名")
    completed: bool = Field(default=False, description="完了状態")


def create_app():
    """Render用のアプリケーション作成関数"""
    # 環境変数からポート取得（Renderで自動設定される）
    port = int(os.environ.get("PORT", 8000))
    
    # APIBuilder作成
    builder = APIBuilder(
        title="Todo API",
        description="シンプルなTodo管理API",
        version="1.0.0",
        db_path=os.environ.get("DATABASE_PATH", "todo.db"),
        cors_origins=["*"]  # 本番環境では適切に設定してください
    )
    
    # リソース登録
    builder.resource("todos", Todo)
    
    return builder.get_app()


def main():
    """ローカル開発用"""
    app = create_app()
    
    print("🚀 Todo APIサーバーを起動中...")
    print("📍 URL: http://127.0.0.1:8000")
    print("📚 ドキュメント: http://127.0.0.1:8000/docs")
    
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


# Render用のアプリケーションインスタンス
app = create_app()

if __name__ == "__main__":
    main() 