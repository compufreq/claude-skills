# Prometheus & Grafana Reference

## Table of Contents
1. Prometheus Setup
2. PromQL Essentials
3. Alerting Rules & Alertmanager
4. Grafana Dashboards
5. Recording Rules

---

## 1. Prometheus Setup

### Helm Installation (kube-prometheus-stack)
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f monitoring-values.yaml
```

### monitoring-values.yaml
```yaml
prometheus:
  prometheusSpec:
    retention: 15d
    retentionSize: 50GB
    resources:
      requests: { cpu: 500m, memory: 2Gi }
      limits: { cpu: 2, memory: 4Gi }
    storageSpec:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 100Gi
    serviceMonitorSelectorNilUsesHelmValues: false
    podMonitorSelectorNilUsesHelmValues: false

grafana:
  adminPassword: ${GRAFANA_PASSWORD}
  persistence:
    enabled: true
    size: 10Gi
  dashboardProviders:
    dashboardproviders.yaml:
      apiVersion: 1
      providers:
        - name: default
          folder: ''
          type: file
          disableDeletion: false
          editable: true
          options:
            path: /var/lib/grafana/dashboards

alertmanager:
  alertmanagerSpec:
    storage:
      volumeClaimTemplate:
        spec:
          resources:
            requests:
              storage: 10Gi
```

### ServiceMonitor (Scrape Application Metrics)
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: myapp
  namespace: production
  labels:
    release: prometheus    # Must match Prometheus operator selector
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: myapp
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
      scrapeTimeout: 10s
  namespaceSelector:
    matchNames: [production]
```

### PodMonitor (Scrape Pods Without a Service)
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: batch-jobs
spec:
  selector:
    matchLabels:
      app: batch-worker
  podMetricsEndpoints:
    - port: metrics
      interval: 30s
```

---

## 2. PromQL Essentials

### Rate & Increase
```promql
# Request rate (per-second) over 5 minutes
rate(http_requests_total[5m])

# Request rate by status code
sum by (status) (rate(http_requests_total[5m]))

# Error rate percentage
sum(rate(http_requests_total{status=~"5.."}[5m]))
/ sum(rate(http_requests_total[5m])) * 100

# Total requests in last hour
increase(http_requests_total[1h])
```

### Latency (Histograms)
```promql
# P50 latency
histogram_quantile(0.50, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))

# P95 latency
histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))

# P99 latency by endpoint
histogram_quantile(0.99,
  sum by (le, handler) (rate(http_request_duration_seconds_bucket[5m]))
)

# Average latency
rate(http_request_duration_seconds_sum[5m])
/ rate(http_request_duration_seconds_count[5m])
```

### Resource Utilization
```promql
# CPU usage by pod
sum by (pod) (rate(container_cpu_usage_seconds_total{namespace="production"}[5m]))

# Memory usage by pod (bytes → MB)
sum by (pod) (container_memory_working_set_bytes{namespace="production"}) / 1024 / 1024

# Disk usage percentage
(node_filesystem_size_bytes - node_filesystem_avail_bytes)
/ node_filesystem_size_bytes * 100

# Network I/O (bytes/sec)
rate(container_network_receive_bytes_total{namespace="production"}[5m])
```

### Aggregation & Filtering
```promql
# Top 5 pods by CPU
topk(5, sum by (pod) (rate(container_cpu_usage_seconds_total[5m])))

# Requests excluding health checks
rate(http_requests_total{handler!="/health",handler!="/ready"}[5m])

# Average across all instances
avg(rate(http_requests_total[5m]))

# Group by and count
count by (status) (http_requests_total)
```

---

## 3. Alerting Rules & Alertmanager

### PrometheusRule
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: myapp-alerts
  labels:
    release: prometheus
spec:
  groups:
    - name: myapp.rules
      rules:
        # High error rate
        - alert: HighErrorRate
          expr: |
            sum(rate(http_requests_total{status=~"5.."}[5m]))
            / sum(rate(http_requests_total[5m])) > 0.05
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "Error rate > 5% for 5 minutes"
            description: "Current error rate: {{ $value | humanizePercentage }}"
            runbook: "https://wiki.example.com/runbooks/high-error-rate"

        # High latency
        - alert: HighP99Latency
          expr: |
            histogram_quantile(0.99,
              sum by (le) (rate(http_request_duration_seconds_bucket[5m]))
            ) > 2
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "P99 latency > 2 seconds"
            description: "Current p99: {{ $value | humanizeDuration }}"

        # Pod crash looping
        - alert: PodCrashLooping
          expr: increase(kube_pod_container_status_restarts_total{namespace="production"}[1h]) > 3
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "Pod {{ $labels.pod }} is crash-looping"

        # High memory usage
        - alert: HighMemoryUsage
          expr: |
            sum by (pod) (container_memory_working_set_bytes{namespace="production"})
            / sum by (pod) (kube_pod_container_resource_limits{resource="memory",namespace="production"})
            > 0.9
          for: 10m
          labels:
            severity: warning
          annotations:
            summary: "Pod {{ $labels.pod }} memory > 90% of limit"

        # Disk space low
        - alert: DiskSpaceLow
          expr: |
            (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) < 0.15
          for: 10m
          labels:
            severity: warning
          annotations:
            summary: "Disk space < 15% on {{ $labels.instance }}"
```

### Alertmanager Configuration
```yaml
apiVersion: monitoring.coreos.com/v1alpha1
kind: AlertmanagerConfig
metadata:
  name: myapp-routes
spec:
  route:
    receiver: default
    groupBy: ['alertname', 'namespace']
    groupWait: 30s
    groupInterval: 5m
    repeatInterval: 4h
    routes:
      - matchers:
          - name: severity
            value: critical
        receiver: pagerduty
        repeatInterval: 1h
      - matchers:
          - name: severity
            value: warning
        receiver: slack
  receivers:
    - name: default
      slackConfigs:
        - apiURL:
            name: slack-webhook-secret
            key: url
          channel: '#monitoring'
          title: '{{ .GroupLabels.alertname }}'
          text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
    - name: pagerduty
      pagerdutyConfigs:
        - serviceKey:
            name: pagerduty-secret
            key: service-key
          severity: '{{ .CommonLabels.severity }}'
    - name: slack
      slackConfigs:
        - apiURL:
            name: slack-webhook-secret
            key: url
          channel: '#alerts'
```

---

## 4. Grafana Dashboards

### Standard Application Dashboard Panels

A well-structured service dashboard includes these panels in order:

1. **Request Rate** — `sum(rate(http_requests_total[5m]))` (graph)
2. **Error Rate %** — errors/total × 100 (graph with threshold line)
3. **Latency (p50/p95/p99)** — `histogram_quantile` (graph)
4. **Active Connections** — gauge or graph
5. **CPU by Pod** — `container_cpu_usage_seconds_total` (graph)
6. **Memory by Pod** — `container_memory_working_set_bytes` (graph)
7. **Pod Restarts** — `kube_pod_container_status_restarts_total` (stat)
8. **HPA Current vs Desired** — replicas (graph)
9. **Dependency Latency** — database, cache, external APIs (graph)
10. **Recent Logs** — Loki panel with error filter (table)

### Dashboard as Code (Grafana JSON)
```json
{
  "dashboard": {
    "title": "MyApp - Production",
    "panels": [
      {
        "title": "Request Rate",
        "type": "timeseries",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{namespace=\"production\"}[5m]))",
            "legendFormat": "Total RPS"
          }
        ]
      }
    ]
  }
}
```

Store dashboards in Git, deploy via Grafana provisioning or the API.

---

## 5. Recording Rules

Pre-compute expensive queries for dashboard performance:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: recording-rules
spec:
  groups:
    - name: myapp.recordings
      interval: 30s
      rules:
        - record: myapp:request_rate:5m
          expr: sum(rate(http_requests_total[5m]))

        - record: myapp:error_rate:5m
          expr: |
            sum(rate(http_requests_total{status=~"5.."}[5m]))
            / sum(rate(http_requests_total[5m]))

        - record: myapp:latency_p99:5m
          expr: |
            histogram_quantile(0.99,
              sum by (le) (rate(http_request_duration_seconds_bucket[5m]))
            )

        # Use in dashboards: myapp:request_rate:5m (fast lookup, no computation)
```



---
