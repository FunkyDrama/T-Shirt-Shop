from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, declared_attr


class Base(DeclarativeBase):
    """
    Base class for defining database models with common attributes.

    This abstract base class is used to provide shared functionality for
    database models. It includes common attributes such as `id`,
    `updated_at`, and `created_at`, and automatically generates a
    tablename based on the class name. It ensures consistency and reduces
    redundant code across different model definitions.

    :ivar id: Unique identifier for the record. Acts as the primary key.
    :type id: int
    :ivar updated_at: Timestamp of the last update to the record.
    :type updated_at: datetime
    :ivar created_at: Timestamp of when the record was created.
    :type created_at: datetime
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
        onupdate=datetime.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"
