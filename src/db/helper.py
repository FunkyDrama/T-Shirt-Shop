import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
)

from src.core.settings import settings

log = logging.getLogger(__name__)


class DatabaseHelper:
    """
    Helper class for managing database connections and sessions.

    This class provides functionalities to manage an asynchronous database engine,
    create session factories, and dispose of resources when necessary. It is
    designed to streamline database operations, including session management
    and connection handling.

    :ivar engine: Asynchronous database engine used for managing connections.
    :type engine: AsyncEngine
    :ivar session_factory: Factory to create database sessions for asynchronous
                           operations.
    :type session_factory: async_sessionmaker[AsyncSession]
    """

    def __init__(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        await self.engine.dispose()
        log.info("Database engine disposed")

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session


db_helper = DatabaseHelper(
    url=settings.DATABASE_URL,
    echo=settings.echo,
    echo_pool=settings.echo_pool,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
)
