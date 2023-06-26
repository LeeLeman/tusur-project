import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi.testclient import TestClient

from settings import settings
from src import Base
from src.database import get_db
from src.main import app


engine_test = create_async_engine(settings.TEST_DATABASE_URL, connect_args={"check_same_thread": False})
async_session_test = async_sessionmaker(engine_test)
metadata = Base.metadata


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def get_session() -> AsyncSession:
    async with async_session_test() as session:
        yield session


async def _get_test_db() -> AsyncSession:
    async with async_session_test() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def override_dependency():
    app.dependency_overrides[get_db] = _get_test_db


@pytest.fixture(scope="session")
def client():
    return TestClient(app=app)


@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
