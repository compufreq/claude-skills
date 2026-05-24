# NoSQL Database Reference

## Table of Contents
1. AWS DynamoDB
2. Azure Cosmos DB
3. Data Modeling Patterns
4. Performance & Cost

---

## 1. AWS DynamoDB

### Production Table
```hcl
resource "aws_dynamodb_table" "main" {
  name         = "${var.project}-${var.environment}-items"
  billing_mode = var.environment == "production" ? "PROVISIONED" : "PAY_PER_REQUEST"
  hash_key     = "PK"
  range_key    = "SK"

  attribute {
    name = "PK"
    type = "S"
  }
  attribute {
    name = "SK"
    type = "S"
  }
  attribute {
    name = "GSI1PK"
    type = "S"
  }
  attribute {
    name = "GSI1SK"
    type = "S"
  }

  # Provisioned throughput (production)
  read_capacity  = var.environment == "production" ? 100 : null
  write_capacity = var.environment == "production" ? 50 : null

  # Global Secondary Index
  global_secondary_index {
    name            = "GSI1"
    hash_key        = "GSI1PK"
    range_key       = "GSI1SK"
    projection_type = "ALL"
    read_capacity   = var.environment == "production" ? 50 : null
    write_capacity  = var.environment == "production" ? 25 : null
  }

  # TTL
  ttl {
    attribute_name = "ExpiresAt"
    enabled        = true
  }

  # Streams (for CDC, replication, triggers)
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  # Point-in-time recovery
  point_in_time_recovery { enabled = true }

  # Encryption
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb.arn
  }

  tags = { Name = "${var.project}-${var.environment}-items" }
}

# Auto-scaling (provisioned mode)
resource "aws_appautoscaling_target" "dynamodb_read" {
  count              = var.environment == "production" ? 1 : 0
  max_capacity       = 1000
  min_capacity       = 50
  resource_id        = "table/${aws_dynamodb_table.main.name}"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "dynamodb_read" {
  count              = var.environment == "production" ? 1 : 0
  name               = "DynamoDBReadAutoScaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.dynamodb_read[0].resource_id
  scalable_dimension = aws_appautoscaling_target.dynamodb_read[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.dynamodb_read[0].service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }
    target_value = 70.0
  }
}
```

### Single Table Design Pattern
```
PK (Partition Key)     | SK (Sort Key)        | Attributes
-----------------------|----------------------|------------------
USER#user123           | PROFILE              | name, email, plan
USER#user123           | ORDER#2025-01-15#001 | total, status
USER#user123           | ORDER#2025-01-16#002 | total, status
ORDER#order001         | METADATA             | userId, total
ORDER#order001         | ITEM#sku123          | qty, price
ORG#acme               | MEMBER#user123       | role, joinedAt

GSI1PK                 | GSI1SK               | (Inverted index)
ORDER#order001         | USER#user123         | status, total
ORG#acme               | PLAN#enterprise      | seats, expires
```

### Access Patterns
```
Get user profile:       PK = "USER#123",  SK = "PROFILE"
Get user's orders:      PK = "USER#123",  SK begins_with "ORDER#"
Get order details:      PK = "ORDER#001", SK = "METADATA"
Get order items:        PK = "ORDER#001", SK begins_with "ITEM#"
Get orders by status:   GSI1PK = "STATUS#pending", GSI1SK begins_with "ORDER#"
```

### DynamoDB Application Code
```python
import boto3
from boto3.dynamodb.conditions import Key

table = boto3.resource('dynamodb').Table('myapp-production-items')

# Put item
table.put_item(Item={
    'PK': 'USER#user123',
    'SK': 'PROFILE',
    'name': 'Alice',
    'email': 'alice@example.com',
    'plan': 'premium',
})

# Query user's orders
response = table.query(
    KeyConditionExpression=Key('PK').eq('USER#user123') & Key('SK').begins_with('ORDER#'),
    ScanIndexForward=False,  # Newest first
    Limit=10,
)

# Transactional write
client = boto3.client('dynamodb')
client.transact_write_items(TransactItems=[
    {'Put': {'TableName': 'items', 'Item': {'PK': {'S': 'ORDER#002'}, 'SK': {'S': 'METADATA'}, 'status': {'S': 'pending'}}}},
    {'Update': {'TableName': 'items', 'Key': {'PK': {'S': 'USER#123'}, 'SK': {'S': 'PROFILE'}},
                'UpdateExpression': 'SET orderCount = orderCount + :inc',
                'ExpressionAttributeValues': {':inc': {'N': '1'}}}},
])
```

---

## 2. Azure Cosmos DB

### Production Cosmos DB
```hcl
resource "azurerm_cosmosdb_account" "main" {
  name                = "${var.project}-${var.environment}-cosmos"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level = "Session"    # Session, Strong, BoundedStaleness, ConsistentPrefix, Eventual
  }

  geo_location {
    location          = azurerm_resource_group.main.location
    failover_priority = 0
    zone_redundant    = var.environment == "production"
  }

  geo_location {
    location          = var.secondary_location
    failover_priority = 1
  }

  capabilities {
    name = "EnableServerless"    # Remove for provisioned throughput
  }

  backup {
    type                = "Continuous"
    tier                = "Continuous7Days"
  }

  is_virtual_network_filter_enabled = true
  virtual_network_rule {
    id = azurerm_subnet.app.id
  }
}

resource "azurerm_cosmosdb_sql_database" "main" {
  name                = var.project
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
}

resource "azurerm_cosmosdb_sql_container" "items" {
  name                = "items"
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
  database_name       = azurerm_cosmosdb_sql_database.main.name

  partition_key_paths   = ["/partitionKey"]
  partition_key_version = 2

  indexing_policy {
    indexing_mode = "consistent"
    included_path { path = "/*" }
    excluded_path { path = "/description/?" }
    composite_index {
      index { path = "/status"; order = "ascending" }
      index { path = "/createdAt"; order = "descending" }
    }
  }

  default_ttl = -1    # TTL enabled, per-item
}
```

### Consistency Levels (Cosmos DB)

| Level | Latency | Consistency | Cost | Use Case |
|-------|---------|------------|------|---------|
| Strong | Higher | Linearizable | Highest | Financial, inventory |
| Bounded Staleness | Medium | Within K versions or T time | High | Leaderboards |
| Session | Low | Read-your-writes per session | Medium | Most apps (recommended) |
| Consistent Prefix | Low | Ordered, eventually consistent | Lower | Social feeds |
| Eventual | Lowest | No ordering guarantee | Lowest | Logging, analytics |

---

## 3. Data Modeling Patterns

### Partition Key Selection Rules
1. **High cardinality** — many unique values (userId, orderId, NOT status)
2. **Even distribution** — avoid hot partitions
3. **Query-aligned** — most queries should target a single partition
4. **Avoid time-based** for PK — creates hot partitions on recent data

### Common NoSQL Patterns

| Pattern | Description | Example |
|---------|------------|---------|
| **Single Table** | All entities in one table with composite keys | Users + Orders + Items |
| **Adjacency List** | Related items share partition key | User → Orders, User → Addresses |
| **Write Sharding** | Append random suffix to spread writes | `STATUS#pending#3` |
| **GSI Overloading** | Reuse GSI for multiple access patterns | GSI1PK/GSI1SK for different entities |
| **Sparse Index** | GSI only contains items with the indexed attribute | Only items with `isActive` |

---

## 4. Performance & Cost

### DynamoDB Capacity Modes

| Mode | Cost Model | Best For |
|------|-----------|---------|
| On-Demand | Per request ($1.25/million reads) | Unpredictable, spiky, dev |
| Provisioned | Per RCU/WCU ($0.00065/RCU/hr) | Predictable, steady-state |
| Provisioned + Auto-scaling | Per RCU/WCU with auto-adjust | Production (recommended) |
| Reserved | 1yr/3yr commitment | High-volume production |

### Cosmos DB RU Estimation
- Point read (1KB): 1 RU
- Point write (1KB): 5 RUs
- Query (single partition): 3-10 RUs
- Cross-partition query: 10-100+ RUs

### Optimization Tips
1. **Avoid scans** — always query by partition key
2. **Project only needed attributes** — reduces RUs and bandwidth
3. **Use TTL** for ephemeral data — auto-cleanup without write cost
4. **Batch writes** — DynamoDB BatchWriteItem up to 25 items
5. **DAX / Cosmos DB integrated cache** for read-heavy workloads



---
