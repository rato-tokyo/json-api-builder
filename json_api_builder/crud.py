"""
CRUD operations for the GenericTable model.
"""

import json
from typing import Type

from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import models


def create_item(
    db: Session, resource_type: str, item_data: BaseModel
) -> models.GenericTable:
    """Creates a new item in the database."""
    data_dict = item_data.model_dump(exclude={"id"})
    db_item = models.GenericTable(
        resource_type=resource_type,
        data=json.dumps(data_dict, default=str, ensure_ascii=False),
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_items(db: Session, resource_type: str) -> list[models.GenericTable]:
    """Retrieves all items of a specific resource type."""
    return db.query(models.GenericTable).filter_by(resource_type=resource_type).all()


def get_item(db: Session, resource_type: str, item_id: int) -> models.GenericTable | None:
    """Retrieves a single item by its ID and resource type."""
    return (
        db.query(models.GenericTable)
        .filter_by(resource_type=resource_type, id=item_id)
        .first()
    )


def update_item(
    db: Session, db_item: models.GenericTable, item_data: BaseModel
) -> models.GenericTable:
    """Updates an existing item in the database."""
    data_dict = item_data.model_dump(exclude={"id"})
    db_item.data = json.dumps(data_dict, default=str, ensure_ascii=False)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, db_item: models.GenericTable) -> None:
    """Deletes an item from the database."""
    db.delete(db_item)
    db.commit()
