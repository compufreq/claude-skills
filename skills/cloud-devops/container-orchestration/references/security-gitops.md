# Security & GitOps Reference

## Table of Contents
1. Pod Security
2. Network Policies
3. RBAC
4. ArgoCD
5. Flux

---

## 1. Pod Security

### Pod Security Admission (PSA)

PSA enforces security standards at the namespace level. Three profiles:

| Profile | Level | What It Blocks |
|---------|-------|---------------|
| **Privileged** | Unrestricted | Nothing — use for system namespaces |
| **Baseline** | Minimal restrictions | Privileged containers, hostNetwork, hostPID |
| **Restricted** | Maximum security | Non-root, drop ALL caps, read-only root FS |

```yaml
# Enforce restricted on a namespace
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

### Security Context (Pod-Level)
```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1001
    runAsGroup: 1001
    fsGroup: 1001
    seccompProfile:
      type: RuntimeDefault
```

### Security Context (Container-Level)
```yaml
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
    # add: ["NET_BIND_SERVICE"]   # Only if needed
  privileged: false
```

---

## 2. Network Policies

### Default Deny All
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

### Allow Specific Traffic
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-myapp
  namespace: production
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: myapp
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: ingress-nginx
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: api-gateway
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: postgres
      ports:
        - protocol: TCP
          port: 5432
    - to:                          # Allow DNS
        - namespaceSelector: {}
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
    - to:                          # Allow external HTTPS
        - ipBlock:
            cidr: 0.0.0.0/0
      ports:
        - protocol: TCP
          port: 443
```

---

## 3. RBAC

### ServiceAccount + Role + RoleBinding
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp
  namespace: production
  annotations:
    # AWS IRSA
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/myapp-role
    # GCP Workload Identity
    # iam.gke.io/gcp-service-account: myapp@project.iam.gserviceaccount.com
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: myapp-role
  namespace: production
rules:
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: myapp-rolebinding
  namespace: production
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: myapp-role
subjects:
  - kind: ServiceAccount
    name: myapp
    namespace: production
```

---

## 4. ArgoCD

### Application Definition
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/org/k8s-manifests.git
    targetRevision: main
    path: apps/myapp/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

### Helm-Based Application
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-helm
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/org/helm-charts.git
    targetRevision: main
    path: charts/myapp
    helm:
      valueFiles:
        - values-production.yaml
      parameters:
        - name: image.tag
          value: abc1234
  destination:
    server: https://kubernetes.default.svc
    namespace: production
```

### ArgoCD ApplicationSet (Multi-Env)
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: myapp
  namespace: argocd
spec:
  generators:
    - list:
        elements:
          - cluster: staging
            url: https://staging-k8s.example.com
            values: values-staging.yaml
          - cluster: production
            url: https://prod-k8s.example.com
            values: values-production.yaml
  template:
    metadata:
      name: 'myapp-{{cluster}}'
    spec:
      source:
        repoURL: https://github.com/org/helm-charts.git
        path: charts/myapp
        helm:
          valueFiles:
            - '{{values}}'
      destination:
        server: '{{url}}'
        namespace: myapp
```

### GitOps Directory Structure
```
k8s-manifests/
├── apps/
│   ├── myapp/
│   │   ├── base/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   ├── kustomization.yaml
│   │   │   └── hpa.yaml
│   │   └── overlays/
│   │       ├── staging/
│   │       │   ├── kustomization.yaml
│   │       │   └── patch-replicas.yaml
│   │       └── production/
│   │           ├── kustomization.yaml
│   │           └── patch-replicas.yaml
│   └── another-app/
├── infrastructure/
│   ├── cert-manager/
│   ├── ingress-nginx/
│   └── external-secrets/
└── argocd/
    ├── apps.yaml
    └── infrastructure.yaml
```

---

## 5. Flux

### Bootstrap
```bash
flux bootstrap github \
  --owner=org \
  --repository=fleet-infra \
  --branch=main \
  --path=clusters/production \
  --personal
```

### Kustomization
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 5m
  sourceRef:
    kind: GitRepository
    name: flux-system
  path: ./apps/myapp/overlays/production
  prune: true
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: myapp
      namespace: production
  timeout: 5m
```

### HelmRelease
```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: myapp
  namespace: production
spec:
  interval: 5m
  chart:
    spec:
      chart: myapp
      version: ">=0.1.0"
      sourceRef:
        kind: HelmRepository
        name: myrepo
        namespace: flux-system
  values:
    replicaCount: 3
    image:
      tag: abc1234
  upgrade:
    remediation:
      retries: 3
```



---

<!-- Script: scripts/generate_helm_chart.py -->

# Script: generate_helm_chart.py

```python
#!/usr/bin/env python3
"""
Scaffold a complete Helm chart with production-ready templates.

Usage:
    python generate_helm_chart.py \
        --chart-name myapp \
        --app-version 1.0.0 \
        --port 8080 \
        --features ingress,hpa,pdb,netpol,serviceaccount \
        --output ./charts/
"""

import argparse
import os


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


def gen_chart_yaml(name, version):
    return f"""apiVersion: v2
name: {name}
description: Helm chart for {name}
type: application
version: 0.1.0
appVersion: "{version}"
maintainers:
  - name: Team
    email: team@example.com
"""


def gen_values(name, port, features):
    feat = set(features.split(","))
    return f"""replicaCount: 3

image:
  repository: ghcr.io/org/{name}
  pullPolicy: IfNotPresent
  tag: ""

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: {"true" if "serviceaccount" in feat else "false"}
  annotations: {{}}
  name: ""

podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "{port}"

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

containerPort: {port}

ingress:
  enabled: {"true" if "ingress" in feat else "false"}
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: {name}.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: {name}-tls
      hosts: [{name}.example.com]

resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: "1"
    memory: 512Mi

autoscaling:
  enabled: {"true" if "hpa" in feat else "false"}
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

pdb:
  enabled: {"true" if "pdb" in feat else "false"}
  minAvailable: 2

networkPolicy:
  enabled: {"true" if "netpol" in feat else "false"}

probes:
  liveness:
    path: /healthz
    initialDelaySeconds: 15
    periodSeconds: 20
  readiness:
    path: /ready
    initialDelaySeconds: 5
    periodSeconds: 10
  startup:
    path: /healthz
    initialDelaySeconds: 10
    periodSeconds: 5
    failureThreshold: 30

env: {{}}
config: {{}}
"""


def gen_helpers(name):
    return """{{/*
Expand the name of the chart.
*/}}
{{- define \"""" + name + """.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define \"""" + name + """.fullname" -}}
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

{{- define \"""" + name + """.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define \"""" + name + """.labels" -}}
helm.sh/chart: {{ include \"""" + name + """.chart" . }}
{{ include \"""" + name + """.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define \"""" + name + """.selectorLabels" -}}
app.kubernetes.io/name: {{ include \"""" + name + """.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define \"""" + name + """.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include \"""" + name + """.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
"""


def gen_deployment_template(name):
    n = name
    return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{{{ include "{n}.fullname" . }}}}
  labels:
    {{{{- include "{n}.labels" . | nindent 4 }}}}
spec:
  {{{{- if not .Values.autoscaling.enabled }}}}
  replicas: {{{{ .Values.replicaCount }}}}
  {{{{- end }}}}
  revisionHistoryLimit: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      {{{{- include "{n}.selectorLabels" . | nindent 6 }}}}
  template:
    metadata:
      annotations:
        checksum/config: {{{{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}}}
        {{{{- with .Values.podAnnotations }}}}
        {{{{- toYaml . | nindent 8 }}}}
        {{{{- end }}}}
      labels:
        {{{{- include "{n}.selectorLabels" . | nindent 8 }}}}
    spec:
      serviceAccountName: {{{{ include "{n}.serviceAccountName" . }}}}
      securityContext:
        {{{{- toYaml .Values.podSecurityContext | nindent 8 }}}}
      terminationGracePeriodSeconds: 60
      containers:
        - name: {{{{ .Chart.Name }}}}
          image: "{{{{ .Values.image.repository }}}}:{{{{ .Values.image.tag | default .Chart.AppVersion }}}}"
          imagePullPolicy: {{{{ .Values.image.pullPolicy }}}}
          ports:
            - name: http
              containerPort: {{{{ .Values.containerPort }}}}
          {{{{- with .Values.env }}}}
          env:
            {{{{- range $key, $value := . }}}}
            - name: {{{{ $key }}}}
              value: {{{{ $value | quote }}}}
            {{{{- end }}}}
          {{{{- end }}}}
          envFrom:
            - configMapRef:
                name: {{{{ include "{n}.fullname" . }}}}-config
          livenessProbe:
            httpGet:
              path: {{{{ .Values.probes.liveness.path }}}}
              port: http
            initialDelaySeconds: {{{{ .Values.probes.liveness.initialDelaySeconds }}}}
            periodSeconds: {{{{ .Values.probes.liveness.periodSeconds }}}}
          readinessProbe:
            httpGet:
              path: {{{{ .Values.probes.readiness.path }}}}
              port: http
            initialDelaySeconds: {{{{ .Values.probes.readiness.initialDelaySeconds }}}}
            periodSeconds: {{{{ .Values.probes.readiness.periodSeconds }}}}
          startupProbe:
            httpGet:
              path: {{{{ .Values.probes.startup.path }}}}
              port: http
            initialDelaySeconds: {{{{ .Values.probes.startup.initialDelaySeconds }}}}
            periodSeconds: {{{{ .Values.probes.startup.periodSeconds }}}}
            failureThreshold: {{{{ .Values.probes.startup.failureThreshold }}}}
          resources:
            {{{{- toYaml .Values.resources | nindent 12 }}}}
          securityContext:
            {{{{- toYaml .Values.securityContext | nindent 12 }}}}
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {{{{}}}}
"""


def gen_service_template(name):
    n = name
    return f"""apiVersion: v1
kind: Service
metadata:
  name: {{{{ include "{n}.fullname" . }}}}
  labels:
    {{{{- include "{n}.labels" . | nindent 4 }}}}
spec:
  type: {{{{ .Values.service.type }}}}
  selector:
    {{{{- include "{n}.selectorLabels" . | nindent 4 }}}}
  ports:
    - name: http
      port: {{{{ .Values.service.port }}}}
      targetPort: http
      protocol: TCP
"""


def gen_configmap_template(name):
    n = name
    return f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: {{{{ include "{n}.fullname" . }}}}-config
  labels:
    {{{{- include "{n}.labels" . | nindent 4 }}}}
data:
  {{{{- range $key, $value := .Values.config }}}}
  {{{{ $key }}}}: {{{{ $value | quote }}}}
  {{{{- end }}}}
"""


def gen_ingress_template(name):
    n = name
    return f"""{{{{- if .Values.ingress.enabled -}}}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{{{ include "{n}.fullname" . }}}}
  labels:
    {{{{- include "{n}.labels" . | nindent 4 }}}}
  {{{{- with .Values.ingress.annotations }}}}
  annotations:
    {{{{- toYaml . | nindent 4 }}}}
  {{{{- end }}}}
spec:
  ingressClassName: {{{{ .Values.ingress.className }}}}
  {{{{- if .Values.ingress.tls }}}}
  tls:
    {{{{- range .Values.ingress.tls }}}}
    - hosts:
        {{{{- range .hosts }}}}
        - {{{{ . | quote }}}}
        {{{{- end }}}}
      secretName: {{{{ .secretName }}}}
    {{{{- end }}}}
  {{{{- end }}}}
  rules:
    {{{{- range .Values.ingress.hosts }}}}
    - host: {{{{ .host | quote }}}}
      http:
        paths:
          {{{{- range .paths }}}}
          - path: {{{{ .path }}}}
            pathType: {{{{ .pathType }}}}
            backend:
              service:
                name: {{{{ include "{n}.fullname" $ }}}}
                port:
                  number: {{{{ $.Values.service.port }}}}
          {{{{- end }}}}
    {{{{- end }}}}
{{{{- end }}}}
"""


def gen_hpa_template(name):
    n = name
    return f"""{{{{- if .Values.autoscaling.enabled }}}}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{{{ include "{n}.fullname" . }}}}
  labels:
    {{{{- include "{n}.labels" . | nindent 4 }}}}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{{{ include "{n}.fullname" . }}}}
  minReplicas: {{{{ .Values.autoscaling.minReplicas }}}}
  maxReplicas: {{{{ .Values.autoscaling.maxReplicas }}}}
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{{{ .Values.autoscaling.targetCPUUtilizationPercentage }}}}
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: {{{{ .Values.autoscaling.targetMemoryUtilizationPercentage }}}}
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
{{{{- end }}}}
"""


def gen_pdb_template(name):
    n = name
    return f"""{{{{- if .Values.pdb.enabled }}}}
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{{{ include "{n}.fullname" . }}}}
  labels:
    {{{{- include "{n}.labels" . | nindent 4 }}}}
spec:
  minAvailable: {{{{ .Values.pdb.minAvailable }}}}
  selector:
    matchLabels:
      {{{{- include "{n}.selectorLabels" . | nindent 6 }}}}
{{{{- end }}}}
"""


def gen_netpol_template(name):
    n = name
    return f"""{{{{- if .Values.networkPolicy.enabled }}}}
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{{{ include "{n}.fullname" . }}}}
  labels:
    {{{{- include "{n}.labels" . | nindent 4 }}}}
spec:
  podSelector:
    matchLabels:
      {{{{- include "{n}.selectorLabels" . | nindent 6 }}}}
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: ingress-nginx
      ports:
        - protocol: TCP
          port: {{{{ .Values.containerPort }}}}
  egress:
    - ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
    - to: []
{{{{- end }}}}
"""


def gen_sa_template(name):
    n = name
    return f"""{{{{- if .Values.serviceAccount.create -}}}}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{{{ include "{n}.serviceAccountName" . }}}}
  labels:
    {{{{- include "{n}.labels" . | nindent 4 }}}}
  {{{{- with .Values.serviceAccount.annotations }}}}
  annotations:
    {{{{- toYaml . | nindent 4 }}}}
  {{{{- end }}}}
{{{{- end }}}}
"""


def gen_notes(name):
    n = name
    return f"""1. Get the application URL:
{{{{- if .Values.ingress.enabled }}}}
  {{{{- range .Values.ingress.hosts }}}}
  http{{{{- if $.Values.ingress.tls }}}}s{{{{- end }}}}://{{{{ .host }}}}
  {{{{- end }}}}
{{{{- else }}}}
  kubectl port-forward svc/{{{{ include "{n}.fullname" . }}}} 8080:{{{{ .Values.service.port }}}} -n {{{{ .Release.Namespace }}}}
  Then visit: http://localhost:8080
{{{{- end }}}}
"""


def gen_test(name):
    n = name
    return f"""apiVersion: v1
kind: Pod
metadata:
  name: "{{{{ include "{n}.fullname" . }}}}-test"
  labels:
    {{{{- include "{n}.labels" . | nindent 4 }}}}
  annotations:
    "helm.sh/hook": test
spec:
  restartPolicy: Never
  containers:
    - name: test
      image: busybox:1.36
      command: ['wget']
      args: ['--timeout=5', '{{{{ include "{n}.fullname" . }}}}:{{{{ .Values.service.port }}}}/ready']
"""


def gen_helmignore():
    return """# Patterns to ignore
.git/
.gitignore
.DS_Store
*.swp
*.bak
*.tmp
charts/
README.md
LICENSE
ci/
"""


def main():
    parser = argparse.ArgumentParser(description="Scaffold Helm Chart")
    parser.add_argument("--chart-name", required=True, help="Chart name")
    parser.add_argument("--app-version", default="1.0.0", help="App version")
    parser.add_argument("--port", type=int, default=8080, help="Container port")
    parser.add_argument("--features", default="ingress,hpa,pdb,netpol,serviceaccount",
                        help="Comma-separated features")
    parser.add_argument("--output", default="./charts", help="Output directory")
    args = parser.parse_args()

    name = args.chart_name
    base = os.path.join(args.output, name)
    tmpl = os.path.join(base, "templates")
    feat = set(args.features.split(","))

    print(f"\n⎈ Scaffolding Helm chart: {name}\n")

    # Core files
    create_file(os.path.join(base, "Chart.yaml"), gen_chart_yaml(name, args.app_version))
    create_file(os.path.join(base, "values.yaml"), gen_values(name, args.port, args.features))
    create_file(os.path.join(base, ".helmignore"), gen_helmignore())

    # Templates
    create_file(os.path.join(tmpl, "_helpers.tpl"), gen_helpers(name))
    create_file(os.path.join(tmpl, "deployment.yaml"), gen_deployment_template(name))
    create_file(os.path.join(tmpl, "service.yaml"), gen_service_template(name))
    create_file(os.path.join(tmpl, "configmap.yaml"), gen_configmap_template(name))
    create_file(os.path.join(tmpl, "NOTES.txt"), gen_notes(name))

    # Optional templates
    if "ingress" in feat:
        create_file(os.path.join(tmpl, "ingress.yaml"), gen_ingress_template(name))
    if "hpa" in feat:
        create_file(os.path.join(tmpl, "hpa.yaml"), gen_hpa_template(name))
    if "pdb" in feat:
        create_file(os.path.join(tmpl, "pdb.yaml"), gen_pdb_template(name))
    if "netpol" in feat:
        create_file(os.path.join(tmpl, "networkpolicy.yaml"), gen_netpol_template(name))
    if "serviceaccount" in feat:
        create_file(os.path.join(tmpl, "serviceaccount.yaml"), gen_sa_template(name))

    # Tests
    create_file(os.path.join(tmpl, "tests", "test-connection.yaml"), gen_test(name))

    file_count = len([f for f in os.listdir(tmpl) if os.path.isfile(os.path.join(tmpl, f))])
    print(f"\n✅ Helm chart scaffolded at: {base}/")
    print(f"   Chart: {name}")
    print(f"   App version: {args.app_version}")
    print(f"   Templates: {file_count}")
    print(f"   Features: {args.features}")
    print(f"\n   Lint: helm lint {base}")
    print(f"   Template: helm template myrelease {base}")
    print(f"   Install: helm install myrelease {base} -n production")


if __name__ == "__main__":
    main()

```


---

<!-- Script: scripts/generate_k8s_manifests.py -->

# Script: generate_k8s_manifests.py

```python
#!/usr/bin/env python3
"""
Generate production-ready Kubernetes manifests.

Usage:
    python generate_k8s_manifests.py \
        --app-name myapp \
        --image ghcr.io/org/myapp:latest \
        --port 8080 \
        --replicas 3 \
        --namespace production \
        --features hpa,pdb,netpol,ingress,sa \
        --ingress-host app.example.com \
        --output ./k8s/
"""

import argparse
import os
import sys

import json as json_module


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


def gen_deployment(args):
    return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {args.app_name}
  namespace: {args.namespace}
  labels:
    app.kubernetes.io/name: {args.app_name}
    app.kubernetes.io/version: "1.0.0"
spec:
  replicas: {args.replicas}
  revisionHistoryLimit: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app.kubernetes.io/name: {args.app_name}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {args.app_name}
        app.kubernetes.io/version: "1.0.0"
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "{args.port}"
        prometheus.io/path: "/metrics"
    spec:
      {"serviceAccountName: " + args.app_name if "sa" in args.feature_set else ""}
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
                    app.kubernetes.io/name: {args.app_name}
      containers:
        - name: {args.app_name}
          image: {args.image}
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: {args.port}
              protocol: TCP
          envFrom:
            - configMapRef:
                name: {args.app_name}-config
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
            failureThreshold: 30
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 10"]
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
          emptyDir: {{}}
"""


def gen_service(args):
    return f"""apiVersion: v1
kind: Service
metadata:
  name: {args.app_name}
  namespace: {args.namespace}
  labels:
    app.kubernetes.io/name: {args.app_name}
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: {args.app_name}
  ports:
    - name: http
      port: 80
      targetPort: http
      protocol: TCP
"""


def gen_configmap(args):
    return f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: {args.app_name}-config
  namespace: {args.namespace}
data:
  APP_NAME: "{args.app_name}"
  LOG_LEVEL: "info"
  PORT: "{args.port}"
"""


def gen_ingress(args):
    host = args.ingress_host or f"{args.app_name}.example.com"
    return f"""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {args.app_name}
  namespace: {args.namespace}
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts: [{host}]
      secretName: {args.app_name}-tls
  rules:
    - host: {host}
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {args.app_name}
                port:
                  number: 80
"""


def gen_hpa(args):
    return f"""apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {args.app_name}
  namespace: {args.namespace}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {args.app_name}
  minReplicas: {args.replicas}
  maxReplicas: {args.replicas * 5}
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 25
          periodSeconds: 60
"""


def gen_pdb(args):
    min_avail = max(1, args.replicas - 1)
    return f"""apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {args.app_name}
  namespace: {args.namespace}
spec:
  minAvailable: {min_avail}
  selector:
    matchLabels:
      app.kubernetes.io/name: {args.app_name}
"""


def gen_networkpolicy(args):
    return f"""apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {args.app_name}
  namespace: {args.namespace}
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: {args.app_name}
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: ingress-nginx
      ports:
        - protocol: TCP
          port: {args.port}
  egress:
    - to: []  # Allow all egress (customize as needed)
    - ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
"""


def gen_serviceaccount(args):
    return f"""apiVersion: v1
kind: ServiceAccount
metadata:
  name: {args.app_name}
  namespace: {args.namespace}
  labels:
    app.kubernetes.io/name: {args.app_name}
  # annotations:
  #   eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT:role/{args.app_name}-role
"""


def gen_namespace(args):
    return f"""apiVersion: v1
kind: Namespace
metadata:
  name: {args.namespace}
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
"""


def gen_kustomization(args, files):
    resources = "\n".join(f"  - {os.path.basename(f)}" for f in files)
    return f"""apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: {args.namespace}

resources:
{resources}

commonLabels:
  app.kubernetes.io/name: {args.app_name}
  app.kubernetes.io/managed-by: kustomize
"""


def main():
    parser = argparse.ArgumentParser(description="Generate K8s Manifests")
    parser.add_argument("--app-name", required=True, help="Application name")
    parser.add_argument("--image", required=True, help="Container image")
    parser.add_argument("--port", type=int, default=8080, help="Container port")
    parser.add_argument("--replicas", type=int, default=3, help="Replica count")
    parser.add_argument("--namespace", default="production", help="Namespace")
    parser.add_argument("--features", default="hpa,pdb,netpol,ingress,sa",
                        help="Comma-separated: hpa,pdb,netpol,ingress,sa")
    parser.add_argument("--ingress-host", default=None, help="Ingress hostname")
    parser.add_argument("--output", default="./k8s", help="Output directory")
    args = parser.parse_args()
    args.feature_set = set(args.features.split(","))

    print(f"\n☸️  Generating K8s manifests for {args.app_name}\n")

    files = []

    # Always generate core files
    create_file(os.path.join(args.output, "namespace.yaml"), gen_namespace(args))
    files.append("namespace.yaml")

    create_file(os.path.join(args.output, "deployment.yaml"), gen_deployment(args))
    files.append("deployment.yaml")

    create_file(os.path.join(args.output, "service.yaml"), gen_service(args))
    files.append("service.yaml")

    create_file(os.path.join(args.output, "configmap.yaml"), gen_configmap(args))
    files.append("configmap.yaml")

    # Optional features
    if "sa" in args.feature_set:
        create_file(os.path.join(args.output, "serviceaccount.yaml"), gen_serviceaccount(args))
        files.append("serviceaccount.yaml")

    if "ingress" in args.feature_set:
        create_file(os.path.join(args.output, "ingress.yaml"), gen_ingress(args))
        files.append("ingress.yaml")

    if "hpa" in args.feature_set:
        create_file(os.path.join(args.output, "hpa.yaml"), gen_hpa(args))
        files.append("hpa.yaml")

    if "pdb" in args.feature_set:
        create_file(os.path.join(args.output, "pdb.yaml"), gen_pdb(args))
        files.append("pdb.yaml")

    if "netpol" in args.feature_set:
        create_file(os.path.join(args.output, "networkpolicy.yaml"), gen_networkpolicy(args))
        files.append("networkpolicy.yaml")

    # Kustomization
    create_file(os.path.join(args.output, "kustomization.yaml"), gen_kustomization(args, files))

    print(f"\n✅ Generated {len(files) + 1} manifests at: {args.output}/")
    print(f"   App: {args.app_name}")
    print(f"   Image: {args.image}")
    print(f"   Namespace: {args.namespace}")
    print(f"   Features: {args.features}")
    print(f"\n   Apply: kubectl apply -k {args.output}/")


if __name__ == "__main__":
    main()

```
