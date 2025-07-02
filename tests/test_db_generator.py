# tests/test_db_generator.py
import json
import os
import tempfile
from pathlib import Path

import pytest
from sqlmodel import Field, Session, SQLModel, create_engine, select

from json_api_builder import generate_db_from_directory

# --- 1. テスト用のモデル定義 ---
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    name: str

class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: int | None = Field(default=None, primary_key=True)
    title: str
    user_id: int | None = Field(default=None, foreign_key="users.id")

MODELS = [User, Post]

# --- 2. テスト用のセットアップフィクスチャ ---
@pytest.fixture
def temp_db_setup():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test.db")
        json_dir = Path(temp_dir) / "json_data"
        yield db_path, str(json_dir)

# --- 3. テス���ケース ---
def test_generate_from_directory(temp_db_setup):
    db_path, json_dir = temp_db_setup
    
    # Setup JSON files
    (Path(json_dir) / "users").mkdir(parents=True)
    with open(Path(json_dir) / "users" / "1.json", "w") as f:
        json.dump({"name": "Alice"}, f)

    # Generate database
    generate_db_from_directory(
        models=MODELS,
        db_path=db_path,
        input_dir=json_dir,
    )

    # Verify database content
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        assert len(users) == 1
        assert users[0].name == "Alice"
    engine.dispose()
