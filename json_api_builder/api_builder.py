"""
json-api-builder: A simple API builder.
"""

from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.engine import Engine

from .database import Database
from .db_download import add_download_info_endpoint
from .json_export import JSONExporter
from .router import create_resource_router


class APIBuilder:
    """
    A simple API builder that constructs a FastAPI application with CRUD endpoints,
    database management, and JSON export/import functionalities.
    """

    def __init__(
        self,
        title: str,
        description: str,
        version: str,
        db_path: str,
    ):
        self.db = Database(db_path)
        self.db.create_tables()

        self.app = FastAPI(
            title=title,
            description=description,
            version=version,
            lifespan=self._lifespan,
        )
        self.models: dict[str, type[BaseModel]] = {}
        add_download_info_endpoint(self.app, db_path)

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI) -> Any:
        """Manages the application's lifespan to prevent file locks."""
        yield
        # On shutdown, dispose the engine to release file handles.
        self.db.dispose_engine()

    @property
    def engine(self) -> Engine:
        """Returns the SQLAlchemy engine."""
        return self.db.engine

    def _validate_model(self, model: type[BaseModel]) -> None:
        """Validates the Pydantic model."""
        if not issubclass(model, BaseModel):
            raise ValueError("Model must be a Pydantic BaseModel subclass")

    def resource(self, name: str, model: type[BaseModel]) -> None:
        """Registers a resource endpoint."""
        self._validate_model(model)
        self.models[name] = model
        router = create_resource_router(name, model, self.db)
        self.app.include_router(router)

    def get_app(self) -> FastAPI:
        """Returns the FastAPI app instance."""
        return self.app

    def run(self, host: str, port: int, reload: bool = False) -> None:
        """Runs the API server."""
        uvicorn.run(self.app, host=host, port=port, reload=reload)
