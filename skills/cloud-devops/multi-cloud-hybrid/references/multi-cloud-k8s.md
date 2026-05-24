# Multi-Cloud Kubernetes Reference

## Table of Contents
1. Multi-Cluster Strategies
2. Fleet Management Tools
3. Multi-Cloud GitOps
4. Cross-Cluster Service Mesh
5. Cluster Federation

---

## 1. Multi-Cluster Strategies

| Strategy | Description | Complexity | Use Case |
|----------|------------|-----------|---------|
| **Independent** | Separate clusters, no coordination | Low | Different teams/regions |
| **Replicated** | Same workloads on each cluster | Medium | DR, geo-distribution |
| **Federated** | Coordinated clusters, shared config | High | Large enterprise |
| **Hybrid** | On-prem + cloud clusters | High | Migration, compliance |

### Independent Clusters (Most Common)
```
EKS (us-east-1)         AKS (westeurope)
┌──────────────┐        ┌──────────────┐
│ US workloads │        │ EU workloads │
│ ArgoCD       │        │ ArgoCD       │
│ Prometheus   │        │ Prometheus   │
└──────────────┘        └──────────────┘
        │                       │
   Same Git repo          Same Git repo
   Same Helm charts       Different values
```

### Replicated (Active-Active)
```
Global LB (Cloudflare / Route53)
       ╱              ╲
EKS (us-east-1)    AKS (westeurope)
┌──────────┐       ┌──────────┐
│ Same app │       │ Same app │
│ Same ver │       │ Same ver │
└────┬─────┘       └────┬─────┘
     │                   │
  RDS (us)          Azure SQL (eu)
  (async replication)
```

---

## 2. Fleet Management Tools

| Tool | Provider | What It Does |
|------|---------|-------------|
| **ArgoCD** | Any K8s | GitOps deployment to multiple clusters |
| **Flux** | Any K8s | GitOps with multi-tenancy |
| **Rancher** | Any K8s | Cluster lifecycle management, UI |
| **Anthos** | GKE + any | Google's multi-cloud K8s platform |
| **Azure Arc** | AKS + any | Extend Azure management to any K8s |
| **EKS Anywhere** | EKS + on-prem | Run EKS on your own hardware |

### ArgoCD Multi-Cluster
```yaml
# Register multiple clusters
apiVersion: v1
kind: Secret
metadata:
  name: eks-production
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: cluster
type: Opaque
stringData:
  name: eks-production
  server: https://eks-cluster.us-east-1.eks.amazonaws.com
  config: |
    {
      "execProviderConfig": {
        "command": "aws",
        "args": ["eks", "get-token", "--cluster-name", "production"],
        "apiVersion": "client.authentication.k8s.io/v1beta1"
      }
    }
---
apiVersion: v1
kind: Secret
metadata:
  name: aks-production
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: cluster
type: Opaque
stringData:
  name: aks-production
  server: https://aks-cluster.westeurope.azmk8s.io
  config: |
    {
      "execProviderConfig": {
        "command": "kubelogin",
        "args": ["get-token", "--server-id", "..."]
      }
    }
```

### ApplicationSet (Deploy to Multiple Clusters)
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: myapp
  namespace: argocd
spec:
  generators:
    - clusters:
        selector:
          matchLabels:
            environment: production
  template:
    metadata:
      name: 'myapp-{{name}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/org/k8s-manifests.git
        path: apps/myapp
        targetRevision: main
        helm:
          valueFiles:
            - 'values-{{metadata.labels.cloud}}.yaml'
            - 'values-{{metadata.labels.region}}.yaml'
      destination:
        server: '{{server}}'
        namespace: myapp
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

---

## 3. Multi-Cloud GitOps

### Repository Structure
```
k8s-manifests/
├── apps/
│   └── myapp/
│       ├── base/
│       │   ├── deployment.yaml
│       │   ├── service.yaml
│       │   └── kustomization.yaml
│       └── overlays/
│           ├── aws-production/
│           │   ├── kustomization.yaml
│           │   ├── patch-resources.yaml    # AWS-specific sizing
│           │   └── patch-ingress.yaml      # ALB annotations
│           ├── azure-production/
│           │   ├── kustomization.yaml
│           │   ├── patch-resources.yaml    # Azure-specific sizing
│           │   └── patch-ingress.yaml      # App GW annotations
│           └── values/
│               ├── values-aws.yaml
│               └── values-azure.yaml
├── infrastructure/
│   ├── aws/
│   │   ├── ingress-nginx/
│   │   └── cert-manager/
│   └── azure/
│       ├── ingress-nginx/
│       └── cert-manager/
└── argocd/
    ├── applications.yaml
    └── applicationsets.yaml
```

### Cloud-Specific Overlays (Kustomize)
```yaml
# overlays/aws-production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: myapp
resources:
  - ../../base
patches:
  - path: patch-ingress.yaml
  - path: patch-resources.yaml

# overlays/aws-production/patch-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
```

```yaml
# overlays/azure-production/patch-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
```

---

## 4. Cross-Cluster Service Mesh

### Istio Multi-Cluster
```
Cluster A (AWS)              Cluster B (Azure)
┌─────────────────┐         ┌─────────────────┐
│ Istio Control   │◄─mTLS──►│ Istio Control   │
│ Plane           │         │ Plane           │
│                 │         │                 │
│ Service A ──────┼────────►│ Service B       │
│ (with sidecar)  │  mTLS   │ (with sidecar)  │
└─────────────────┘         └─────────────────┘
```

Cross-cluster communication:
- Services discover each other via Istio's service registry
- All traffic encrypted with mTLS automatically
- Traffic policies (retries, circuit breakers) work cross-cluster
- Supports east-west gateway for cross-network connectivity

### Linkerd Multi-Cluster
```yaml
# Link clusters
apiVersion: multicluster.linkerd.io/v1alpha1
kind: Link
metadata:
  name: azure-cluster
  namespace: linkerd-multicluster
spec:
  targetClusterName: azure-production
  targetClusterDomain: cluster.local
  targetClusterLinkerdNamespace: linkerd
  gatewayAddress: gateway.azure-cluster.example.com
  gatewayPort: 4143
  gatewayIdentity: "gateway.linkerd-multicluster.cluster.local"
```

Mirror services from remote cluster:
```bash
linkerd multicluster link --cluster-name azure-production | kubectl apply -f -

# Services from azure-production appear as:
# service-name.namespace.svc.azure-production.cluster.local
```

---

## 5. Cluster Federation

### Kubefed (Kubernetes Federation v2)
```yaml
# Federated Deployment — deployed to all member clusters
apiVersion: types.kubefed.io/v1beta1
kind: FederatedDeployment
metadata:
  name: myapp
  namespace: default
spec:
  template:
    spec:
      replicas: 3
      selector:
        matchLabels:
          app: myapp
      template:
        spec:
          containers:
            - name: myapp
              image: myapp:latest
  placement:
    clusters:
      - name: eks-production
      - name: aks-production
  overrides:
    - clusterName: eks-production
      clusterOverrides:
        - path: "/spec/replicas"
          value: 5    # More replicas on AWS
    - clusterName: aks-production
      clusterOverrides:
        - path: "/spec/replicas"
          value: 3
```

### When to Federate vs Not

| Use Federation | Don't Federate |
|----------------|---------------|
| Same app on multiple clouds | Different apps per cloud |
| Unified config management needed | Teams own their clusters |
| Compliance requires consistent policies | Independent workloads |
| Active-active multi-cloud DR | Simple single-cloud setup |
