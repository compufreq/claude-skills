# Kubernetes Reference

## Table of Contents
1. Core Resources
2. Production Deployment Pattern
3. Services & Networking
4. Configuration & Secrets
5. Autoscaling
6. Storage
7. Workload Types

---

## 1. Core Resources

### Resource Hierarchy
```
Cluster → Namespace → Deployment → ReplicaSet → Pod → Container
                   → Service → Endpoints
                   → Ingress → Backend Services
                   → ConfigMap / Secret
                   → HPA / VPA / PDB
```

### Namespace Strategy
```yaml
# Environment-based
namespaces: [development, staging, production]

# Team-based
namespaces: [team-platform, team-product, team-data]

# Hybrid
namespaces: [team-platform-prod, team-platform-staging, team-product-prod]
```

---

## 2. Production Deployment Pattern

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: production
  labels:
    app.kubernetes.io/name: myapp
    app.kubernetes.io/version: "1.2.3"
    app.kubernetes.io/component: api
    app.kubernetes.io/part-of: myplatform
    app.kubernetes.io/managed-by: helm
spec:
  replicas: 3
  revisionHistoryLimit: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0          # Zero-downtime deployments
  selector:
    matchLabels:
      app.kubernetes.io/name: myapp
  template:
    metadata:
      labels:
        app.kubernetes.io/name: myapp
        app.kubernetes.io/version: "1.2.3"
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: myapp
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        runAsGroup: 1001
        fsGroup: 1001
        seccompProfile:
          type: RuntimeDefault
      terminationGracePeriodSeconds: 60
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                topologyKey: kubernetes.io/hostname
                labelSelector:
                  matchLabels:
                    app.kubernetes.io/name: myapp
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app.kubernetes.io/name: myapp
      containers:
        - name: myapp
          image: ghcr.io/org/myapp:abc1234    # Pinned to SHA
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
          env:
            - name: NODE_ENV
              value: "production"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: myapp-secrets
                  key: database-url
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
          envFrom:
            - configMapRef:
                name: myapp-config
          resources:
            requests:
              cpu: 250m
              memory: 256Mi
            limits:
              cpu: "1"
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            initialDelaySeconds: 15
            periodSeconds: 20
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          startupProbe:
            httpGet:
              path: /healthz
              port: http
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 30   # 30 × 5s = 150s max startup
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 10"]  # Graceful shutdown
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}
```

### Probe Types

| Probe | Purpose | Failure Action |
|-------|---------|---------------|
| **startupProbe** | Wait for slow-starting apps | Kill and restart pod |
| **livenessProbe** | Detect deadlocked/hung app | Kill and restart pod |
| **readinessProbe** | Is app ready for traffic? | Remove from Service endpoints |

### Resource Sizing Guidelines

| App Type | CPU Request | CPU Limit | Memory Request | Memory Limit |
|----------|-----------|-----------|---------------|-------------|
| API (Node/Python) | 100-250m | 500m-1 | 128-256Mi | 256-512Mi |
| API (Java/Go) | 250-500m | 1-2 | 256-512Mi | 512Mi-1Gi |
| Worker/Queue | 100-250m | 500m-1 | 128-256Mi | 512Mi |
| Database | 500m-1 | 2-4 | 512Mi-1Gi | 2-4Gi |
| Cache | 100-250m | 500m | 256Mi-1Gi | 1-2Gi |

---

## 3. Services & Networking

### Service Types
```yaml
# ClusterIP (internal only — default)
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: myapp
  ports:
    - port: 80
      targetPort: http
      protocol: TCP

# NodePort (expose on each node)
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080    # 30000-32767

# LoadBalancer (cloud provider LB)
spec:
  type: LoadBalancer
  ports:
    - port: 443
      targetPort: 8080
```

### Ingress (NGINX)
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts: [app.example.com]
      secretName: myapp-tls
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: myapp-api
                port:
                  number: 80
          - path: /
            pathType: Prefix
            backend:
              service:
                name: myapp-web
                port:
                  number: 80
```

### Ingress (AWS ALB)
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:...
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'
    alb.ingress.kubernetes.io/ssl-redirect: "443"
    alb.ingress.kubernetes.io/healthcheck-path: /health
spec:
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: myapp
                port:
                  number: 80
```

---

## 4. Configuration & Secrets

### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  APP_NAME: "MyApp"
  LOG_LEVEL: "info"
  CACHE_TTL: "300"
  config.yaml: |
    server:
      port: 8080
      timeout: 30s
    features:
      new_checkout: true
```

### External Secrets (AWS Secrets Manager)
```yaml
# Using External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: myapp-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: myapp-secrets
  data:
    - secretKey: database-url
      remoteRef:
        key: production/myapp
        property: DATABASE_URL
    - secretKey: api-key
      remoteRef:
        key: production/myapp
        property: API_KEY
```

---

## 5. Autoscaling

### Horizontal Pod Autoscaler (HPA)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "100"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300    # Wait 5 min before scaling down
      policies:
        - type: Percent
          value: 25
          periodSeconds: 60
```

### Pod Disruption Budget (PDB)
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp
spec:
  minAvailable: 2                        # Or: maxUnavailable: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: myapp
```

---

## 6. Storage

### PersistentVolumeClaim
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: myapp-data
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: gp3                  # AWS EBS gp3
  resources:
    requests:
      storage: 20Gi
```

---

## 7. Workload Types

| Resource | Use Case | Scaling |
|----------|---------|---------|
| **Deployment** | Stateless apps (APIs, web servers) | Horizontal (HPA) |
| **StatefulSet** | Stateful apps (databases, queues) | Ordered, stable network IDs |
| **DaemonSet** | One pod per node (agents, log collectors) | Auto per node |
| **Job** | One-time tasks (migrations, backups) | Parallelism parameter |
| **CronJob** | Scheduled tasks (reports, cleanup) | Schedule-based |

### CronJob Example
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
spec:
  schedule: "0 2 * * *"                  # Daily at 2 AM
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      backoffLimit: 2
      activeDeadlineSeconds: 3600
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: backup
              image: backup-tool:1.0
              command: ["./backup.sh"]
```



---
