from typing import Any

from src.core.settings import settings

settings.DATABASE_URL = "sqlite+aiosqlite:///./test.db"

import pytest_asyncio
from collections.abc import AsyncGenerator
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
import fakeredis.aioredis as fakeredis

from src.db.base import Base
from src.main import create_app
from src.db.helper import DatabaseHelper
from src.core.dependencies import get_session
import src.core.redis_conf as lifecycle


@pytest_asyncio.fixture(autouse=True)
def patch_redis(monkeypatch):
    """
    Fixture to automatically patch the Redis connection with a fake Redis
    instance for testing purposes.

    This fixture intercepts the creation of Redis connections by replacing
    the `from_url` method in the `lifecycle.redis` module. It substitutes
    it with a `fakeredis.FakeRedis` instance, which provides an in-memory
    Redis-like behavior. This ensures that tests using this fixture can run
    without requiring an actual Redis server.

    :param monkeypatch: Instance of `monkeypatch` used to modify the behavior
        of the Redis connection during tests.
    :return: A patched `from_url` method with a fake Redis instance.
    """
    monkeypatch.setattr(
        lifecycle.redis,
        "from_url",
        lambda *a, **kw: fakeredis.FakeRedis(decode_responses=True),
        raising=True,
    )
    yield


@pytest_asyncio.fixture
async def app() -> FastAPI:
    """
    Creates and provides a FastAPI application instance for testing purposes.

    The application instance is set up asynchronously using the provided `create_app` function.
    This fixture is useful for integration and endpoint testing in FastAPI applications.

    :return: The FastAPI application instance
    :rtype: FastAPI
    """
    return create_app()


@pytest_asyncio.fixture
async def client(app: FastAPI, monkeypatch) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture providing an asynchronous HTTP client for testing FastAPI applications. This
    fixture sets up a test database, overrides the FastAPI dependency for database sessions
    with a mocked session getter, and manages the application lifespan asynchronously.
    It also ensures the database schema is created and dropped as part of the test setup
    and teardown process.

    :param app: FastAPI application instance used for testing.
    :type app: FastAPI
    :param monkeypatch: pytest monkeypatch fixture for dynamic modifications.
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :return: An asynchronous HTTP client for performing requests against the application.
    :rtype: AsyncGenerator[AsyncClient, None]
    """
    test_db = DatabaseHelper(url=settings.DATABASE_URL, echo=False, echo_pool=False)
    app.dependency_overrides[get_session] = test_db.session_getter

    async with LifespanManager(app):
        async with test_db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            yield ac

    await test_db.dispose()


def make_product_payload(**overrides: Any) -> dict:
    """
    Generate a dictionary payload for a product, based on a base template and optional overrides.

    The function creates a dictionary that represents a product's details, including its
    name, price, description, image URL, quantity, size, and color. Users can customize
    the payload by providing specific values through keyword arguments, which override
    the base template.

    :param overrides: Arbitrary keyword arguments used to override default values in the
        product payload. Each key in `overrides` corresponds to a field in the payload.
        (e.g., name, price, description, etc.)
    :type overrides: Any

    :return: A dictionary representing a product payload with default values, updated
        with any overrides provided.
    :rtype: dict
    """
    base = {
        "name": "Test Product",
        "price": "10.99",
        "description": "A test product",
        "image_url": "https://example.com/image.jpg",
        "quantity": 100,
        "size": "M",
        "color": "RED",
    }
    base.update(overrides)
    return base
