# Caching Reference

## Table of Contents
1. Caching Patterns
2. AWS ElastiCache
3. Azure Cache for Redis
4. Application Integration
5. Cache Management

---

## 1. Caching Patterns

### Cache-Aside (Lazy Loading)
```
App reads cache → miss → read DB → write cache → return
App reads cache → hit → return (fast)
```
```python
def get_user(user_id):
    cached = redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)

    user = db.query("SELECT * FROM users WHERE id = %s", user_id)
    redis.setex(f"user:{user_id}", 300, json.dumps(user))  # TTL 5 min
    return user
```

### Write-Through
```
App writes DB + cache simultaneously
App reads cache → always fresh
```
```python
def update_user(user_id, data):
    db.execute("UPDATE users SET ... WHERE id = %s", user_id)
    redis.setex(f"user:{user_id}", 300, json.dumps(data))
```

### Write-Behind (Write-Back)
```
App writes cache → async write to DB (batched)
Faster writes, risk of data loss if cache fails
```

### Pattern Selection

| Pattern | Read Performance | Write Performance | Consistency | Complexity |
|---------|-----------------|-------------------|-------------|-----------|
| Cache-Aside | Good (after warm) | N/A | Eventual | Low |
| Write-Through | Good | Slower (2 writes) | Strong | Medium |
| Write-Behind | Good | Fast | Eventual (risk) | High |
| Read-Through | Good | N/A | Eventual | Medium |

### What to Cache

| Good for Caching | Bad for Caching |
|-------------------|-----------------|
| User sessions | Frequently changing data |
| API responses | Unique per-request data |
| Database query results | Large blobs (> 1MB) |
| Computed results | Data requiring strict consistency |
| Rate limit counters | Sensitive data (unless encrypted) |
| Feature flags | |
| Configuration | |

---

## 2. AWS ElastiCache

### Redis Cluster (Terraform)
```hcl
resource "aws_elasticache_replication_group" "main" {
  replication_group_id = "${var.project}-${var.environment}"
  description          = "${var.project} Redis cluster"
  node_type            = var.environment == "production" ? "cache.r7g.large" : "cache.t4g.micro"
  num_cache_clusters   = var.environment == "production" ? 3 : 1
  port                 = 6379

  engine               = "redis"
  engine_version       = "7.1"
  parameter_group_name = aws_elasticache_parameter_group.main.name

  automatic_failover_enabled = var.environment == "production"
  multi_az_enabled           = var.environment == "production"
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = var.redis_auth_token

  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  snapshot_retention_limit = var.environment == "production" ? 7 : 0
  snapshot_window          = "03:00-05:00"
  maintenance_window       = "mon:05:00-mon:06:00"

  auto_minor_version_upgrade = true
  apply_immediately          = var.environment != "production"

  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis.name
    destination_type = "cloudwatch-logs"
    log_format       = "json"
    log_type         = "slow-log"
  }

  tags = { Name = "${var.project}-${var.environment}-redis" }
}

resource "aws_elasticache_parameter_group" "main" {
  name   = "${var.project}-${var.environment}-redis7"
  family = "redis7"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }
  parameter {
    name  = "notify-keyspace-events"
    value = "Ex"    # Expired key notifications
  }
}

resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project}-${var.environment}"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "redis" {
  name   = "${var.project}-${var.environment}-redis"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "Redis from app"
  }
}
```

---

## 3. Azure Cache for Redis

### Production Redis (Terraform)
```hcl
resource "azurerm_redis_cache" "main" {
  name                = "${var.project}-${var.environment}-redis"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = var.environment == "production" ? 2 : 0
  family              = var.environment == "production" ? "P" : "C"    # P = Premium, C = Standard
  sku_name            = var.environment == "production" ? "Premium" : "Basic"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"

  redis_configuration {
    maxmemory_policy       = "allkeys-lru"
    maxmemory_reserved     = 50
    maxfragmentationmemory_reserved = 50
    rdb_backup_enabled     = var.environment == "production"
    rdb_backup_frequency   = 60
    rdb_backup_max_snapshot_count = 1
  }

  # Premium features
  zones             = var.environment == "production" ? ["1", "2", "3"] : null
  replicas_per_master = var.environment == "production" ? 1 : null
  shard_count       = var.environment == "production" ? 2 : null    # Cluster mode

  subnet_id = var.environment == "production" ? azurerm_subnet.data.id : null

  tags = {
    Environment = var.environment
    Project     = var.project
  }
}

# Private endpoint for Premium tier
resource "azurerm_private_endpoint" "redis" {
  count               = var.environment == "production" ? 1 : 0
  name                = "${var.project}-redis-pe"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.data.id

  private_service_connection {
    name                           = "redis-connection"
    private_connection_resource_id = azurerm_redis_cache.main.id
    subresource_names              = ["redisCache"]
    is_manual_connection           = false
  }
}
```

---

## 4. Application Integration

### Python (redis-py)
```python
import redis
import json
from functools import wraps

# Connection
pool = redis.ConnectionPool(
    host='redis.example.com',
    port=6379,
    password='auth-token',
    ssl=True,
    decode_responses=True,
    max_connections=20,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
)
r = redis.Redis(connection_pool=pool)

# Cache decorator
def cached(ttl=300, prefix="cache"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached_value = r.get(key)
            if cached_value:
                return json.loads(cached_value)
            result = func(*args, **kwargs)
            r.setex(key, ttl, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator

@cached(ttl=300, prefix="users")
def get_user(user_id):
    return db.query("SELECT * FROM users WHERE id = %s", user_id)
```

### Node.js (ioredis)
```javascript
const Redis = require('ioredis');
const redis = new Redis({
  host: process.env.REDIS_HOST,
  port: 6379,
  password: process.env.REDIS_PASSWORD,
  tls: { rejectUnauthorized: true },
  retryStrategy: (times) => Math.min(times * 100, 3000),
  maxRetriesPerRequest: 3,
});

// Cache-aside pattern
async function getUser(userId) {
  const cached = await redis.get(`user:${userId}`);
  if (cached) return JSON.parse(cached);

  const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);
  await redis.setex(`user:${userId}`, 300, JSON.stringify(user));
  return user;
}

// Rate limiting
async function checkRateLimit(clientId, limit = 100, windowSec = 60) {
  const key = `ratelimit:${clientId}`;
  const current = await redis.incr(key);
  if (current === 1) await redis.expire(key, windowSec);
  return current <= limit;
}

// Session store
async function setSession(sessionId, data, ttlSec = 3600) {
  await redis.setex(`session:${sessionId}`, ttlSec, JSON.stringify(data));
}

async function getSession(sessionId) {
  const data = await redis.get(`session:${sessionId}`);
  return data ? JSON.parse(data) : null;
}
```

---

## 5. Cache Management

### Eviction Policies

| Policy | Description | Use Case |
|--------|------------|---------|
| `allkeys-lru` | Evict least recently used | General purpose (recommended) |
| `allkeys-lfu` | Evict least frequently used | Popular items stay cached |
| `volatile-lru` | LRU among keys with TTL | Mixed data (some permanent) |
| `volatile-ttl` | Evict keys closest to expiry | TTL-driven expiry |
| `noeviction` | Return error when full | When you can't lose data |

### Cache Invalidation Strategies

| Strategy | How | Consistency | Complexity |
|----------|-----|------------|-----------|
| TTL-based | Keys expire automatically | Eventual (max = TTL) | Low |
| Event-driven | Delete on write/update | Near-real-time | Medium |
| Version-based | Key includes version number | Strong | Medium |
| Pub/Sub | Broadcast invalidation | Near-real-time | High |

### Monitoring Metrics

| Metric | Healthy | Action if Unhealthy |
|--------|---------|-------------------|
| Hit rate | > 80% | Review TTLs, cache more |
| Memory usage | < 80% | Scale up or evict more |
| Evictions | Low, steady | Scale up or reduce TTLs |
| Connection count | < max_connections | Use pooling, increase limit |
| Latency (P99) | < 5ms | Check network, reduce key sizes |
| CPU | < 70% | Scale up node type |



---
