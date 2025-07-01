"""
Database file download functionality.
"""

import os
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse

from .database import Database


class DBDownloadMixin:
    """Mixin to add a database download endpoint."""

    app: FastAPI
    db: Database

    def add_db_download_endpoint(
        self,
        endpoint_path: str = "/download/database",
        require_auth: bool = False,
        auth_token: str | None = None,
    ) -> None:
        """Adds an endpoint to download the database file."""

        @self.app.get(endpoint_path)
        async def download_database(token: str | None = None) -> Response:
            """Downloads the database file."""
            if require_auth:
                if not auth_token:
                    raise HTTPException(
                        status_code=500, detail="Authentication token not configured"
                    )
                if token != auth_token:
                    raise HTTPException(
                        status_code=401, detail="Invalid authentication token"
                    )

            db_path = self.db.get_db_file_path()
            if not os.path.exists(db_path):
                raise HTTPException(status_code=404, detail="Database file not found")

            file_size = os.path.getsize(db_path)
            if file_size == 0:
                raise HTTPException(status_code=404, detail="Database file is empty")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_filename = f"database_backup_{timestamp}.db"

            return FileResponse(
                path=db_path,
                filename=download_filename,
                media_type="application/octet-stream",
            )

    def _get_db_file_path(self) -> str:
        """Gets the database file path from the Database object."""
        return self.db.get_db_file_path()


def add_download_info_endpoint(app: FastAPI, db_path: str) -> None:
    """Adds an endpoint to show database download information."""

    @app.get("/download/info")
    async def download_info() -> dict[str, Any]:
        """Gets information about the database file."""
        if not os.path.exists(db_path):
            return {
                "exists": False,
                "path": db_path,
                "message": "Database file not found",
            }

        stat = os.stat(db_path)
        return {
            "exists": True,
            "path": db_path,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "download_url": "/download/database",
        }
