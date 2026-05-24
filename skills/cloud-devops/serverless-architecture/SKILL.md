---
name: serverless-architecture
description: >
  Comprehensive serverless architecture skill covering API patterns, event-driven design,
  workflow orchestration, and data patterns for AWS and Azure. Use this skill whenever the user
  mentions serverless architecture, serverless design, event-driven architecture, API Gateway
  pattern, Lambda architecture, Azure Functions architecture, Step Functions, Durable Functions,
  state machine, workflow orchestration, EventBridge, SNS, SQS, fan-out, fan-in, Event Grid,
  Service Bus, choreography, saga pattern, serverless API, GraphQL serverless, AppSync,
  DynamoDB streams, S3 events, serverless data pipeline, CQRS serverless, event sourcing
  serverless, serverless microservices, function composition, cold start architecture,
  serverless security, serverless testing, or any request involving designing applications
  that use serverless compute, event-driven messaging, or managed orchestration services.
---

# Serverless Architecture

A production-grade skill for designing event-driven, API, and workflow architectures
using serverless services across AWS and Azure.

## Quick Reference

| Pattern | AWS | Azure | Reference |
|---------|-----|-------|-----------|
| API | API Gateway + Lambda | API Management + Functions | `references/api-patterns.md` |
| Events | EventBridge, SNS/SQS | Event Grid, Service Bus | `references/event-patterns.md` |
| Orchestration | Step Functions | Durable Functions | `references/orchestration.md` |
| Data | DynamoDB, S3, Streams | Cosmos DB, Blob, Event Hubs | `references/data-patterns.md` |

## Serverless Architecture Principles

1. **Event-driven by default** — react to events, don't poll
2. **Single-purpose functions** — one function = one responsibility
3. **Stateless compute** — store state in databases/queues, not in functions
4. **Push complexity to managed services** — let API Gateway handle auth, let DynamoDB handle scaling
5. **Design for failure** — idempotent handlers, DLQs, retries with backoff
6. **Minimize cold starts** — right-size memory, use ARM, provisioned concurrency for critical paths
7. **Observe everything** — structured logs, traces, custom metrics

## Architecture Decision Tree

```
Need to expose an API?
├── REST API → API Gateway + Lambda / APIM + Functions
├── GraphQL → AppSync + Lambda / Functions + Hot Chocolate
└── WebSocket → API Gateway WebSocket / SignalR + Functions

Need to process events?
├── AWS events → EventBridge rules → Lambda
├── Queue processing → SQS → Lambda / Service Bus → Functions
├── Fan-out → SNS → SQS → Lambda / Event Grid → Functions
└── Stream processing → Kinesis/DDB Streams → Lambda / Event Hubs → Functions

Need to orchestrate steps?
├── Sequential workflow → Step Functions / Durable Functions
├── Parallel fan-out/in → Step Functions Map / Durable Fan-out
├── Human approval → Step Functions + callback / Durable + external event
└── Long-running (days) → Step Functions Standard / Durable eternal orchestration

Need to process data?
├── File upload → S3 event → Lambda / Blob trigger → Functions
├── Database change → DDB Streams → Lambda / Cosmos Change Feed → Functions
├── Scheduled → EventBridge schedule → Lambda / Timer trigger → Functions
└── ETL pipeline → Step Functions + Lambda / Durable Functions + Data Factory
```

## Cost Model

```
Serverless Cost = Invocations × Duration × Memory + Data Transfer + Managed Service Fees

AWS Lambda: $0.20 per 1M requests + $0.0000166667 per GB-second
Azure Functions: $0.20 per 1M requests + $0.000016 per GB-second
Both: First 1M requests/month free
```

### When Serverless Saves Money
- Variable / spiky traffic (pay nothing at zero traffic)
- Low-to-moderate traffic APIs (< 10M requests/month)
- Event processing with variable volume
- Glue code between services

### When Serverless Gets Expensive
- Sustained high throughput (> 100M requests/month → consider containers)
- Long-running processes (> 5 minutes per invocation)
- Memory-intensive workloads (> 3 GB per function)
- High-frequency polling patterns

---

## Scripts

### generate_serverless_terraform.py
```bash
python scripts/generate_serverless_terraform.py \
  --provider aws|azure \
  --pattern api|event-processing|workflow|data-pipeline \
  --project myapp \
  --environment production \
  --output ./serverless/
```

---

## Best Practices

1. **Keep functions small** — < 250 lines, single responsibility
2. **Initialize outside handler** — DB connections, SDK clients at module level
3. **Use structured logging** — JSON with requestId, traceId
4. **Set timeouts appropriately** — API: 10-30s, async: 60-300s
5. **DLQ everything** — every async invocation needs a dead letter queue
6. **Idempotent handlers** — same event processed twice = same result
7. **Minimize package size** — tree-shake, use layers, exclude dev deps
8. **Use ARM/Graviton** — 20% cheaper, often faster cold starts
9. **Monitor concurrency** — set reserved concurrency to protect downstream
10. **Test locally** — SAM, Serverless Framework, Azure Functions Core Tools



---
