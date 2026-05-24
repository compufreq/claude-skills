# Architecture Patterns Reference

## Table of Contents
1. Multi-Tier (N-Tier)
2. Microservices
3. Event-Driven
4. CQRS & Event Sourcing
5. Pattern Selection Guide

---

## 1. Multi-Tier (N-Tier)

### Three-Tier Web Application

```
              ┌─────────────────────────────┐
              │    Presentation Tier          │
              │  CloudFront/Front Door + S3   │
              │  Static assets, SPA           │
              └──────────┬──────────────────┘
                         │
              ┌──────────▼──────────────────┐
              │    Application Tier           │
              │  ALB/App GW → ECS/AKS        │
              │  API servers, business logic  │
              │  Auto-scaling, multi-AZ       │
              └──────────┬──────────────────┘
                         │
              ┌──────────▼──────────────────┐
              │    Data Tier                  │
              │  RDS Multi-AZ / Azure SQL     │
              │  ElastiCache / Redis          │
              │  S3 / Blob for files          │
              └─────────────────────────────┘
```

### AWS Implementation
```
User → CloudFront → S3 (SPA)
                  → ALB → ECS Fargate (API)
                              ↓
                     RDS PostgreSQL (Multi-AZ)
                     ElastiCache Redis
                     S3 (uploads)
```

### Azure Implementation
```
User → Front Door → Blob Storage (SPA)
                  → App Gateway → AKS / App Service (API)
                                      ↓
                           Azure SQL (Zone Redundant)
                           Azure Cache for Redis
                           Blob Storage (uploads)
```

### When to Use
- Traditional web applications with clear separation of concerns
- Teams familiar with layered architecture
- Applications with moderate complexity (5-15 services)

---

## 2. Microservices

### Architecture
```
                    API Gateway
                   ╱    │      ╲
           ┌──────┐ ┌──────┐ ┌──────┐
           │User  │ │Order │ │Payment│
           │Svc   │ │Svc   │ │Svc   │
           └──┬───┘ └──┬───┘ └──┬───┘
              │        │        │
           ┌──▼──┐  ┌──▼──┐  ┌─▼────┐
           │UserDB│  │Order│  │Pay DB│
           │      │  │DB   │  │      │
           └──────┘  └─────┘  └──────┘
                    Event Bus (SNS/SQS, Event Hub, Kafka)
```

### Service Design Principles
1. **Single responsibility** — each service owns one business capability
2. **Database per service** — no shared databases
3. **API-first** — services communicate through well-defined APIs
4. **Independent deployment** — deploy any service without affecting others
5. **Decentralized governance** — teams choose their own tech stack
6. **Design for failure** — circuit breakers, retries, fallbacks

### Communication Patterns

| Pattern | When | Example |
|---------|------|---------|
| **Synchronous (REST/gRPC)** | Need immediate response | Get user profile |
| **Async (events/queues)** | Eventual consistency OK | Order placed → notify |
| **Saga** | Distributed transactions | Order → Payment → Inventory |
| **CQRS** | Different read/write models | Write to DB, read from cache |

### Service Boundaries
```
Bounded Contexts (DDD):
  User Context:     Registration, Profile, Authentication
  Order Context:    Cart, Checkout, Order History
  Payment Context:  Payment Processing, Refunds, Invoicing
  Inventory Context: Stock, Warehousing, Shipping
  Notification:     Email, SMS, Push Notifications
```

### AWS Microservices Stack
```
API Gateway (HTTP API) → NLB (gRPC)
ECS Fargate / EKS (compute)
SQS / SNS / EventBridge (async messaging)
DynamoDB / RDS per service (data)
ElastiCache (caching)
X-Ray (tracing)
CloudWatch (metrics/logs)
```

### Azure Microservices Stack
```
API Management / Front Door (gateway)
AKS / Container Apps (compute)
Service Bus / Event Grid (messaging)
Cosmos DB / SQL per service (data)
Azure Cache for Redis (caching)
Application Insights (tracing/metrics)
```

---

## 3. Event-Driven

### Architecture
```
Producers → Event Bus → Consumers

Example:
  Order Service → "OrderPlaced" event → Event Bus
                                          ├→ Payment Service (process payment)
                                          ├→ Inventory Service (reserve stock)
                                          ├→ Notification Service (send email)
                                          └→ Analytics Service (update metrics)
```

### AWS Event-Driven
```
Producers: Lambda, ECS, API Gateway
Event Bus: EventBridge, SNS+SQS, Kinesis
Consumers: Lambda, ECS, Step Functions
Orchestration: Step Functions (workflows)
```

### Azure Event-Driven
```
Producers: Functions, Container Apps, API Management
Event Bus: Event Grid, Service Bus, Event Hubs
Consumers: Functions, Container Apps, Logic Apps
Orchestration: Durable Functions, Logic Apps
```

### Event Design
```json
{
  "eventType": "order.placed",
  "eventId": "evt_abc123",
  "timestamp": "2025-01-15T10:30:00Z",
  "source": "order-service",
  "version": "1.0",
  "data": {
    "orderId": "ord_456",
    "userId": "usr_789",
    "total": 99.99,
    "items": [{"sku": "ITEM-001", "qty": 2}]
  },
  "metadata": {
    "correlationId": "req_def456",
    "traceId": "trace_ghi789"
  }
}
```

---

## 4. CQRS & Event Sourcing

### CQRS (Command Query Responsibility Segregation)
```
Write Path:                        Read Path:
  Client → API → Command Handler    Client → API → Query Handler
                    ↓                                  ↓
              Write Database              Read Database (denormalized)
              (normalized)                (optimized for queries)
                    ↓
              Event → Projection → Read Database
```

### When CQRS Adds Value
- Read and write patterns differ significantly
- Read-heavy workloads (10:1 read:write ratio)
- Complex queries that don't map to write model
- Need different scaling for reads vs writes

### Saga Pattern (Distributed Transactions)
```
Choreography Saga:
  Order Service → "OrderCreated" → Payment Service → "PaymentCompleted" → Inventory Service
                                   "PaymentFailed" → Order Service (compensate: cancel order)

Orchestration Saga (Step Functions / Durable Functions):
  Orchestrator → Create Order → Process Payment → Reserve Inventory → Confirm Order
                                      ↓ (failure)
                              Compensate: Refund → Cancel Order
```

---

## 5. Pattern Selection Guide

| Factor | Monolith | Multi-Tier | Microservices | Serverless |
|--------|---------|-----------|---------------|-----------|
| Team size | 1-5 | 3-15 | 10+ | 1-10 |
| Complexity | Low-Medium | Medium | High | Low-Medium |
| Deployment speed | Slow (all-or-nothing) | Medium | Fast (per service) | Fast (per function) |
| Scaling | Vertical | Tier-based | Per service | Automatic |
| Operations | Simple | Medium | Complex | Low (managed) |
| Cost at low scale | Low | Medium | High (overhead) | Very low |
| Cost at high scale | High | Medium | Optimized | Variable |
| Best for | MVPs, simple apps | Traditional web apps | Complex domains, large teams | Event-driven, APIs |

### Migration Path
```
Monolith → Modular Monolith → Multi-Tier → Microservices
                                              ↓
Start here ─────────── Don't start here ──────┘
(unless you've earned the complexity)
```

### Architecture Fitness Functions
Validate architecture decisions with measurable criteria:

| Fitness Function | Target | Measurement |
|-----------------|--------|-------------|
| Deployment frequency | > 1/day per service | CI/CD metrics |
| Lead time | < 1 hour | Commit to production |
| Service independence | 0 shared databases | Architecture review |
| Blast radius | < 5% users affected per deploy | Feature flags + canary |
| Recovery time | < 15 minutes | Chaos engineering tests |
| Cost per transaction | Decreasing trend | FinOps dashboard |



---
