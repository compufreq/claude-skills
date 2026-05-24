#!/usr/bin/env python3
"""
Generate multi-cloud architecture assessment and planning documents.

Usage:
    python generate_multicloud_plan.py \
        --type assessment|connectivity|k8s-fleet|identity-plan \
        --clouds aws,azure \
        --project myapp \
        --output ./multicloud/
"""

import argparse
import os
from datetime import datetime


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


def gen_assessment(project, clouds, output):
    date = datetime.now().strftime("%Y-%m-%d")
    cloud_list = clouds.split(",")
    content = f"""# Multi-Cloud Assessment: {project}

**Date:** {date}
**Clouds:** {', '.join(c.upper() for c in cloud_list)}

---

## Multi-Cloud Justification

| Reason | Applicable? | Details |
|--------|------------|---------|
| Regulatory / data sovereignty | ☐ Yes ☐ No | |
| Best-of-breed services | ☐ Yes ☐ No | |
| M&A / acquired infrastructure | ☐ Yes ☐ No | |
| DR across cloud providers | ☐ Yes ☐ No | |
| Vendor negotiation leverage | ☐ Yes ☐ No | |
| **Conclusion:** | ☐ Multi-cloud justified ☐ Single cloud recommended | |

## Workload Distribution

| Workload | Primary Cloud | Reason | Secondary Cloud | DR Strategy |
|----------|-------------|--------|-----------------|-------------|
| | {cloud_list[0].upper()} | | {cloud_list[1].upper() if len(cloud_list) > 1 else "N/A"} | |
| | | | | |
| | | | | |

## Cloud-Specific Services in Use

| Service Category | {' | '.join(c.upper() for c in cloud_list)} | Portable? |
|-----------------|{'|'.join(['---' for _ in cloud_list])}|-----------|
| Compute | {'| '.join(['' for _ in cloud_list])}| |
| Database | {'| '.join(['' for _ in cloud_list])}| |
| Storage | {'| '.join(['' for _ in cloud_list])}| |
| Messaging | {'| '.join(['' for _ in cloud_list])}| |
| AI/ML | {'| '.join(['' for _ in cloud_list])}| |
| Identity | {'| '.join(['' for _ in cloud_list])}| |

## Vendor Lock-In Risk

| Component | Lock-In Level | Mitigation |
|-----------|-------------|-----------|
| Compute (K8s) | Low | Kubernetes is portable |
| Database | | |
| Object Storage | | |
| Serverless | | |
| Messaging | | |
| Identity | | |

## Cross-Cloud Requirements

### Connectivity
- [ ] VPN between clouds established
- [ ] CIDR ranges non-overlapping
- [ ] DNS resolution cross-cloud working
- [ ] Latency acceptable for cross-cloud calls

### Identity
- [ ] Single IdP configured (Okta / Azure AD / Google)
- [ ] SAML/OIDC federation to all clouds
- [ ] Service-to-service identity (SPIFFE or cloud-native)
- [ ] MFA enforced on all cloud consoles

### Data
- [ ] Data sovereignty requirements documented
- [ ] Cross-cloud replication strategy defined
- [ ] Data transfer costs estimated
- [ ] Backup strategy covers all clouds

### Operations
- [ ] Unified monitoring across clouds
- [ ] Centralized logging
- [ ] Single IaC tool (Terraform)
- [ ] GitOps for all deployments
- [ ] Incident response covers all clouds

## Cost Estimate

| Cloud | Monthly Compute | Storage | Data Transfer | Total |
|-------|----------------|---------|--------------|-------|
| {cloud_list[0].upper()} | $ | $ | $ | $ |
| {cloud_list[1].upper() if len(cloud_list) > 1 else "N/A"} | $ | $ | $ | $ |
| Cross-cloud transfer | — | — | $ | $ |
| **Total** | | | | **$** |

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Increased operational complexity | High | Medium | Platform team, automation, training |
| Cross-cloud latency | Medium | Medium | Minimize cross-cloud calls, cache |
| Data transfer costs | High | Medium | Process data where it lives |
| Skill gap | Medium | High | Training budget, cloud certifications |
| Inconsistent security | Medium | High | Unified IdP, centralized policies |

## Action Items

| # | Action | Owner | Due | Status |
|---|--------|-------|-----|--------|
| 1 | Establish cross-cloud VPN | Infra | | ☐ |
| 2 | Configure identity federation | Security | | ☐ |
| 3 | Set up unified monitoring | SRE | | ☐ |
| 4 | Create Terraform multi-provider modules | Platform | | ☐ |
| 5 | Define data replication strategy | Data | | ☐ |
"""
    create_file(os.path.join(output, f"multicloud-assessment-{project}.md"), content)


def gen_connectivity(project, clouds, output):
    date = datetime.now().strftime("%Y-%m-%d")
    cloud_list = clouds.split(",")
    content = f"""# Cross-Cloud Connectivity Plan: {project}

**Date:** {date}
**Clouds:** {', '.join(c.upper() for c in cloud_list)}

---

## Network Topology

```
{"AWS VPC" if "aws" in cloud_list else "Cloud A"} (10.0.0.0/16) ←── IPsec VPN ──→ {"Azure VNet" if "azure" in cloud_list else "Cloud B"} (10.1.0.0/16)
```

## CIDR Allocation

| Network | CIDR | Cloud | Purpose |
|---------|------|-------|---------|
| Production | 10.0.0.0/16 | {cloud_list[0].upper()} | Primary workloads |
| Production | 10.1.0.0/16 | {cloud_list[1].upper() if len(cloud_list) > 1 else "DR"} | {"DR / secondary" if len(cloud_list) > 1 else "DR"} |
| Staging | 10.2.0.0/16 | {cloud_list[0].upper()} | Staging |
| Management | 10.20.0.0/16 | {cloud_list[0].upper()} | Shared services |
| On-Premises | 192.168.0.0/16 | DC | Legacy systems |

## Connectivity Matrix

| From \\ To | {' | '.join(c.upper() for c in cloud_list)} | On-Prem |
|-----------|{'|'.join(['---' for _ in cloud_list])}|---------|
| {cloud_list[0].upper()} | — | VPN | VPN/DX |
{f'| {cloud_list[1].upper()} | VPN | — | VPN/ER |' if len(cloud_list) > 1 else ''}
| On-Prem | VPN/DX | {"VPN/ER" if "azure" in cloud_list else "VPN"} | — |

## Implementation Checklist

### Phase 1: VPN Setup
- [ ] Create VPN gateways in both clouds
- [ ] Exchange public IPs and pre-shared keys
- [ ] Configure IPsec tunnels (IKEv2, AES-256)
- [ ] Verify tunnel connectivity (ping cross-cloud)
- [ ] Configure BGP or static routes
- [ ] Test failover (bring down one tunnel)

### Phase 2: DNS
- [ ] Configure DNS forwarding between clouds
- [ ] Set up split-horizon DNS
- [ ] Test name resolution cross-cloud
- [ ] Configure health checks on DNS records

### Phase 3: Monitoring
- [ ] Monitor tunnel status (up/down alerts)
- [ ] Monitor cross-cloud latency
- [ ] Monitor bandwidth utilization
- [ ] Monitor data transfer costs
- [ ] Set up alerts for tunnel failures

## Security Requirements

- [ ] All cross-cloud traffic encrypted (IPsec)
- [ ] Network ACLs/NSGs restrict cross-cloud traffic to necessary ports
- [ ] No direct internet path between clouds (VPN only)
- [ ] Firewall rules reviewed quarterly
- [ ] VPN credentials rotated annually
"""
    create_file(os.path.join(output, f"connectivity-plan-{project}.md"), content)


def gen_k8s_fleet(project, clouds, output):
    date = datetime.now().strftime("%Y-%m-%d")
    cloud_list = clouds.split(",")
    content = f"""# Multi-Cloud Kubernetes Fleet Plan: {project}

**Date:** {date}
**Clusters:** {', '.join(f"{c.upper()} K8s" for c in cloud_list)}

---

## Cluster Inventory

| Cluster | Cloud | Region | K8s Version | Purpose | Nodes |
|---------|-------|--------|-------------|---------|-------|
| {project}-prod-1 | {cloud_list[0].upper()} | | 1.31 | Production (primary) | |
{f'| {project}-prod-2 | {cloud_list[1].upper()} | | 1.31 | Production (secondary) | |' if len(cloud_list) > 1 else ''}
| {project}-staging | {cloud_list[0].upper()} | | 1.31 | Staging | |

## GitOps Strategy

### Repository Structure
```
k8s-manifests/
├── apps/{project}/
│   ├── base/              (shared manifests)
│   └── overlays/
│       ├── {cloud_list[0]}-production/
{f"│       ├── {cloud_list[1]}-production/" if len(cloud_list) > 1 else ""}
│       └── staging/
├── infrastructure/
│   ├── {cloud_list[0]}/   (cloud-specific infra)
{f"│   └── {cloud_list[1]}/" if len(cloud_list) > 1 else ""}
└── argocd/
    └── applicationsets.yaml
```

### Deployment Strategy
- [ ] ArgoCD ApplicationSet for multi-cluster deployment
- [ ] Cloud-specific overlays (ingress annotations, storage classes)
- [ ] Shared base manifests for application workloads
- [ ] Automated image promotion across clusters

## Service Mesh (Cross-Cluster)

| Option | Complexity | Cross-Cloud Support |
|--------|-----------|-------------------|
| Istio multi-cluster | High | Full (east-west gateway) |
| Linkerd multi-cluster | Medium | Full (gateway mirroring) |
| No mesh (DNS-based) | Low | Limited (no mTLS) |

**Recommendation:** Start without mesh. Add Linkerd when cross-cluster service calls are needed.

## Checklist

- [ ] All clusters registered in ArgoCD
- [ ] GitOps repository structure created
- [ ] Base + overlay manifests for each cluster
- [ ] Monitoring (Prometheus) on each cluster with central Grafana
- [ ] Logging (Loki) on each cluster
- [ ] Image registry accessible from all clusters
- [ ] Network policies consistent across clusters
- [ ] RBAC consistent across clusters
- [ ] Disaster recovery procedure documented and tested
"""
    create_file(os.path.join(output, f"k8s-fleet-plan-{project}.md"), content)


def gen_identity(project, clouds, output):
    date = datetime.now().strftime("%Y-%m-%d")
    cloud_list = clouds.split(",")
    content = f"""# Cross-Cloud Identity Plan: {project}

**Date:** {date}
**Clouds:** {', '.join(c.upper() for c in cloud_list)}

---

## Identity Architecture

### Central IdP
- **Provider:** ☐ Okta  ☐ Azure AD  ☐ Google Workspace  ☐ Other: ___
- **Protocol:** ☐ SAML 2.0  ☐ OIDC  ☐ Both

### Federation Map

| IdP → | {' | '.join(c.upper() for c in cloud_list)} | On-Prem AD |
|-------|{'|'.join(['---' for _ in cloud_list])}|------------|
| Human users | {'| '.join(["SAML SSO" for _ in cloud_list])} | LDAP/Kerberos |
| CI/CD | {'| '.join(["OIDC (GitHub)" for _ in cloud_list])} | N/A |
| Service-to-service | {'| '.join(["Workload Identity" for _ in cloud_list])} | Service account |

## User Groups → Cloud Roles

| Group | {' | '.join(f"{c.upper()} Role" for c in cloud_list)} |
|-------|{'|'.join(['---' for _ in cloud_list])}|
| Platform Admins | {'| '.join(["Admin" for _ in cloud_list])} |
| Developers | {'| '.join(["Developer/Contributor" for _ in cloud_list])} |
| Read-Only | {'| '.join(["ReadOnly/Reader" for _ in cloud_list])} |
| CI/CD | {'| '.join(["Deploy Role" for _ in cloud_list])} |

## Implementation Checklist

### Phase 1: Human Identity
- [ ] Select central IdP
- [ ] Configure SAML/OIDC federation to each cloud
- [ ] Map groups to cloud roles
- [ ] Enable MFA for all cloud access
- [ ] Test SSO login to each cloud console

### Phase 2: Service Identity
- [ ] Configure OIDC federation for CI/CD (GitHub Actions → each cloud)
- [ ] Set up Kubernetes workload identity (IRSA, Workload Identity)
- [ ] Document all service accounts and their permissions
- [ ] Implement just-in-time access for privileged operations

### Phase 3: Audit & Compliance
- [ ] Centralize audit logs from all clouds
- [ ] Quarterly access reviews
- [ ] Automated detection of unused permissions
- [ ] Emergency access (break-glass) procedure documented
"""
    create_file(os.path.join(output, f"identity-plan-{project}.md"), content)


GENERATORS = {
    "assessment": gen_assessment,
    "connectivity": gen_connectivity,
    "k8s-fleet": gen_k8s_fleet,
    "identity-plan": gen_identity,
}


def main():
    parser = argparse.ArgumentParser(description="Generate Multi-Cloud Planning Documents")
    parser.add_argument("--type", choices=GENERATORS.keys(), required=True)
    parser.add_argument("--clouds", default="aws,azure", help="Comma-separated clouds")
    parser.add_argument("--project", default="myapp")
    parser.add_argument("--output", default="./multicloud")
    args = parser.parse_args()

    print(f"\n🌍 Generating {args.type} for {args.project} ({args.clouds})\n")
    GENERATORS[args.type](args.project, args.clouds, args.output)
    print(f"\n✅ Document generated at: {args.output}/")


if __name__ == "__main__":
    main()
