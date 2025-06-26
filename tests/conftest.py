"""
テスト共通設定
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from json_api_builder import APIBuilder


@pytest.fixture(scope="session")
def test_engine():
    """テスト用データベースエンジン"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """テスト用データベースセッション"""
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def app():
    """テスト用FastAPIアプリケーション"""
    builder = APIBuilder(db_path=":memory:")
    return builder.get_app()


@pytest.fixture
def client(app):
    """テスト用クライアント"""
    return TestClient(app) 