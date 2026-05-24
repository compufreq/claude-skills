# Helm Charts Reference

## Table of Contents
1. Chart Structure
2. Values & Templates
3. Template Helpers
4. Chart Lifecycle
5. Chart Repository

---

## 1. Chart Structure

```
mychart/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration
├── values-staging.yaml     # Environment overrides
├── values-production.yaml
├── templates/
│   ├── _helpers.tpl        # Template helper functions
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── serviceaccount.yaml
│   ├── networkpolicy.yaml
│   ├── NOTES.txt           # Post-install instructions
│   └── tests/
│       └── test-connection.yaml
└── .helmignore
```

### Chart.yaml
```yaml
apiVersion: v2
name: myapp
description: My application Helm chart
type: application
version: 0.1.0               # Chart version
appVersion: "1.2.3"           # Application version
maintainers:
  - name: Team
    email: team@example.com
dependencies:
  - name: postgresql
    version: "15.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
  - name: redis
    version: "19.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
```

---

## 2. Values & Templates

### values.yaml
```yaml
# -- Number of replicas
replicaCount: 3

image:
  # -- Container image repository
  repository: ghcr.io/org/myapp
  # -- Image pull policy
  pullPolicy: IfNotPresent
  # -- Image tag (defaults to chart appVersion)
  tag: ""

# -- Image pull secrets
imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8080"

podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1001
  fsGroup: 1001
  seccompProfile:
    type: RuntimeDefault

securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: app.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: myapp-tls
      hosts: [app.example.com]

resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: "1"
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

pdb:
  enabled: true
  minAvailable: 2

networkPolicy:
  enabled: true

env: {}
envFrom: []

config:
  LOG_LEVEL: "info"

probes:
  liveness:
    path: /healthz
    initialDelaySeconds: 15
    periodSeconds: 20
  readiness:
    path: /ready
    initialDelaySeconds: 5
    periodSeconds: 10

# Subchart toggles
postgresql:
  enabled: false
redis:
  enabled: false
```

### Deployment Template
```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        {{- with .Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      labels:
        {{- include "myapp.selectorLabels" . | nindent 8 }}
    spec:
      serviceAccountName: {{ include "myapp.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 8080
          {{- with .Values.env }}
          env:
            {{- range $key, $value := . }}
            - name: {{ $key }}
              value: {{ $value | quote }}
            {{- end }}
          {{- end }}
          {{- with .Values.envFrom }}
          envFrom:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          livenessProbe:
            httpGet:
              path: {{ .Values.probes.liveness.path }}
              port: http
            initialDelaySeconds: {{ .Values.probes.liveness.initialDelaySeconds }}
            periodSeconds: {{ .Values.probes.liveness.periodSeconds }}
          readinessProbe:
            httpGet:
              path: {{ .Values.probes.readiness.path }}
              port: http
            initialDelaySeconds: {{ .Values.probes.readiness.initialDelaySeconds }}
            periodSeconds: {{ .Values.probes.readiness.periodSeconds }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}
```

---

## 3. Template Helpers

```yaml
# templates/_helpers.tpl
{{- define "myapp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "myapp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "myapp.labels" -}}
helm.sh/chart: {{ include "myapp.chart" . }}
{{ include "myapp.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "myapp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "myapp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "myapp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "myapp.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "myapp.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
```

---

## 4. Chart Lifecycle

```bash
# Lint
helm lint ./mychart
helm lint ./mychart -f values-production.yaml

# Template (dry run — see generated YAML)
helm template myrelease ./mychart -f values-production.yaml

# Install
helm install myrelease ./mychart -n production -f values-production.yaml

# Upgrade
helm upgrade myrelease ./mychart -n production -f values-production.yaml

# Rollback
helm rollback myrelease 1 -n production    # Rollback to revision 1

# Uninstall
helm uninstall myrelease -n production

# Diff (requires helm-diff plugin)
helm diff upgrade myrelease ./mychart -f values-production.yaml
```

---

## 5. Chart Repository

### OCI Registry (recommended)
```bash
# Package
helm package ./mychart

# Push to OCI registry
helm push mychart-0.1.0.tgz oci://ghcr.io/org/charts

# Install from OCI
helm install myrelease oci://ghcr.io/org/charts/mychart --version 0.1.0
```

### ChartMuseum / GitHub Pages
```bash
# Add repo
helm repo add myrepo https://charts.example.com
helm repo update

# Search
helm search repo myrepo/

# Install
helm install myrelease myrepo/mychart --version 0.1.0
```



---
