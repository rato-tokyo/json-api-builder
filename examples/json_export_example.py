#!/usr/bin/env python3
"""
JSON展開機能のサンプル

データベースファイルをJSONファイルとして展開する機能のデモンストレーション
"""

import json
import os
import tempfile
from pathlib import Path

from pydantic import BaseModel, Field

from json_api_builder import (
    APIBuilder,
    export_database_to_json,
    export_resource_to_json,
)


# データモデル
class Item(BaseModel):
    id: int | None = None
    name: str = Field(description="アイテム名")
    description: str = Field(description="説明")
    price: float = Field(description="価格", ge=0)
    category: str = Field(description="カテゴリ")


class User(BaseModel):
    id: int | None = None
    username: str = Field(description="ユーザー名")
    email: str = Field(description="メールアドレス")
    age: int = Field(description="年齢", ge=0)
    is_active: bool = Field(description="アクティブ状態", default=True)


def create_sample_data():
    """サンプルデータを作成"""
    # 一時データベースファイル作成
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    print(f"📄 データベースファイル作成: {db_path}")

    # APIBuilder作成
    builder = APIBuilder(
        title="JSON展開サンプルAPI",
        description="JSON展開機能のデモンストレーション用API",
        version="1.0.0",
        db_path=db_path,
    )

    # リソース登録
    builder.resource("items", Item)
    builder.resource("users", User)

    # サンプルデータを追加
    from json_api_builder.api_builder import GenericTable

    db = builder.SessionLocal()
    try:
        # アイテムデータ
        items_data = [
            {
                "name": "ノートパソコン",
                "description": "高性能なビジネス用ノートパソコン",
                "price": 120000.0,
                "category": "電子機器",
            },
            {
                "name": "マウス",
                "description": "ワイヤレスマウス",
                "price": 3000.0,
                "category": "電子機器",
            },
            {
                "name": "コーヒー豆",
                "description": "エチオピア産の高級コーヒー豆",
                "price": 2500.0,
                "category": "食品",
            },
            {
                "name": "本",
                "description": "プログラミング入門書",
                "price": 3500.0,
                "category": "書籍",
            },
        ]

        for data in items_data:
            db_item = GenericTable(
                resource_type="items",
                data=json.dumps(data, ensure_ascii=False),
            )
            db.add(db_item)

        # ユーザーデータ
        users_data = [
            {
                "username": "alice",
                "email": "alice@example.com",
                "age": 28,
                "is_active": True,
            },
            {
                "username": "bob",
                "email": "bob@example.com",
                "age": 35,
                "is_active": True,
            },
            {
                "username": "charlie",
                "email": "charlie@example.com",
                "age": 22,
                "is_active": False,
            },
        ]

        for data in users_data:
            db_user = GenericTable(
                resource_type="users",
                data=json.dumps(data, ensure_ascii=False),
            )
            db.add(db_user)

        db.commit()
        print("✅ サンプルデータ作成完了")

    finally:
        db.close()
        builder.engine.dispose()

    return db_path


def demo_json_export():
    """JSON展開機能のデモ"""
    print("🚀 JSON展開機能デモ開始")
    print("=" * 50)

    # サンプルデータベース作成
    db_path = create_sample_data()

    try:
        # 出力ディレクトリ作成
        output_dir = Path("./json_output")
        output_dir.mkdir(exist_ok=True)

        print(f"📁 出力ディレクトリ: {output_dir.absolute()}")
        print()

        # 1. 関数を使った全データ展開
        print("1️⃣ 全データをJSON展開（関数版）")
        result = export_database_to_json(db_path, str(output_dir))

        print(f"   データベース: {result['database_path']}")
        print(f"   出力先: {result['output_directory']}")
        print(f"   エクスポートファイル: {result['exported_files']}")
        print(f"   リソース別レコード数: {result['resource_counts']}")
        print(f"   総レコード数: {result['total_records']}")
        print()

        # 2. 特定リソースのみ展開
        print("2️⃣ 特定リソース（items）のみ展開")
        items_file = output_dir / "items_only.json"
        result = export_resource_to_json(db_path, "items", str(items_file))

        print(f"   リソースタイプ: {result['resource_type']}")
        print(f"   出力ファイル: {result['output_file']}")
        print(f"   レコード数: {result['record_count']}")
        print()

        # 3. APIBuilderを使った展開
        print("3️⃣ APIBuilderを使った展開")
        builder = APIBuilder(
            title="デモAPI",
            description="JSON展開デモ",
            version="1.0.0",
            db_path=db_path,
        )

        try:
            # 全データ展開（整形なし）
            compact_dir = output_dir / "compact"
            result = builder.export_to_json(str(compact_dir), pretty=False)
            print(f"   コンパクト版出力: {compact_dir.absolute()}")
            print(f"   総レコード数: {result['total_records']}")

            # 特定リソース展開
            users_file = output_dir / "users_from_api.json"
            result = builder.export_resource_to_json("users", str(users_file))
            print(f"   ユーザーファイル: {users_file.absolute()}")
            print(f"   レコード数: {result['record_count']}")

        finally:
            builder.engine.dispose()

        print()

        # 4. 生成されたファイルの内容確認
        print("4️⃣ 生成されたファイルの内容確認")

        # アイテムファイルの確認
        items_json_file = output_dir / "items.json"
        if items_json_file.exists():
            with open(items_json_file, encoding="utf-8") as f:
                items_data = json.load(f)
            print(f"   📋 items.json: {len(items_data)}件のアイテム")
            print(
                f"      最初のアイテム: {items_data[0]['name']} (¥{items_data[0]['price']:,})"
            )

        # ユーザーファイルの確認
        users_json_file = output_dir / "users.json"
        if users_json_file.exists():
            with open(users_json_file, encoding="utf-8") as f:
                users_data = json.load(f)
            print(f"   👥 users.json: {len(users_data)}人のユーザー")
            active_users = [u for u in users_data if u["is_active"]]
            print(f"      アクティブユーザー: {len(active_users)}人")

        print()
        print("✅ JSON展開デモ完了！")
        print(f"📁 出力ファイルは {output_dir.absolute()} に保存されました")

        # ファイル一覧表示
        print("\n📄 生成されたファイル一覧:")
        for file_path in sorted(output_dir.rglob("*.json")):
            file_size = file_path.stat().st_size
            print(f"   {file_path.relative_to(output_dir)} ({file_size:,} bytes)")

    except Exception as e:
        print(f"❌ エラー: {e}")

    finally:
        # データベースファイル削除
        if os.path.exists(db_path):
            os.unlink(db_path)
            print(f"🗑️ 一時データベースファイル削除: {db_path}")


if __name__ == "__main__":
    demo_json_export()
