---
description: Comprehensive multi-cloud and hybrid cloud skill covering strategy, connectivity, multi-cloud
  Kubernetes, cloud-agnostic tooling, identity federation, and data replication. Use this skill whenever
  the user mentions multi-cloud, hybrid cloud, multi-cloud strategy, vendor lock-in, cloud portability,
  cloud abstraction, cloud-agnostic, Crossplane, Pulumi multi-cloud, Terraform multi-provider, hybrid
  connectivity, Direct Connect, ExpressRoute, site-to-site VPN, SD-WAN, federated Kubernetes, multi-cluster,
  fleet management, Anthos, Azure Arc, EKS Anywhere, cross-cloud identity, identity federation, SAML,
  OIDC federation, cross-cloud DNS, global DNS, cross-cloud data replication, data sovereignty, multi-cloud
  networking, transit, interconnect, or any request involving running workloads across multiple cloud
  providers, connecting on-premises to cloud, managing infrastructure across clouds, or designing cloud-agnostic
  architectures.
name: multi-cloud-hybrid
---

# Multi-Cloud & Hybrid Cloud

A production-grade skill for designing and implementing multi-cloud and hybrid cloud
architectures with cross-cloud connectivity, identity, data, and Kubernetes patterns.

## Quick Reference

| Area | Key Concepts | Reference |
|------|-------------|-----------|
| Strategy | When/why, lock-in, abstraction | `references/strategy.md` |
| Connectivity | VPN, DX/ER, peering, SD-WAN | `references/connectivity.md` |
| Multi-Cloud K8s | Fleet management, GitOps, service mesh | `references/multi-cloud-k8s.md` |
| Identity & Data | Federation, DNS, replication | `references/identity-data.md` |

## Multi-Cloud Decision Framework

```
Do you NEED multi-cloud?
│
├── Regulatory / data sovereignty requirement?
│   └── YES → Multi-cloud (or hybrid) required
│
├── Vendor lock-in risk unacceptable?
│   └── Consider cloud-agnostic abstractions (Terraform, K8s, Crossplane)
│
├── Best-of-breed services needed from different clouds?
│   └── Multi-cloud for specific workloads (not everything)
│
├── DR across cloud providers?
│   └── Active-passive across clouds (expensive but resilient)
│
└── None of the above?
    └── Single cloud is simpler, cheaper, and recommended
```

### Multi-Cloud Maturity Levels

| Level | Description | Tooling |
|-------|------------|---------|
| **L1: Separate silos** | Different teams use different clouds independently | Per-cloud Terraform |
| **L2: Unified IaC** | Single Terraform codebase, multi-provider | Terraform multi-provider |
| **L3: Abstracted infra** | Cloud-agnostic resource definitions | Crossplane, Pulumi |
| **L4: Unified platform** | Common platform across clouds | Multi-cloud K8s + GitOps |
| **L5: Seamless workloads** | Apps move between clouds transparently | Service mesh + federation |

### Cost of Multi-Cloud

| Cost Factor | Single Cloud | Multi-Cloud |
|-------------|-------------|-------------|
| Engineering complexity | 1× | 2-3× |
| Operational overhead | 1× | 2× |
| Data transfer | Minimal | Significant (egress fees) |
| Tooling/training | 1 cloud to learn | 2-3 clouds + abstraction layer |
| Vendor discounts | Maximum leverage | Split spend = less discount |
| DR capability | Multi-region | Multi-cloud (stronger) |

---

## Architecture Patterns

### Pattern 1: Primary + DR (Active-Passive)
```
AWS (Primary)                    Azure (DR)
┌──────────────┐                ┌──────────────┐
│  Full stack   │───VPN/DX───→ │  Minimal      │
│  serving      │   replication │  standby      │
│  traffic      │              │  (data sync)  │
└──────────────┘                └──────────────┘
```

### Pattern 2: Best-of-Breed
```
AWS                              Azure
┌──────────────┐                ┌──────────────┐
│  Compute     │                │  AI/ML       │
│  (EKS)       │◄──── API ────►│  (Cognitive)  │
│  Data (DDB)  │                │  Analytics   │
└──────────────┘                └──────────────┘
```

### Pattern 3: Geo-Distributed
```
AWS us-east-1          Azure westeurope        AWS ap-southeast-1
┌──────────┐           ┌──────────┐            ┌──────────┐
│ US users │           │ EU users │            │ APAC     │
└──────────┘           └──────────┘            └──────────┘
      ↕ Global DNS (Route53 / Cloudflare) ↕
```

### Pattern 4: Hybrid (On-Prem + Cloud)
```
On-Premises DC              AWS / Azure
┌──────────────┐           ┌──────────────┐
│  Legacy apps  │──VPN/DX─►│  Modern apps  │
│  Databases    │  /ER     │  K8s workloads│
│  Compliance   │          │  Data lakes   │
└──────────────┘           └──────────────┘
```

---

## Best Practices

1. **Don't multi-cloud for the sake of it** — single cloud is simpler; justify the complexity
2. **Standardize on Kubernetes** — the most portable workload platform
3. **Use Terraform for all IaC** — works across all clouds consistently
4. **Minimize cross-cloud data transfer** — egress costs add up fast
5. **Federate identity** — single IdP (Okta/Azure AD) for all clouds
6. **GitOps for deployments** — ArgoCD/Flux works across any K8s cluster
7. **Abstract where it matters** — databases and compute, not every service
8. **Monitor uniformly** — Datadog, Grafana Cloud, or Prometheus across all clouds
9. **Centralize DNS** — one DNS provider for global traffic management
10. **Test cross-cloud failover** — regularly, not just once
