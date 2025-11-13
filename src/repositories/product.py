import logging
from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import Product
from src.schemas.product import ProductIn


class ProductRepository:
    """
    Repository class for managing and interacting with Product data.

    This class provides asynchronous methods to retrieve, add, and manage
    Product information from a data source using an asynchronous session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_product_by_id(self, product_id: int) -> Product | None:
        stmt = await self.session.execute(
            select(Product).where(Product.id == product_id),
        )
        return stmt.scalar_one_or_none()

    async def get_all_products(self) -> Sequence[Product]:
        stmt = await self.session.execute(select(Product))
        return stmt.scalars().all()

    async def get_products_by_name(self, name: str) -> Product | None:
        stmt = await self.session.execute(select(Product).where(Product.name == name))
        return stmt.scalar_one_or_none()

    async def add_product(self, new_product: ProductIn) -> Product:
        product = Product(**new_product.model_dump())
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def update_product(
        self,
        product: Product,
        new_product_data: ProductIn,
    ) -> Product:
        for key, value in new_product_data.model_dump().items():
            setattr(product, key, value)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def delete_product(self, product_id: int) -> None:
        stmt = await self.session.execute(
            select(Product).where(Product.id == product_id),
        )
        product = stmt.scalar_one_or_none()
        await self.session.delete(product)
        await self.session.commit()
