# Deployment Reference

## Table of Contents
1. [Dockerfile (Production)](#dockerfile-production)
2. [Dockerfile (Development)](#dockerfile-development)
3. [Docker Compose](#docker-compose)
4. [Environment Configuration](#environment-configuration)
5. [CI/CD Pipelines](#cicd-pipelines)
6. [AWS Deployment](#aws-deployment)
7. [Health Checks](#health-checks)

---

## Dockerfile (Production)

Multi-stage build optimized for size and security:

```dockerfile
# Dockerfile
FROM python:3.14-slim AS builder

WORKDIR /build

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first (layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN uv sync --frozen --no-dev --no-editable

# --- Production stage ---
FROM python:3.14-slim AS production

# Security: run as non-root
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /build/.venv /app/.venv

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## Dockerfile (Development)

```dockerfile
# Dockerfile.dev
FROM python:3.14-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

---

## Docker Compose

### Development Stack

```yaml
# docker-compose.dev.yml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - backend

  postgres:
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: ${DB_USER:-app}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-secret}
      POSTGRES_DB: ${DB_NAME:-appdb}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-app}"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - backend

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - backend

  mongo:
    image: mongo:7
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER:-admin}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD:-secret}
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    networks:
      - backend

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.17.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data
    networks:
      - backend

volumes:
  postgres_data:
  redis_data:
  mongo_data:
  es_data:

networks:
  backend:
    driver: bridge
```

### Production Stack

```yaml
# docker-compose.yml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file: .env
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "1.0"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - backend
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

Only include the database services you need — remove mongo/elasticsearch blocks if the
project doesn't use them.

---

## Environment Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "FastAPI Service"
    debug: bool = False
    environment: str = "production"  # development, staging, production

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # Database (PostgreSQL)
    database_url: str = "postgresql+asyncpg://app:secret@localhost:5432/appdb"

    # MongoDB (optional)
    mongodb_url: str = ""
    mongodb_db_name: str = "appdb"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Elasticsearch (optional)
    elasticsearch_url: str = ""
    es_user: str = ""
    es_password: str = ""
    es_verify_certs: bool = True

    # Auth
    secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # OAuth2 (optional)
    google_client_id: str = ""
    google_client_secret: str = ""

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # Logging
    log_level: str = "INFO"

settings = Settings()
```

### .env.example

```env
# Application
APP_NAME=my-service
DEBUG=false
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql+asyncpg://app:secret@localhost:5432/appdb

# Redis
REDIS_URL=redis://localhost:6379/0

# Auth
SECRET_KEY=change-me-to-a-real-secret-key-at-least-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Logging
LOG_LEVEL=INFO
```

---

## CI/CD Pipelines

### GitHub Actions CI

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd="pg_isready -U test"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd="redis-cli ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Set up Python
        run: uv python install 3.14

      - name: Install dependencies
        run: uv sync --frozen

      - name: Lint (ruff)
        run: uv run ruff check .

      - name: Format check (ruff)
        run: uv run ruff format --check .

      - name: Type check (mypy)
        run: uv run mypy app/

      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret-key-for-ci-minimum-32-chars
        run: uv run pytest tests/ -v --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
```

### GitHub Actions CD

```yaml
# .github/workflows/cd.yml
name: CD

on:
  push:
    tags: ["v*"]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}

      - name: Login to ECR
        id: ecr-login
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, push
        env:
          REGISTRY: ${{ steps.ecr-login.outputs.registry }}
          REPO: ${{ vars.ECR_REPOSITORY }}
          TAG: ${{ github.ref_name }}
        run: |
          docker build -t $REGISTRY/$REPO:$TAG -t $REGISTRY/$REPO:latest .
          docker push $REGISTRY/$REPO:$TAG
          docker push $REGISTRY/$REPO:latest

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster ${{ vars.ECS_CLUSTER }} \
            --service ${{ vars.ECS_SERVICE }} \
            --force-new-deployment
```

---

## AWS Deployment

### ECS Fargate Task Definition (key parts)

```json
{
  "containerDefinitions": [
    {
      "name": "api",
      "image": "<account>.dkr.ecr.<region>.amazonaws.com/my-service:latest",
      "portMappings": [{ "containerPort": 8000, "protocol": "tcp" }],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 15
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/my-service",
          "awslogs-region": "eu-central-1",
          "awslogs-stream-prefix": "api"
        }
      },
      "secrets": [
        { "name": "SECRET_KEY", "valueFrom": "arn:aws:ssm:<region>:<account>:parameter/my-service/secret-key" },
        { "name": "DATABASE_URL", "valueFrom": "arn:aws:ssm:<region>:<account>:parameter/my-service/database-url" }
      ]
    }
  ],
  "cpu": "512",
  "memory": "1024",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"]
}
```

### Infrastructure Notes

- Store secrets in AWS Systems Manager Parameter Store or Secrets Manager, never in env files or code.
- Use ALB (Application Load Balancer) in front of ECS tasks for TLS termination and health checks.
- For databases, prefer RDS PostgreSQL (with async connections via asyncpg) or DocumentDB for MongoDB workloads.
- Use ElastiCache for Redis in production.
- Configure auto-scaling based on CPU/memory or request count.

---

## Health Checks

```python
# app/api/v1/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.db.redis import get_redis

router = APIRouter(tags=["health"])

@router.get("/health")
async def health():
    """Basic liveness check."""
    return {"status": "ok"}

@router.get("/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    """Readiness check — verifies all dependencies are reachable."""
    checks = {}

    # PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = f"error: {str(e)}"

    # Redis
    try:
        redis = await get_redis()
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"

    all_ok = all(v == "ok" for v in checks.values())
    return {"status": "ok" if all_ok else "degraded", "checks": checks}
```
