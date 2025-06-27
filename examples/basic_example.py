#!/usr/bin/env python3
"""
json-api-builder 基本サンプル
"""

from datetime import datetime

from pydantic import BaseModel, Field

from json_api_builder import APIBuilder


# ユーザーモデル
class User(BaseModel):
    id: int | None = None
    name: str = Field(description="ユーザー名")
    email: str = Field(description="メールアドレス")
    created_at: datetime | None = Field(
        default_factory=datetime.now, description="作成日時"
    )


# 投稿モデル
class Post(BaseModel):
    id: int | None = None
    title: str = Field(description="タイトル")
    content: str = Field(description="内容")
    published: bool = Field(default=False, description="公開状態")
    author_id: int | None = Field(description="投稿者ID")
    created_at: datetime | None = Field(
        default_factory=datetime.now, description="作成日時"
    )


def main():
    # APIBuilder作成
    builder = APIBuilder(
        title="ブログAPI",
        description="ユーザーと投稿を管理するAPI",
        version="1.0.0",
        db_path="blog.db",
    )

    # リソース登録
    builder.resource("users", User)
    builder.resource("posts", Post)

    print("🚀 ブログAPIサーバーを起動中...")
    print("📍 URL: http://127.0.0.1:8000")
    print("📚 ドキュメント: http://127.0.0.1:8000/docs")
    print()
    print("📝 利用可能なエンドポイント:")
    print("  - GET    /users/     - ユーザー一覧")
    print("  - POST   /users/     - ユーザー作成")
    print("  - GET    /users/{id} - ユーザー詳細")
    print("  - PUT    /users/{id} - ユーザー更新")
    print("  - DELETE /users/{id} - ユーザー削除")
    print("  - GET    /posts/     - 投稿一覧")
    print("  - POST   /posts/     - 投稿作成")
    print("  - GET    /posts/{id} - 投稿詳細")
    print("  - PUT    /posts/{id} - 投稿更新")
    print("  - DELETE /posts/{id} - 投稿削除")

    # サーバー起動
    builder.run(host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
