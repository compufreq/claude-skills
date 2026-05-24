# Authentication & Security Reference

## Table of Contents
1. [JWT Authentication](#jwt-authentication)
2. [OAuth2 Flows](#oauth2-flows)
3. [API Key Authentication](#api-key-authentication)
4. [Role-Based Access Control (RBAC)](#role-based-access-control)
5. [Security Middleware & Headers](#security-middleware--headers)
6. [Password Hashing](#password-hashing)
7. [Rate Limiting](#rate-limiting)
8. [CORS Configuration](#cors-configuration)

---

## JWT Authentication

### Token Creation & Validation

```python
# app/auth/jwt.py
from datetime import datetime, timedelta, timezone
from uuid import UUID
import jwt
from pydantic import BaseModel
from app.config import settings

class TokenPayload(BaseModel):
    sub: str          # User ID
    exp: datetime
    iat: datetime
    type: str         # "access" or "refresh"
    roles: list[str] = []

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

def create_access_token(user_id: UUID, roles: list[str]) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "iat": now,
        "type": "access",
        "roles": roles,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

def create_refresh_token(user_id: UUID) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "exp": now + timedelta(days=settings.refresh_token_expire_days),
        "iat": now,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

def create_token_pair(user_id: UUID, roles: list[str]) -> TokenPair:
    return TokenPair(
        access_token=create_access_token(user_id, roles),
        refresh_token=create_refresh_token(user_id),
    )

def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### FastAPI Dependency for JWT

```python
# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt import decode_token
from app.services.user_service import UserService

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_service: UserService = Depends(get_user_service),
):
    payload = decode_token(credentials.credentials)
    if payload.type != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    user = await user_service.get_by_id(payload.sub)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user
```

---

## OAuth2 Flows

### Password Flow (for first-party clients)

```python
# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.jwt import create_token_pair
from app.auth.passwords import verify_password
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return create_token_pair(user.id, user.roles)

@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    user_service: UserService = Depends(get_user_service),
):
    payload = decode_token(refresh_token)
    if payload.type != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    user = await user_service.get_by_id(payload.sub)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return create_token_pair(user.id, user.roles)
```

### OAuth2 with External Providers (Google, GitHub)

```python
# app/auth/oauth2.py
from httpx import AsyncClient
from app.config import settings

class OAuth2Provider:
    def __init__(self, client_id: str, client_secret: str,
                 authorize_url: str, token_url: str, userinfo_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorize_url = authorize_url
        self.token_url = token_url
        self.userinfo_url = userinfo_url

    def get_authorize_url(self, redirect_uri: str, state: str) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
            "scope": "openid email profile",
        }
        return f"{self.authorize_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

    async def exchange_code(self, code: str, redirect_uri: str) -> dict:
        async with AsyncClient() as client:
            response = await client.post(self.token_url, data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            })
            response.raise_for_status()
            return response.json()

    async def get_user_info(self, access_token: str) -> dict:
        async with AsyncClient() as client:
            response = await client.get(
                self.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()

# Pre-configured providers
google_oauth = OAuth2Provider(
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    token_url="https://oauth2.googleapis.com/token",
    userinfo_url="https://www.googleapis.com/oauth2/v2/userinfo",
)
```

---

## API Key Authentication

```python
# app/auth/api_key.py
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.db.redis import get_redis

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key_user(
    api_key: str | None = Security(api_key_header),
):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    redis = await get_redis()
    # API keys stored in Redis for fast lookup: api_key:<key> -> user_id
    user_id = await redis.get(f"api_key:{api_key}")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user_id

# Generate API keys
import secrets

def generate_api_key(prefix: str = "sk") -> str:
    """Generate a secure API key like sk_live_abc123..."""
    return f"{prefix}_live_{secrets.token_urlsafe(32)}"
```

### Supporting Multiple Auth Methods

```python
# app/dependencies.py
from fastapi import Depends, HTTPException

async def get_current_user_flexible(
    bearer_user = Depends(get_current_user_optional),
    api_key_user = Depends(get_api_key_user_optional),
):
    """Accept either JWT bearer token or API key."""
    user = bearer_user or api_key_user
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user
```

---

## Role-Based Access Control

```python
# app/auth/permissions.py
from enum import StrEnum
from functools import wraps
from fastapi import HTTPException, status

class Role(StrEnum):
    ADMIN = "admin"
    USER = "user"
    SERVICE = "service"
    READONLY = "readonly"

class Permission(StrEnum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

# Role -> permissions mapping
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN},
    Role.USER: {Permission.READ, Permission.WRITE},
    Role.SERVICE: {Permission.READ, Permission.WRITE},
    Role.READONLY: {Permission.READ},
}

def require_permissions(*permissions: Permission):
    """Dependency that checks the current user has required permissions."""
    async def checker(current_user = Depends(get_current_user)):
        user_permissions = set()
        for role in current_user.roles:
            user_permissions |= ROLE_PERMISSIONS.get(Role(role), set())

        missing = set(permissions) - user_permissions
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(missing)}",
            )
        return current_user
    return checker

# Usage in routes:
@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user = Depends(require_permissions(Permission.DELETE)),
    service: UserService = Depends(get_user_service),
):
    await service.delete(user_id)
```

---

## Password Hashing

```python
# app/auth/passwords.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

---

## Rate Limiting

```python
# app/middleware/rate_limit.py
from fastapi import Request, HTTPException
from app.db.redis import get_redis

async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for health checks
    if request.url.path in ("/health", "/ready"):
        return await call_next(request)

    client_ip = request.client.host
    redis = await get_redis()
    key = f"rate_limit:{client_ip}:{request.url.path}"

    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, 60)  # 60-second window

    if current > 100:  # 100 requests per minute
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = str(max(0, 100 - current))
    return response
```

---

## CORS Configuration

```python
# app/middleware/cors.py
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,      # Explicit list, never ["*"] in prod
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
        max_age=600,
    )
```

---

## Security Headers Middleware

```python
# app/middleware/security_headers.py
from fastapi import Request

async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response
```
