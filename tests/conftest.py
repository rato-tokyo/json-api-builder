"""
Common test configurations for the application.
"""

import json
import os
import tempfile
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
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
def sample_app_builder() -> Generator[APIBuilder, None, None]:
    """
    Creates a fully configured APIBuilder instance with a temporary database
    and sample data for testing.
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

    # Pre-populate data
    with builder.db.get_db() as session:
        from json_api_builder.models import GenericTable
        session.add(GenericTable(resource_type="items", data='{"name": "Item 1", "description": "desc1", "price": 100}'))
        session.add(GenericTable(resource_type="users", data='{"username": "user1", "email": "a@a.com", "age": 20}'))
        session.commit()

    yield builder

    builder.db.dispose_engine()
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture(scope="function")
def client(sample_app_builder: APIBuilder) -> Generator[TestClient, None, None]:
    """Creates a TestClient and manages the app's lifespan."""
    with TestClient(sample_app_builder.get_app()) as c:
        yield c