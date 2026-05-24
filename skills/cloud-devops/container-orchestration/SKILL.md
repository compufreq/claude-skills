---
name: container-orchestration
description: >-
  Docker, Kubernetes, Helm, service mesh, GitOps, and managed clusters (EKS, GKE, AKS). Use when the user mentions Docker, Dockerfile, docker-compose, Kubernetes, k8s, kubectl, pod, deployment, service, ingress, Helm, Istio, Linkerd, ArgoCD, Flux, GitOps, RBAC, HPA, StatefulSet, DaemonSet, NetworkPolicy, EKS, GKE, AKS, container registry, kustomize, or any request involving containerizing apps, orchestrating containers, or deploying to Kubernetes.
---

# Container Orchestration

A production-grade skill covering the full container lifecycle: building containers with Docker,
orchestrating with Kubernetes, packaging with Helm, securing with pod security and network policies,
deploying with GitOps, and observing with Prometheus/Grafana.

## Quick Reference

| Area | Key Technologies | Reference File |
|------|-----------------|----------------|
| Containers | Docker, Compose, multi-stage builds | `references/docker.md` |
| Orchestration | K8s resources, production patterns | `references/kubernetes.md` |
| Packaging | Helm charts, templating, repos | `references/helm.md` |
| Security & GitOps | Pod security, NetworkPolicy, ArgoCD, Flux | `references/security-gitops.md` |
| Mesh & Observability | Istio, Linkerd, Prometheus, Grafana | `references/mesh-observability.md` |
| Cluster Setup | EKS, GKE, AKS, managed vs self-hosted | `references/cluster-setup.md` |

## Core Workflow

1. **Identify the need:**
   - Containerize an app → `references/docker.md`
   - Deploy to Kubernetes → `references/kubernetes.md`
   - Package as Helm chart → `references/helm.md`
   - Secure the deployment → `references/security-gitops.md`
   - Set up observability → `references/mesh-observability.md`
   - Create/manage a cluster → `references/cluster-setup.md`

2. **Generate configurations** using scripts:
   - `scripts/generate_k8s_manifests.py` — Production-ready K8s manifests
   - `scripts/generate_helm_chart.py` — Complete Helm chart scaffold

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Developer Workflow                                      │
│  Code → Dockerfile → Image → Registry → Deploy           │
└──────────┬──────────────────────────────────────────────┘
           │
┌──────────▼──────────────────────────────────────────────┐
│  Container Registry (ECR / GCR / ACR / GHCR / DockerHub)│
└──────────┬──────────────────────────────────────────────┘
           │
┌──────────▼──────────────────────────────────────────────┐
│  GitOps (ArgoCD / Flux)                                  │
│  Watches Git repo → Syncs manifests → Deploys to cluster │
└──────────┬──────────────────────────────────────────────┘
           │
┌──────────▼──────────────────────────────────────────────┐
│  Kubernetes Cluster (EKS / GKE / AKS)                    │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Namespace: production                                │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐      │ │
│  │  │Deployment│  │ Service  │  │    Ingress    │      │ │
│  │  │ (Pods)   │──│(ClusterIP)──│(ALB/NLB/Nginx)│      │ │
│  │  └──────────┘  └──────────┘  └──────────────┘      │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐      │ │
│  │  │ConfigMap │  │  Secret  │  │  HPA / VPA   │      │ │
│  │  └──────────┘  └──────────┘  └──────────────┘      │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Observability                                        │ │
│  │  Prometheus → Grafana → Alertmanager                 │ │
│  │  Loki (logs) → Jaeger/Tempo (traces)                 │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Service Mesh (optional)                              │ │
│  │  Istio / Linkerd — mTLS, traffic management, retries │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Production Readiness Checklist

### Container (Docker)
- [ ] Multi-stage build (small final image)
- [ ] Non-root user in container
- [ ] No secrets baked into image
- [ ] `.dockerignore` excludes unnecessary files
- [ ] Pinned base image version (not `latest`)
- [ ] Health check defined in Dockerfile

### Kubernetes Deployment
- [ ] Resource requests AND limits set for all containers
- [ ] Liveness and readiness probes configured
- [ ] Pod Disruption Budget (PDB) defined
- [ ] Anti-affinity for spreading pods across nodes
- [ ] Security context: `runAsNonRoot: true`, `readOnlyRootFilesystem: true`
- [ ] Network policies restrict traffic
- [ ] Horizontal Pod Autoscaler (HPA) configured
- [ ] Secrets stored in external secret manager (not K8s Secrets directly)

### Helm Chart
- [ ] `values.yaml` has sensible defaults
- [ ] All configurable values are documented
- [ ] Chart passes `helm lint` and `helm template`
- [ ] Chart tested with `helm test`

### Observability
- [ ] Prometheus metrics exposed (`/metrics` endpoint)
- [ ] Grafana dashboards for key metrics
- [ ] Alerting rules for SLOs
- [ ] Structured logging (JSON)
- [ ] Distributed tracing headers propagated

### Security
- [ ] Pod Security Admission enforced
- [ ] RBAC with least privilege
- [ ] Image scanning in CI pipeline
- [ ] Network policies applied
- [ ] Secrets encrypted at rest

---

## Scripts

### generate_k8s_manifests.py
Generate production-ready Kubernetes manifests (Deployment, Service, Ingress, HPA, PDB,
NetworkPolicy, ConfigMap).

```bash
python scripts/generate_k8s_manifests.py \
  --app-name myapp \
  --image ghcr.io/org/myapp:latest \
  --port 8080 \
  --replicas 3 \
  --namespace production \
  --features hpa,pdb,netpol,ingress \
  --output ./k8s/
```

### generate_helm_chart.py
Scaffold a complete Helm chart with templates, values, helpers, and tests.

```bash
python scripts/generate_helm_chart.py \
  --chart-name myapp \
  --app-version 1.0.0 \
  --port 8080 \
  --features ingress,hpa,pdb,netpol,serviceaccount \
  --output ./charts/
```

---

## Best Practices

1. **One process per container** — don't run supervisord with 5 services
2. **Immutable images** — tag with SHA, never overwrite tags
3. **Resource limits always** — prevents noisy neighbor problems
4. **Probes are mandatory** — without them, K8s can't manage your app
5. **PDB for high availability** — ensures rolling updates don't take everything down
6. **Namespaces for isolation** — per environment and/or per team
7. **GitOps for production** — all changes through Git, never `kubectl apply` manually
8. **External secrets** — AWS Secrets Manager / GCP Secret Manager / HashiCorp Vault
9. **Structured logging** — JSON logs → Loki/Elasticsearch → dashboards
10. **Horizontal over vertical** — scale out (more pods) before scaling up (bigger pods)



---
