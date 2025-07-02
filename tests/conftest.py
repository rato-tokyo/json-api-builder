"""
Common test configurations for the application.
"""

from pydantic import BaseModel, Field


class ItemModel(BaseModel):
    """Test item model."""

    id: int | None = None
    name: str = Field(description="Item Name")
    price: float = Field(description="Price", ge=0)


class UserModel(BaseModel):
    """Test user model."""

    id: int | None = None
    username: str = Field(description="Username")
    age: int = Field(description="Age", ge=0)
