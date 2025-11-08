from typing import Annotated
from fastapi import APIRouter, Depends

from src.core.dependencies import get_product_service
from src.schemas.product import ProductsOut, ProductOut, ProductIn
from src.services.product import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get(
    "",
    response_model=ProductsOut,
    response_model_exclude_unset=True,
    status_code=200,
)
async def get_products(
    svc: Annotated[
        ProductService,
        Depends(get_product_service),
    ],
) -> ProductsOut:
    """
    Retrieves a list of products using the provided service and returns the data
    in the response model format. This endpoint is facilitated by the ProductService
    and performs the retrieval operation asynchronously.

    :param svc: The product service instance responsible for fetching
        the products data.
    :type svc: ProductService
    :return: A list of products adhering to the ProductsOut response model.
    :rtype: ProductsOut
    """
    return await svc.get_products()


@router.get(
    "/{product_id}",
    response_model=ProductOut,
    response_model_exclude_unset=True,
    status_code=200,
)
async def get_product(
    product_id: int,
    svc: Annotated[
        ProductService,
        Depends(get_product_service),
    ],
) -> ProductOut:
    """
    Fetches a product by its unique identifier.

    This function is part of a FastAPI application and is used to retrieve
    product details from the service layer. It utilizes dependency injection
    to access the product service.

    :param product_id: The unique identifier of the product.
    :type product_id: int
    :param svc: The instance of ProductService injected via dependency
        resolution.
    :type svc: ProductService
    :return: The product details as a response model conforming to
        ``ProductOut``.
    :rtype: ProductOut
    """
    return await svc.get_product(product_id)


@router.post(
    "",
    response_model=ProductOut,
    response_model_exclude_unset=True,
    status_code=201,
)
async def add_product(
    product: ProductIn,
    svc: Annotated[
        ProductService,
        Depends(get_product_service),
    ],
) -> ProductOut:
    """
    Adds a new product by handling the provided input and delegating the process
    to the product service. This endpoint enables the creation of products.

    :param product: The product details provided as input.
    :type product: ProductIn
    :param svc: The service dependency used for product operations.
    :type svc: ProductService
    :return: The created product data returned by the service.
    :rtype: ProductOut
    """
    return await svc.add_product(product)
