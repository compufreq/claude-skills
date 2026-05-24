# SLO Framework Reference

## Table of Contents
1. SLI / SLO / SLA Definitions
2. Choosing SLIs
3. Setting SLO Targets
4. Error Budgets
5. Burn Rate Alerts
6. SLO Implementation

---

## 1. SLI / SLO / SLA Definitions

| Term | Definition | Example |
|------|-----------|---------|
| **SLI** (Service Level Indicator) | A metric that measures service quality | "99.2% of requests return 2xx in < 500ms" |
| **SLO** (Service Level Objective) | A target value for an SLI | "99.9% availability over 30 days" |
| **SLA** (Service Level Agreement) | A contract with consequences | "99.9% uptime or we refund 10%" |
| **Error Budget** | Allowed failure = 1 - SLO target | "0.1% of requests can fail per month" |

### Relationship
```
SLA ≤ SLO (SLO is stricter than the SLA you promise customers)

Example:
  SLA: 99.9% availability (contractual)
  SLO: 99.95% availability (internal target — leaves margin)
  SLI: (successful requests / total requests) over 30 days
  Error Budget: 0.05% = ~21.6 minutes/month of downtime
```

---

## 2. Choosing SLIs

### SLI Types

| SLI Type | Measures | Formula |
|----------|---------|---------|
| **Availability** | Successful requests | good_events / total_events |
| **Latency** | Fast enough responses | fast_requests / total_requests |
| **Correctness** | Accurate results | correct_responses / total_responses |
| **Freshness** | Data recency | fresh_data_reads / total_reads |
| **Throughput** | Capacity | requests_served / capacity_limit |

### SLI Selection by Service Type

| Service Type | Primary SLI | Secondary SLI |
|-------------|------------|---------------|
| API / Web app | Availability + Latency | Error rate |
| Database | Availability + Latency | Replication lag |
| Queue / Stream | Processing latency | Queue depth |
| Batch / ETL | Completion rate | Processing time |
| CDN / Static | Availability + Latency | Cache hit rate |
| Storage | Availability + Durability | Latency |

### SLI Specification

```yaml
# SLI: Availability
sli:
  name: api_availability
  description: "Proportion of successful HTTP requests"
  type: availability
  good_events: "http_requests_total{status!~'5..'}"
  total_events: "http_requests_total"
  measurement_window: 30d

# SLI: Latency
sli:
  name: api_latency
  description: "Proportion of requests served under 500ms"
  type: latency
  good_events: "http_request_duration_seconds_bucket{le='0.5'}"
  total_events: "http_request_duration_seconds_count"
  measurement_window: 30d
```

---

## 3. Setting SLO Targets

### Common Targets

| SLO Level | Downtime/Month | Downtime/Year | Use Case |
|-----------|---------------|---------------|---------|
| 99% | 7.2 hours | 3.65 days | Internal tools, dev |
| 99.5% | 3.6 hours | 1.83 days | Internal apps |
| 99.9% | 43.2 minutes | 8.76 hours | Production APIs |
| 99.95% | 21.6 minutes | 4.38 hours | Critical services |
| 99.99% | 4.3 minutes | 52.6 minutes | Payment, auth |
| 99.999% | 26 seconds | 5.26 minutes | Life-critical systems |

### How to Choose a Target
1. **Start with 99.9%** for most production services
2. **Measure current performance** — your SLO can't be better than reality
3. **Consider dependencies** — you can't be more reliable than your least reliable dependency
4. **Talk to users** — what do they actually need?
5. **Leave SLA margin** — SLO should be stricter than SLA (e.g., SLO 99.95% → SLA 99.9%)

### Multi-SLI SLO
```yaml
slos:
  - name: api_quality
    description: "API requests are fast and successful"
    slis:
      - name: availability
        target: 99.95%
        good: "http_requests_total{status!~'5..'}"
        total: "http_requests_total"
      - name: latency_p99
        target: 99.0%
        good: "http_request_duration_seconds_bucket{le='1.0'}"
        total: "http_request_duration_seconds_count"
    window: 30d
```

---

## 4. Error Budgets

### Calculating Error Budget
```
Error Budget = 1 - SLO Target

Example (30-day window):
  SLO: 99.9% availability
  Error Budget: 0.1%
  Total requests/month: 10,000,000
  Allowed failures: 10,000 requests
  
  OR in time:
  30 days × 24 hours × 60 minutes = 43,200 minutes
  Error budget = 43,200 × 0.001 = 43.2 minutes of downtime
```

### Error Budget Policies

| Budget Remaining | Action |
|-----------------|--------|
| > 50% | Normal development velocity, deploy freely |
| 25-50% | Caution — prioritize reliability work |
| 10-25% | Slow down — no risky deploys, focus on stability |
| < 10% | Freeze deployments — all hands on reliability |
| 0% (exhausted) | Full feature freeze until budget recovers |

### Error Budget Tracking

```promql
# Current error budget consumption (Prometheus)
# SLO: 99.9% availability over 30 days

# Error budget remaining (as percentage)
1 - (
  (1 - (
    sum(rate(http_requests_total{status!~"5.."}[30d]))
    / sum(rate(http_requests_total[30d]))
  ))
  / (1 - 0.999)
)

# Simplified: budget_consumed = actual_error_rate / allowed_error_rate
# budget_remaining = 1 - budget_consumed
```

---

## 5. Burn Rate Alerts

### Why Burn Rate > Simple Threshold

Simple threshold alerts ("error rate > 0.1%") fire too early or too late.
Burn rate measures how quickly you're consuming your error budget.

```
Burn Rate = actual error rate / allowed error rate

Burn Rate 1.0 = consuming budget at exactly the allowed pace
Burn Rate 2.0 = consuming budget 2x faster than allowed (exhausted in 15 days)
Burn Rate 10.0 = consuming budget 10x faster (exhausted in 3 days)
Burn Rate 100.0 = consuming budget 100x faster (exhausted in ~7 hours)
```

### Multi-Window Burn Rate Alerts (Google SRE Recommendation)

| Alert | Burn Rate | Long Window | Short Window | Budget Consumed | Page? |
|-------|-----------|-------------|-------------|----------------|-------|
| P1 | 14.4× | 1 hour | 5 min | 2% in 1h | Yes |
| P2 | 6× | 6 hours | 30 min | 5% in 6h | Yes |
| P3 | 3× | 1 day | 2 hours | 10% in 1d | Ticket |
| P4 | 1× | 3 days | 6 hours | 10% in 3d | Ticket |

### Prometheus Burn Rate Alert Rules
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: slo-burn-rate-alerts
spec:
  groups:
    - name: slo.burn_rate
      rules:
        # Recording rules for error ratios at different windows
        - record: slo:error_ratio:1h
          expr: |
            1 - (
              sum(rate(http_requests_total{status!~"5.."}[1h]))
              / sum(rate(http_requests_total[1h]))
            )

        - record: slo:error_ratio:6h
          expr: |
            1 - (
              sum(rate(http_requests_total{status!~"5.."}[6h]))
              / sum(rate(http_requests_total[6h]))
            )

        - record: slo:error_ratio:1d
          expr: |
            1 - (
              sum(rate(http_requests_total{status!~"5.."}[1d]))
              / sum(rate(http_requests_total[1d]))
            )

        - record: slo:error_ratio:3d
          expr: |
            1 - (
              sum(rate(http_requests_total{status!~"5.."}[3d]))
              / sum(rate(http_requests_total[3d]))
            )

        # P1: 2% budget consumed in 1 hour (burn rate 14.4x)
        - alert: SLOBurnRateCritical
          expr: |
            slo:error_ratio:1h > (14.4 * 0.001)
            and
            slo:error_ratio:5m > (14.4 * 0.001)
          for: 2m
          labels:
            severity: critical
            slo: api_availability
          annotations:
            summary: "SLO burn rate critical — 2% budget consumed in 1 hour"
            description: "Error ratio: {{ $value | humanizePercentage }}"
            runbook: "https://wiki.example.com/runbooks/slo-burn-critical"

        # P2: 5% budget consumed in 6 hours (burn rate 6x)
        - alert: SLOBurnRateHigh
          expr: |
            slo:error_ratio:6h > (6 * 0.001)
            and
            slo:error_ratio:30m > (6 * 0.001)
          for: 5m
          labels:
            severity: warning
            slo: api_availability
          annotations:
            summary: "SLO burn rate high — 5% budget consumed in 6 hours"

        # P3: 10% budget consumed in 1 day (burn rate 3x)
        - alert: SLOBurnRateMedium
          expr: |
            slo:error_ratio:1d > (3 * 0.001)
            and
            slo:error_ratio:2h > (3 * 0.001)
          for: 15m
          labels:
            severity: info
            slo: api_availability
          annotations:
            summary: "SLO burn rate elevated — 10% budget consumed in 1 day"
```

---

## 6. SLO Implementation

### SLO Dashboard (Grafana)

Key panels for an SLO dashboard:
1. **Current SLI value** — e.g., "99.94% availability" (stat panel, green/yellow/red)
2. **Error budget remaining** — percentage and time remaining (gauge)
3. **Error budget burn over time** — consumption trend (graph)
4. **SLI over time** — availability/latency trend (graph)
5. **Burn rate** — current burn rate multiplier (stat)
6. **Budget forecast** — when will budget be exhausted at current rate (stat)

### Tooling Options

| Tool | Platform | Features |
|------|----------|---------|
| **Sloth** | Prometheus | Generates recording rules + alerts from SLO spec |
| **Google SLO Generator** | GCP/Prometheus | Multi-backend SLO monitoring |
| **Nobl9** | Any | SaaS SLO platform |
| **Dynatrace** | Any | Built-in SLO tracking |
| **OpenSLO** | Spec only | Vendor-neutral SLO specification |

### Sloth (Recommended for Prometheus)
```yaml
# sloth.yaml
version: "prometheus/v1"
service: "myapp"
labels:
  owner: "platform-team"
slos:
  - name: "requests-availability"
    objective: 99.9
    description: "99.9% of requests are successful"
    sli:
      events:
        error_query: sum(rate(http_requests_total{status=~"5.."}[{{.window}}]))
        total_query: sum(rate(http_requests_total[{{.window}}]))
    alerting:
      name: MyAppAvailability
      labels:
        category: availability
      annotations:
        runbook: "https://wiki.example.com/runbooks/myapp-availability"
      page_alert:
        labels:
          severity: critical
      ticket_alert:
        labels:
          severity: warning
```

```bash
# Generate Prometheus rules from SLO spec
sloth generate -i sloth.yaml -o prometheus-rules/
```

### SLO Review Cadence
- **Weekly**: Check error budget consumption, investigate any burns
- **Monthly**: SLO report to stakeholders, review targets
- **Quarterly**: Adjust SLO targets based on user needs and system capability
- **Post-incident**: Update SLIs/SLOs if incident revealed measurement gaps



---

<!-- Script: scripts/generate_monitoring_terraform.py -->

# Script: generate_monitoring_terraform.py

```python
#!/usr/bin/env python3
"""
Generate monitoring/alerting Terraform configurations.

Usage:
    python generate_monitoring_terraform.py \
        --provider aws|azure|prometheus \
        --services api,database,cache,queue \
        --environment production \
        --project myapp \
        --output ./monitoring/
"""

import argparse
import os


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


def aws_monitoring(env, project, services, output):
    svc_set = set(services.split(","))
    is_prod = env == "production"

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

# ── SNS Topics ─────────────────────────────────────────
resource "aws_sns_topic" "critical" {{
  name = "{project}-{env}-critical"
}}

resource "aws_sns_topic" "warning" {{
  name = "{project}-{env}-warning"
}}

resource "aws_sns_topic_subscription" "critical_email" {{
  topic_arn = aws_sns_topic.critical.arn
  protocol  = "email"
  endpoint  = var.critical_email
}}

resource "aws_sns_topic_subscription" "warning_email" {{
  topic_arn = aws_sns_topic.warning.arn
  protocol  = "email"
  endpoint  = var.warning_email
}}
'''

    if "api" in svc_set:
        main += f'''
# ── API Alarms ─────────────────────────────────────────
resource "aws_cloudwatch_metric_alarm" "alb_5xx" {{
  alarm_name          = "{project}-{env}-alb-5xx"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 5
  treat_missing_data  = "notBreaching"
  alarm_description   = "ALB 5xx error rate > 5%"

  metric_query {{
    id          = "error_rate"
    expression  = "(errors / requests) * 100"
    label       = "Error Rate %"
    return_data = true
  }}
  metric_query {{
    id = "errors"
    metric {{
      metric_name = "HTTPCode_ELB_5XX_Count"
      namespace   = "AWS/ApplicationELB"
      period      = 300
      stat        = "Sum"
      dimensions  = {{ LoadBalancer = var.alb_arn_suffix }}
    }}
  }}
  metric_query {{
    id = "requests"
    metric {{
      metric_name = "RequestCount"
      namespace   = "AWS/ApplicationELB"
      period      = 300
      stat        = "Sum"
      dimensions  = {{ LoadBalancer = var.alb_arn_suffix }}
    }}
  }}
  alarm_actions = [aws_sns_topic.critical.arn]
  ok_actions    = [aws_sns_topic.critical.arn]
}}

resource "aws_cloudwatch_metric_alarm" "alb_latency" {{
  alarm_name          = "{project}-{env}-alb-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  extended_statistic  = "p99"
  threshold           = 2
  treat_missing_data  = "notBreaching"
  alarm_description   = "P99 latency > 2 seconds"
  dimensions          = {{ LoadBalancer = var.alb_arn_suffix }}
  alarm_actions       = [aws_sns_topic.warning.arn]
}}
'''

    if "database" in svc_set:
        main += f'''
# ── Database Alarms ────────────────────────────────────
resource "aws_cloudwatch_metric_alarm" "rds_cpu" {{
  alarm_name          = "{project}-{env}-rds-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  dimensions          = {{ DBInstanceIdentifier = var.rds_identifier }}
  alarm_actions       = [aws_sns_topic.warning.arn]
}}

resource "aws_cloudwatch_metric_alarm" "rds_connections" {{
  alarm_name          = "{project}-{env}-rds-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 150
  dimensions          = {{ DBInstanceIdentifier = var.rds_identifier }}
  alarm_actions       = [aws_sns_topic.warning.arn]
}}

resource "aws_cloudwatch_metric_alarm" "rds_storage" {{
  alarm_name          = "{project}-{env}-rds-storage"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 5368709120    # 5 GB in bytes
  dimensions          = {{ DBInstanceIdentifier = var.rds_identifier }}
  alarm_actions       = [aws_sns_topic.critical.arn]
}}
'''

    if "cache" in svc_set:
        main += f'''
# ── Cache Alarms ───────────────────────────────────────
resource "aws_cloudwatch_metric_alarm" "redis_cpu" {{
  alarm_name          = "{project}-{env}-redis-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "EngineCPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  dimensions          = {{ ReplicationGroupId = var.redis_replication_group_id }}
  alarm_actions       = [aws_sns_topic.warning.arn]
}}

resource "aws_cloudwatch_metric_alarm" "redis_memory" {{
  alarm_name          = "{project}-{env}-redis-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  dimensions          = {{ ReplicationGroupId = var.redis_replication_group_id }}
  alarm_actions       = [aws_sns_topic.critical.arn]
}}
'''

    # Dashboard
    main += f'''
# ── Dashboard ──────────────────────────────────────────
resource "aws_cloudwatch_dashboard" "main" {{
  dashboard_name = "{project}-{env}"
  dashboard_body = jsonencode({{
    widgets = [
      {{
        type = "text"
        x = 0; y = 0; width = 24; height = 1
        properties = {{ markdown = "# {project} ({env}) Dashboard" }}
      }},
      {{
        type = "metric"
        x = 0; y = 1; width = 12; height = 6
        properties = {{
          title  = "Request Rate"
          view   = "timeSeries"
          region = var.region
          period = 60
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", var.alb_arn_suffix, {{ stat = "Sum", label = "Requests/min" }}]
          ]
        }}
      }},
      {{
        type = "metric"
        x = 12; y = 1; width = 12; height = 6
        properties = {{
          title  = "Error Rate"
          view   = "timeSeries"
          region = var.region
          period = 60
          metrics = [
            ["AWS/ApplicationELB", "HTTPCode_ELB_5XX_Count", "LoadBalancer", var.alb_arn_suffix, {{ stat = "Sum", label = "5xx", color = "#d62728" }}]
          ]
        }}
      }}
    ]
  }})
}}
'''

    variables = f'''variable "region" {{ default = "us-east-1" }}
variable "critical_email" {{ default = "oncall@example.com" }}
variable "warning_email" {{ default = "team@example.com" }}
variable "alb_arn_suffix" {{ default = "" }}
variable "rds_identifier" {{ default = "" }}
variable "redis_replication_group_id" {{ default = "" }}
variable "ecs_cluster_name" {{ default = "" }}
variable "ecs_service_name" {{ default = "" }}
'''

    create_file(os.path.join(output, "main.tf"), main)
    create_file(os.path.join(output, "variables.tf"), variables)


def prometheus_monitoring(env, project, services, output):
    svc_set = set(services.split(","))

    rules = f"""apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: {project}-alerts
  namespace: monitoring
  labels:
    release: prometheus
spec:
  groups:
    - name: {project}.recording
      interval: 30s
      rules:
        - record: {project}:request_rate:5m
          expr: sum(rate(http_requests_total{{namespace="{env}"}}[5m]))
        - record: {project}:error_rate:5m
          expr: |
            sum(rate(http_requests_total{{namespace="{env}",status=~"5.."}}[5m]))
            / sum(rate(http_requests_total{{namespace="{env}"}}[5m]))
        - record: {project}:latency_p99:5m
          expr: |
            histogram_quantile(0.99,
              sum by (le) (rate(http_request_duration_seconds_bucket{{namespace="{env}"}}[5m]))
            )

    - name: {project}.alerts
      rules:
        - alert: HighErrorRate
          expr: {project}:error_rate:5m > 0.05
          for: 5m
          labels:
            severity: critical
            service: {project}
          annotations:
            summary: "Error rate > 5%"
            description: "Current: {{{{ $value | humanizePercentage }}}}"
            runbook: "https://wiki.example.com/runbooks/{project}-errors"

        - alert: HighP99Latency
          expr: {project}:latency_p99:5m > 2
          for: 5m
          labels:
            severity: warning
            service: {project}
          annotations:
            summary: "P99 latency > 2 seconds"
            description: "Current: {{{{ $value | humanizeDuration }}}}"

        - alert: PodCrashLooping
          expr: increase(kube_pod_container_status_restarts_total{{namespace="{env}"}}[1h]) > 3
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "Pod {{{{ $labels.pod }}}} is crash-looping"
"""

    if "database" in svc_set:
        rules += f"""
        - alert: HighDBLatency
          expr: |
            histogram_quantile(0.99,
              sum by (le) (rate(db_query_duration_seconds_bucket{{namespace="{env}"}}[5m]))
            ) > 1
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "DB P99 query latency > 1 second"
"""

    if "cache" in svc_set:
        rules += f"""
        - alert: LowCacheHitRate
          expr: |
            sum(rate(redis_keyspace_hits_total[5m]))
            / (sum(rate(redis_keyspace_hits_total[5m])) + sum(rate(redis_keyspace_misses_total[5m])))
            < 0.8
          for: 15m
          labels:
            severity: warning
          annotations:
            summary: "Redis cache hit rate < 80%"
"""

    # SLO burn rate alerts
    slo_rules = f"""
    - name: {project}.slo
      rules:
        - record: slo:{project}:error_ratio:1h
          expr: |
            1 - (sum(rate(http_requests_total{{namespace="{env}",status!~"5.."}}[1h]))
            / sum(rate(http_requests_total{{namespace="{env}"}}[1h])))

        - record: slo:{project}:error_ratio:6h
          expr: |
            1 - (sum(rate(http_requests_total{{namespace="{env}",status!~"5.."}}[6h]))
            / sum(rate(http_requests_total{{namespace="{env}"}}[6h])))

        - alert: SLOBurnRateCritical
          expr: slo:{project}:error_ratio:1h > (14.4 * 0.001)
          for: 2m
          labels:
            severity: critical
            slo: {project}_availability
          annotations:
            summary: "SLO burn rate critical — exhausting error budget in < 7 hours"

        - alert: SLOBurnRateHigh
          expr: slo:{project}:error_ratio:6h > (6 * 0.001)
          for: 5m
          labels:
            severity: warning
            slo: {project}_availability
          annotations:
            summary: "SLO burn rate high — exhausting error budget in < 5 days"
"""

    rules += slo_rules

    # ServiceMonitor
    service_monitor = f"""apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {project}
  namespace: {env}
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: {project}
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
"""

    create_file(os.path.join(output, "prometheus-rules.yaml"), rules)
    create_file(os.path.join(output, "service-monitor.yaml"), service_monitor)


def main():
    parser = argparse.ArgumentParser(description="Generate Monitoring Configuration")
    parser.add_argument("--provider", choices=["aws", "azure", "prometheus"], required=True)
    parser.add_argument("--services", default="api,database,cache",
                        help="Comma-separated: api,database,cache,queue")
    parser.add_argument("--environment", default="production")
    parser.add_argument("--project", default="myapp")
    parser.add_argument("--output", default="./monitoring")
    args = parser.parse_args()

    print(f"\n📊 Generating {args.provider.upper()} monitoring ({args.environment})\n")
    print(f"   Services: {args.services}\n")

    if args.provider == "aws":
        aws_monitoring(args.environment, args.project, args.services, args.output)
    elif args.provider == "prometheus":
        prometheus_monitoring(args.environment, args.project, args.services, args.output)
    else:
        print(f"   Azure monitoring generated via references — use azurerm Terraform examples from references/azure-monitoring.md")

    print(f"\n✅ Monitoring config generated at: {args.output}/")


if __name__ == "__main__":
    main()

```
