"""
Common test configurations for the application.
"""

import json
import os
import tempfile

import pytest
from pydantic import BaseModel, Field

from json_api_builder import APIBuilder


class ItemModel(BaseModel):
    """Test item model."""

    id: int | None = None
    name: str = Field(description="Item Name")
    description: str = Field(description="Description")
    price: float = Field(description="Price", ge=0)


class UserModel(BaseModel):
    """Test user model."""

    id: int | None = None
    username: str = Field(description="Username")
    email: str = Field(description="Email")
    age: int = Field(description="Age", ge=0)


@pytest.fixture(scope="function")
def sample_app_builder():
    """
    Creates a fully configured APIBuilder instance with a temporary database
    and sample data for testing.
    This fixture is responsible for the entire lifecycle, including cleanup.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    builder = APIBuilder(
        title="Test API",
        description="API for testing",
        version="1.0.0",
        db_path=db_path,
    )
    builder.resource("items", ItemModel)
    builder.resource("users", UserModel)

    db = builder.db
    with db.get_db() as session:
        from json_api_builder.models import GenericTable

        item_data = [
            {"name": "Item 1", "description": "First item", "price": 1000.0},
            {"name": "Item 2", "description": "Second item", "price": 2000.0},
            {"name": "Item 3", "description": "Third item", "price": 1500.0},
        ]
        for data in item_data:
            db_item = GenericTable(
                resource_type="items",
                data=json.dumps(data, ensure_ascii=False),
            )
            session.add(db_item)

        user_data = [
            {"username": "user1", "email": "user1@example.com", "age": 25},
            {"username": "user2", "email": "user2@example.com", "age": 30},
        ]
        for data in user_data:
            db_user = GenericTable(
                resource_type="users",
                data=json.dumps(data, ensure_ascii=False),
            )
            session.add(db_user)

        session.commit()

    yield builder

    # Cleanup: Dispose the engine and remove the temp database file
    builder.db.engine.dispose()
    if os.path.exists(db_path):
        os.unlink(db_path)
