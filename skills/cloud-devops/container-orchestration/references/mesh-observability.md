# Service Mesh & Observability Reference

## Table of Contents
1. Istio Essentials
2. Linkerd Essentials
3. Prometheus & Grafana
4. Logging (Loki)
5. Tracing
6. Choosing: Istio vs Linkerd

---

## 1. Istio Essentials

### Installation
```bash
istioctl install --set profile=default -y
kubectl label namespace production istio-injection=enabled
```

### VirtualService (Traffic Routing)
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts: [myapp]
  http:
    - match:
        - headers:
            x-canary: { exact: "true" }
      route:
        - destination:
            host: myapp
            subset: canary
    - route:
        - destination:
            host: myapp
            subset: stable
          weight: 90
        - destination:
            host: myapp
            subset: canary
          weight: 10
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: myapp
spec:
  host: myapp
  subsets:
    - name: stable
      labels:
        version: v1
    - name: canary
      labels:
        version: v2
  trafficPolicy:
    connectionPool:
      tcp: { maxConnections: 100 }
      http: { h2UpgradePolicy: DEFAULT, http1MaxPendingRequests: 100 }
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
```

### Istio Features
- **mTLS**: Automatic mutual TLS between all services
- **Traffic splitting**: Canary deployments, A/B testing
- **Fault injection**: Test resilience by injecting errors/delays
- **Rate limiting**: Control traffic to prevent overload
- **Circuit breaking**: Prevent cascading failures
- **Retries & timeouts**: Automatic retry with exponential backoff

---

## 2. Linkerd Essentials

### Installation
```bash
linkerd install --crds | kubectl apply -f -
linkerd install | kubectl apply -f -
linkerd viz install | kubectl apply -f -

# Inject sidecar
kubectl get deploy -n production -o yaml | linkerd inject - | kubectl apply -f -
```

### Traffic Split
```yaml
apiVersion: split.smi-spec.io/v1alpha1
kind: TrafficSplit
metadata:
  name: myapp
  namespace: production
spec:
  service: myapp
  backends:
    - service: myapp-stable
      weight: 900
    - service: myapp-canary
      weight: 100
```

### Service Profile (Retries + Timeouts)
```yaml
apiVersion: linkerd.io/v1alpha2
kind: ServiceProfile
metadata:
  name: myapp.production.svc.cluster.local
  namespace: production
spec:
  routes:
    - name: GET /api/users
      condition:
        method: GET
        pathRegex: /api/users
      timeout: 5s
      isRetryable: true
    - name: POST /api/orders
      condition:
        method: POST
        pathRegex: /api/orders
      timeout: 10s
      isRetryable: false    # Don't retry mutations
```

---

## 3. Prometheus & Grafana

### ServiceMonitor (for Prometheus Operator)
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: myapp
  labels:
    release: prometheus    # Match Prometheus operator selector
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: myapp
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
      scrapeTimeout: 10s
```

### PrometheusRule (Alerting)
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: myapp-alerts
spec:
  groups:
    - name: myapp.rules
      rules:
        - alert: HighErrorRate
          expr: |
            sum(rate(http_requests_total{job="myapp",status=~"5.."}[5m]))
            / sum(rate(http_requests_total{job="myapp"}[5m])) > 0.05
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "High 5xx error rate on {{ $labels.instance }}"
            description: "Error rate is {{ $value | humanizePercentage }}"

        - alert: HighLatency
          expr: |
            histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="myapp"}[5m])) > 1
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "P95 latency above 1 second"

        - alert: PodCrashLooping
          expr: increase(kube_pod_container_status_restarts_total{namespace="production"}[1h]) > 3
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "Pod {{ $labels.pod }} is crash-looping"
```

### Grafana Dashboard JSON (Key Panels)

Standard application dashboard should include:
- Request rate (RPS) by status code
- Error rate (5xx / total)
- Latency (P50, P95, P99)
- Active connections
- Pod CPU / Memory utilization
- Pod restart count
- HPA current vs desired replicas

### Application Metrics Endpoint

**Node.js (prom-client):**
```javascript
const client = require('prom-client');
client.collectDefaultMetrics();

const httpDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration',
  labelNames: ['method', 'route', 'status'],
  buckets: [0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
});

app.get('/metrics', async (req, res) => {
  res.set('Content-Type', client.register.contentType);
  res.end(await client.register.metrics());
});
```

---

## 4. Logging (Loki)

### Structured Logging Best Practices
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "error",
  "message": "Failed to process payment",
  "service": "payment-api",
  "trace_id": "abc123",
  "span_id": "def456",
  "user_id": "usr_789",
  "order_id": "ord_012",
  "error": "stripe_timeout",
  "duration_ms": 5023
}
```

### Loki + Promtail Setup
```yaml
# Promtail config (collects logs from pods)
config:
  clients:
    - url: http://loki:3100/loki/api/v1/push
  scrape_configs:
    - job_name: kubernetes-pods
      kubernetes_sd_configs:
        - role: pod
      relabel_configs:
        - source_labels: [__meta_kubernetes_pod_label_app_kubernetes_io_name]
          target_label: app
        - source_labels: [__meta_kubernetes_namespace]
          target_label: namespace
```

### LogQL Queries (Grafana)
```
# Error logs for myapp
{app="myapp"} |= "error"

# JSON parsed with filter
{app="myapp"} | json | level="error" | duration_ms > 5000

# Rate of errors
rate({app="myapp"} |= "error" [5m])
```

---

## 5. Tracing

### OpenTelemetry Collector
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
data:
  config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
    processors:
      batch:
        timeout: 5s
    exporters:
      otlp:
        endpoint: tempo:4317
        tls:
          insecure: true
    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [batch]
          exporters: [otlp]
```

---

## 6. Choosing: Istio vs Linkerd

| Criteria | Istio | Linkerd |
|----------|-------|---------|
| Complexity | High | Low |
| Resource usage | Heavy (~100MB/sidecar) | Light (~20MB/sidecar) |
| Features | Comprehensive | Focused |
| Learning curve | Steep | Gentle |
| mTLS | Yes (auto) | Yes (auto) |
| Traffic splitting | Yes (VirtualService) | Yes (TrafficSplit) |
| Fault injection | Yes | Limited |
| Multi-cluster | Yes | Yes |
| Best for | Large, complex microservices | Most teams, simpler setups |

**Recommendation:** Start with Linkerd unless you need Istio-specific features (advanced traffic management, fault injection, WASM extensibility).



---
