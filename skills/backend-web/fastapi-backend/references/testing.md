# Testing Reference

## Table of Contents
1. [Project Setup (pyproject.toml)](#project-setup)
2. [Fixtures (conftest.py)](#fixtures)
3. [Unit Tests](#unit-tests)
4. [Integration Tests (API)](#integration-tests)
5. [Database Testing](#database-testing)
6. [Auth Testing Helpers](#auth-testing-helpers)
7. [WebSocket & SSE Testing](#websocket--sse-testing)
8. [Coverage & Quality](#coverage--quality)

---

## Project Setup

```toml
# pyproject.toml (testing section)
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
filterwarnings = ["ignore::DeprecationWarning"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "unit: Unit tests (no I/O)",
    "integration: Integration tests (requires DB/services)",
    "e2e: End-to-end tests",
]

[tool.coverage.run]
source = ["app"]
omit = ["app/main.py", "*/migrations/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "pass",
]
```

---

## Fixtures

```python
# tests/conftest.py
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.main import create_app
from app.models.base import Base
from app.db.session import get_db
from app.config import settings
from app.auth.jwt import create_access_token

# Use a separate test database
TEST_DB_URL = settings.database_url.replace("/appdb", "/testdb")

engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all tables once per test session, drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session():
    """Per-test database session with automatic rollback."""
    async with TestSessionLocal() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.fixture
async def app(db_session):
    """FastAPI app with test DB override."""
    application = create_app()

    async def override_get_db():
        yield db_session

    application.dependency_overrides[get_db] = override_get_db
    yield application
    application.dependency_overrides.clear()


@pytest.fixture
async def client(app):
    """Async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers():
    """Generate auth headers for a test user."""
    def _make_headers(user_id: str = "test-user-id", roles: list[str] = None):
        token = create_access_token(user_id, roles or ["user"])
        return {"Authorization": f"Bearer {token}"}
    return _make_headers
```

---

## Unit Tests

Unit tests verify business logic in the service layer without touching the database.
Mock the repository layer:

```python
# tests/unit/test_user_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.exceptions import ConflictError

@pytest.fixture
def user_repo():
    return AsyncMock()

@pytest.fixture
def user_service(user_repo):
    return UserService(user_repo=user_repo)


class TestUserServiceCreate:
    async def test_create_user_success(self, user_service, user_repo):
        user_repo.get_by_email.return_value = None
        user_repo.create.return_value = MagicMock(
            id=uuid4(), email="new@example.com", full_name="New User"
        )

        result = await user_service.create(
            UserCreate(email="new@example.com", password="password123", full_name="New User")
        )

        assert result.email == "new@example.com"
        user_repo.create.assert_called_once()

    async def test_create_user_duplicate_email(self, user_service, user_repo):
        user_repo.get_by_email.return_value = MagicMock()  # User exists

        with pytest.raises(ConflictError):
            await user_service.create(
                UserCreate(email="taken@example.com", password="password123", full_name="Dupe")
            )
```

---

## Integration Tests

Integration tests hit the actual API endpoints through the test client:

```python
# tests/integration/test_user_api.py
import pytest

class TestUserAPI:
    async def test_create_user(self, client):
        response = await client.post("/api/v1/users/", json={
            "email": "integration@test.com",
            "password": "securepass123",
            "full_name": "Test User",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "integration@test.com"
        assert "password" not in data  # Never expose passwords

    async def test_create_user_invalid_email(self, client):
        response = await client.post("/api/v1/users/", json={
            "email": "not-an-email",
            "password": "securepass123",
            "full_name": "Test User",
        })
        assert response.status_code == 422

    async def test_list_users_requires_auth(self, client):
        response = await client.get("/api/v1/users/")
        assert response.status_code in (401, 403)

    async def test_list_users_authenticated(self, client, auth_headers):
        response = await client.get(
            "/api/v1/users/",
            headers=auth_headers(),
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
```

---

## Database Testing

For tests that need a real database with data:

```python
# tests/conftest.py (additional fixtures)
from app.models.user import User
from app.auth.passwords import hash_password

@pytest.fixture
async def sample_user(db_session) -> User:
    """Create and return a sample user in the test DB."""
    user = User(
        email="fixture@test.com",
        hashed_password=hash_password("testpass123"),
        full_name="Fixture User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user
```

---

## Auth Testing Helpers

```python
# tests/conftest.py (auth fixtures)

@pytest.fixture
async def authenticated_client(client, sample_user):
    """Client pre-authenticated as the sample user."""
    token = create_access_token(str(sample_user.id), ["user"])
    client.headers["Authorization"] = f"Bearer {token}"
    return client

@pytest.fixture
async def admin_client(client, admin_user):
    """Client pre-authenticated as an admin."""
    token = create_access_token(str(admin_user.id), ["admin"])
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

Test auth enforcement:

```python
class TestAuthEnforcement:
    async def test_expired_token_rejected(self, client):
        # Create a token that's already expired
        expired_token = create_token_with_expiry(minutes=-5)
        response = await client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    async def test_invalid_token_rejected(self, client):
        response = await client.get(
            "/api/v1/users/",
            headers={"Authorization": "Bearer garbage.token.here"},
        )
        assert response.status_code == 401

    async def test_insufficient_permissions(self, authenticated_client):
        # Regular user trying to delete (requires DELETE permission)
        response = await authenticated_client.delete("/api/v1/users/some-id")
        assert response.status_code == 403
```

---

## WebSocket & SSE Testing

```python
# tests/integration/test_websocket.py
import pytest
from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport

async def test_websocket_connection(app):
    async with aconnect_ws(
        "ws://test/api/v1/ws/notifications",
        app,
        transport=ASGIWebSocketTransport(app),
    ) as ws:
        await ws.send_json({"type": "subscribe", "channel": "updates"})
        message = await ws.receive_json()
        assert message["type"] == "subscribed"

# SSE Testing
async def test_sse_stream(client):
    async with client.stream("GET", "/api/v1/events") as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        # Read first event
        async for line in response.aiter_lines():
            if line.startswith("data:"):
                break
```

---

## Coverage & Quality

Run tests with coverage:

```bash
# Run all tests
pytest tests/ -v --cov=app --cov-report=html

# Run only unit tests
pytest tests/unit/ -m unit -v

# Run with parallel execution
pytest tests/ -n auto -v

# Type checking
mypy app/ --strict

# Linting
ruff check .
ruff format --check .
```

### pyproject.toml Quality Tools

```toml
[tool.ruff]
target-version = "py314"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "SIM", "TCH", "RUF"]

[tool.mypy]
python_version = "3.14"
strict = true
plugins = ["pydantic.mypy"]

[tool.mypy.plugins.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true
```
