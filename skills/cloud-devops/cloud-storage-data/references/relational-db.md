# Relational Database Reference

## Table of Contents
1. AWS RDS / Aurora
2. Azure SQL Database
3. High Availability Patterns
4. Connection Management
5. Backup & Recovery

---

## 1. AWS RDS / Aurora

### Production RDS PostgreSQL
```hcl
resource "aws_db_instance" "main" {
  identifier     = "${var.project}-${var.environment}"
  engine         = "postgres"
  engine_version = "16.3"
  instance_class = var.db_instance_class

  allocated_storage     = var.db_storage
  max_allocated_storage = var.db_storage * 2    # Auto-expand
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.rds.arn

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  multi_az                = var.environment == "production"
  db_subnet_group_name    = aws_db_subnet_group.main.name
  vpc_security_group_ids  = [aws_security_group.db.id]
  publicly_accessible     = false
  port                    = 5432

  backup_retention_period   = var.environment == "production" ? 14 : 3
  backup_window             = "03:00-04:00"
  maintenance_window        = "Mon:04:00-Mon:05:00"
  copy_tags_to_snapshot     = true
  deletion_protection       = var.environment == "production"
  skip_final_snapshot       = var.environment != "production"
  final_snapshot_identifier = "${var.project}-${var.environment}-final"

  performance_insights_enabled          = true
  performance_insights_retention_period = var.environment == "production" ? 731 : 7
  monitoring_interval                   = 60
  monitoring_role_arn                   = aws_iam_role.rds_monitoring.arn
  enabled_cloudwatch_logs_exports       = ["postgresql", "upgrade"]

  parameter_group_name = aws_db_parameter_group.main.name

  tags = { Name = "${var.project}-${var.environment}-postgres" }
}

resource "aws_db_parameter_group" "main" {
  name   = "${var.project}-${var.environment}-pg16"
  family = "postgres16"

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"    # Log queries > 1 second
  }
  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"
  }
  parameter {
    name  = "max_connections"
    value = "200"
  }
}

# Read Replica
resource "aws_db_instance" "replica" {
  count               = var.environment == "production" ? var.read_replica_count : 0
  identifier          = "${var.project}-${var.environment}-replica-${count.index}"
  replicate_source_db = aws_db_instance.main.identifier
  instance_class      = var.replica_instance_class
  storage_encrypted   = true

  performance_insights_enabled = true
  monitoring_interval          = 60
  monitoring_role_arn          = aws_iam_role.rds_monitoring.arn

  tags = { Name = "${var.project}-${var.environment}-replica-${count.index}" }
}

# RDS Proxy (connection pooling)
resource "aws_db_proxy" "main" {
  name                   = "${var.project}-${var.environment}-proxy"
  engine_family          = "POSTGRESQL"
  role_arn               = aws_iam_role.rds_proxy.arn
  vpc_subnet_ids         = module.vpc.private_subnets
  vpc_security_group_ids = [aws_security_group.db.id]
  require_tls            = true
  idle_client_timeout    = 1800

  auth {
    auth_scheme = "SECRETS"
    iam_auth    = "REQUIRED"
    secret_arn  = aws_secretsmanager_secret.db_credentials.arn
  }
}
```

### Aurora PostgreSQL (Higher HA/Performance)
```hcl
resource "aws_rds_cluster" "aurora" {
  cluster_identifier     = "${var.project}-${var.environment}"
  engine                 = "aurora-postgresql"
  engine_version         = "16.1"
  master_username        = var.db_username
  master_password        = var.db_password
  database_name          = var.db_name
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]
  storage_encrypted      = true
  kms_key_id             = aws_kms_key.rds.arn

  backup_retention_period = 14
  preferred_backup_window = "03:00-04:00"
  deletion_protection     = true
  skip_final_snapshot     = false

  serverlessv2_scaling_configuration {
    min_capacity = 0.5    # ACUs — scales to zero-ish
    max_capacity = 16
  }
}

resource "aws_rds_cluster_instance" "aurora" {
  count              = var.environment == "production" ? 3 : 1
  identifier         = "${var.project}-${var.environment}-${count.index}"
  cluster_identifier = aws_rds_cluster.aurora.id
  instance_class     = "db.serverless"    # Aurora Serverless v2
  engine             = aws_rds_cluster.aurora.engine
  engine_version     = aws_rds_cluster.aurora.engine_version

  performance_insights_enabled = true
  monitoring_interval          = 60
  monitoring_role_arn          = aws_iam_role.rds_monitoring.arn
}
```

---

## 2. Azure SQL Database

### Production Azure SQL
```hcl
resource "azurerm_mssql_server" "main" {
  name                         = "${var.project}-${var.environment}-sql"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = var.db_admin_username
  administrator_login_password = var.db_admin_password
  minimum_tls_version          = "1.2"
  public_network_access_enabled = false

  azuread_administrator {
    login_username = "AzureAD Admin"
    object_id      = var.azuread_admin_object_id
  }

  identity { type = "SystemAssigned" }
}

resource "azurerm_mssql_database" "main" {
  name         = "${var.project}-${var.environment}"
  server_id    = azurerm_mssql_server.main.id
  collation    = "SQL_Latin1_General_CP1_CI_AS"
  license_type = "LicenseIncluded"
  sku_name     = var.environment == "production" ? "GP_Gen5_4" : "GP_S_Gen5_1"  # S = Serverless

  max_size_gb = var.environment == "production" ? 100 : 10

  short_term_retention_policy {
    retention_days           = 14
    backup_interval_in_hours = 12
  }

  long_term_retention_policy {
    weekly_retention  = "P4W"
    monthly_retention = "P12M"
    yearly_retention  = "P5Y"
    week_of_year      = 1
  }

  threat_detection_policy {
    state = "Enabled"
  }

  zone_redundant = var.environment == "production"
}

# Failover Group (Multi-Region HA)
resource "azurerm_mssql_failover_group" "main" {
  count     = var.environment == "production" ? 1 : 0
  name      = "${var.project}-fog"
  server_id = azurerm_mssql_server.main.id
  partner_server { id = azurerm_mssql_server.secondary.id }

  databases = [azurerm_mssql_database.main.id]

  read_write_endpoint_failover_policy {
    mode          = "Automatic"
    grace_minutes = 60
  }
}
```

### PostgreSQL on Azure
```hcl
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "${var.project}-${var.environment}-pg"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "16"
  administrator_login    = var.db_admin_username
  administrator_password = var.db_admin_password
  zone                   = "1"

  storage_mb   = var.environment == "production" ? 65536 : 32768
  sku_name     = var.environment == "production" ? "GP_Standard_D4s_v3" : "B_Standard_B1ms"

  delegated_subnet_id    = azurerm_subnet.data.id
  private_dns_zone_id    = azurerm_private_dns_zone.postgres.id

  backup_retention_days  = var.environment == "production" ? 14 : 7
  geo_redundant_backup_enabled = var.environment == "production"

  high_availability {
    mode                      = var.environment == "production" ? "ZoneRedundant" : "Disabled"
    standby_availability_zone = "2"
  }
}
```

---

## 3. High Availability Patterns

| Pattern | AWS | Azure | RPO | RTO |
|---------|-----|-------|-----|-----|
| Multi-AZ | RDS Multi-AZ | Zone Redundant | 0 | < 2 min |
| Read Replicas | RDS Read Replica | Read Scale-out | Seconds | Promotion: minutes |
| Cross-Region | Aurora Global DB | Failover Groups | < 1 sec | < 1 min |
| Backup/Restore | Automated backups | PITR | Up to 5 min | Hours |

### Failover Testing
1. **Planned:** Use `aws rds reboot-db-instance --force-failover` or Azure planned failover
2. **Frequency:** Test quarterly in production
3. **Verify:** Application reconnects, no data loss, monitoring alerts fire

---

## 4. Connection Management

### Connection Pooling
```
App (100 instances × 10 connections = 1000)
    ↓
RDS Proxy / PgBouncer (pools to 200 actual DB connections)
    ↓
PostgreSQL (max_connections = 200)
```

**Why pooling matters:**
- Each DB connection uses ~5-10MB RAM
- Opening connections is expensive (~50ms)
- Lambda/serverless can exhaust connections quickly

### RDS Proxy
- Managed connection pooler for RDS/Aurora
- Supports IAM authentication
- Handles failover transparently
- Essential for Lambda → RDS connections

### Application-Level Pooling
```python
# Python (SQLAlchemy)
engine = create_engine(
    DATABASE_URL,
    pool_size=10,           # Connections in pool
    max_overflow=20,        # Extra connections if pool exhausted
    pool_timeout=30,        # Wait time for connection
    pool_recycle=1800,      # Recycle connections every 30 min
    pool_pre_ping=True,     # Test connection before use
)
```

---

## 5. Backup & Recovery

### Backup Strategy

| Backup Type | Frequency | Retention | Use Case |
|-------------|-----------|-----------|---------|
| Automated snapshots | Daily + transaction logs | 7-35 days | Primary recovery |
| Manual snapshots | Before changes | As needed | Pre-migration safety |
| Cross-region copy | Continuous (Aurora) or scheduled | Match primary | DR |
| Logical export | Weekly | 90 days | Migration, compliance |

### Point-in-Time Recovery (PITR)
```bash
# AWS — restore to any second within retention period
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier prod-db \
  --target-db-instance-identifier prod-db-restored \
  --restore-time "2025-01-15T10:30:00Z"

# Azure — restore
az sql db restore \
  --dest-name prod-db-restored \
  --name prod-db \
  --resource-group myapp-rg \
  --server myapp-sql \
  --time "2025-01-15T10:30:00Z"
```



---

<!-- Script: scripts/generate_data_terraform.py -->

# Script: generate_data_terraform.py

```python
#!/usr/bin/env python3
"""
Generate Terraform configurations for storage and data services.

Usage:
    python generate_data_terraform.py \
        --provider aws|azure \
        --services s3,rds,dynamodb,elasticache \
        --environment production \
        --project myapp \
        --output ./data/
"""

import argparse
import os


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


def aws_s3(env, project):
    return f"""
# ── S3 Bucket ──────────────────────────────────────────
resource "aws_s3_bucket" "main" {{
  bucket = "{project}-{env}-assets"
  tags   = {{ Name = "{project}-{env}-assets" }}
}}

resource "aws_s3_bucket_versioning" "main" {{
  bucket = aws_s3_bucket.main.id
  versioning_configuration {{ status = "Enabled" }}
}}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {{
  bucket = aws_s3_bucket.main.id
  rule {{
    apply_server_side_encryption_by_default {{ sse_algorithm = "aws:kms" }}
    bucket_key_enabled = true
  }}
}}

resource "aws_s3_bucket_public_access_block" "main" {{
  bucket                  = aws_s3_bucket.main.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}

resource "aws_s3_bucket_lifecycle_configuration" "main" {{
  bucket = aws_s3_bucket.main.id
  rule {{
    id     = "transition"
    status = "Enabled"
    transition {{ days = 30; storage_class = "STANDARD_IA" }}
    transition {{ days = 90; storage_class = "GLACIER_IR" }}
    noncurrent_version_expiration {{ noncurrent_days = 30 }}
  }}
}}
"""


def aws_rds(env, project):
    is_prod = env == "production"
    return f"""
# ── RDS PostgreSQL ─────────────────────────────────────
resource "aws_db_subnet_group" "main" {{
  name       = "{project}-{env}"
  subnet_ids = var.private_subnet_ids
}}

resource "aws_security_group" "db" {{
  name   = "{project}-{env}-db"
  vpc_id = var.vpc_id
  ingress {{
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = var.app_cidr_blocks
    description = "PostgreSQL from app"
  }}
}}

resource "aws_db_instance" "main" {{
  identifier     = "{project}-{env}"
  engine         = "postgres"
  engine_version = "16.3"
  instance_class = var.db_instance_class

  allocated_storage     = var.db_storage
  max_allocated_storage = var.db_storage * 2
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "{project.replace('-', '_')}"
  username = var.db_username
  password = var.db_password

  multi_az               = {"true" if is_prod else "false"}
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]
  publicly_accessible    = false

  backup_retention_period = {"14" if is_prod else "3"}
  deletion_protection     = {"true" if is_prod else "false"}
  skip_final_snapshot     = {"false" if is_prod else "true"}

  performance_insights_enabled = true
  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = {{ Name = "{project}-{env}-postgres" }}
}}
"""


def aws_dynamodb(env, project):
    is_prod = env == "production"
    return f"""
# ── DynamoDB ───────────────────────────────────────────
resource "aws_dynamodb_table" "main" {{
  name         = "{project}-{env}-items"
  billing_mode = "{"PROVISIONED" if is_prod else "PAY_PER_REQUEST"}"
  hash_key     = "PK"
  range_key    = "SK"

  attribute {{
    name = "PK"
    type = "S"
  }}
  attribute {{
    name = "SK"
    type = "S"
  }}
  attribute {{
    name = "GSI1PK"
    type = "S"
  }}
  attribute {{
    name = "GSI1SK"
    type = "S"
  }}

  {"read_capacity  = 100" if is_prod else ""}
  {"write_capacity = 50" if is_prod else ""}

  global_secondary_index {{
    name            = "GSI1"
    hash_key        = "GSI1PK"
    range_key       = "GSI1SK"
    projection_type = "ALL"
    {"read_capacity  = 50" if is_prod else ""}
    {"write_capacity = 25" if is_prod else ""}
  }}

  ttl {{
    attribute_name = "ExpiresAt"
    enabled        = true
  }}

  point_in_time_recovery {{ enabled = true }}
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
  server_side_encryption {{ enabled = true }}

  tags = {{ Name = "{project}-{env}-items" }}
}}
"""


def aws_elasticache(env, project):
    is_prod = env == "production"
    return f"""
# ── ElastiCache Redis ──────────────────────────────────
resource "aws_elasticache_subnet_group" "main" {{
  name       = "{project}-{env}"
  subnet_ids = var.private_subnet_ids
}}

resource "aws_security_group" "redis" {{
  name   = "{project}-{env}-redis"
  vpc_id = var.vpc_id
  ingress {{
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = var.app_cidr_blocks
    description = "Redis from app"
  }}
}}

resource "aws_elasticache_replication_group" "main" {{
  replication_group_id = "{project}-{env}"
  description          = "{project} Redis"
  node_type            = "{"cache.r7g.large" if is_prod else "cache.t4g.micro"}"
  num_cache_clusters   = {"3" if is_prod else "1"}
  port                 = 6379
  engine               = "redis"
  engine_version       = "7.1"

  automatic_failover_enabled = {"true" if is_prod else "false"}
  multi_az_enabled           = {"true" if is_prod else "false"}
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  snapshot_retention_limit = {"7" if is_prod else "0"}

  tags = {{ Name = "{project}-{env}-redis" }}
}}
"""


def azure_blob(env, project):
    return f"""
# ── Azure Blob Storage ─────────────────────────────────
resource "azurerm_storage_account" "main" {{
  name                     = "{project.replace('-', '')}{env[:4]}"
  resource_group_name      = azurerm_resource_group.data.name
  location                 = azurerm_resource_group.data.location
  account_tier             = "Standard"
  account_replication_type = "{"GRS" if env == "production" else "LRS"}"
  min_tls_version          = "TLS1_2"

  blob_properties {{
    versioning_enabled = true
    delete_retention_policy {{ days = 30 }}
  }}
}}

resource "azurerm_storage_container" "assets" {{
  name                  = "assets"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}}
"""


def azure_sql(env, project):
    is_prod = env == "production"
    return f"""
# ── Azure PostgreSQL ───────────────────────────────────
resource "azurerm_postgresql_flexible_server" "main" {{
  name                   = "{project}-{env}-pg"
  resource_group_name    = azurerm_resource_group.data.name
  location               = azurerm_resource_group.data.location
  version                = "16"
  administrator_login    = var.db_admin_username
  administrator_password = var.db_admin_password
  zone                   = "1"
  storage_mb             = {"65536" if is_prod else "32768"}
  sku_name               = "{"GP_Standard_D4s_v3" if is_prod else "B_Standard_B1ms"}"

  backup_retention_days        = {"14" if is_prod else "7"}
  geo_redundant_backup_enabled = {"true" if is_prod else "false"}

  high_availability {{
    mode                      = "{"ZoneRedundant" if is_prod else "Disabled"}"
    {"standby_availability_zone = \"2\"" if is_prod else ""}
  }}
}}

resource "azurerm_postgresql_flexible_server_database" "main" {{
  name      = "{project.replace('-', '_')}"
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}}
"""


def azure_redis(env, project):
    is_prod = env == "production"
    return f"""
# ── Azure Cache for Redis ──────────────────────────────
resource "azurerm_redis_cache" "main" {{
  name                = "{project}-{env}-redis"
  location            = azurerm_resource_group.data.location
  resource_group_name = azurerm_resource_group.data.name
  capacity            = {"2" if is_prod else "0"}
  family              = "{"P" if is_prod else "C"}"
  sku_name            = "{"Premium" if is_prod else "Basic"}"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"

  redis_configuration {{
    maxmemory_policy = "allkeys-lru"
  }}

  {"zones = [\"1\", \"2\", \"3\"]" if is_prod else ""}

  tags = {{ Environment = "{env}", Project = "{project}" }}
}}
"""


AWS_GENERATORS = {"s3": aws_s3, "rds": aws_rds, "dynamodb": aws_dynamodb, "elasticache": aws_elasticache}
AZURE_GENERATORS = {"blob": azure_blob, "sql": azure_sql, "redis": azure_redis}


def main():
    parser = argparse.ArgumentParser(description="Generate Data Terraform")
    parser.add_argument("--provider", choices=["aws", "azure"], required=True)
    parser.add_argument("--services", required=True, help="Comma-separated services")
    parser.add_argument("--environment", default="production")
    parser.add_argument("--project", default="myapp")
    parser.add_argument("--output", default="./data")
    args = parser.parse_args()

    services = args.services.split(",")
    generators = AWS_GENERATORS if args.provider == "aws" else AZURE_GENERATORS

    print(f"\n💾 Generating {args.provider.upper()} data services ({args.environment})\n")

    header = f"""terraform {{
  required_version = ">= 1.7.0"
  required_providers {{
    {"aws = { source = \"hashicorp/aws\"; version = \"~> 5.0\" }" if args.provider == "aws" else "azurerm = { source = \"hashicorp/azurerm\"; version = \"~> 3.0\" }"}
  }}
}}

{"provider \"aws\" { region = var.region }" if args.provider == "aws" else "provider \"azurerm\" { features {} }"}

{"" if args.provider == "aws" else f'''resource "azurerm_resource_group" "data" {{
  name     = "{args.project}-{args.environment}-data-rg"
  location = var.location
}}'''}
"""

    main_content = header
    for svc in services:
        gen = generators.get(svc.strip())
        if gen:
            main_content += gen(args.environment, args.project)
            print(f"  ✓ Added {svc}")
        else:
            print(f"  ⚠ Skipped {svc} (not available for {args.provider})")

    variables = f"""variable "{"region" if args.provider == "aws" else "location"}" {{ default = "{"us-east-1" if args.provider == "aws" else "eastus"}" }}
variable "vpc_id" {{ type = string; default = "" }}
variable "private_subnet_ids" {{ type = list(string); default = [] }}
variable "app_cidr_blocks" {{ type = list(string); default = ["10.0.0.0/16"] }}
variable "db_instance_class" {{ default = "{"db.r6g.xlarge" if args.environment == "production" else "db.t4g.medium"}" }}
variable "db_storage" {{ default = {"100" if args.environment == "production" else "20"} }}
variable "db_username" {{ default = "admin" }}
variable "db_password" {{ type = string; sensitive = true; default = "" }}
variable "db_admin_username" {{ default = "adminuser" }}
variable "db_admin_password" {{ type = string; sensitive = true; default = "" }}
"""

    create_file(os.path.join(args.output, "main.tf"), main_content)
    create_file(os.path.join(args.output, "variables.tf"), variables)

    print(f"\n✅ Data config generated at: {args.output}/")


if __name__ == "__main__":
    main()

```
