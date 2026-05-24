# Event-Driven Patterns Reference

## Table of Contents
1. Event Bus (EventBridge / Event Grid)
2. Queue Processing (SQS / Service Bus)
3. Fan-Out Patterns
4. Event Design Standards
5. Error Handling & DLQ

---

## 1. Event Bus (EventBridge / Event Grid)

### AWS EventBridge
```hcl
resource "aws_cloudwatch_event_bus" "app" {
  name = "${var.project}-events"
}

# Rule: Route order events to processing Lambda
resource "aws_cloudwatch_event_rule" "order_placed" {
  name           = "order-placed"
  event_bus_name = aws_cloudwatch_event_bus.app.name
  event_pattern = jsonencode({
    source      = ["order-service"]
    detail-type = ["OrderPlaced"]
  })
}

resource "aws_cloudwatch_event_target" "process_order" {
  rule           = aws_cloudwatch_event_rule.order_placed.name
  event_bus_name = aws_cloudwatch_event_bus.app.name
  arn            = aws_lambda_function.process_order.arn
  dead_letter_config { arn = aws_sqs_queue.event_dlq.arn }
  retry_policy {
    maximum_event_age_in_seconds = 3600
    maximum_retry_attempts       = 3
  }
}

# Multiple targets (fan-out)
resource "aws_cloudwatch_event_target" "notify" {
  rule           = aws_cloudwatch_event_rule.order_placed.name
  event_bus_name = aws_cloudwatch_event_bus.app.name
  arn            = aws_lambda_function.send_notification.arn
}

resource "aws_cloudwatch_event_target" "analytics" {
  rule           = aws_cloudwatch_event_rule.order_placed.name
  event_bus_name = aws_cloudwatch_event_bus.app.name
  arn            = aws_sqs_queue.analytics.arn
}
```

### Publishing Events
```javascript
const { EventBridgeClient, PutEventsCommand } = require('@aws-sdk/client-eventbridge');
const eb = new EventBridgeClient({});

async function publishEvent(eventType, data) {
  await eb.send(new PutEventsCommand({
    Entries: [{
      Source: 'order-service',
      DetailType: eventType,
      Detail: JSON.stringify({
        ...data,
        metadata: {
          correlationId: context.awsRequestId,
          timestamp: new Date().toISOString(),
          version: '1.0',
        },
      }),
      EventBusName: process.env.EVENT_BUS_NAME,
    }],
  }));
}

// Usage
await publishEvent('OrderPlaced', { orderId: 'ord-123', userId: 'usr-456', total: 99.99 });
```

### Azure Event Grid
```hcl
resource "azurerm_eventgrid_topic" "app" {
  name                = "${var.project}-events"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  input_schema        = "CloudEventSchemaV1_0"
}

resource "azurerm_eventgrid_event_subscription" "process_order" {
  name  = "process-order"
  scope = azurerm_eventgrid_topic.app.id

  azure_function_endpoint {
    function_id = "${azurerm_linux_function_app.main.id}/functions/ProcessOrder"
    max_events_per_batch              = 1
    preferred_batch_size_in_kilobytes = 64
  }

  subject_filter {
    subject_begins_with = "/orders/"
  }

  advanced_filter {
    string_in {
      key    = "data.eventType"
      values = ["OrderPlaced", "OrderUpdated"]
    }
  }

  retry_policy {
    max_delivery_attempts = 30
    event_time_to_live    = 1440
  }

  dead_letter_identity {
    type = "SystemAssigned"
  }
}
```

---

## 2. Queue Processing (SQS / Service Bus)

### AWS SQS → Lambda
```hcl
resource "aws_sqs_queue" "tasks" {
  name                       = "${var.project}-tasks"
  visibility_timeout_seconds = 300    # 6x Lambda timeout
  message_retention_seconds  = 1209600  # 14 days
  receive_wait_time_seconds  = 20     # Long polling

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.tasks_dlq.arn
    maxReceiveCount     = 3
  })
}

resource "aws_sqs_queue" "tasks_dlq" {
  name                      = "${var.project}-tasks-dlq"
  message_retention_seconds = 1209600
}

resource "aws_lambda_event_source_mapping" "tasks" {
  event_source_arn                   = aws_sqs_queue.tasks.arn
  function_name                      = aws_lambda_function.worker.arn
  batch_size                         = 10
  maximum_batching_window_in_seconds = 5
  function_response_types            = ["ReportBatchItemFailures"]

  scaling_config {
    maximum_concurrency = 50
  }
}
```

### Partial Batch Failure Handling
```javascript
exports.handler = async (event) => {
  const failedItems = [];

  for (const record of event.Records) {
    try {
      const body = JSON.parse(record.body);
      await processTask(body);
    } catch (error) {
      console.error({ level: 'error', messageId: record.messageId, error: error.message });
      failedItems.push({ itemIdentifier: record.messageId });
    }
  }

  // Only failed items will be retried (not the whole batch)
  return { batchItemFailures: failedItems };
};
```

### Azure Service Bus → Functions
```javascript
// function.json
{
  "bindings": [{
    "name": "message",
    "type": "serviceBusTrigger",
    "direction": "in",
    "queueName": "tasks",
    "connection": "ServiceBusConnection",
    "maxConcurrentCalls": 16,
    "autoCompleteMessages": true
  }]
}
```

---

## 3. Fan-Out Patterns

### SNS → SQS Fan-Out (AWS)
```
                   ┌──→ SQS Queue A → Lambda (process)
Event → SNS Topic ─┼──→ SQS Queue B → Lambda (notify)
                   └──→ SQS Queue C → Lambda (archive)
```

```hcl
resource "aws_sns_topic" "order_events" {
  name = "${var.project}-order-events"
}

# Each consumer gets its own queue (independent processing, backpressure)
resource "aws_sqs_queue" "process" {
  name = "${var.project}-order-process"
}

resource "aws_sqs_queue" "notify" {
  name = "${var.project}-order-notify"
}

resource "aws_sns_topic_subscription" "process" {
  topic_arn = aws_sns_topic.order_events.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.process.arn

  filter_policy = jsonencode({
    eventType = ["OrderPlaced", "OrderShipped"]
  })
}

resource "aws_sns_topic_subscription" "notify" {
  topic_arn = aws_sns_topic.order_events.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.notify.arn
}
```

### EventBridge Fan-Out (Preferred)
```
Event → EventBridge ──→ Rule 1 → Lambda (process)
                    ──→ Rule 2 → Lambda (notify)
                    ──→ Rule 3 → SQS (archive)
                    ──→ Rule 4 → Step Functions (complex workflow)
```

Advantages over SNS: content filtering, schema registry, event replay, cross-account routing.

---

## 4. Event Design Standards

### CloudEvents Envelope
```json
{
  "specversion": "1.0",
  "type": "com.example.order.placed",
  "source": "urn:example:order-service",
  "id": "evt-abc123",
  "time": "2025-01-15T10:30:00Z",
  "datacontenttype": "application/json",
  "data": {
    "orderId": "ord-456",
    "userId": "usr-789",
    "total": 99.99,
    "currency": "USD",
    "items": [{"sku": "ITEM-001", "qty": 2, "price": 49.99}]
  }
}
```

### Event Naming Convention
```
{domain}.{entity}.{action}

Examples:
  order.placed
  order.confirmed
  order.shipped
  order.cancelled
  payment.processed
  payment.failed
  user.registered
  user.profile.updated
  inventory.reserved
  inventory.released
```

### Event Versioning
```json
{
  "type": "order.placed",
  "dataVersion": "2",
  "data": {
    "orderId": "ord-456",
    "totalAmount": 99.99,
    "currency": "USD"
  }
}
```
- Add new fields (backward compatible) — consumers ignore unknown fields
- Breaking changes → new event type (e.g., `order.placed.v2`)
- Use schema registry (EventBridge Schema Registry) for documentation

---

## 5. Error Handling & DLQ

### Dead Letter Queue Strategy
```
Every async Lambda invocation MUST have a DLQ:
  - SQS event source → SQS DLQ (via redrive policy)
  - SNS → SQS DLQ (on the subscription)
  - EventBridge → SQS DLQ (on the target)
  - Async invoke → Lambda destination (on-failure)
  - Step Functions → catch block → error handler
```

### DLQ Processing
```javascript
// DLQ processor — analyze and reprocess or alert
exports.handler = async (event) => {
  for (const record of event.Records) {
    const originalMessage = JSON.parse(record.body);
    const receiveCount = record.attributes.ApproximateReceiveCount;

    console.log(JSON.stringify({
      level: 'warn',
      message: 'DLQ message received',
      messageId: record.messageId,
      receiveCount,
      originalMessage,
    }));

    // Option 1: Reprocess (with fix)
    // await reprocess(originalMessage);

    // Option 2: Alert and store for manual review
    await alertOncall(originalMessage);
    await storeForReview(originalMessage);
  }
};
```

### Retry Strategy

| Invocation Type | Retry | Backoff | DLQ |
|----------------|-------|---------|-----|
| API Gateway (sync) | No retry | N/A | No — return error to client |
| SQS (async) | 3 retries | Visibility timeout | SQS DLQ |
| SNS (push) | 3 retries | Exponential | SQS DLQ |
| EventBridge | Configurable | Configurable | SQS DLQ |
| DynamoDB Streams | Infinite until shard expires | Bisect batch | Lambda destination |
| Step Functions | Per-state catch/retry | Configurable | Catch → error handler |



---
