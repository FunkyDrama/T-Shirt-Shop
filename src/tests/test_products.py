import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from src.tests.conftest import make_product_payload

API_PREFIX = "/api/v1"


@pytest.mark.asyncio
async def test_health_check(app: FastAPI, client: AsyncClient):
    """
    Asynchronous test for the health check endpoint. Verifies if the health
    check endpoint responds correctly with a status code of 200 and the
    expected JSON response indicating a healthy status.

    :param app: Instance of FastAPI application.
    :type app: FastAPI
    :param client: Asynchronous HTTP client used for making requests.
    :type client: AsyncClient
    :return: None
    """
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_root(app: FastAPI, client: AsyncClient):
    """
    Test the root endpoint of the FastAPI application to ensure it returns
    the expected status code and response message.

    :param app: FastAPI application instance
    :type app: FastAPI
    :param client: HTTP client used for making asynchronous requests
    :type client: AsyncClient
    :return: None
    """
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "App is running"}


@pytest.mark.asyncio
async def test_add_product(app: FastAPI, client: AsyncClient):
    """
    Tests asynchronous product addition to the application backend.

    This test makes a POST request to the API to add a new product using a
    payload created by the `make_product_payload` function. It verifies that
    the response status code indicates successful creation and that the
    received data matches the original payload, including an automatically
    generated product ID.

    :param app: FastAPI application instance used for testing.
    :type app: FastAPI
    :param client: Asynchronous HTTP client used to make API requests.
    :type client: AsyncClient
    :return: None. The test performs assertions to validate behavior.
    :rtype: None
    """
    payload = make_product_payload()
    resp = await client.post(f"{API_PREFIX}/products", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data and isinstance(data["id"], int)
    for k, v in payload.items():
        assert data[k] == v


@pytest.mark.asyncio
async def test_get_products(app: FastAPI, client: AsyncClient):
    """
    Tests the `GET /products` endpoint to verify that it successfully retrieves
    all created products and correctly calculates metadata such as total product
    count. It also ensures that newly created products appear in the fetched listing.

    :param app: The FastAPI application instance used for testing.
    :type app: FastAPI
    :param client: The asynchronous HTTP client used to interact with the API.
    :type client: AsyncClient
    :return: None
    """
    payload = make_product_payload(name="Second Product", price="5.00", quantity=5)
    create = await client.post(f"{API_PREFIX}/products", json=payload)
    assert create.status_code == 201
    created = create.json()
    resp = await client.get(f"{API_PREFIX}/products")
    assert resp.status_code == 200
    listing = resp.json()
    assert "products" in listing and isinstance(listing["products"], list)
    assert "total" in listing and isinstance(listing["total"], int)
    assert any(p["id"] == created["id"] for p in listing["products"])
    assert listing["total"] == len(listing["products"])


@pytest.mark.asyncio
async def test_update_products(app: FastAPI, client: AsyncClient):
    payload = make_product_payload(name="Second Product", price="5.00", quantity=5)
    create = await client.post(f"{API_PREFIX}/products", json=payload)
    assert create.status_code == 201
    created = create.json()
    resp = await client.get(f"{API_PREFIX}/products/{created['id']}")
    assert resp.status_code == 200
    new_payload = make_product_payload(name="Updated Product", price="10.00", quantity=10)
    update = await client.patch(f"{API_PREFIX}/products/{created['id']}", json=new_payload)
    assert update.status_code == 200
    new_resp = await client.get(f"{API_PREFIX}/products/{created['id']}")
    assert new_resp.status_code == 200
    updated_product = new_resp.json()
    assert updated_product['name'] == new_payload['name']
    assert updated_product['price'] == new_payload['price']
    assert updated_product['quantity'] == new_payload['quantity']


@pytest.mark.asyncio
async def test_delete_products(app: FastAPI, client: AsyncClient):
    payload = make_product_payload(name="Second Product", price="5.00", quantity=5)
    create = await client.post(f"{API_PREFIX}/products", json=payload)
    assert create.status_code == 201
    created = create.json()
    delete = await client.delete(f"{API_PREFIX}/products/{created['id']}")
    assert delete.status_code == 204
    read = await client.get(f"{API_PREFIX}/products/{created['id']}")
    assert read.status_code == 404

