# tests/test_db_generator.py
import json
import shutil
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
def test_artifacts_setup():
    # テスト成果物用のディレクトリを tests 配下に作成
    artifacts_dir = Path(__file__).parent / "test_artifacts"
    artifacts_dir.mkdir(exist_ok=True)

    db_path = artifacts_dir / "test.db"
    json_dir = artifacts_dir / "json_data"

    # クリーンアップのために、テスト開始前に既存のファイルを削除
    if db_path.exists():
        db_path.unlink()
    if json_dir.exists():
        shutil.rmtree(json_dir)

    yield str(db_path), str(json_dir)

    # テスト完了後に成果物ディレクトリをクリーンアップ
    shutil.rmtree(artifacts_dir)


# --- 3. テストケース ---
def test_generate_from_directory(test_artifacts_setup):
    db_path, json_dir = test_artifacts_setup

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
