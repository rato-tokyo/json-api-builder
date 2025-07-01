"""
json-api-builder: シンプルなAPIビルダー

SQLAlchemy + FastAPI + Pydanticの標準的な組み合わせを使用した
シンプルで確実に動作するAPIビルダー。
"""

import json
from datetime import datetime
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .db_download import DBDownloadMixin, add_download_info_endpoint

# SQLAlchemy設定
Base = declarative_base()


class GenericTable(Base):
    """汎用JSONデータ保存テーブル"""

    __tablename__ = "generic_data"

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String(50), index=True, nullable=False)
    data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class APIBuilder(DBDownloadMixin):
    """シンプルなAPIビルダー"""

    def __init__(self, title: str, description: str, version: str, db_path: str):
        self.title = title
        self.description = description
        self.version = version
        self.db_path = db_path

        # データベース設定（ファイルベースSQLiteのみ）
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            echo=False,
        )

        # テーブル作成
        Base.metadata.create_all(bind=self.engine)

        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # FastAPIアプリ作成
        self.app = FastAPI(
            title=title,
            description=description,
            version=version,
        )

        # 登録されたモデル
        self.models: dict[str, type[BaseModel]] = {}

        # ダウンロード情報エンドポイントを追加
        add_download_info_endpoint(self.app, db_path)

    def _validate_model(self, model: type[BaseModel]) -> None:
        """モデル検証"""
        if not issubclass(model, BaseModel):
            raise ValueError("Model must be a Pydantic BaseModel subclass")

    def resource(self, name: str, model: type[BaseModel]) -> None:
        """リソースエンドポイント登録"""
        self._validate_model(model)

        # モデル登録
        self.models[name] = model

        # プレフィックス設定
        prefix = f"/{name}"

        # 依存性注入用のDB取得関数
        def get_db():
            db = self.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        # CREATE - アイテム作成
        @self.app.post(f"{prefix}/", response_model=model)
        async def create_item(item_data: model, db: Session = Depends(get_db)):
            # IDを除外したデータを取得
            data_dict = item_data.model_dump(exclude={"id"})

            # データベースに保存
            db_item = GenericTable(
                resource_type=name,
                data=json.dumps(data_dict, default=str, ensure_ascii=False),
            )
            db.add(db_item)
            db.commit()
            db.refresh(db_item)

            # レスポンス用にIDを追加
            response_data = data_dict.copy()
            response_data["id"] = db_item.id

            return model(**response_data)

        # READ - アイテム一覧取得
        @self.app.get(f"{prefix}/", response_model=list[model])
        async def get_items(db: Session = Depends(get_db)):
            db_items = (
                db.query(GenericTable).filter(GenericTable.resource_type == name).all()
            )
            items = []
            for db_item in db_items:
                data = json.loads(db_item.data)
                data["id"] = db_item.id
                items.append(model(**data))
            return items

        # READ - アイテム詳細取得
        @self.app.get(f"{prefix}/{{item_id}}", response_model=model)
        async def get_item(item_id: int, db: Session = Depends(get_db)):
            db_item = (
                db.query(GenericTable)
                .filter(GenericTable.id == item_id, GenericTable.resource_type == name)
                .first()
            )

            if not db_item:
                raise HTTPException(status_code=404, detail="Item not found")

            data = json.loads(db_item.data)
            data["id"] = db_item.id

            return model(**data)

        # UPDATE - アイテム更新
        @self.app.put(f"{prefix}/{{item_id}}", response_model=model)
        async def update_item(
            item_id: int, item_data: model, db: Session = Depends(get_db)
        ):
            db_item = (
                db.query(GenericTable)
                .filter(GenericTable.id == item_id, GenericTable.resource_type == name)
                .first()
            )

            if not db_item:
                raise HTTPException(status_code=404, detail="Item not found")

            # IDを除外したデータを取得
            data_dict = item_data.model_dump(exclude={"id"})

            # データ更新
            db_item.data = json.dumps(data_dict, default=str, ensure_ascii=False)
            db_item.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(db_item)

            # レスポンス用にIDを追加
            response_data = data_dict.copy()
            response_data["id"] = db_item.id

            return model(**response_data)

        # DELETE - アイテム削除
        @self.app.delete(f"{prefix}/{{item_id}}")
        async def delete_item(item_id: int, db: Session = Depends(get_db)):
            db_item = (
                db.query(GenericTable)
                .filter(GenericTable.id == item_id, GenericTable.resource_type == name)
                .first()
            )

            if not db_item:
                raise HTTPException(status_code=404, detail="Item not found")

            db.delete(db_item)
            db.commit()

            return {"message": "Item deleted successfully"}

    def get_app(self) -> FastAPI:
        """FastAPIアプリ取得"""
        return self.app

    def run(self, host: str, port: int, reload: bool = False) -> None:
        """サーバー起動"""
        uvicorn.run(self.app, host=host, port=port, reload=reload)

    def export_to_json(self, output_dir: str, pretty: bool = True) -> dict[str, Any]:
        """
        データベースの全データをJSONファイルとして展開

        Args:
            output_dir: 出力先ディレクトリ
            pretty: JSONファイルを整形するか

        Returns:
            エクスポート結果の情報
        """
        # 遅延インポートで循環インポートを回避
        from .json_export import JSONExporter
        
        exporter = JSONExporter(self.db_path)
        return exporter.export_to_json(output_dir, pretty)

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
        """
        # 遅延インポートで循環インポートを回避
        from .json_export import JSONExporter
        
        exporter = JSONExporter(self.db_path)
        return exporter.export_resource_to_json(resource_type, output_file, pretty)
