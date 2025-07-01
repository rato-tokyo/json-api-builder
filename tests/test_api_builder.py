"""
APIBuilder simplified tests.
"""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from json_api_builder import APIBuilder


class Item(BaseModel):
    id: int | None = None
    name: str
    description: str
    price: float


@pytest.fixture(scope="function")
def temp_db():
    """Provides a temporary database path and ensures cleanup."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name
    yield db_path
    if os.path.exists(db_path):
        os.unlink(db_path)


def test_basic_functionality(temp_db):
    """Tests basic CRUD functionality."""
    builder = APIBuilder(
        title="Test", description="Test", version="1.0", db_path=temp_db
    )
    builder.resource("items", Item)
    client = TestClient(builder.get_app())

    try:
        item_data = {"name": "test", "description": "test item", "price": 100.0}
        response = client.post("/items/", json=item_data)
        assert response.status_code == 200
        created_item = response.json()
        assert "id" in created_item
        item_id = created_item["id"]

        response = client.get(f"/items/{item_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "test"

        response = client.get("/items/")
        assert response.status_code == 200
        assert len(response.json()) == 1

        update_data = {"name": "updated", "description": "updated", "price": 200.0}
        response = client.put(f"/items/{item_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["name"] == "updated"

        response = client.delete(f"/items/{item_id}")
        assert response.status_code == 200

        response = client.get(f"/items/{item_id}")
        assert response.status_code == 404
    finally:
        builder.db.engine.dispose()


def test_model_validation(temp_db):
    """Tests that the builder validates models correctly."""
    builder = APIBuilder(
        title="Test", description="Test", version="1.0", db_path=temp_db
    )
    try:

        class InvalidModel:
            pass

        with pytest.raises(ValueError):
            builder.resource("invalid", InvalidModel)
    finally:
        builder.db.engine.dispose()


def test_multiple_resources(temp_db):
    """Tests functionality with multiple registered resources."""
    builder = APIBuilder(
        title="Test", description="Test", version="1.0", db_path=temp_db
    )

    class User(BaseModel):
        id: int | None = None
        name: str
        email: str

    builder.resource("items", Item)
    builder.resource("users", User)
    client = TestClient(builder.get_app())

    try:
        client.post(
            "/items/", json={"name": "item1", "description": "desc1", "price": 1.0}
        )
        client.post("/users/", json={"name": "user1", "email": "user1@test.com"})

        response = client.get("/items/")
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.get("/users/")
        assert response.status_code == 200
        assert len(response.json()) == 1
    finally:
        builder.db.engine.dispose()
