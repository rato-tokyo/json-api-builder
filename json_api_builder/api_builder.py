"""
json-api-builder: シンプルなAPIビルダー

SQLAlchemy + FastAPI + Pydanticの標準的な組み合わせを使用した
シンプルで確実に動作するAPIビルダー。
"""

import json
from datetime import datetime

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Query
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from typing import Annotated

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
        async def get_items(db: Session = Depends(get_db), **filters):
            # FastAPIのRequestからクエリパラメータを取得
            def get_query_params(request: Request):
                return dict(request.query_params)

            # 実際のエンドポイント
            async def inner_get_items(
                db: Session = Depends(get_db),
                request: Request = Depends(Request),
            ):
                query_params = dict(request.query_params)
                db_items = db.query(GenericTable).filter(GenericTable.resource_type == name).all()
                items = []
                for db_item in db_items:
                    data = json.loads(db_item.data)
                    data["id"] = db_item.id
                    # フィルタ適用
                    match = True
                    for k, v in query_params.items():
                        if k not in data:
                            match = False
                            break
                        # null文字列はNone判定
                        if v == "null":
                            if data[k] is not None:
                                match = False
                                break
                        else:
                            # 型変換（int, float, bool, str）
                            field_type = model.model_fields[k].annotation if k in model.model_fields else str
                            try:
                                if field_type is int:
                                    v_cast = int(v)
                                elif field_type is float:
                                    v_cast = float(v)
                                elif field_type is bool:
                                    v_cast = v.lower() in ("true", "1", "yes")
                                else:
                                    v_cast = v
                            except Exception:
                                v_cast = v
                            if data[k] != v_cast:
                                match = False
                                break
                    if match:
                        items.append(model(**data))
                return items
            return await inner_get_items(db)

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
