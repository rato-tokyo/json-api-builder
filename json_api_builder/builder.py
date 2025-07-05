# json_api_builder/builder.py
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastcrud import crud_router
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel


class AppBuilder:
    """
    A builder class to simplify the creation of a FastAPI application
    with CRUD endpoints powered by FastCRUD.
    """

    def __init__(
        self, db_path: str, title: str = "FastAPI App", version: str = "1.0.0"
    ):
        self.engine = create_async_engine(db_path, echo=False)

        @asynccontextmanager
        async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
            await self._create_db_and_tables()
            yield

        self.app = FastAPI(lifespan=lifespan, title=title, version=version)

    async def _create_db_and_tables(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSession(self.engine) as session:
            yield session

    def add_resource(
        self,
        model: type[SQLModel],
        create_schema: type[SQLModel] | None = None,
        update_schema: type[SQLModel] | None = None,
        path: str | None = None,
    ) -> None:
        """
        Adds a new CRUD resource to the application.

        Args:
            model: The SQLModel class for the resource.
            create_schema: The Pydantic/SQLModel schema for creating items. Defaults to `model`.
            update_schema: The Pydantic/SQLModel schema for updating items. Defaults to `model`.
            path: The URL path for the resource. Defaults to `/model_name_plural`.
        """
        table_name = str(model.__tablename__)
        resource_path = path or f"/{table_name}"

        self.app.include_router(
            crud_router(
                session=self.get_session,
                model=model,
                create_schema=create_schema or model,
                update_schema=update_schema or model,
                path=resource_path,
                tags=[table_name.capitalize()],
            )
        )

    def add_custom_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        methods: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Adds a custom route to the FastAPI application.

        Args:
            path: The URL path for the route.
            endpoint: The endpoint function to handle the request.
            methods: A list of HTTP methods for the route, e.g., ["GET", "POST"].
            **kwargs: Additional arguments to pass to FastAPI's `add_api_route`.
        """
        self.app.add_api_route(path, endpoint, methods=methods, **kwargs)

    def get_app(self) -> FastAPI:
        """Returns the configured FastAPI application instance."""
        return self.app
