# T‑Shirt Shop – FastAPI Backend

A minimal FastAPI service for a T‑shirt shop with async SQLAlchemy (PostgreSQL), Redis caching, Pydantic v2 schemas, and a clean test setup (pytest‑asyncio + httpx). Includes Docker Compose for local dev and a lightweight SQLite‑based test mode.

---

## ✨ Features
- **FastAPI** with versioned routes under `/api/v1`.
- **Async SQLAlchemy** (2.x) + **Alembic** migrations.
- **Pydantic v2** models.
- **Redis** cache for product list and item detail.
- **Service layer** (`ProductService`) decoupled from transport & repository.
- **Tests** with `pytest-asyncio`, `httpx.AsyncClient`, `asgi-lifespan`, and **fakeredis**.
- **Docker Compose**: `app`, `db` (Postgres 17), `redis`, and a separate `tests` service.

---

## 🧱 Project Structure (key parts)
```
src/
  api/v1/products.py         # /api/v1/products endpoints
  core/
    db.py                    # DatabaseHelper (engine + async_sessionmaker)
    dependencies.py          # Depends(get_session/get_product_service) etc.
    redis_conf.py            # redis.from_url(...) init
    settings.py              # Settings
  db/
    base.py                  # Base = declarative base with naming_convention
    product.py               # ORM model + enums Size, Color
  repositories/product.py    # ProductRepository (CRUD)
  schemas/product.py         # Pydantic v2 schemas (ProductIn/Out/ProductsOut)
  services/product.py        # ProductService with Redis cache
  main.py                    # create_app(), routers, startup/health

alembic/                     # migrations
Dockerfile
docker-compose.yml
pytest.ini / pyproject.toml
```

---

## ⚙️ Tech Stack
- **Python** 3.13
- **FastAPI**
- **SQLAlchemy** (async) + **asyncpg** (prod) / **aiosqlite** (tests)
- **Pydantic v2**
- **Redis** (via `redis.asyncio`), **fakeredis** for tests
- **Alembic**, **Poetry** (optional)
- **pytest-asyncio**, **httpx**, **asgi-lifespan**

---

## 🔌 API
### Health
- `GET /` → `{ "message": "App is running" }`
- `GET /health` → `{ "status": "healthy" }`

### Products (prefix: `/api/v1/products`)
- `GET /` → `ProductsOut`: `{ products: ProductOut[], total: int }` (**404** if empty)
- `GET /{product_id}` → `ProductOut` (**404** if not found)
- `POST /` → **201** → `ProductOut` (invalidates cache)

**ProductIn / ProductOut**
```jsonc
{
  "name": "T-shirt",
  "description": "Cotton tee",
  "price": 10.99,         // Decimal
  "quantity": 100,
  "size": "M",          // enum Size
  "color": "RED",       // enum Color
  "image_url": "https://..."
}
```
`ProductOut` additionally contains `id`.

Redis cache keys:
- list: `products:all` (TTL 60s)
- detail: `product:{id}` (TTL 60s)

---

## 🧩 Settings & Environment
File: `src/core/settings.py` (Pydantic Settings).

- **DATABASE_URL** is built from `POSTGRES_*` vars but can be **overridden** via the property:
  ```python
  from src.core.settings import settings
  settings.DATABASE_URL = "sqlite+aiosqlite:///./test.db"
  ```
- Default `REDIS_URL` is `redis://redis:6379/0` (see `RedisSettings`).

### Example `.env`
```
POSTGRES_USER=app
POSTGRES_PASSWORD=app
POSTGRES_DB=app
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379/0
```

---

## ▶️ Run with Docker Compose
```bash
# bring up the app (app + db + redis)
docker compose up --build app
# API: http://localhost:8000
```
The `app` service runs:
```sh
alembic -c alembic.ini upgrade head && python -m src.main
```

---

## 🧪 Tests
Two modes:

### 1) Unit mode (default): SQLite + fakeredis (fast)
- Tests **do not** require Postgres/Redis. In `conftest.py`, early override:
  ```python
  from src.core.settings import settings
  settings.DATABASE_URL = "sqlite+aiosqlite:///./test.db"
  ```
- The fixture builds a `DatabaseHelper` for that URL, overrides `Depends(get_session)`, monkeypatches the global `db_helper`, and swaps `redis.from_url` to `fakeredis`.
- Run in Docker:
  ```bash
  docker compose run --rm tests
  ```

### 2) Integration mode (real Postgres/Redis)
- Remove the SQLite override from `conftest.py`.
- Ensure `tests` depends on `db` and `redis` and is on the same network.
- Run:
  ```bash
  docker compose up --build --exit-code-from=tests tests
  ```
The test fixture performs `drop_all/create_all` via SQLAlchemy for a clean schema (Alembic not required for unit tests).

---

## 🔧 Local Development (without Docker, optional)
```bash
# 1) Install deps
poetry install

# 2) Export .env or environment variables
export POSTGRES_HOST=localhost ...

# 3) Migrations
alembic upgrade head

# 4) Dev server
uvicorn src.main:create_app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Test Snippets
```python
# health
r = await client.get("/health")
assert r.status_code == 200
assert r.json() == {"status": "healthy"}

# create
payload = {"name":"Test","price":"10.99","quantity":100,
           "size":"M","color":"RED","description":"A test","image_url":"https://..."}
r = await client.post("/api/v1/products", json=payload)
assert r.status_code == 201

# list
r = await client.get("/api/v1/products")
assert r.status_code == 200
```

---

## 📜 License
MIT.

---

## 🙋 Support
This is a test project shop, so support inquiries are not available. Feel free to use and modify the code as needed!

