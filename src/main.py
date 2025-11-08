import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn

from src.api import router as api_router
from src.core.redis_conf import init_redis, close_redis
from src.db.helper import db_helper

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Asynchronous lifespan context manager for a FastAPI application. It initializes
    and disposes of resources needed during the application's lifespan.

    This function ensures that necessary resources, such as Redis connections and
    database helpers, are appropriately initialized when the application starts and
    cleaned up properly when it shuts down.

    :param app: The FastAPI application instance.
    :type app: FastAPI

    :return: Yields control back to the caller. No value is returned.
    :rtype: AsyncGenerator[None, None]
    """
    await init_redis(app)
    yield
    await db_helper.dispose()
    await close_redis(app)


def create_app() -> FastAPI:
    """
    Creates and configures a FastAPI application instance for the T-Shirt Shop API.

    This function initializes a FastAPI app with predefined settings including middleware
    for Cross-Origin Resource Sharing (CORS) and sets up API routes. The application
    provides basic health-check endpoints and main configurations for a t-shirt shop
    platform. It also attempts to optimize the event loop policy using uvloop if available.

    :raises Exception: If the uvloop event loop policy could not be initialized (logged as a warning).

    :return: Configured FastAPI application instance.
    :rtype: FastAPI
    """
    try:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except Exception as e:
        logger.warning("uvloop is not active: %s", e)

    app = FastAPI(
        title="T-Shirt Shop Api",
        description="API for t-shirt shop",
        version="1.0.0",
        lifespan=lifespan,
        swagger_ui_parameters={"persistAuthorization": True},
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"message": "App is running"}

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
