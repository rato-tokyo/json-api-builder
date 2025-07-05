# tests/test_main.py
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlmodel import Field, SQLModel

from json_api_builder import AppBuilder


# --- 1. テスト用のモデル定義 ---
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: int | None = None


# --- 2. AppBuilderのフィクスチャ ---
@pytest_asyncio.fixture(name="builder")
async def builder_fixture() -> AppBuilder:
    test_database_url = "sqlite+aiosqlite:///:memory:"
    builder = AppBuilder(db_path=test_database_url)
    builder.add_resource(Hero, path="/heroes")

    # テーブルを作成
    async with builder.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield builder

    # テーブルを削除
    async with builder.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


# --- 3. 非同期HTTPクライアントのフィクスチャ ---
@pytest_asyncio.fixture(name="client")
async def client_fixture(builder: AppBuilder) -> AsyncClient:
    app = builder.get_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# --- 4. テストケース ---
@pytest.mark.asyncio
async def test_full_crud_cycle(client: AsyncClient):
    # Create
    response = await client.post(
        "/heroes",
        json={"name": "Deadpond", "secret_name": "Dive Wilson", "age": 12},
    )
    assert response.status_code == 200

    # Read (to get the created item with its ID)
    response = await client.get("/heroes")
    assert response.status_code == 200
    all_heroes = response.json()["data"]
    assert len(all_heroes) == 1
    hero = all_heroes[0]
    assert hero["name"] == "Deadpond"
    hero_id = hero["id"]

    # Read One
    response = await client.get(f"/heroes/{hero_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Deadpond"

    # Update
    response = await client.patch(f"/heroes/{hero_id}", json={"name": "Updated"})
    assert response.status_code == 200
    # Verify update by reading again
    response = await client.get(f"/heroes/{hero_id}")
    assert response.json()["name"] == "Updated"

    # Delete
    response = await client.delete(f"/heroes/{hero_id}")
    assert response.status_code == 200

    # Verify Deletion
    response = await client.get(f"/heroes/{hero_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_custom_route(builder: AppBuilder):
    # Add a custom route
    async def custom_endpoint():
        return {"message": "Hello from custom route"}

    builder.add_custom_route(
        "/custom", custom_endpoint, methods=["GET"], tags=["Custom"]
    )

    # Create a new client with the updated app
    app = builder.get_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test the custom route
        response = await client.get("/custom")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello from custom route"}

        # Verify that the route appears in OpenAPI docs
        openapi_schema = app.openapi()
        assert "/custom" in openapi_schema["paths"]
        assert "get" in openapi_schema["paths"]["/custom"]
        assert "Custom" in openapi_schema["paths"]["/custom"]["get"]["tags"]
