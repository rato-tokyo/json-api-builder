"""
Dynamic router generation for API resources.
"""

import json
from collections.abc import Generator
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import crud
from .database import Database


def create_resource_router(
    name: str, model: type[BaseModel], db_provider: Database
) -> APIRouter:
    """Creates a FastAPI router with CRUD endpoints for a given resource."""
    router = APIRouter(prefix=f"/{name}", tags=[name])

    def get_db() -> Generator[Session, None, None]:
        with db_provider.get_db() as session:
            yield session

    @router.post("/", response_model=model)
    async def create_item_endpoint(
        item_data: model,
        db: Session = Depends(get_db),  # type: ignore
    ) -> Any:
        db_item = crud.create_item(db, resource_type=name, item_data=item_data)
        response_data = json.loads(db_item.data)
        response_data["id"] = db_item.id
        return response_data

    @router.get("/", response_model=list[model])
    async def get_items_endpoint(db: Session = Depends(get_db)) -> list[Any]:
        db_items = crud.get_items(db, resource_type=name)
        return [(json.loads(item.data) | {"id": item.id}) for item in db_items]

    @router.get("/{item_id}", response_model=model)
    async def get_item_endpoint(item_id: int, db: Session = Depends(get_db)) -> Any:
        db_item = crud.get_item(db, resource_type=name, item_id=item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        response_data = json.loads(db_item.data)
        response_data["id"] = db_item.id
        return response_data

    @router.put("/{item_id}", response_model=model)
    async def update_item_endpoint(
        item_id: int,
        item_data: model,
        db: Session = Depends(get_db),  # type: ignore
    ) -> Any:
        db_item = crud.get_item(db, resource_type=name, item_id=item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        updated_item = crud.update_item(db, db_item=db_item, item_data=item_data)
        response_data = json.loads(updated_item.data)
        response_data["id"] = updated_item.id
        return response_data

    @router.delete("/{item_id}")
    async def delete_item_endpoint(
        item_id: int, db: Session = Depends(get_db)
    ) -> dict[str, str]:
        db_item = crud.get_item(db, resource_type=name, item_id=item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        crud.delete_item(db, db_item=db_item)
        return {"message": "Item deleted successfully"}

    return router
