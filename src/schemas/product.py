from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from src.db.product import Size, Color


class Product(BaseModel):
    """
    Representation of a product with its various properties.

    This class models a product in an inventory or e-commerce system. It is designed
    to store and handle essential data about a product, such as its name, description,
    price, quantity, size, color, and image URL. The class serves as a blueprint for
    product instances, allowing easy integration and use within larger systems like
    databases, APIs, or front-end applications.

    :ivar name: The name of the product.
    :type name: str
    :ivar description: A brief description of the product, optional.
    :type description: str | None
    :ivar price: The price of the product.
    :type price: Decimal
    :ivar quantity: The quantity of the product available in stock.
    :type quantity: int
    :ivar size: The size attribute of the product.
    :type size: Size
    :ivar color: The color attribute of the product.
    :type color: Color
    :ivar image_url: URL of the product image, optional.
    :type image_url: str | None
    """

    name: str
    description: str | None = None
    price: Decimal
    quantity: int
    size: Size
    color: Color
    image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductOut(Product):
    """
    Represents the output structure of a product, extending the base Product class.

    This class is used to define the additional attributes and properties that
    are part of the product output. It includes details specific to the output
    representation of a product.

    :ivar id: Unique identifier for the product.
    :type id: int
    """

    id: int


class ProductsOut(BaseModel):
    """
    Represents the output of a product listing in a structured format.

    This class is designed to provide structured data that includes a list of
    products and a total count. It is useful for scenarios where a structured
    response about product data is required, for instance, in APIs or data
    serialization.

    :ivar products: List of products where each product is represented as an
        instance of the ProductOut class.
    :type products: list[ProductOut]
    :ivar total: Total count of products available.
    :type total: int
    """

    products: list[ProductOut]
    total: int


class ProductIn(Product):
    """
    Represents a specific type of product input derived from the base Product class.

    This class is used to define specific characteristics or behaviors of products
    that are applicable to input scenarios. It inherits all attributes and methods
    from the base Product class.

    No additional attributes or functionality are defined within this class. It
    serves as a placeholder or base for further extensions of product input
    definitions.
    """

    pass
