"""
Tests for the APIBuilder class.
"""

import os
import tempfile

from fastapi.testclient import TestClient

from json_api_builder import APIBuilder
from tests.conftest import ItemModel, UserModel


def test_api_builder_basic():
    """Tests basic API server creation and endpoint functionality."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    builder = APIBuilder("Test API", "Test Desc", "1.0", db_path)
    builder.resource("items", ItemModel)
    builder.resource("users", UserModel)

    with TestClient(builder.get_app()) as client:
        # Test item creation
        client.post("/items/", json={"name": "Test Item", "price": 10.0})
        response = client.get("/items/")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "Test Item"

        # Test user creation
        client.post("/users/", json={"username": "testuser", "age": 30})
        response = client.get("/users/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    os.unlink(db_path)
