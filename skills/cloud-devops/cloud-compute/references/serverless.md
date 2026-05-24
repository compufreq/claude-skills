# Serverless Compute Reference

## Table of Contents
1. AWS Lambda
2. Azure Functions
3. Cold Start Optimization
4. Event Sources & Triggers
5. Patterns & Anti-Patterns

---

## 1. AWS Lambda

### Production Lambda (Terraform)
```hcl
resource "aws_lambda_function" "api" {
  function_name = "${var.project}-${var.environment}-api"
  role          = aws_iam_role.lambda.arn
  handler       = "index.handler"
  runtime       = "nodejs20.x"
  architectures = ["arm64"]          # Graviton — 20% cheaper
  memory_size   = 512                # Also affects CPU allocation
  timeout       = 30
  publish       = true               # Enable versioning

  filename         = "lambda.zip"
  source_code_hash = filebase64sha256("lambda.zip")

  # Or use container image
  # image_uri = "${aws_ecr_repository.api.repository_url}:latest"
  # package_type = "Image"

  environment {
    variables = {
      ENVIRONMENT   = var.environment
      DB_SECRET_ARN = aws_secretsmanager_secret.db.arn
      TABLE_NAME    = aws_dynamodb_table.main.name
      LOG_LEVEL     = "info"
    }
  }

  vpc_config {
    subnet_ids         = module.vpc.private_subnets
    security_group_ids = [aws_security_group.lambda.id]
  }

  tracing_config {
    mode = "Active"    # X-Ray tracing
  }

  dead_letter_config {
    target_arn = aws_sqs_queue.dlq.arn
  }

  reserved_concurrent_executions = var.environment == "production" ? 100 : 10

  tags = { Name = "${var.project}-api" }
}

# Provisioned concurrency (eliminate cold starts)
resource "aws_lambda_provisioned_concurrency_config" "api" {
  count                             = var.environment == "production" ? 1 : 0
  function_name                     = aws_lambda_function.api.function_name
  qualifier                         = aws_lambda_function.api.version
  provisioned_concurrent_executions = 5
}

# API Gateway trigger
resource "aws_apigatewayv2_api" "main" {
  name          = "${var.project}-${var.environment}-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Event source: SQS
resource "aws_lambda_event_source_mapping" "sqs" {
  event_source_arn                   = aws_sqs_queue.tasks.arn
  function_name                      = aws_lambda_function.worker.arn
  batch_size                         = 10
  maximum_batching_window_in_seconds = 5
  function_response_types            = ["ReportBatchItemFailures"]

  scaling_config {
    maximum_concurrency = 50
  }
}

# Event source: DynamoDB Streams
resource "aws_lambda_event_source_mapping" "dynamodb" {
  event_source_arn  = aws_dynamodb_table.main.stream_arn
  function_name     = aws_lambda_function.stream_processor.arn
  starting_position = "LATEST"
  batch_size        = 100

  filter_criteria {
    filter {
      pattern = jsonencode({
        eventName = ["INSERT", "MODIFY"]
      })
    }
  }
}

# Scheduled (cron)
resource "aws_cloudwatch_event_rule" "daily" {
  name                = "${var.project}-daily-cleanup"
  schedule_expression = "cron(0 2 * * ? *)"    # 2 AM UTC daily
}

resource "aws_cloudwatch_event_target" "daily" {
  rule      = aws_cloudwatch_event_rule.daily.name
  target_id = "lambda"
  arn       = aws_lambda_function.cleanup.arn
}
```

### Lambda Layers
```hcl
resource "aws_lambda_layer_version" "shared" {
  layer_name          = "${var.project}-shared-libs"
  filename            = "layers/shared.zip"
  compatible_runtimes = ["nodejs20.x"]
  compatible_architectures = ["arm64"]
}

# Reference in function
resource "aws_lambda_function" "api" {
  layers = [aws_lambda_layer_version.shared.arn]
  # ...
}
```

---

## 2. Azure Functions

### Production Function App (Terraform)
```hcl
resource "azurerm_service_plan" "functions" {
  name                = "${var.project}-${var.environment}-asp"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = var.environment == "production" ? "EP1" : "Y1"  # EP = Premium, Y1 = Consumption
}

resource "azurerm_linux_function_app" "main" {
  name                = "${var.project}-${var.environment}-func"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.functions.id

  storage_account_name       = azurerm_storage_account.functions.name
  storage_account_access_key = azurerm_storage_account.functions.primary_access_key

  site_config {
    application_stack {
      node_version = "20"
    }
    application_insights_connection_string = azurerm_application_insights.main.connection_string
    always_on = var.environment == "production"   # Premium plan only

    cors {
      allowed_origins = ["https://app.example.com"]
    }
  }

  app_settings = {
    ENVIRONMENT                     = var.environment
    FUNCTIONS_WORKER_RUNTIME        = "node"
    WEBSITE_RUN_FROM_PACKAGE        = "1"
    AzureWebJobsDisableHomepage     = "true"
    APPINSIGHTS_INSTRUMENTATIONKEY  = azurerm_application_insights.main.instrumentation_key
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = var.environment
    Project     = var.project
  }
}
```

### Function Triggers Comparison

| Trigger | AWS Lambda | Azure Functions |
|---------|-----------|----------------|
| HTTP | API Gateway / Function URL | HTTP trigger (built-in) |
| Queue | SQS event source | Queue Storage / Service Bus |
| Schedule | EventBridge rule | Timer trigger |
| Storage | S3 event notification | Blob trigger |
| Database | DynamoDB Streams | Cosmos DB trigger |
| Event stream | Kinesis, Kafka | Event Hub, Kafka |

---

## 3. Cold Start Optimization

### Cold Start Factors

| Factor | Impact | Mitigation |
|--------|--------|-----------|
| Runtime | Java > Python > Node.js > Go/Rust | Use lightweight runtimes |
| Package size | Larger = slower | Minimize deps, use layers, tree-shake |
| VPC | +2-8 seconds (AWS) | Use VPC endpoints, or avoid VPC |
| Memory | More memory = more CPU | Allocate more memory |
| Init code | Heavy initialization | Lazy-load, cache outside handler |

### Cold Start Mitigation

**AWS Lambda:**
```javascript
// Initialize outside handler (reused across invocations)
const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const client = new DynamoDBClient({});  // Reused on warm invocations

exports.handler = async (event) => {
  // Handler code uses pre-initialized client
  return { statusCode: 200 };
};
```

- **Provisioned Concurrency**: Pre-warms instances ($$$)
- **SnapStart** (Java): Snapshots initialized JVM — 10x faster starts
- **ARM (Graviton)**: Slightly faster cold starts + 20% cheaper
- **Keep functions warm**: CloudWatch scheduled ping (hacky but works)

**Azure Functions:**
- **Premium Plan (EP)**: Pre-warmed instances, no cold starts
- **Always On**: Keep at least one instance running
- **Durable Functions**: Orchestrate without cold starts between steps

---

## 4. Event Sources & Triggers

### AWS Lambda Event Sources

| Source | Invocation | Scaling |
|--------|-----------|---------|
| API Gateway | Synchronous | Automatic (per-request) |
| SQS | Polling (batch) | Based on queue depth |
| SNS | Push | Per-message |
| S3 | Push | Per-event |
| DynamoDB Streams | Polling | Per-shard |
| Kinesis | Polling | Per-shard |
| EventBridge | Push | Per-event |
| CloudWatch Events | Push (cron) | Single invocation |
| Step Functions | Synchronous | Per-execution |

### Event Processing Patterns

**Fan-Out (SNS → Multiple Lambdas):**
```
Event → SNS Topic → Lambda A (process)
                   → Lambda B (notify)
                   → Lambda C (archive)
                   → SQS Queue (retry)
```

**Queue Processing (SQS → Lambda):**
```
Producer → SQS Queue → Lambda (batch of 10) → DynamoDB
              ↓
          DLQ (failed messages after 3 retries)
```

**Event Sourcing (DynamoDB Streams → Lambda):**
```
API → DynamoDB (write) → Stream → Lambda → Elasticsearch (read model)
                                        → SNS (notifications)
                                        → S3 (archive)
```

---

## 5. Patterns & Anti-Patterns

### Patterns
1. **Single-purpose functions** — one function, one responsibility
2. **Idempotent handlers** — same event processed twice = same result
3. **Dead letter queues** — capture failed events for investigation
4. **Batch processing** — process 10-100 messages per invocation
5. **Connection pooling** — reuse DB connections across invocations
6. **Environment variables** — config outside code, secrets via SSM/KV

### Anti-Patterns
1. **Monolith Lambda** — one function with 50 routes (use API Gateway routing)
2. **Lambda calling Lambda** — use Step Functions or SQS instead
3. **Heavy initialization** — load everything at startup (lazy-load instead)
4. **Long-running functions** — > 5 min usually means wrong tool (use Fargate)
5. **Storing state in /tmp** — ephemeral; use DynamoDB/S3 for state
6. **Ignoring concurrency limits** — can overwhelm downstream services (use reserved concurrency)



---
