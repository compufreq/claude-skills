---
name: cloud-monitoring
description: >
  Comprehensive cloud monitoring skill covering AWS CloudWatch, Azure Monitor, Prometheus/Grafana,
  SLO/SLI frameworks, and observability best practices. Use this skill whenever the user mentions
  CloudWatch, CloudWatch Logs, Logs Insights, CloudWatch Alarms, CloudWatch dashboards, Azure
  Monitor, Application Insights, Log Analytics, KQL, Prometheus, PromQL, Grafana, Alertmanager,
  metrics, monitoring, observability, alerting, dashboards, SLO, SLI, SLA, error budget, burn
  rate, golden signals, RED method, USE method, latency, throughput, error rate, saturation,
  APM, tracing, distributed tracing, structured logging, log aggregation, metric collection,
  anomaly detection, or any request involving setting up monitoring, creating dashboards,
  configuring alerts, defining SLOs, or implementing observability for cloud applications.
  Also trigger for performance troubleshooting, incident investigation, or capacity planning.
---

# Cloud Monitoring

A production-grade skill for implementing observability across AWS, Azure, and
Prometheus/Grafana, including SLO frameworks and alerting strategies.

## Quick Reference

| Platform | Metrics | Logs | Traces | Reference |
|----------|---------|------|--------|-----------|
| AWS | CloudWatch Metrics | CloudWatch Logs | X-Ray | `references/aws-monitoring.md` |
| Azure | Azure Monitor | Log Analytics | App Insights | `references/azure-monitoring.md` |
| OSS | Prometheus | Loki | Jaeger/Tempo | `references/prometheus-grafana.md` |
| SLOs | All platforms | — | — | `references/slo-framework.md` |

## Observability Pillars

```
                    Observability
                    ╱     │      ╲
              Metrics   Logs    Traces
              (what)   (why)   (where)
```

| Pillar | Purpose | Example |
|--------|---------|---------|
| **Metrics** | Measure system health numerically | CPU 72%, error rate 0.3%, p99 latency 450ms |
| **Logs** | Record discrete events with context | `{"level":"error","msg":"DB timeout","query_ms":5023}` |
| **Traces** | Follow a request across services | Request → API → Auth → DB → Cache → Response |

## Golden Signals (Google SRE)

| Signal | What to Measure | Alert Threshold |
|--------|----------------|----------------|
| **Latency** | Request duration (p50, p95, p99) | p99 > 1s for 5 min |
| **Traffic** | Requests per second | Anomaly detection |
| **Errors** | Error rate (5xx / total) | > 1% for 5 min |
| **Saturation** | Resource utilization (CPU, memory, disk, connections) | > 85% for 10 min |

## RED Method (Request-focused)

| Metric | Description | For |
|--------|------------|-----|
| **Rate** | Requests per second | All services |
| **Errors** | Failed requests per second | All services |
| **Duration** | Request latency distribution | All services |

## USE Method (Resource-focused)

| Metric | Description | For |
|--------|------------|-----|
| **Utilization** | % time resource is busy | CPU, disk, network |
| **Saturation** | Queue depth / backlog | I/O queues, thread pools |
| **Errors** | Error count on resource | Disk errors, network drops |

---

## Alerting Strategy

### Alert Severity Levels

| Level | Response | Example | Notification |
|-------|----------|---------|-------------|
| **P1 Critical** | Immediate, wake up on-call | Service down, data loss | PagerDuty/OpsGenie page |
| **P2 High** | Respond within 1 hour | Degraded performance, high errors | Slack + email |
| **P3 Medium** | Respond within 4 hours | Elevated latency, disk filling | Slack |
| **P4 Low** | Next business day | Non-critical warning | Email/ticket |

### Alert Design Rules
1. **Every alert must be actionable** — if nobody needs to do anything, it's noise
2. **Include runbook links** — alert description should link to resolution steps
3. **Tune thresholds** — review monthly, suppress false positives
4. **Alert on symptoms, not causes** — "error rate high" not "CPU high"
5. **Use multi-window burn rates for SLOs** — not simple thresholds
6. **Group related alerts** — don't page 10 times for one incident
7. **Test alerting** — regularly verify alerts fire and notifications reach on-call

---

## Scripts

### generate_monitoring_terraform.py
```bash
python scripts/generate_monitoring_terraform.py \
  --provider aws|azure|prometheus \
  --services api,database,cache,queue \
  --environment production \
  --project myapp \
  --output ./monitoring/
```

---

## Best Practices

1. **Structured logging everywhere** — JSON, consistent fields, trace IDs
2. **Instrument from day one** — don't wait for production issues
3. **Dashboard per service** — RED metrics + dependencies + infrastructure
4. **SLOs before scaling** — know what "good enough" means
5. **Centralize logs** — one place to search across all services
6. **Correlate metrics, logs, traces** — same request ID across all three
7. **Retention policies** — metrics 15 months, logs 30-90 days, traces 7-30 days
8. **Cost management** — high-cardinality metrics and verbose logs are expensive
9. **Anomaly detection** — use ML-based alerts for traffic patterns
10. **Runbooks for every alert** — if an alert fires, someone should know what to do



---
