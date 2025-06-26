"""
json-api-builder: シンプルなAPIビルダー

SQLAlchemy + FastAPI + Pydanticの標準的な組み合わせを使用した
シンプルで確実に動作するAPIビルダー。
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool


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


class APIBuilder:
    """シンプルなAPIビルダー"""
    
    def __init__(
        self,
        title: str = "JSON API",
        description: str = "JSON API built with json-api-builder",
        version: str = "1.0.0",
        db_path: str = "data.db",
        cors_origins: Optional[List[str]] = None,
    ):
        self.title = title
        self.description = description
        self.version = version
        self.cors_origins = cors_origins or []
        
        # データベース設定
        if db_path == ":memory:":
            # メモリ内データベースの場合、接続を共有
            self.engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            self.engine = create_engine(
                f"sqlite:///{db_path}",
                connect_args={"check_same_thread": False},
                echo=False
            )
        
        # テーブル作成（先に作成）
        Base.metadata.create_all(bind=self.engine)
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # FastAPIアプリ作成
        self.app = FastAPI(
            title=title,
            description=description,
            version=version,
        )
        
        # CORS設定
        if self.cors_origins:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=self.cors_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # 登録されたモデル
        self.models: Dict[str, Type[BaseModel]] = {}
        
        # ヘルスチェックエンドポイント
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy"}
    
    def get_db(self) -> Session:
        """データベースセッション取得"""
        db = self.SessionLocal()
        try:
            return db
        finally:
            db.close()
    
    def _validate_model(self, model: Type[BaseModel]) -> None:
        """モデル検証"""
        if not issubclass(model, BaseModel):
            raise ValueError("Model must be a Pydantic BaseModel subclass")
    
    def resource(
        self,
        name: str,
        model: Type[BaseModel],
        prefix: Optional[str] = None,
    ) -> None:
        """リソースエンドポイント登録"""
        self._validate_model(model)
        
        # モデル登録
        self.models[name] = model
        
        # プレフィックス設定
        if prefix is None:
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
            try:
                # IDを除外したデータを取得
                data_dict = item_data.model_dump(exclude={"id"})
                
                # データベースに保存
                db_item = GenericTable(
                    resource_type=name,
                    data=json.dumps(data_dict, default=str, ensure_ascii=False)
                )
                db.add(db_item)
                db.commit()
                db.refresh(db_item)
                
                # レスポンス用にIDを追加
                response_data = data_dict.copy()
                response_data["id"] = db_item.id
                
                return model(**response_data)
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=str(e))
        
        # READ - アイテム一覧取得
        @self.app.get(f"{prefix}/", response_model=List[model])
        async def get_items(db: Session = Depends(get_db)):
            try:
                db_items = db.query(GenericTable).filter(
                    GenericTable.resource_type == name
                ).all()
                
                items = []
                for db_item in db_items:
                    data = json.loads(db_item.data)
                    data["id"] = db_item.id
                    items.append(model(**data))
                
                return items
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # READ - アイテム詳細取得
        @self.app.get(f"{prefix}/{{item_id}}", response_model=model)
        async def get_item(item_id: int, db: Session = Depends(get_db)):
            try:
                db_item = db.query(GenericTable).filter(
                    GenericTable.id == item_id,
                    GenericTable.resource_type == name
                ).first()
                
                if not db_item:
                    raise HTTPException(status_code=404, detail="Item not found")
                
                data = json.loads(db_item.data)
                data["id"] = db_item.id
                
                return model(**data)
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # UPDATE - アイテム更新
        @self.app.put(f"{prefix}/{{item_id}}", response_model=model)
        async def update_item(
            item_id: int,
            item_data: model,
            db: Session = Depends(get_db)
        ):
            try:
                db_item = db.query(GenericTable).filter(
                    GenericTable.id == item_id,
                    GenericTable.resource_type == name
                ).first()
                
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
            except HTTPException:
                raise
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=str(e))
        
        # DELETE - アイテム削除
        @self.app.delete(f"{prefix}/{{item_id}}")
        async def delete_item(item_id: int, db: Session = Depends(get_db)):
            try:
                db_item = db.query(GenericTable).filter(
                    GenericTable.id == item_id,
                    GenericTable.resource_type == name
                ).first()
                
                if not db_item:
                    raise HTTPException(status_code=404, detail="Item not found")
                
                db.delete(db_item)
                db.commit()
                
                return {"message": "Item deleted successfully"}
            except HTTPException:
                raise
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(e))
    
    def get_app(self) -> FastAPI:
        """FastAPIアプリ取得"""
        return self.app
    
    def run(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        reload: bool = False,
        **kwargs
    ) -> None:
        """サーバー起動"""
        uvicorn.run(self.app, host=host, port=port, reload=reload, **kwargs)
