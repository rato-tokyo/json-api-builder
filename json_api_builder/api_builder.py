"""
json-api-builder: A simple API builder.
"""

import contextlib
from collections.abc import Generator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base
from .router import create_resource_router


class APIBuilder:
    """
    A simple API builder that constructs a FastAPI application.
    The primary responsibility is to build and run the API server.
    """

    def __init__(
        self,
        title: str,
        description: str,
        version: str,
        db_path: str,
    ):
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            echo=False,
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.app = FastAPI(
            title=title,
            description=description,
            version=version,
            lifespan=self._lifespan,
        )
        self.models: dict[str, type[BaseModel]] = {}
        self._create_tables()

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI) -> Any:
        """Manages the application's lifespan to prevent file locks."""
        yield
        self.engine.dispose()

    def _create_tables(self) -> None:
        """Creates all tables in the database."""
        Base.metadata.create_all(bind=self.engine)

    @contextlib.contextmanager
    def get_db(self) -> Generator[Session, None, None]:
        """Provides a database session."""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def resource(self, name: str, model: type[BaseModel]) -> None:
        """Registers a resource endpoint."""
        if not issubclass(model, BaseModel):
            raise ValueError("Model must be a Pydantic BaseModel subclass")
        self.models[name] = model
        # Pass the get_db method to the router factory
        router = create_resource_router(name, model, self.get_db)
        self.app.include_router(router)

    def get_app(self) -> FastAPI:
        """Returns the FastAPI app instance."""
        return self.app

    def run(self, host: str, port: int, reload: bool = False) -> None:
        """Runs the API server."""
        uvicorn.run(self.app, host=host, port=port, reload=reload)
