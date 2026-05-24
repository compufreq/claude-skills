# Performance Testing Methodology

## 1. Test Types

| Type | Purpose | Load Pattern | Duration |
|------|---------|-------------|----------|
| **Load test** | Verify under expected load | Normal traffic | 10-30 min |
| **Stress test** | Find breaking point | Ramp beyond capacity | Until failure |
| **Soak test** | Find memory leaks, degradation | Sustained normal load | 2-12 hours |
| **Spike test** | Handle sudden traffic burst | Instant spike then drop | 5-15 min |
| **Breakpoint test** | Find max capacity | Gradual increase | Until error threshold |
| **Scalability test** | Verify auto-scaling works | Gradual ramp | 30-60 min |

### Load Patterns
```
Load Test:        Stress Test:      Spike Test:       Soak Test:
   ┌──────┐         ╱╲                ▲               ┌──────────────┐
   │      │        ╱  ╲              ╱╲              │              │
  ╱│      │╲      ╱    ╲            ╱  ╲             │              │
 ╱ │      │ ╲    ╱      ╲          ╱    ╲            │              │
╱  └──────┘  ╲  ╱        ╲        ╱      ╲           └──────────────┘
  10-30 min      Until break    Instant     2-12 hours
```

## 2. Key Metrics

| Metric | What | Target | Alert |
|--------|------|--------|-------|
| **Response time (p50)** | Median latency | < 200ms | > 500ms |
| **Response time (p95)** | Tail latency | < 500ms | > 1s |
| **Response time (p99)** | Worst case | < 1s | > 2s |
| **Throughput (RPS)** | Requests per second | Depends on SLO | < expected |
| **Error rate** | Failed requests % | < 0.1% | > 1% |
| **Concurrent users** | Simultaneous connections | Depends on app | > max capacity |
| **CPU utilization** | Server CPU % | < 70% under load | > 85% |
| **Memory utilization** | Server RAM % | < 80% | > 90% |
| **Network I/O** | Bandwidth usage | < 80% capacity | Saturation |
| **DB connections** | Active connections | < 80% max | > 90% |
| **Queue depth** | Backlog size | Near 0 at steady state | Growing trend |

## 3. Test Planning

### Performance Test Plan Template
```markdown
## Performance Test Plan: [Application]

### Objectives
1. Verify SLO compliance under expected peak load
2. Identify bottlenecks before production launch
3. Determine maximum capacity
4. Validate auto-scaling behavior

### Scope
- Endpoints under test: [list]
- User flows: [list critical journeys]
- Excluded: [admin panels, batch jobs, etc.]

### Workload Model
| Scenario | % of Traffic | Users | RPS | Think Time |
|----------|-------------|-------|-----|-----------|
| Browse products | 50% | 500 | 100 | 5-10s |
| Search | 20% | 200 | 40 | 3-5s |
| Add to cart | 15% | 150 | 30 | 2-4s |
| Checkout | 10% | 100 | 20 | 10-30s |
| Account management | 5% | 50 | 10 | 5-10s |

### Success Criteria
- p95 response time < 500ms for all endpoints
- Error rate < 0.1% under peak load
- System stable at 2x expected peak for 30 minutes
- Auto-scaling triggers within 2 minutes of load increase

### Environment
- Target: staging (production-like sizing)
- Data: production-like dataset (anonymized)
- External dependencies: mocked / throttled
```

## 4. Performance Budgets

### Web Performance Budget
| Metric | Budget | Tool |
|--------|--------|------|
| Largest Contentful Paint (LCP) | < 2.5s | Lighthouse |
| First Input Delay (FID) | < 100ms | Lighthouse |
| Cumulative Layout Shift (CLS) | < 0.1 | Lighthouse |
| Time to First Byte (TTFB) | < 200ms | WebPageTest |
| Total page weight | < 1 MB | Webpack analyzer |
| JavaScript bundle | < 300 KB (gzipped) | Bundle analyzer |

### API Performance Budget
| Metric | Budget | Enforcement |
|--------|--------|-------------|
| GET endpoints (p95) | < 200ms | CI perf test |
| POST/PUT endpoints (p95) | < 500ms | CI perf test |
| Search endpoints (p95) | < 1s | CI perf test |
| Error rate under load | < 0.1% | Load test |
| Throughput (sustained) | > 500 RPS | Load test |

### Enforcing Budgets in CI
```yaml
# Lighthouse CI
- name: Lighthouse Budget Check
  run: |
    npx lhci autorun --config=lighthouserc.json
    # Fails CI if budget exceeded

# k6 threshold
export const options = {
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
  },
};
```

## 5. Common Bottlenecks

| Bottleneck | Symptoms | Investigation | Fix |
|-----------|----------|--------------|-----|
| **N+1 queries** | Latency scales with data size | APM, slow query log | Eager loading, batch queries |
| **Missing indexes** | Slow DB queries under load | EXPLAIN ANALYZE | Add appropriate indexes |
| **No connection pooling** | DB connection errors at load | Connection count monitoring | RDS Proxy, PgBouncer |
| **Synchronous I/O** | Thread/worker pool exhaustion | Thread dump, profiler | Async I/O, event loop |
| **No caching** | Same expensive computation repeated | Cache hit rate metrics | Redis, CDN, memoization |
| **Large payloads** | High bandwidth, slow responses | Network waterfall | Pagination, compression, field selection |
| **Memory leaks** | Growing memory over time | Heap dumps, soak test | Fix leak, restart strategy |
| **Cold starts** | Spiky latency after idle | Latency distribution | Provisioned concurrency, keep-alive |
| **GC pauses** | Periodic latency spikes | GC logs, profiler | Tune GC, reduce allocations |



---
