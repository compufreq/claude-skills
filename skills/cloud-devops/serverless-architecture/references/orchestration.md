# Orchestration Reference

## Table of Contents
1. AWS Step Functions
2. Azure Durable Functions
3. Common Workflow Patterns
4. Orchestration vs Choreography

---

## 1. AWS Step Functions

### Step Functions Types

| Type | Max Duration | Pricing | Best For |
|------|-------------|---------|---------|
| **Standard** | 1 year | Per state transition ($0.025/1K) | Long-running, auditable |
| **Express** | 5 minutes | Per execution + duration | High-volume, short |

### Order Processing Workflow (ASL)
```json
{
  "Comment": "Order Processing Workflow",
  "StartAt": "ValidateOrder",
  "States": {
    "ValidateOrder": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456:function:validate-order",
      "Next": "ProcessPayment",
      "Catch": [{
        "ErrorEquals": ["ValidationError"],
        "Next": "OrderFailed",
        "ResultPath": "$.error"
      }],
      "Retry": [{
        "ErrorEquals": ["States.TaskFailed"],
        "IntervalSeconds": 2,
        "MaxAttempts": 3,
        "BackoffRate": 2
      }]
    },
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456:function:process-payment",
      "Next": "ParallelFulfillment",
      "Catch": [{
        "ErrorEquals": ["PaymentError"],
        "Next": "RefundAndCancel",
        "ResultPath": "$.error"
      }]
    },
    "ParallelFulfillment": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "ReserveInventory",
          "States": {
            "ReserveInventory": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:us-east-1:123456:function:reserve-inventory",
              "End": true
            }
          }
        },
        {
          "StartAt": "SendConfirmation",
          "States": {
            "SendConfirmation": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:us-east-1:123456:function:send-confirmation",
              "End": true
            }
          }
        }
      ],
      "Next": "OrderComplete",
      "Catch": [{
        "ErrorEquals": ["States.ALL"],
        "Next": "CompensateOrder",
        "ResultPath": "$.error"
      }]
    },
    "OrderComplete": {
      "Type": "Succeed"
    },
    "CompensateOrder": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456:function:compensate-order",
      "Next": "OrderFailed"
    },
    "RefundAndCancel": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456:function:refund-payment",
      "Next": "OrderFailed"
    },
    "OrderFailed": {
      "Type": "Fail",
      "Error": "OrderProcessingFailed",
      "Cause": "Order could not be processed"
    }
  }
}
```

### Terraform
```hcl
resource "aws_sfn_state_machine" "order" {
  name     = "${var.project}-order-processing"
  role_arn = aws_iam_role.step_functions.arn
  type     = "STANDARD"

  definition = file("${path.module}/workflows/order-processing.asl.json")

  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.sfn.arn}:*"
    include_execution_data = true
    level                  = "ALL"
  }

  tracing_configuration { enabled = true }
}

# Trigger from EventBridge
resource "aws_cloudwatch_event_rule" "order_placed" {
  name          = "start-order-workflow"
  event_pattern = jsonencode({
    source      = ["order-service"]
    detail-type = ["OrderPlaced"]
  })
}

resource "aws_cloudwatch_event_target" "sfn" {
  rule     = aws_cloudwatch_event_rule.order_placed.name
  arn      = aws_sfn_state_machine.order.arn
  role_arn = aws_iam_role.eventbridge_sfn.arn
}
```

### Step Functions Patterns

**Wait for Callback (Human Approval):**
```json
{
  "WaitForApproval": {
    "Type": "Task",
    "Resource": "arn:aws:states:::sqs:sendMessage.waitForTaskToken",
    "Parameters": {
      "QueueUrl": "${ApprovalQueueUrl}",
      "MessageBody": {
        "taskToken.$": "$$.Task.Token",
        "orderId.$": "$.orderId",
        "amount.$": "$.amount"
      }
    },
    "TimeoutSeconds": 86400,
    "Next": "ProcessApprovedOrder"
  }
}
```

**Map (Parallel Processing):**
```json
{
  "ProcessItems": {
    "Type": "Map",
    "ItemsPath": "$.items",
    "MaxConcurrency": 10,
    "Iterator": {
      "StartAt": "ProcessItem",
      "States": {
        "ProcessItem": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:...:function:process-item",
          "End": true
        }
      }
    },
    "Next": "AllItemsProcessed"
  }
}
```

---

## 2. Azure Durable Functions

### Orchestrator Function
```javascript
// OrderOrchestrator/index.js
const df = require('durable-functions');

module.exports = df.orchestrator(function* (context) {
  const order = context.df.getInput();

  try {
    // Step 1: Validate
    const validated = yield context.df.callActivity('ValidateOrder', order);

    // Step 2: Process payment
    const payment = yield context.df.callActivity('ProcessPayment', {
      orderId: validated.orderId,
      amount: validated.total,
    });

    // Step 3: Parallel fulfillment
    const [inventory, notification] = yield context.df.Task.all([
      context.df.callActivity('ReserveInventory', validated),
      context.df.callActivity('SendConfirmation', { ...validated, paymentId: payment.id }),
    ]);

    return { status: 'completed', orderId: validated.orderId };
  } catch (error) {
    // Compensation
    yield context.df.callActivity('CompensateOrder', { orderId: order.orderId, error: error.message });
    throw error;
  }
});
```

### Durable Functions Patterns

| Pattern | Description | Use Case |
|---------|------------|---------|
| **Function chaining** | A → B → C (sequential) | Multi-step processing |
| **Fan-out/fan-in** | A → [B1, B2, B3] → C | Parallel batch processing |
| **Async HTTP APIs** | Start, poll status, get result | Long-running operations |
| **Monitor** | Periodic polling until condition | Wait for external event |
| **Human interaction** | Wait for external approval | Approval workflows |
| **Eternal orchestrations** | Loop forever with cleanup | Monitoring, aggregation |

### Human Approval Pattern
```javascript
module.exports = df.orchestrator(function* (context) {
  const request = context.df.getInput();

  yield context.df.callActivity('SendApprovalRequest', {
    to: request.approver,
    requestId: context.df.instanceId,
  });

  // Wait up to 72 hours for approval
  const deadline = new Date(context.df.currentUtcDateTime);
  deadline.setHours(deadline.getHours() + 72);

  const approvalEvent = yield context.df.waitForExternalEvent('ApprovalResponse', deadline);

  if (approvalEvent && approvalEvent.approved) {
    yield context.df.callActivity('ProcessApproved', request);
    return { status: 'approved' };
  } else {
    yield context.df.callActivity('HandleRejection', request);
    return { status: 'rejected' };
  }
});
```

---

## 3. Common Workflow Patterns

### Saga Pattern (Distributed Transaction)
```
Order → Payment → Inventory → Shipping → Complete
  ↓ (fail)   ↓ (fail)    ↓ (fail)
Cancel    Refund      Unreserve
```

### Batch Processing
```
Step Functions Map:
  Input: [item1, item2, ..., item1000]
  → Map state (concurrency 10) → Process each item → Collect results
  
Durable Functions Fan-out:
  orchestrator → [activity1, activity2, ..., activity1000] → aggregate results
```

### Approval Workflow
```
Submit → Validate → Wait for Approval (timeout: 72h) → Process
                         ↓ (rejected)     ↓ (timeout)
                      Notify Requester   Auto-Reject
```

---

## 4. Orchestration vs Choreography

| Factor | Orchestration (Step Functions) | Choreography (Events) |
|--------|-------------------------------|----------------------|
| Flow visibility | Central, visual | Distributed, harder to trace |
| Coupling | Orchestrator knows all steps | Services are independent |
| Error handling | Central try/catch/compensate | Per-service DLQ + retry |
| Adding steps | Change orchestrator | Add new event consumer |
| Complexity | Simple flows: easy; complex: manageable | Simple: easy; complex: hard to reason |
| Debugging | Step Functions console, execution history | Distributed tracing, log correlation |
| Best for | Multi-step business processes | Event notifications, fan-out |

### When to Use Each
- **Orchestration:** Order processing, ETL pipelines, approval workflows, anything with compensation
- **Choreography:** Notifications, analytics events, audit logging, cache invalidation
- **Hybrid:** Orchestration for the core workflow, choreography for side effects



---

<!-- Script: scripts/generate_serverless_terraform.py -->

# Script: generate_serverless_terraform.py

```python
#!/usr/bin/env python3
"""
Generate serverless architecture Terraform configurations.

Usage:
    python generate_serverless_terraform.py \
        --provider aws|azure \
        --pattern api|event-processing|workflow|data-pipeline \
        --project myapp \
        --environment production \
        --output ./serverless/
"""

import argparse
import os


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


def aws_api(env, project, output):
    main = f'''terraform {{
  required_version = ">= 1.7.0"
  required_providers {{
    aws = {{ source = "hashicorp/aws"; version = "~> 5.0" }}
  }}
}}

provider "aws" {{
  region = var.region
  default_tags {{
    tags = {{ Environment = "{env}", Project = "{project}", ManagedBy = "terraform" }}
  }}
}}

# ── API Gateway ────────────────────────────────────────
resource "aws_apigatewayv2_api" "main" {{
  name          = "{project}-{env}-api"
  protocol_type = "HTTP"
  cors_configuration {{
    allow_origins = var.cors_origins
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
    max_age       = 3600
  }}
}}

resource "aws_apigatewayv2_stage" "default" {{
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true
  access_log_settings {{
    destination_arn = aws_cloudwatch_log_group.apigw.arn
    format = jsonencode({{
      requestId = "$context.requestId"
      method    = "$context.httpMethod"
      path      = "$context.path"
      status    = "$context.status"
      latency   = "$context.responseLatency"
    }})
  }}
}}

# ── Lambda Functions ───────────────────────────────────
resource "aws_lambda_function" "api" {{
  function_name = "{project}-{env}-api"
  role          = aws_iam_role.lambda.arn
  handler       = "index.handler"
  runtime       = "nodejs20.x"
  architectures = ["arm64"]
  memory_size   = 512
  timeout       = 30
  publish       = true

  filename         = "${{path.module}}/lambda.zip"
  source_code_hash = filebase64sha256("${{path.module}}/lambda.zip")

  environment {{
    variables = {{
      ENVIRONMENT = "{env}"
      TABLE_NAME  = aws_dynamodb_table.main.name
    }}
  }}

  tracing_config {{ mode = "Active" }}
}}

# ── DynamoDB ───────────────────────────────────────────
resource "aws_dynamodb_table" "main" {{
  name         = "{project}-{env}"
  billing_mode = "{"PROVISIONED" if env == "production" else "PAY_PER_REQUEST"}"
  hash_key     = "PK"
  range_key    = "SK"

  attribute {{ name = "PK"; type = "S" }}
  attribute {{ name = "SK"; type = "S" }}
  attribute {{ name = "GSI1PK"; type = "S" }}
  attribute {{ name = "GSI1SK"; type = "S" }}

  {"read_capacity  = 25" if env == "production" else ""}
  {"write_capacity = 25" if env == "production" else ""}

  global_secondary_index {{
    name            = "GSI1"
    hash_key        = "GSI1PK"
    range_key       = "GSI1SK"
    projection_type = "ALL"
    {"read_capacity  = 25" if env == "production" else ""}
    {"write_capacity = 25" if env == "production" else ""}
  }}

  point_in_time_recovery {{ enabled = true }}
  server_side_encryption {{ enabled = true }}
  ttl {{ attribute_name = "ExpiresAt"; enabled = true }}
}}

# ── Routes ─────────────────────────────────────────────
resource "aws_apigatewayv2_integration" "api" {{
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}}

resource "aws_apigatewayv2_route" "default" {{
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "$default"
  target    = "integrations/${{aws_apigatewayv2_integration.api.id}}"
}}

resource "aws_lambda_permission" "apigw" {{
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${{aws_apigatewayv2_api.main.execution_arn}}/*/*"
}}

# ── Logging ────────────────────────────────────────────
resource "aws_cloudwatch_log_group" "apigw" {{
  name              = "/aws/apigateway/{project}-{env}"
  retention_in_days = {"90" if env == "production" else "14"}
}}

resource "aws_cloudwatch_log_group" "lambda" {{
  name              = "/aws/lambda/{project}-{env}-api"
  retention_in_days = {"90" if env == "production" else "14"}
}}

# ── IAM ────────────────────────────────────────────────
resource "aws_iam_role" "lambda" {{
  name = "{project}-{env}-lambda"
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{ Action = "sts:AssumeRole", Effect = "Allow", Principal = {{ Service = "lambda.amazonaws.com" }} }}]
  }})
}}

resource "aws_iam_role_policy_attachment" "lambda_basic" {{
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}}

resource "aws_iam_role_policy" "dynamodb" {{
  name = "dynamodb-access"
  role = aws_iam_role.lambda.id
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Effect   = "Allow"
      Action   = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:Query", "dynamodb:UpdateItem", "dynamodb:DeleteItem"]
      Resource = [aws_dynamodb_table.main.arn, "${{aws_dynamodb_table.main.arn}}/index/*"]
    }}]
  }})
}}
'''

    variables = f'''variable "region" {{ default = "us-east-1" }}
variable "cors_origins" {{ type = list(string); default = ["*"] }}
'''

    outputs = f'''output "api_endpoint" {{
  value = aws_apigatewayv2_stage.default.invoke_url
}}
output "table_name" {{
  value = aws_dynamodb_table.main.name
}}
'''

    create_file(os.path.join(output, "main.tf"), main)
    create_file(os.path.join(output, "variables.tf"), variables)
    create_file(os.path.join(output, "outputs.tf"), outputs)


def aws_event_processing(env, project, output):
    main = f'''terraform {{
  required_version = ">= 1.7.0"
  required_providers {{
    aws = {{ source = "hashicorp/aws"; version = "~> 5.0" }}
  }}
}}

provider "aws" {{
  region = var.region
  default_tags {{
    tags = {{ Environment = "{env}", Project = "{project}", ManagedBy = "terraform" }}
  }}
}}

# ── EventBridge ────────────────────────────────────────
resource "aws_cloudwatch_event_bus" "app" {{
  name = "{project}-{env}-events"
}}

# Rule: Route events to processor
resource "aws_cloudwatch_event_rule" "process" {{
  name           = "{project}-process-events"
  event_bus_name = aws_cloudwatch_event_bus.app.name
  event_pattern = jsonencode({{
    source      = ["{project}"]
    detail-type = ["ItemCreated", "ItemUpdated"]
  }})
}}

resource "aws_cloudwatch_event_target" "process" {{
  rule           = aws_cloudwatch_event_rule.process.name
  event_bus_name = aws_cloudwatch_event_bus.app.name
  arn            = aws_sqs_queue.process.arn
  dead_letter_config {{ arn = aws_sqs_queue.events_dlq.arn }}
}}

# ── SQS Queues ─────────────────────────────────────────
resource "aws_sqs_queue" "process" {{
  name                       = "{project}-{env}-process"
  visibility_timeout_seconds = 300
  message_retention_seconds  = 1209600
  redrive_policy = jsonencode({{
    deadLetterTargetArn = aws_sqs_queue.process_dlq.arn
    maxReceiveCount     = 3
  }})
}}

resource "aws_sqs_queue" "process_dlq" {{
  name                      = "{project}-{env}-process-dlq"
  message_retention_seconds = 1209600
}}

resource "aws_sqs_queue" "events_dlq" {{
  name                      = "{project}-{env}-events-dlq"
  message_retention_seconds = 1209600
}}

# ── Worker Lambda ──────────────────────────────────────
resource "aws_lambda_function" "worker" {{
  function_name = "{project}-{env}-worker"
  role          = aws_iam_role.lambda.arn
  handler       = "worker.handler"
  runtime       = "nodejs20.x"
  architectures = ["arm64"]
  memory_size   = 512
  timeout       = 60

  filename         = "${{path.module}}/worker.zip"
  source_code_hash = filebase64sha256("${{path.module}}/worker.zip")

  environment {{
    variables = {{
      ENVIRONMENT    = "{env}"
      EVENT_BUS_NAME = aws_cloudwatch_event_bus.app.name
    }}
  }}

  tracing_config {{ mode = "Active" }}
  reserved_concurrent_executions = {"50" if env == "production" else "5"}
}}

resource "aws_lambda_event_source_mapping" "worker" {{
  event_source_arn                   = aws_sqs_queue.process.arn
  function_name                      = aws_lambda_function.worker.arn
  batch_size                         = 10
  maximum_batching_window_in_seconds = 5
  function_response_types            = ["ReportBatchItemFailures"]
}}

# ── IAM ────────────────────────────────────────────────
resource "aws_iam_role" "lambda" {{
  name = "{project}-{env}-worker-role"
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{ Action = "sts:AssumeRole", Effect = "Allow", Principal = {{ Service = "lambda.amazonaws.com" }} }}]
  }})
}}

resource "aws_iam_role_policy_attachment" "basic" {{
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}}

resource "aws_iam_role_policy" "sqs" {{
  name = "sqs-access"
  role = aws_iam_role.lambda.id
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Effect = "Allow"
      Action = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
      Resource = aws_sqs_queue.process.arn
    }}, {{
      Effect = "Allow"
      Action = ["events:PutEvents"]
      Resource = aws_cloudwatch_event_bus.app.arn
    }}]
  }})
}}

# SQS policy to allow EventBridge to send messages
resource "aws_sqs_queue_policy" "process" {{
  queue_url = aws_sqs_queue.process.id
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Effect    = "Allow"
      Principal = {{ Service = "events.amazonaws.com" }}
      Action    = "sqs:SendMessage"
      Resource  = aws_sqs_queue.process.arn
      Condition = {{ ArnEquals = {{ "aws:SourceArn" = aws_cloudwatch_event_rule.process.arn }} }}
    }}]
  }})
}}
'''

    create_file(os.path.join(output, "main.tf"), main)
    create_file(os.path.join(output, "variables.tf"), f'variable "region" {{ default = "us-east-1" }}\n')


def aws_workflow(env, project, output):
    # Step Functions workflow
    asl = f'''{{
  "Comment": "{project} workflow",
  "StartAt": "Validate",
  "States": {{
    "Validate": {{
      "Type": "Task",
      "Resource": "${{ValidateFunctionArn}}",
      "Next": "Process",
      "Retry": [{{ "ErrorEquals": ["States.TaskFailed"], "IntervalSeconds": 2, "MaxAttempts": 3, "BackoffRate": 2 }}],
      "Catch": [{{ "ErrorEquals": ["States.ALL"], "Next": "HandleError", "ResultPath": "$.error" }}]
    }},
    "Process": {{
      "Type": "Task",
      "Resource": "${{ProcessFunctionArn}}",
      "Next": "Complete",
      "Catch": [{{ "ErrorEquals": ["States.ALL"], "Next": "Compensate", "ResultPath": "$.error" }}]
    }},
    "Complete": {{
      "Type": "Succeed"
    }},
    "Compensate": {{
      "Type": "Task",
      "Resource": "${{CompensateFunctionArn}}",
      "Next": "HandleError"
    }},
    "HandleError": {{
      "Type": "Fail",
      "Error": "WorkflowFailed",
      "Cause": "Workflow failed after compensation"
    }}
  }}
}}'''

    main = f'''terraform {{
  required_version = ">= 1.7.0"
  required_providers {{
    aws = {{ source = "hashicorp/aws"; version = "~> 5.0" }}
  }}
}}

provider "aws" {{
  region = var.region
  default_tags {{
    tags = {{ Environment = "{env}", Project = "{project}", ManagedBy = "terraform" }}
  }}
}}

resource "aws_sfn_state_machine" "main" {{
  name     = "{project}-{env}-workflow"
  role_arn = aws_iam_role.sfn.arn
  type     = "STANDARD"

  definition = templatefile("${{path.module}}/workflow.asl.json", {{
    ValidateFunctionArn   = aws_lambda_function.validate.arn
    ProcessFunctionArn    = aws_lambda_function.process.arn
    CompensateFunctionArn = aws_lambda_function.compensate.arn
  }})

  logging_configuration {{
    log_destination        = "${{aws_cloudwatch_log_group.sfn.arn}}:*"
    include_execution_data = true
    level                  = "ALL"
  }}
  tracing_configuration {{ enabled = true }}
}}

resource "aws_lambda_function" "validate" {{
  function_name = "{project}-{env}-validate"
  role          = aws_iam_role.lambda.arn
  handler       = "validate.handler"
  runtime       = "nodejs20.x"
  architectures = ["arm64"]
  memory_size   = 256
  timeout       = 30
  filename      = "${{path.module}}/functions.zip"
  source_code_hash = filebase64sha256("${{path.module}}/functions.zip")
}}

resource "aws_lambda_function" "process" {{
  function_name = "{project}-{env}-process"
  role          = aws_iam_role.lambda.arn
  handler       = "process.handler"
  runtime       = "nodejs20.x"
  architectures = ["arm64"]
  memory_size   = 512
  timeout       = 60
  filename      = "${{path.module}}/functions.zip"
  source_code_hash = filebase64sha256("${{path.module}}/functions.zip")
}}

resource "aws_lambda_function" "compensate" {{
  function_name = "{project}-{env}-compensate"
  role          = aws_iam_role.lambda.arn
  handler       = "compensate.handler"
  runtime       = "nodejs20.x"
  architectures = ["arm64"]
  memory_size   = 256
  timeout       = 30
  filename      = "${{path.module}}/functions.zip"
  source_code_hash = filebase64sha256("${{path.module}}/functions.zip")
}}

resource "aws_cloudwatch_log_group" "sfn" {{
  name              = "/aws/states/{project}-{env}"
  retention_in_days = {"90" if env == "production" else "14"}
}}

resource "aws_iam_role" "sfn" {{
  name = "{project}-{env}-sfn-role"
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{ Action = "sts:AssumeRole", Effect = "Allow", Principal = {{ Service = "states.amazonaws.com" }} }}]
  }})
}}

resource "aws_iam_role_policy" "sfn" {{
  role = aws_iam_role.sfn.id
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{ Effect = "Allow", Action = "lambda:InvokeFunction", Resource = "arn:aws:lambda:*:*:function:{project}-{env}-*" }},
      {{ Effect = "Allow", Action = ["logs:CreateLogDelivery", "logs:GetLogDelivery", "logs:UpdateLogDelivery", "logs:DeleteLogDelivery", "logs:ListLogDeliveries", "logs:PutResourcePolicy", "logs:DescribeResourcePolicies", "logs:DescribeLogGroups"], Resource = "*" }},
    ]
  }})
}}

resource "aws_iam_role" "lambda" {{
  name = "{project}-{env}-wf-lambda"
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{ Action = "sts:AssumeRole", Effect = "Allow", Principal = {{ Service = "lambda.amazonaws.com" }} }}]
  }})
}}

resource "aws_iam_role_policy_attachment" "lambda_basic" {{
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}}
'''

    create_file(os.path.join(output, "main.tf"), main)
    create_file(os.path.join(output, "workflow.asl.json"), asl)
    create_file(os.path.join(output, "variables.tf"), f'variable "region" {{ default = "us-east-1" }}\n')


GENERATORS = {
    ("aws", "api"): aws_api,
    ("aws", "event-processing"): aws_event_processing,
    ("aws", "workflow"): aws_workflow,
}


def main():
    parser = argparse.ArgumentParser(description="Generate Serverless Terraform")
    parser.add_argument("--provider", choices=["aws", "azure"], required=True)
    parser.add_argument("--pattern", choices=["api", "event-processing", "workflow", "data-pipeline"], required=True)
    parser.add_argument("--project", default="myapp")
    parser.add_argument("--environment", default="production")
    parser.add_argument("--output", default="./serverless")
    args = parser.parse_args()

    key = (args.provider, args.pattern)
    gen = GENERATORS.get(key)

    if not gen:
        print(f"⚠️  {args.provider}/{args.pattern} — use reference docs for this combo.")
        print(f"   Available generators: {list(GENERATORS.keys())}")
        return

    print(f"\n⚡ Generating {args.provider.upper()} {args.pattern} serverless ({args.environment})\n")
    gen(args.environment, args.project, args.output)
    print(f"\n✅ Serverless config generated at: {args.output}/")


if __name__ == "__main__":
    main()

```
