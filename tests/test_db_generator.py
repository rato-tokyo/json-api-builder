# tests/test_db_generator.py
import json
import shutil
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import Field, SQLModel, Session, create_engine, select

from json_api_builder import (
    generate_db_from_json_file,
    import_from_json_async,
)


# --- 1. テスト用のモデル定義 ---
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    age: int


# --- 2. ヘルパー関数 ---
def setup_test_environment(artifacts_dir_name="test_artifacts"):
    artifacts_dir = Path(__file__).parent / artifacts_dir_name
    artifacts_dir.mkdir(exist_ok=True)
    db_path = artifacts_dir / "test.db"
    json_path = artifacts_dir / "users.json"
    return artifacts_dir, db_path, json_path


def create_test_json(json_path, data):
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def cleanup_test_environment(artifacts_dir):
    shutil.rmtree(artifacts_dir, ignore_errors=True)


# --- 3. テストケース ---
@pytest.mark.asyncio
async def test_import_from_json_async():
    artifacts_dir, db_path, json_path = setup_test_environment("async_test")
    create_test_json(
        json_path,
        [
            {"name": "Alice", "age": 30},
            {"id": 99, "name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35},
        ],
    )
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")

    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        await import_from_json_async(model=User, json_path=json_path, engine=engine)

        async with AsyncSession(engine) as session:
            result = await session.execute(select(User).order_by(User.id))
            users = result.scalars().all()
            assert len(users) == 3
            assert users[1].name == "Bob"
    finally:
        await engine.dispose()
        cleanup_test_environment(artifacts_dir)


def test_generate_db_from_json_file_deprecated():
    artifacts_dir, db_path, json_path = setup_test_environment("deprecated_test")
    create_test_json(
        json_path,
        [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}],
    )

    try:
        with pytest.warns(DeprecationWarning):
            generate_db_from_json_file(
                model=User, db_path=db_path, json_path=json_path, overwrite=True
            )

        engine = create_engine(f"sqlite:///{db_path}")
        with Session(engine) as session:
            users = session.exec(select(User).order_by(User.id)).all()
            assert len(users) == 2
            assert users[1].name == "Bob"
        engine.dispose()
    finally:
        cleanup_test_environment(artifacts_dir)


def test_generate_from_invalid_json():
    artifacts_dir, db_path, json_path = setup_test_environment("invalid_json_test")
    create_test_json(json_path, {"1": {"name": "Alice"}})

    try:
        with pytest.raises(TypeError, match="JSON file must contain a list of records."):
            with pytest.warns(DeprecationWarning):
                generate_db_from_json_file(
                    model=User, db_path=db_path, json_path=json_path
                )
    finally:
        cleanup_test_environment(artifacts_dir)
