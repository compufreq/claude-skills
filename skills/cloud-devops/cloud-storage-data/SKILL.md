---
name: cloud-storage-data
description: >
  Comprehensive cloud storage and data services skill covering object storage, relational databases,
  NoSQL databases, and caching across AWS and Azure. Use this skill whenever the user mentions S3,
  Azure Blob, object storage, bucket policy, lifecycle rules, cross-region replication, RDS, Aurora,
  Azure SQL, Cloud SQL, database, PostgreSQL, MySQL, read replica, Multi-AZ, failover, DynamoDB,
  Cosmos DB, NoSQL, partition key, sort key, GSI, LSI, consistency model, ElastiCache, Azure Cache
  for Redis, Redis, Memcached, caching strategy, cache-aside, write-through, TTL, eviction,
  database migration, connection pooling, database proxy, RDS Proxy, or any request involving
  provisioning storage or database resources, designing data models, implementing caching layers,
  or optimizing data access patterns in the cloud. Also trigger for data backup strategies,
  disaster recovery for databases, database performance tuning, or storage cost optimization.
---

# Cloud Storage & Data

A production-grade skill for designing and implementing storage, database, and caching
solutions across AWS and Azure.

## Quick Reference

| Service Type | AWS | Azure | Reference |
|-------------|-----|-------|-----------|
| Object Storage | S3 | Blob Storage | `references/object-storage.md` |
| Relational DB | RDS, Aurora | SQL Database | `references/relational-db.md` |
| NoSQL DB | DynamoDB | Cosmos DB | `references/nosql-db.md` |
| Caching | ElastiCache | Cache for Redis | `references/caching.md` |

## Data Service Decision Framework

```
What kind of data?
│
├── Files, images, backups, logs
│   └── Object Storage (S3 / Blob)
│
├── Structured data with relationships
│   ├── Need transactions, joins, complex queries → Relational (RDS / SQL)
│   ├── Need global scale, single-digit ms → DynamoDB / Cosmos DB
│   └── Need full-text search → OpenSearch / Cognitive Search
│
├── Session data, leaderboards, rate limiting
│   └── Redis (ElastiCache / Azure Cache)
│
├── Time-series metrics
│   └── Timestream / Azure Data Explorer
│
└── Document/JSON storage
    ├── Flexible schema, moderate scale → MongoDB Atlas / Cosmos DB
    └── Simple key-value → DynamoDB / Cosmos DB (Table API)
```

### Service Comparison

| Factor | S3/Blob | RDS/SQL | DynamoDB/Cosmos | ElastiCache/Redis |
|--------|---------|---------|-----------------|-------------------|
| Latency | 50-100ms | 1-10ms | 1-10ms | <1ms |
| Throughput | Very high | Medium | Very high | Very high |
| Max size | 5TB/object | 64TB | 400KB/item | ~512MB/key |
| Query | GET by key | SQL | Key/index lookup | Key lookup |
| Cost model | Per GB + requests | Per hour + storage | Per RCU/WCU or on-demand | Per node/hour |
| Best for | Files, archives | OLTP, reporting | High-scale OLTP | Hot data, sessions |

---

## Cost Optimization

### Storage Tiers

| Tier | AWS S3 | Azure Blob | Use Case |
|------|--------|-----------|---------|
| Hot | Standard | Hot | Frequently accessed |
| Warm | IA (Infrequent Access) | Cool | Monthly access |
| Cold | Glacier Instant | Cold | Quarterly access |
| Archive | Glacier Deep Archive | Archive | Yearly access, compliance |

### Database Cost Strategies
1. **Reserved instances** for production databases (30-60% savings)
2. **Aurora Serverless v2 / SQL Serverless** for dev/staging (pay per use)
3. **Read replicas** to offload read traffic from primary
4. **DynamoDB on-demand** for unpredictable workloads
5. **Right-size instances** — monitor CPU/memory, downsize if under-utilized
6. **Delete unused snapshots** — old backups accumulate cost

---

## Scripts

### generate_data_terraform.py
```bash
python scripts/generate_data_terraform.py \
  --provider aws|azure \
  --services s3,rds,dynamodb,elasticache \
  --environment production \
  --project myapp \
  --output ./data/
```

---

## Best Practices

1. **Encrypt everything at rest** — KMS/CMK for databases, SSE for storage
2. **Encrypt in transit** — TLS for all connections, enforce SSL on databases
3. **Automated backups** — enable with appropriate retention (7-35 days)
4. **Multi-AZ for production databases** — automatic failover
5. **Connection pooling** — use RDS Proxy / PgBouncer to manage connections
6. **Lifecycle policies on object storage** — auto-transition to cheaper tiers
7. **Monitor and alert** — CloudWatch/Azure Monitor for IOPS, connections, latency
8. **Point-in-time recovery** — enable for all production databases
9. **Test restore procedures** — backups are useless if you can't restore
10. **Least privilege access** — IAM policies / RBAC scoped to specific resources



---
