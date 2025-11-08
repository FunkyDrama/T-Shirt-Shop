import json
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.product import ProductRepository
from src.schemas.product import ProductIn, ProductOut, ProductsOut
import redis


class ProductService:
    """
    Handles operations related to products including retrieval, addition, and caching.

    This class interacts with a database session and a Redis instance to fetch, cache,
    and add product information. It ensures efficient data retrieval via caching
    mechanisms and maintains the integrity of cached data through operations like
    deletion of relevant keys upon data modification.

    :ivar session: AsyncSession instance for database interactions.
    :type session: AsyncSession
    :ivar redis: Redis instance for caching product data.
    :type redis: redis.Redis
    :ivar cache_ttl: Time-to-live (in seconds) for cached products. Default is 60 seconds.
    :type cache_ttl: int
    """

    def __init__(self, session: AsyncSession, redis: redis.Redis):
        self.session = session
        self.redis = redis
        self.cache_ttl = 60

    async def get_products(self) -> ProductsOut:
        cache_key = "products:all"
        cached = await self.redis.get(cache_key)

        if cached:
            data = json.loads(cached)
            return ProductsOut(**data)

        async with self.session as session:
            repo = ProductRepository(session)
            products = await repo.get_all_products()
            if not products:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="No products found"
                )

            result = ProductsOut(
                products=[ProductOut.model_validate(product) for product in products],
                total=len(products),
            )
            await self.redis.set(cache_key, result.model_dump_json(), ex=self.cache_ttl)
            return result

    async def get_product(self, product_id: int) -> ProductOut:
        cache_key = f"product:{product_id}"
        cached = await self.redis.get(cache_key)
        if cached:
            return ProductOut(**json.loads(cached))

        async with self.session as session:
            repo = ProductRepository(session)
            product = await repo.get_product_by_id(product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

            result = ProductOut.model_validate(product)
            await self.redis.set(cache_key, result.model_dump_json(), ex=self.cache_ttl)
            return result

    async def add_product(self, product: ProductIn) -> ProductOut:
        async with self.session as session:
            repo = ProductRepository(session)
            new_product = await repo.add_product(product)
            await self.redis.delete("products:all")
            result = ProductOut.model_validate(new_product)
            await self.redis.set(
                f"product:{result.id}", result.model_dump_json(), ex=self.cache_ttl
            )
            return result
