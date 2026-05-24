# Docker Reference

## Table of Contents
1. Dockerfile Best Practices
2. Multi-Stage Builds
3. Docker Compose
4. Image Optimization
5. Security Hardening

---

## 1. Dockerfile Best Practices

### Production Dockerfile Template
```dockerfile
# syntax=docker/dockerfile:1

# ── Build Stage ─────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

# Install dependencies first (cache layer)
COPY package.json package-lock.json ./
RUN npm ci --production=false

# Copy source and build
COPY . .
RUN npm run build

# Prune dev dependencies
RUN npm prune --production

# ── Production Stage ────────────────────────────────────
FROM node:20-alpine AS production

# Security: non-root user
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser

WORKDIR /app

# Copy only production artifacts
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/package.json ./

# Security: read-only filesystem where possible
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Layer Ordering (Cache Optimization)
```dockerfile
# GOOD — changes less often at top, more often at bottom
FROM node:20-alpine
WORKDIR /app

# 1. System deps (rarely change)
RUN apk add --no-cache curl

# 2. Package manifest (changes on dep updates)
COPY package.json package-lock.json ./

# 3. Install deps (cached if manifests unchanged)
RUN npm ci

# 4. Source code (changes on every commit)
COPY . .

# 5. Build (re-runs on source change)
RUN npm run build
```

### .dockerignore
```
node_modules
npm-debug.log
.git
.github
.env
.env.*
*.md
docs/
tests/
coverage/
.vscode/
.idea/
Dockerfile
docker-compose*.yml
.dockerignore
```

---

## 2. Multi-Stage Builds

### Python (FastAPI)
```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
COPY . .

FROM python:3.12-slim
RUN useradd -m -r appuser
WORKDIR /app
COPY --from=builder /install /usr/local
COPY --from=builder /app .
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Go
```dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /bin/app ./cmd/app

FROM scratch
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /bin/app /app
USER 65534:65534
EXPOSE 8080
ENTRYPOINT ["/app"]
```

### Java (Spring Boot)
```dockerfile
FROM eclipse-temurin:21-jdk AS builder
WORKDIR /app
COPY gradle/ gradle/
COPY gradlew build.gradle* settings.gradle* ./
RUN ./gradlew dependencies --no-daemon
COPY src/ src/
RUN ./gradlew bootJar --no-daemon -x test
RUN java -Djarmode=tools -jar build/libs/*.jar extract --layers --destination extracted

FROM eclipse-temurin:21-jre
RUN useradd -m -r appuser
WORKDIR /app
COPY --from=builder /app/extracted/dependencies/ ./
COPY --from=builder /app/extracted/spring-boot-loader/ ./
COPY --from=builder /app/extracted/snapshot-dependencies/ ./
COPY --from=builder /app/extracted/application/ ./
USER appuser
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

---

## 3. Docker Compose

### Production-Like Compose
```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
      target: production
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://user:pass@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d myapp"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    command: redis-server --appendonly yes

volumes:
  pgdata:
  redisdata:
```

### Development Compose Override
```yaml
# docker-compose.override.yml (auto-loaded in development)
services:
  app:
    build:
      target: builder
    volumes:
      - .:/app
      - /app/node_modules    # Anonymous volume to preserve container's node_modules
    command: npm run dev
    environment:
      - NODE_ENV=development
      - DEBUG=app:*
    ports:
      - "9229:9229"          # Node.js debugger
```

---

## 4. Image Optimization

### Size Reduction

| Base Image | Size | Use Case |
|-----------|------|---------|
| `ubuntu:24.04` | ~78MB | When you need apt packages |
| `node:20` | ~350MB | Development |
| `node:20-slim` | ~200MB | Production (Debian minimal) |
| `node:20-alpine` | ~130MB | Production (smallest with shell) |
| `gcr.io/distroless/nodejs20` | ~120MB | Production (no shell, most secure) |
| `scratch` | 0MB | Go binaries (statically compiled) |

### Best Practices
- Use `.dockerignore` to exclude unnecessary files
- Combine `RUN` commands to reduce layers: `RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*`
- Use `--no-cache-dir` with pip, `--no-cache` with apk
- Remove build tools in the same layer they're installed
- Use multi-stage builds — final image has only runtime

---

## 5. Security Hardening

### Non-Root User
```dockerfile
# Alpine
RUN addgroup -g 1001 appgroup && adduser -u 1001 -G appgroup -s /bin/sh -D appuser
USER appuser

# Debian
RUN useradd -m -r -u 1001 appuser
USER appuser

# Numeric (works with any base)
USER 1001:1001
```

### Read-Only Filesystem
```yaml
# In Kubernetes
securityContext:
  readOnlyRootFilesystem: true

# Writable dirs via emptyDir volumes
volumes:
  - name: tmp
    emptyDir: {}
volumeMounts:
  - name: tmp
    mountPath: /tmp
```

### Image Scanning
```bash
# Trivy
trivy image myapp:latest

# Grype
grype myapp:latest

# Docker Scout
docker scout cves myapp:latest
```

### Signed Images
```bash
# Sign with Cosign (keyless via OIDC)
cosign sign ghcr.io/org/myapp:v1.0.0

# Verify before deploying
cosign verify ghcr.io/org/myapp:v1.0.0
```



---
