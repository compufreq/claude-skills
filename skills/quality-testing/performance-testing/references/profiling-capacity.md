# Profiling, APM & Capacity Planning Reference

## 1. Application Profiling

### CPU Profiling

| Language | Tool | How |
|----------|------|-----|
| Python | `cProfile`, `py-spy` | `py-spy record -o profile.svg -- python app.py` |
| Node.js | `--prof`, `clinic.js` | `node --prof app.js` then `node --prof-process` |
| Java | `async-profiler`, JFR | `async-profiler -d 30 -o flamegraph -f out.html PID` |
| Go | `pprof` | `go tool pprof http://localhost:6060/debug/pprof/profile` |

### Flamegraph Interpretation
```
Width = time spent in function (wider = more time)
Height = call stack depth
Color = random (not meaningful)

Look for:
- Wide bars at the top → functions consuming most CPU
- Deep stacks → excessive nesting or recursion
- Plateaus → blocking operations (I/O, locks)
```

### Memory Profiling

| Language | Tool | What It Shows |
|----------|------|-------------|
| Python | `tracemalloc`, `objgraph` | Memory allocations by line |
| Node.js | `--inspect` + Chrome DevTools | Heap snapshots, allocations |
| Java | `jmap`, VisualVM, JFR | Heap dump, object retention |
| Go | `pprof` heap profile | Allocation sizes and counts |

### Database Query Profiling
```sql
-- PostgreSQL: slow query log
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1s

-- PostgreSQL: explain analyze
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE user_id = '123' ORDER BY created_at DESC LIMIT 20;

-- Look for:
-- Seq Scan on large tables → add index
-- Nested Loop with high row count → optimize join
-- Sort with high memory → add index for ORDER BY
-- Buffers: shared read (high) → data not in cache
```

## 2. APM (Application Performance Monitoring)

### APM Tool Comparison

| Tool | Strength | Pricing | Cloud-Native |
|------|---------|---------|-------------|
| **Datadog** | Full-stack, traces, logs, metrics | Per-host | Yes |
| **New Relic** | Transaction tracing, errors | Per-GB ingested | Yes |
| **Grafana/Tempo** | Open source, K8s-native | Self-hosted free | Yes |
| **AWS X-Ray** | AWS-native, Lambda support | Per-trace | AWS only |
| **Azure App Insights** | Azure-native, full APM | Per-GB | Azure only |
| **Jaeger** | Open source distributed tracing | Self-hosted free | Yes |

### OpenTelemetry (Vendor-Agnostic)
```python
# Python auto-instrumentation
pip install opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install

# Run with auto-instrumentation
opentelemetry-instrument \
  --service_name myapp \
  --exporter_otlp_endpoint http://otel-collector:4317 \
  python app.py
```

```javascript
// Node.js auto-instrumentation
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');

const sdk = new NodeSDK({
  serviceName: 'myapp',
  traceExporter: new OTLPTraceExporter({ url: 'http://otel-collector:4318/v1/traces' }),
});
sdk.start();
```

### Key APM Metrics to Track

| Metric | Description | Alert Threshold |
|--------|------------|----------------|
| Apdex score | User satisfaction index (0-1) | < 0.85 |
| Transaction p95 | 95th percentile response time | > SLO target |
| Error rate | % of failed transactions | > 1% |
| Throughput | Transactions per minute | < baseline - 20% |
| DB query time | Average query duration | > 100ms |
| External call time | Third-party API latency | > 500ms |
| GC pause time | Garbage collection duration | > 100ms |

## 3. Capacity Planning

### Capacity Model
```
Current capacity:
  Max RPS = 500 (at p95 < 500ms, error rate < 1%)
  Instances = 4 × m6i.xlarge (4 vCPU, 16 GB)
  DB = db.r6g.xlarge (4 vCPU, 32 GB)

Growth projection:
  Current traffic: 200 RPS peak
  Growth rate: 15% month-over-month
  Time to capacity: ~6 months

Scaling plan:
  Month 3: Upgrade DB to 2xlarge (headroom)
  Month 4: Add caching layer (Redis — reduce DB load 40%)
  Month 6: Add 2 more app instances (6 total)
  Month 9: Evaluate architecture changes
```

### Capacity Planning Formula
```
Required capacity = Peak traffic × Safety margin × Growth factor

Peak traffic: 200 RPS (measured)
Safety margin: 1.5× (handle spikes)
Growth factor: 1.15^6 = 2.3× (6 months at 15%/month)

Required = 200 × 1.5 × 2.3 = 690 RPS capacity needed in 6 months
```

### Right-Sizing Methodology
```
1. Measure current usage (30 days of production metrics)
2. Identify peak patterns (daily, weekly, seasonal)
3. Determine headroom needed (1.5-2× peak)
4. Calculate cost per RPS at different instance sizes
5. Choose optimal instance family
6. Set auto-scaling to handle peaks automatically
7. Review quarterly
```

### Load Test → Capacity Map

| Instance Count | Max RPS | p95 Latency | Error Rate | Cost/Month |
|---------------|---------|-------------|-----------|-----------|
| 2 | 250 | 200ms | 0.01% | $140 |
| 4 | 500 | 180ms | 0.01% | $280 |
| 6 | 720 | 210ms | 0.02% | $420 |
| 8 | 900 | 250ms | 0.05% | $560 |
| 10 | 1050 | 350ms | 0.1% | $700 |
| 12 | 1100 | 500ms | 0.5% | $840 |  ← Diminishing returns

**Bottleneck at 10+ instances:** Database becomes the limiter → add read replicas or caching.

## 4. Performance Testing Checklist

### Before Testing
- [ ] Define success criteria (SLOs, thresholds)
- [ ] Prepare test environment (production-like)
- [ ] Prepare test data (realistic volume)
- [ ] Set up monitoring dashboards
- [ ] Notify team about test window
- [ ] Baseline measurement (current performance)

### During Testing
- [ ] Monitor system metrics (CPU, memory, network, disk)
- [ ] Monitor application metrics (latency, errors, throughput)
- [ ] Monitor database metrics (connections, query time, IOPS)
- [ ] Watch for cascading failures
- [ ] Take note of when degradation starts

### After Testing
- [ ] Generate reports with graphs
- [ ] Compare against success criteria
- [ ] Document bottlenecks found
- [ ] Create remediation tickets
- [ ] Update capacity planning model
- [ ] Archive results for trend analysis



---
