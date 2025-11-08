from pathlib import Path
from pydantic import SecretStr, PrivateAttr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class RedisSettings(BaseSettings):
    """
    Manages the configuration for connecting to a Redis database.

    This class is a settings manager that provides the Redis URL required
    for establishing a connection to a Redis database. It makes use of
    BaseSettings for environment variable-based configuration, allowing easy
    customization and integration with various environments. Default configuration
    includes settings for Redis located at `redis://redis:6379/0`. Environment
    overrides can be loaded from a `.env` file specified in the configuration.

    :ivar REDIS_URL: The URL string for the Redis connection.
    :type REDIS_URL: str
    """

    REDIS_URL: str = "redis://redis:6379/0"

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")


class Settings(BaseSettings):
    """
    Configuration settings for the application.

    This class provides configuration parameters for the application's database
    and other settings. It makes use of Pydantic's BaseSettings to parse environment
    variables for configuration. The class also includes functionality for dynamically
    constructing the database URL and an optional override.

    :ivar POSTGRES_USER: The username for the PostgreSQL database.
    :type POSTGRES_USER: SecretStr
    :ivar POSTGRES_PASSWORD: The password for the PostgreSQL database.
    :type POSTGRES_PASSWORD: SecretStr
    :ivar POSTGRES_DB: The name of the PostgreSQL database.
    :type POSTGRES_DB: str
    :ivar POSTGRES_HOST: The hostname of the PostgreSQL database. Default is "users_db".
    :type POSTGRES_HOST: str
    :ivar POSTGRES_PORT: The port number of the PostgreSQL database. Default is 5432.
    :type POSTGRES_PORT: int
    :ivar echo: Enables or disables query logging. Default is False.
    :type echo: bool
    :ivar echo_pool: Enables or disables logging for pool-related operations. Default is False.
    :type echo_pool: bool
    :ivar pool_size: The size of the connection pool. Default is 50.
    :type pool_size: int
    :ivar max_overflow: The maximum number of overflow connections allowed. Default is 10.
    :type max_overflow: int
    :ivar naming_convention: The naming conventions for database constraints.
    :type naming_convention: dict[str, str]
    """

    POSTGRES_USER: SecretStr
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_HOST: str = "users_db"
    POSTGRES_PORT: int = 5432
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")
    _db_url_override: str | None = PrivateAttr(default=None)

    @property
    def DATABASE_URL(self) -> str:
        if self._db_url_override:
            return self._db_url_override
        return (
            "postgresql+asyncpg://"
            f"{self.POSTGRES_USER.get_secret_value()}:"
            f"{self.POSTGRES_PASSWORD.get_secret_value()}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    @DATABASE_URL.setter
    def DATABASE_URL(self, value: str) -> None:
        self._db_url_override = value

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


settings = Settings()
redis_settings = RedisSettings()
