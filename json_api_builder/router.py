"""
Dynamic router generation for API resources.
"""

import json
from collections.abc import Callable, Generator
from contextlib import AbstractContextManager
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .models import GenericTable


def create_resource_router(
    name: str,
    model: type[BaseModel],
    get_db_cm: Callable[[], AbstractContextManager[Session]],
) -> APIRouter:
    """Creates a FastAPI router with CRUD endpoints for a given resource."""
    router = APIRouter(prefix=f"/{name}", tags=[name])

    def get_db() -> Generator[Session, None, None]:
        with get_db_cm() as session:
            yield session

    @router.post("/", response_model=model)
    async def create_item(item_data: model, db: Session = Depends(get_db)) -> Any:  # type: ignore
        data_dict = item_data.model_dump(exclude={"id"})
        db_item = GenericTable(
            resource_type=name,
            data=json.dumps(data_dict, default=str, ensure_ascii=False),
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        response_data = json.loads(db_item.data)
        response_data["id"] = db_item.id
        return response_data

    @router.get("/", response_model=list[model])
    async def get_items(db: Session = Depends(get_db)) -> list[Any]:
        db_items = db.query(GenericTable).filter_by(resource_type=name).all()
        return [(json.loads(item.data) | {"id": item.id}) for item in db_items]

    @router.get("/{item_id}", response_model=model)
    async def get_item(item_id: int, db: Session = Depends(get_db)) -> Any:
        db_item = (
            db.query(GenericTable).filter_by(resource_type=name, id=item_id).first()
        )
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        response_data = json.loads(db_item.data)
        response_data["id"] = db_item.id
        return response_data

    @router.put("/{item_id}", response_model=model)
    async def update_item(
        item_id: int, item_data: model, db: Session = Depends(get_db)
    ) -> Any:  # type: ignore
        db_item = (
            db.query(GenericTable).filter_by(resource_type=name, id=item_id).first()
        )
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        data_dict = item_data.model_dump(exclude={"id"})
        db_item.data = json.dumps(data_dict, default=str, ensure_ascii=False)
        db.commit()
        db.refresh(db_item)
        response_data = json.loads(db_item.data)
        response_data["id"] = db_item.id
        return response_data

    @router.delete("/{item_id}")
    async def delete_item(
        item_id: int, db: Session = Depends(get_db)
    ) -> dict[str, str]:
        db_item = (
            db.query(GenericTable).filter_by(resource_type=name, id=item_id).first()
        )
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        db.delete(db_item)
        db.commit()
        return {"message": "Item deleted successfully"}

    return router
