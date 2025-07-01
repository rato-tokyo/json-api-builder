"""
データベースJSONエクスポート機能

データベースファイルを指定したディレクトリにJSONファイルとして展開する機能を提供します。
"""

import json
import os
from pathlib import Path
from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLAlchemy設定（循環インポートを避けるため直接定義）
Base = declarative_base()


class GenericTable(Base):
    """汎用JSONデータ保存テーブル"""

    __tablename__ = "generic_data"

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String(50), index=True, nullable=False)
    data = Column(Text, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class JSONExporter:
    """データベースをJSONファイルに展開するクラス"""

    def __init__(self, db_path: str):
        """
        JSONExporter初期化

        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            echo=False,
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def export_to_json(self, output_dir: str, pretty: bool = True) -> dict[str, Any]:
        """
        データベースの全データをJSONファイルとして展開

        Args:
            output_dir: 出力先ディレクトリ
            pretty: JSONファイルを整形するか

        Returns:
            エクスポート結果の情報

        Raises:
            FileNotFoundError: データベースファイルが見つからない場合
            OSError: 出力ディレクトリの作成に失敗した場合
        """
        # データベースファイルの存在確認
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

        # 出力ディレクトリの作成
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # データベースセッション開始
        db = self.SessionLocal()
        export_info = {
            "database_path": self.db_path,
            "output_directory": str(output_path.absolute()),
            "exported_files": [],
            "resource_counts": {},
            "total_records": 0,
        }

        try:
            # 全データを取得
            all_items = db.query(GenericTable).all()

            # リソースタイプ別にデータを分類
            resources_data: dict[str, list[dict]] = {}

            for item in all_items:
                resource_type = item.resource_type
                if resource_type not in resources_data:
                    resources_data[resource_type] = []

                # JSONデータを解析してIDを追加
                data = json.loads(item.data)
                data["id"] = item.id
                data["created_at"] = item.created_at.isoformat() if item.created_at else None
                data["updated_at"] = item.updated_at.isoformat() if item.updated_at else None

                resources_data[resource_type].append(data)

            # リソースタイプ別にJSONファイルを作成
            for resource_type, items in resources_data.items():
                filename = f"{resource_type}.json"
                file_path = output_path / filename

                # JSONファイルに書き込み
                with open(file_path, "w", encoding="utf-8") as f:
                    if pretty:
                        json.dump(
                            items,
                            f,
                            ensure_ascii=False,
                            indent=2,
                            default=str,
                        )
                    else:
                        json.dump(
                            items,
                            f,
                            ensure_ascii=False,
                            separators=(",", ":"),
                            default=str,
                        )

                export_info["exported_files"].append(filename)
                export_info["resource_counts"][resource_type] = len(items)
                export_info["total_records"] += len(items)

            return export_info

        finally:
            db.close()
            self.engine.dispose()

    def export_resource_to_json(
        self, resource_type: str, output_file: str, pretty: bool = True
    ) -> dict[str, Any]:
        """
        特定のリソースタイプのデータをJSONファイルとして出力

        Args:
            resource_type: エクスポートするリソースタイプ
            output_file: 出力ファイルパス
            pretty: JSONファイルを整形するか

        Returns:
            エクスポート結果の情報

        Raises:
            FileNotFoundError: データベースファイルが見つからない場合
            ValueError: 指定されたリソースタイプが存在しない場合
        """
        # データベースファイルの存在確認
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

        # 出力ファイルのディレクトリを作成
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # データベースセッション開始
        db = self.SessionLocal()
        export_info = {
            "database_path": self.db_path,
            "resource_type": resource_type,
            "output_file": str(output_path.absolute()),
            "record_count": 0,
        }

        try:
            # 特定のリソースタイプのデータを取得
            items = (
                db.query(GenericTable)
                .filter(GenericTable.resource_type == resource_type)
                .all()
            )

            if not items:
                raise ValueError(f"No data found for resource type: {resource_type}")

            # データを整形
            export_data = []
            for item in items:
                data = json.loads(item.data)
                data["id"] = item.id
                data["created_at"] = item.created_at.isoformat() if item.created_at else None
                data["updated_at"] = item.updated_at.isoformat() if item.updated_at else None
                export_data.append(data)

            # JSONファイルに書き込み
            with open(output_path, "w", encoding="utf-8") as f:
                if pretty:
                    json.dump(
                        export_data,
                        f,
                        ensure_ascii=False,
                        indent=2,
                        default=str,
                    )
                else:
                    json.dump(
                        export_data,
                        f,
                        ensure_ascii=False,
                        separators=(",", ":"),
                        default=str,
                    )

            export_info["record_count"] = len(export_data)
            return export_info

        finally:
            db.close()
            self.engine.dispose()


def export_database_to_json(
    db_path: str, output_dir: str, pretty: bool = True
) -> dict[str, Any]:
    """
    データベースファイルをJSONファイルとして展開（関数版）

    Args:
        db_path: データベースファイルのパス
        output_dir: 出力先ディレクトリ
        pretty: JSONファイルを整形するか

    Returns:
        エクスポート結果の情報

    Example:
        >>> result = export_database_to_json("my_data.db", "./json_output")
        >>> print(f"Exported {result['total_records']} records to {len(result['exported_files'])} files")
    """
    exporter = JSONExporter(db_path)
    return exporter.export_to_json(output_dir, pretty)


def export_resource_to_json(
    db_path: str, resource_type: str, output_file: str, pretty: bool = True
) -> dict[str, Any]:
    """
    特定のリソースタイプをJSONファイルとして出力（関数版）

    Args:
        db_path: データベースファイルのパス
        resource_type: エクスポートするリソースタイプ
        output_file: 出力ファイルパス
        pretty: JSONファイルを整形するか

    Returns:
        エクスポート結果の情報

    Example:
        >>> result = export_resource_to_json("my_data.db", "items", "./items.json")
        >>> print(f"Exported {result['record_count']} items")
    """
    exporter = JSONExporter(db_path)
    return exporter.export_resource_to_json(resource_type, output_file, pretty) 