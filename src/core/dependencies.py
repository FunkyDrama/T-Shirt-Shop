from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.helper import db_helper
from src.services.product import ProductService
from collections.abc import AsyncGenerator


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an asynchronous generator for database sessions.

    This function acts as a context manager for creating an asynchronous
    database session using the configured session factory. It ensures that
    resources are properly managed by yielding a session object within the
    async context.

    :yield: An instance of AsyncSession
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async with db_helper.session_factory() as session:
        yield session


async def get_product_service(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
) -> ProductService:
    """
    Provides an instance of the ProductService configured with the current session and
    Redis client.

    :param request: The current HTTP request being processed.
    :type request: Request
    :param session: The database session associated with the request.
        Automatically provided by dependency injection.
    :type session: Annotated[AsyncSession, Depends(get_session)]
    :return: An instance of ProductService initialized with the provided session and
        Redis client.
    :rtype: ProductService
    """
    redis_client = request.app.state.redis
    return ProductService(session, redis_client)
