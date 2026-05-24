# Database Patterns Reference

## Table of Contents
1. [SQLAlchemy Async + Alembic](#sqlalchemy-async--alembic)
2. [MongoDB with Motor/Beanie](#mongodb-with-motorbeanie)
3. [Redis Caching & Sessions](#redis-caching--sessions)
4. [Elasticsearch Integration](#elasticsearch-integration)
5. [Generic Repository Pattern](#generic-repository-pattern)

---

## SQLAlchemy Async + Alembic

### Engine & Session Setup

```python
# app/db/session.py
"""Async SQLAlchemy engine and session factory.

Configures the database connection pool and provides a session
dependency for FastAPI's dependency injection system. Sessions
use automatic commit on success and rollback on exception.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config import settings

# Connection pool sized for typical web workloads:
# pool_size=20 handles 20 concurrent queries, with 10 overflow
# for burst traffic. pool_pre_ping detects stale connections.
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections every 5 min to avoid timeouts
)

async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a database session.

    Automatically commits on success, rolls back on exception,
    and closes the session when the request completes. Route
    handlers receive this via Depends(get_db).

    Yields:
        AsyncSession bound to the current request lifecycle.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### Declarative Base with Mixins

```python
# app/models/base.py
from datetime import datetime
from uuid import uuid4
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

class UUIDPrimaryKeyMixin:
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
```

### Model Example

```python
# app/models/user.py
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    items: Mapped[list["Item"]] = relationship(back_populates="owner", lazy="selectin")
```

### Alembic Configuration

```python
# alembic/env.py - Key parts for async
from app.db.session import engine
from app.models.base import Base
# Import all models so Alembic sees them
from app.models import user, item  # noqa: F401

target_metadata = Base.metadata

async def run_async_migrations():
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
```

Common Alembic commands:
```bash
alembic init alembic                    # Initialize
alembic revision --autogenerate -m "msg" # Auto-generate migration
alembic upgrade head                     # Apply all migrations
alembic downgrade -1                     # Rollback one step
alembic history                          # Show migration history
```

---

## MongoDB with Motor/Beanie

### Connection Setup

```python
# app/db/mongo.py
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def init_mongo():
    client = AsyncIOMotorClient(settings.mongodb_url)
    await init_beanie(
        database=client[settings.mongodb_db_name],
        document_models=[
            "app.models.mongo_models.UserDocument",
            "app.models.mongo_models.AuditLog",
        ],
    )

async def close_mongo():
    # Motor handles connection pooling; explicit close is optional
    pass
```

### Beanie Document Model

```python
# app/models/mongo_models.py
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from uuid import uuid4

class UserDocument(Document):
    uid: Indexed(str, unique=True) = Field(default_factory=lambda: str(uuid4()))
    email: Indexed(str, unique=True)
    full_name: str
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"                 # Collection name
        use_state_management = True    # Enable save_changes()

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "Jane Doe",
            }
        }
```

### Beanie Repository Pattern

```python
from beanie import PydanticObjectId
from app.models.mongo_models import UserDocument

class UserMongoRepo:
    async def find_by_email(self, email: str) -> UserDocument | None:
        return await UserDocument.find_one(UserDocument.email == email)

    async def create(self, data: dict) -> UserDocument:
        doc = UserDocument(**data)
        await doc.insert()
        return doc

    async def list_paginated(self, page: int, size: int) -> list[UserDocument]:
        skip = (page - 1) * size
        return await UserDocument.find_all().skip(skip).limit(size).to_list()
```

---

## Redis Caching & Sessions

### Connection Setup

```python
# app/db/redis.py
"""Async Redis connection pool management.

Provides a shared connection pool for Redis operations across the
application. Uses decode_responses=True so all values are returned
as strings (not bytes), avoiding manual decoding in every caller.
"""

from redis.asyncio import Redis, ConnectionPool
from app.config import settings

pool: ConnectionPool | None = None


async def init_redis() -> None:
    """Initialize the Redis connection pool on application startup.

    Called from the FastAPI lifespan context manager. Creates a pool
    with up to 20 connections — sized to match the database pool.
    """
    global pool
    pool = ConnectionPool.from_url(
        settings.redis_url,
        max_connections=20,
        decode_responses=True,
    )


async def get_redis() -> Redis:
    """Get a Redis client from the connection pool.

    Returns:
        Redis client bound to the shared connection pool.
    """
    return Redis(connection_pool=pool)


async def close_redis() -> None:
    """Close all Redis connections on application shutdown."""
    if pool:
        await pool.disconnect()
```

### Caching Decorator Pattern

```python
import json
import functools
from app.db.redis import get_redis


def cache(prefix: str, ttl: int = 300):
    """Decorator that caches async function results in Redis.

    Implements a cache-aside (lazy-loading) pattern: check cache
    first, compute on miss, store result for future calls. Cache
    keys are derived from the prefix and hashed function arguments.

    Args:
        prefix: Namespace prefix for cache keys (e.g., "user", "product").
        ttl: Time-to-live in seconds. Defaults to 300 (5 minutes).

    Returns:
        Decorator function that wraps async callables with caching.

    Example:
        @cache(prefix="user", ttl=600)
        async def get_user_by_id(user_id: str) -> dict:
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            redis = await get_redis()
            # Hash arguments to create a deterministic cache key
            key = f"{prefix}:{hash(str(args) + str(kwargs))}"

            cached = await redis.get(key)
            if cached:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            # Use default=str to handle UUIDs, datetimes, etc.
            await redis.set(key, json.dumps(result, default=str), ex=ttl)
            return result
        return wrapper
    return decorator
```

### Cache Invalidation

```python
async def invalidate_user_cache(user_id: str):
    redis = await get_redis()
    keys = await redis.keys(f"user:*{user_id}*")
    if keys:
        await redis.delete(*keys)
```

---

## Elasticsearch Integration

### Client Setup

```python
# app/db/elasticsearch.py
from elasticsearch import AsyncElasticsearch
from app.config import settings

es_client: AsyncElasticsearch | None = None

async def init_elasticsearch():
    global es_client
    es_client = AsyncElasticsearch(
        hosts=[settings.elasticsearch_url],
        basic_auth=(settings.es_user, settings.es_password) if settings.es_user else None,
        verify_certs=settings.es_verify_certs,
        request_timeout=30,
    )

async def get_es() -> AsyncElasticsearch:
    return es_client

async def close_elasticsearch():
    if es_client:
        await es_client.close()
```

### Search Repository Pattern

```python
class SearchRepository:
    def __init__(self, es: AsyncElasticsearch, index: str):
        self.es = es
        self.index = index

    async def index_document(self, doc_id: str, body: dict):
        await self.es.index(index=self.index, id=doc_id, document=body)

    async def search(self, query: str, page: int = 1, size: int = 20) -> dict:
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^2", "description", "content"],
                    "fuzziness": "AUTO",
                }
            },
            "from": (page - 1) * size,
            "size": size,
            "highlight": {"fields": {"content": {}}},
        }
        return await self.es.search(index=self.index, body=body)

    async def delete_document(self, doc_id: str):
        await self.es.delete(index=self.index, id=doc_id, ignore=[404])
```

---

## Generic Repository Pattern

This base repository works with SQLAlchemy async and provides standard CRUD:

```python
# app/repositories/base.py
"""Generic async CRUD repository for SQLAlchemy models.

Provides standard create, read, update, and delete operations
that work with any SQLAlchemy model inheriting from Base. Domain-
specific repositories extend this base to add custom queries
while inheriting consistent CRUD behavior.
"""

from typing import TypeVar, Generic, Type
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository providing async CRUD for any ORM model.

    Subclass this with a specific model type to inherit standard
    CRUD operations. Add domain-specific query methods in the
    subclass (e.g., get_by_email for UserRepository).

    Attributes:
        model: The SQLAlchemy model class this repository manages.
        db: Async database session for executing queries.

    Example:
        class UserRepository(BaseRepository[User]):
            def __init__(self, db):
                super().__init__(User, db)
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession) -> None:
        self.model = model
        self.db = db

    async def get(self, id: UUID) -> ModelType | None:
        """Fetch a single record by primary key.

        Args:
            id: UUID primary key of the record.

        Returns:
            Model instance if found, None otherwise.
        """
        return await self.db.get(self.model, id)

    async def get_or_raise(self, id: UUID) -> ModelType:
        """Fetch a record by primary key, raising NotFoundError if missing.

        Args:
            id: UUID primary key of the record.

        Returns:
            Model instance.

        Raises:
            NotFoundError: If no record exists with the given ID.
        """
        obj = await self.get(id)
        if not obj:
            raise NotFoundError(self.model.__name__, str(id))
        return obj

    async def list(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[ModelType], int]:
        """Retrieve a paginated list of records.

        Args:
            page: Page number (1-indexed).
            page_size: Number of results per page.

        Returns:
            Tuple of (list of model instances, total count).
        """
        offset = (page - 1) * page_size
        query = select(self.model).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        count_query = select(func.count()).select_from(self.model)
        total = (await self.db.execute(count_query)).scalar()
        return items, total

    async def create(self, data: dict) -> ModelType:
        """Persist a new record to the database.

        Uses flush (not commit) to defer transaction control to the
        session manager. This allows batching multiple operations
        in a single transaction.

        Args:
            data: Dictionary of column name → value pairs.

        Returns:
            The created model instance with server-generated fields populated.
        """
        obj = self.model(**data)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, id: UUID, data: dict) -> ModelType:
        """Apply partial updates to an existing record.

        Only non-None values in data are applied, allowing partial
        updates without overwriting unmodified fields.

        Args:
            id: UUID of the record to update.
            data: Dictionary of fields to modify.

        Returns:
            The updated model instance.

        Raises:
            NotFoundError: If no record exists with the given ID.
        """
        obj = await self.get_or_raise(id)
        for key, value in data.items():
            if value is not None:
                setattr(obj, key, value)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, id: UUID) -> None:
        """Remove a record from the database.

        Args:
            id: UUID of the record to delete.

        Raises:
            NotFoundError: If no record exists with the given ID.
        """
        obj = await self.get_or_raise(id)
        await self.db.delete(obj)
        await self.db.flush()
```

### Specialized Repository

```python
# app/repositories/user_repo.py
from sqlalchemy import select
from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
```
