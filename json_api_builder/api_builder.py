"""
json-api-builder: A simple API builder.
"""

from typing import Any

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .database import Database
from .db_download import DBDownloadMixin, add_download_info_endpoint
from .json_export import JSONExporter
from .router import create_resource_router


class APIBuilder(DBDownloadMixin):
    """A simple API builder."""

    def __init__(self, title: str, description: str, version: str, db_path: str):
        self.db_path = db_path
        self.db = Database(db_path)
        self.db.create_tables()

        self.app = FastAPI(
            title=title,
            description=description,
            version=version,
        )
        self.models: dict[str, type[BaseModel]] = {}

        add_download_info_endpoint(self.app, db_path)

    @property
    def engine(self) -> Engine:
        """Returns the SQLAlchemy engine."""
        return self.db.engine

    @property
    def session_local(self) -> sessionmaker[Session]:
        """Returns the SQLAlchemy SessionLocal."""
        return self.db.SessionLocal

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

    def export_to_json(self, output_dir: str, pretty: bool = True) -> dict[str, Any]:
        """Exports all database data to JSON files."""
        exporter = JSONExporter(self.db)
        return exporter.export_to_json(output_dir, pretty)

    def export_resource_to_json(
        self, resource_type: str, output_file: str, pretty: bool = True
    ) -> dict[str, Any]:
        """Exports a specific resource type to a JSON file."""
        exporter = JSONExporter(self.db)
        return exporter.export_resource_to_json(resource_type, output_file, pretty)
