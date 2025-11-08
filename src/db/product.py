import enum
from decimal import Decimal

from sqlalchemy import Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Size(str, enum.Enum):
    """
    Represents various size options as an enumeration.

    This enumeration provides a set of predefined size constants for use in
    scenarios where size designation is required. It inherits from both `str`
    and `enum.Enum`, allowing it to function as a string while also
    providing enumerated values.
    """

    S = "S"
    M = "M"
    L = "L"
    XL = "XL"
    XXL = "XXL"


class Color(str, enum.Enum):
    """
    Enumeration of colors.

    This class represents a set of predefined colors. It extends the `str` and
    `enum.Enum` classes, allowing the color values to be used as constant string
    values in addition to being enumerable members. This can be used to ensure
    consistent color values throughout the application and to limit options
    to the defined set of colors.
    """

    RED = "RED"
    BLUE = "BLUE"
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    BLACK = "BLACK"
    WHITE = "WHITE"


class Product(Base):
    """
    Represents a product with specific attributes such as name, description, price, quantity, size, color, and image_url.

    This class is used to model the properties of a product and may be utilized in
    various domains such as e-commerce, inventory management, or product cataloging.

    :ivar name: The unique name of the product.
    :type name: str
    :ivar description: The description of the product detailing its features.
    :type description: str
    :ivar price: The price of the product, maintained with a precision of two decimal points.
    :type price: Decimal
    :ivar quantity: The available quantity of the product in stock.
    :type quantity: int
    :ivar size: The size of the product, represented as an enumerated value.
    :type size: Size
    :ivar color: The color of the product, represented as an enumerated value.
    :type color: Color
    :ivar image_url: Optional URL of the product's image.
    :type image_url: str
    """

    name: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[str] = mapped_column()
    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    quantity: Mapped[int] = mapped_column()
    size: Mapped[Size] = mapped_column(
        Enum(Size),
        default=Size.M,
        name="size",
    )
    color: Mapped[Color] = mapped_column(
        Enum(Color),
        default=Color.BLACK,
        name="color",
    )
    image_url: Mapped[str] = mapped_column(nullable=True)
