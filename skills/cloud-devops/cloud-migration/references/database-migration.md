# Database Migration Reference

## Table of Contents
1. Migration Strategy Selection
2. AWS DMS & SCT
3. Azure DMS
4. Zero-Downtime Migration Patterns
5. Validation & Testing

---

## 1. Migration Strategy Selection

| Scenario | Strategy | Downtime | Complexity |
|----------|---------|----------|-----------|
| Same engine (PG→PG) | Native replication + DMS | Minutes | Low |
| Different engine (Oracle→PG) | SCT + DMS | Hours | High |
| Small database (<10 GB) | pg_dump/restore, mysqldump | Minutes-hours | Low |
| Large database (>100 GB) | DMS CDC, native streaming replication | Minutes | Medium |
| Complex schema conversion | SCT assessment → manual fixes → DMS | Days-weeks | High |

### Migration Decision Tree
```
Same database engine?
├── Yes → Use native replication or DMS (homogeneous)
│         Zero-downtime possible with CDC
└── No  → Schema conversion required
          ├── AWS: SCT (Schema Conversion Tool) → DMS
          └── Azure: DMS + manual schema work
              
Database size?
├── < 10 GB → Dump/restore (fastest, simplest)
├── 10-500 GB → DMS with full load + CDC
└── > 500 GB → DMS with parallel full load + CDC, or native backup/restore + replication
```

---

## 2. AWS DMS & SCT

### DMS Architecture
```
Source DB → DMS Replication Instance → Target DB
              (reads changes via)
              CDC (Change Data Capture)
```

### DMS Setup (Terraform)
```hcl
resource "aws_dms_replication_instance" "main" {
  replication_instance_id    = "${var.project}-dms"
  replication_instance_class = "dms.r6i.xlarge"
  allocated_storage          = 100
  vpc_security_group_ids     = [aws_security_group.dms.id]
  replication_subnet_group_id = aws_dms_replication_subnet_group.main.id
  multi_az                   = true
  publicly_accessible        = false

  tags = { Name = "${var.project}-dms" }
}

resource "aws_dms_replication_subnet_group" "main" {
  replication_subnet_group_id          = "${var.project}-dms-subnet"
  replication_subnet_group_description = "DMS subnet group"
  subnet_ids                           = module.vpc.private_subnets
}

# Source endpoint (on-premises PostgreSQL)
resource "aws_dms_endpoint" "source" {
  endpoint_id   = "${var.project}-source"
  endpoint_type = "source"
  engine_name   = "postgres"
  server_name   = var.source_db_host
  port          = 5432
  database_name = var.source_db_name
  username      = var.source_db_username
  password      = var.source_db_password
  ssl_mode      = "require"
}

# Target endpoint (RDS PostgreSQL)
resource "aws_dms_endpoint" "target" {
  endpoint_id   = "${var.project}-target"
  endpoint_type = "target"
  engine_name   = "postgres"
  server_name   = aws_db_instance.main.address
  port          = 5432
  database_name = aws_db_instance.main.db_name
  username      = var.target_db_username
  password      = var.target_db_password
  ssl_mode      = "require"
}

# Replication task (full load + CDC)
resource "aws_dms_replication_task" "main" {
  replication_task_id      = "${var.project}-migration"
  migration_type           = "full-load-and-cdc"
  replication_instance_arn = aws_dms_replication_instance.main.replication_instance_arn
  source_endpoint_arn      = aws_dms_endpoint.source.endpoint_arn
  target_endpoint_arn      = aws_dms_endpoint.target.endpoint_arn
  table_mappings           = jsonencode({
    rules = [{
      rule-type = "selection"
      rule-id   = "1"
      rule-name = "all-tables"
      object-locator = {
        schema-name = "public"
        table-name  = "%"
      }
      rule-action = "include"
    }]
  })

  replication_task_settings = jsonencode({
    TargetMetadata = {
      FullLobMode  = false
      LobChunkSize = 64
    }
    FullLoadSettings = {
      TargetTablePrepMode = "DO_NOTHING"
      MaxFullLoadSubTasks = 8
    }
    Logging = {
      EnableLogging = true
    }
  })

  tags = { Name = "${var.project}-migration-task" }
}
```

### Schema Conversion Tool (SCT)
```
Source Schema (Oracle/SQL Server)
  → SCT Assessment Report
    → Auto-converted items (~80%)
    → Manual conversion needed (~20%)
      → Fix incompatible stored procedures
      → Fix data type mismatches
      → Fix Oracle-specific syntax
  → Generate target schema DDL
  → Apply to target database
  → Run DMS for data migration
```

### Common Schema Conversion Issues

| Source | Target | Issue | Fix |
|--------|--------|-------|-----|
| Oracle `NUMBER` | PG `NUMERIC` | Precision differences | Explicit precision mapping |
| Oracle `VARCHAR2` | PG `VARCHAR` | Length semantics | Review max lengths |
| SQL Server `IDENTITY` | PG `SERIAL/GENERATED` | Syntax difference | Auto-converted |
| Oracle packages | PG functions | No package concept | Split into separate functions |
| Oracle `CONNECT BY` | PG `WITH RECURSIVE` | Hierarchical query syntax | Rewrite queries |
| SQL Server `TOP` | PG `LIMIT` | Pagination syntax | Auto-converted |

---

## 3. Azure DMS

### Azure DMS Setup
```hcl
resource "azurerm_database_migration_service" "main" {
  name                = "${var.project}-dms"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.dms.id
  sku_name            = "Standard_4vCores"
}
```

### Azure DMS Migration (CLI)
```bash
# Create migration project
az dms project create \
  --service-name myapp-dms \
  --resource-group migration-rg \
  --name pg-migration \
  --source-platform PostgreSQL \
  --target-platform AzureDbForPostgreSQL

# Create and start migration task
az dms project task create \
  --service-name myapp-dms \
  --resource-group migration-rg \
  --project-name pg-migration \
  --name full-migration \
  --source-connection-json @source.json \
  --target-connection-json @target.json \
  --database-options-json @db-options.json \
  --task-type MigratePostgreSql
```

---

## 4. Zero-Downtime Migration Patterns

### Pattern 1: DMS CDC (Change Data Capture)
```
Phase 1: Full Load
  Source DB ──(full copy)──→ DMS ──→ Target DB (cloud)
  Application still using Source DB

Phase 2: CDC (Continuous replication)
  Source DB ──(changes)──→ DMS ──→ Target DB (stays in sync)
  Application still using Source DB

Phase 3: Cutover (minutes of downtime)
  1. Stop application writes
  2. Wait for CDC to catch up (seconds)
  3. Verify data consistency
  4. Switch application to Target DB
  5. Resume application
  Total downtime: 2-10 minutes
```

### Pattern 2: Blue-Green with Read Replicas
```
Phase 1: Create cloud replica
  Source DB ──(native replication)──→ Cloud DB (read replica)

Phase 2: Application dual-reads
  App reads from both Source and Cloud DB
  Verify consistency

Phase 3: Promote and switch
  1. Promote Cloud DB to primary
  2. Update application connection string
  3. Verify writes going to Cloud DB
  Total downtime: 1-5 minutes (DNS change)
```

### Pattern 3: Application-Level Migration (Zero Downtime)
```
Phase 1: Dual-write
  App writes to BOTH Source and Target DB

Phase 2: Backfill
  Copy historical data to Target DB
  Verify consistency

Phase 3: Switch reads
  App reads from Target DB

Phase 4: Stop dual-write
  App writes only to Target DB
  Decommission Source DB
  
  Downtime: 0 (but complex application changes)
```

---

## 5. Validation & Testing

### Data Validation Checklist

| Check | Method | Tool |
|-------|--------|------|
| Row counts match | `SELECT COUNT(*)` on both | SQL script |
| Checksum match | Hash comparison on key tables | DMS validation, custom script |
| Schema match | Compare DDL | SCT, pg_dump --schema-only |
| Constraints intact | Check FK, unique, check constraints | `\d+ table` / information_schema |
| Sequences correct | Verify sequence current values | `SELECT last_value FROM seq` |
| Indexes exist | Compare index list | `\di` / sys.indexes |
| Permissions match | Compare grants/roles | Role comparison script |
| Application smoke test | Run key user journeys | Automated test suite |
| Performance baseline | Compare query performance | pgbench, custom benchmarks |
| Data integrity | Spot-check specific records | Application-level verification |

### Migration Testing Phases

| Phase | What | Environment |
|-------|------|-------------|
| **Unit test** | Schema conversion, data types | Dev |
| **Integration test** | App + new DB, all features | Staging |
| **Performance test** | Load test against cloud DB | Staging (production-like) |
| **Failover test** | Test rollback procedure | Staging |
| **Dress rehearsal** | Full cutover simulation | Pre-production |
| **Production cutover** | Actual migration | Production |

### Pre-Cutover Validation Script
```bash
#!/bin/bash
echo "=== Pre-Cutover Validation ==="

# Row counts
echo "Checking row counts..."
SOURCE_COUNT=$(psql $SOURCE_URL -t -c "SELECT SUM(n_live_tup) FROM pg_stat_user_tables")
TARGET_COUNT=$(psql $TARGET_URL -t -c "SELECT SUM(n_live_tup) FROM pg_stat_user_tables")
echo "Source: $SOURCE_COUNT | Target: $TARGET_COUNT"
[ "$SOURCE_COUNT" = "$TARGET_COUNT" ] && echo "✅ Row counts match" || echo "❌ Row count mismatch!"

# Replication lag
echo "Checking replication lag..."
LAG=$(aws dms describe-replication-tasks --query 'ReplicationTasks[0].ReplicationTaskStats.CDCLatencyTarget')
echo "CDC Lag: ${LAG}s"
[ "$LAG" -lt 5 ] && echo "✅ Lag acceptable" || echo "❌ Lag too high!"

# Application health
echo "Running smoke tests..."
curl -sf https://staging.example.com/health && echo "✅ App healthy" || echo "❌ App unhealthy!"

echo "=== Validation Complete ==="
```



---
