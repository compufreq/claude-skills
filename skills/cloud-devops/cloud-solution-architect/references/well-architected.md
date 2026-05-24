# Well-Architected Framework Reference

## Table of Contents
1. Framework Overview
2. Operational Excellence
3. Security
4. Reliability
5. Performance Efficiency
6. Cost Optimization
7. Sustainability

---

## 1. Framework Overview

The Well-Architected Framework (shared by AWS and Azure with slight variations) provides
a consistent approach to evaluating architectures against best practices.

| Pillar | Key Question | AWS Tool | Azure Tool |
|--------|-------------|----------|-----------|
| Operational Excellence | Can you run and monitor systems effectively? | Well-Architected Tool | Advisor |
| Security | Can you protect data, systems, and assets? | Security Hub | Defender for Cloud |
| Reliability | Can you recover from failures and meet demand? | Trusted Advisor | Service Health |
| Performance Efficiency | Can you use resources efficiently? | Compute Optimizer | Advisor |
| Cost Optimization | Can you eliminate unnecessary costs? | Cost Explorer | Cost Management |
| Sustainability | Can you minimize environmental impact? | Customer Carbon Footprint | Emissions Impact |

---

## 2. Operational Excellence

### Checklist
- [ ] **IaC for everything** — no manual console changes in production
- [ ] **CI/CD pipelines** with automated testing and deployment
- [ ] **Runbooks** for every alert and common operational tasks
- [ ] **Structured logging** with correlation IDs across services
- [ ] **Dashboards** per service (golden signals: latency, traffic, errors, saturation)
- [ ] **Post-incident reviews** (blameless) after every significant incident
- [ ] **Change management** — all changes through PRs with review
- [ ] **Feature flags** for safe, gradual rollouts
- [ ] **Automated rollback** on deployment failures
- [ ] **Game days** — regularly practice failure scenarios

### Key Practices
```
Deploy small, deploy often → reduce blast radius
Automate responses → reduce MTTR
Learn from failures → prevent recurrence
Anticipate failure → design for it
```

---

## 3. Security

### Checklist
- [ ] **Identity**: MFA everywhere, federated identity (SSO), least privilege IAM
- [ ] **Detection**: CloudTrail/Activity Log, GuardDuty/Defender, VPC Flow Logs
- [ ] **Infrastructure**: Private subnets, security groups, NACLs/NSGs, WAF
- [ ] **Data**: Encryption at rest (KMS/Key Vault), encryption in transit (TLS 1.2+)
- [ ] **Application**: Input validation, parameterized queries, CSRF protection
- [ ] **Incident response**: Documented plan, tested quarterly, automated containment
- [ ] **Compliance**: Automated compliance checks (Config Rules, Azure Policy)
- [ ] **Secrets**: No hardcoded secrets, use Secrets Manager/Key Vault, rotate regularly
- [ ] **Network**: PrivateLink for service access, no public endpoints unless required
- [ ] **Supply chain**: SBOM, dependency scanning, image signing

### Security Architecture Layers
```
Edge        → WAF, DDoS protection, CDN
Network     → VPC/VNet, private subnets, security groups
Compute     → Patched images, non-root containers, IMDSv2
Application → OWASP Top 10 mitigations, input validation
Data        → Encryption at rest/transit, tokenization, masking
Identity    → MFA, SSO, least privilege, JIT access
Monitoring  → SIEM, anomaly detection, audit logging
```

---

## 4. Reliability

### Checklist
- [ ] **Multi-AZ** deployment for all production services
- [ ] **Health checks** and automatic recovery (probes, ASG, LB health)
- [ ] **Automated scaling** to handle demand changes
- [ ] **Backup strategy** with tested restore procedures
- [ ] **Dependency management** — circuit breakers, retries with backoff, timeouts
- [ ] **Chaos engineering** — regularly test failure modes
- [ ] **Service quotas** — monitor and request increases before hitting limits
- [ ] **Loose coupling** — async communication where possible (queues, events)
- [ ] **Bulkhead pattern** — isolate critical from non-critical workloads
- [ ] **Graceful degradation** — serve partial results when dependencies are down

### Reliability Patterns

| Pattern | What | When |
|---------|------|------|
| **Retry with backoff** | Retry failed calls with increasing delay | Transient failures |
| **Circuit breaker** | Stop calling failing service, fail fast | Cascading failures |
| **Bulkhead** | Isolate resources per workload | Resource exhaustion |
| **Queue-based leveling** | Buffer requests through a queue | Traffic spikes |
| **Health endpoint** | Expose /health for LB and monitoring | All services |
| **Throttling** | Rate limit requests | Overload protection |
| **Cache-aside** | Cache frequently read data | Reduce DB load |

### Availability Targets

| Target | Downtime/Year | Approach |
|--------|--------------|---------|
| 99% | 3.65 days | Single AZ, basic monitoring |
| 99.9% | 8.76 hours | Multi-AZ, auto-scaling, health checks |
| 99.95% | 4.38 hours | Multi-AZ, redundant components, automated failover |
| 99.99% | 52.6 minutes | Multi-region active-active, no SPOF |

---

## 5. Performance Efficiency

### Checklist
- [ ] **Right-sized instances** — reviewed quarterly with cloud advisor tools
- [ ] **Caching** at multiple layers (CDN, application, database)
- [ ] **Async processing** for non-time-critical work (queues, events)
- [ ] **Connection pooling** for databases and external services
- [ ] **Read replicas** to offload read traffic
- [ ] **CDN** for static content and API caching where applicable
- [ ] **Appropriate storage** types (SSD for IOPS, HDD for throughput)
- [ ] **Load testing** before major launches
- [ ] **Performance budgets** — define and enforce latency targets (SLOs)
- [ ] **Graviton/ARM** instances where compatible (20-40% better price/performance)

### Performance Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| N+1 queries | DB called per item in a list | Batch queries, eager loading |
| Missing indexes | Full table scans | Add appropriate indexes |
| Synchronous I/O chains | Latency compounds across calls | Parallelize, use async |
| Over-fetching | Retrieving unused data | Select only needed fields |
| No caching | Repeated expensive computations | Cache with appropriate TTL |
| Single large instance | Vertical scaling limit | Distribute across instances |

---

## 6. Cost Optimization

### Checklist
- [ ] **Tagging strategy** — all resources tagged with Environment, Team, Service, CostCenter
- [ ] **Reserved capacity** for steady-state workloads (30-60% savings)
- [ ] **Spot/preemptible** for fault-tolerant workloads (60-90% savings)
- [ ] **Right-sizing** — review instance utilization quarterly
- [ ] **Unused resource cleanup** — unattached EBS/disks, idle LBs, old snapshots
- [ ] **Storage lifecycle** — auto-transition to cheaper tiers
- [ ] **Data transfer optimization** — VPC endpoints, CDN, compression
- [ ] **Serverless for variable load** — pay per use instead of per hour
- [ ] **Budget alerts** — AWS Budgets / Azure Cost Alerts at 50%, 80%, 100%
- [ ] **FinOps reviews** — monthly cost review with engineering and finance

### Cost Visibility
```
Tag all resources → Cost allocation reports → Dashboards per team
     ↓                      ↓                        ↓
Chargeback/showback   Anomaly detection        Optimization recommendations
```

---

## 7. Sustainability

### Checklist
- [ ] **Right-size** — over-provisioning wastes energy
- [ ] **Use managed services** — cloud providers optimize utilization
- [ ] **Choose efficient regions** — some regions use more renewable energy
- [ ] **Optimize storage** — delete unused data, compress, use lifecycle policies
- [ ] **Reduce data transfer** — caching, CDN, regional deployments
- [ ] **ARM/Graviton** — more energy-efficient processors
- [ ] **Serverless** — resources only consumed when needed
- [ ] **Measure carbon footprint** — AWS Customer Carbon Footprint, Azure Emissions Impact



---

<!-- Script: scripts/generate_architecture_review.py -->

# Script: generate_architecture_review.py

```python
#!/usr/bin/env python3
"""
Generate Well-Architected review checklists, ADRs, and cost reports.

Usage:
    python generate_architecture_review.py \
        --type review|adr|cost-report|dr-plan \
        --provider aws|azure|multi-cloud \
        --pillars all|security,reliability,cost \
        --project myapp \
        --output ./architecture/
"""

import argparse
import os
from datetime import datetime


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


PILLARS = {
    "operational-excellence": {
        "title": "Operational Excellence",
        "items": [
            ("Infrastructure as Code", "All infrastructure defined in Terraform/CloudFormation/Bicep"),
            ("CI/CD pipelines", "Automated build, test, deploy for all services"),
            ("Monitoring & alerting", "Dashboards, alerts, and runbooks for all services"),
            ("Structured logging", "JSON logs with correlation IDs across services"),
            ("Incident response", "Documented process, on-call rotation, post-incident reviews"),
            ("Change management", "All changes through PRs with code review"),
            ("Runbooks", "Documented procedures for every alert and common operations"),
            ("Feature flags", "Safe rollout mechanism for new features"),
            ("Automated rollback", "Auto-rollback on health check failure after deploy"),
            ("Game days", "Regular failure simulation exercises"),
        ],
    },
    "security": {
        "title": "Security",
        "items": [
            ("Identity & access", "MFA enabled, SSO configured, least privilege IAM"),
            ("Network security", "Private subnets, security groups, no public DB access"),
            ("Encryption at rest", "All storage and databases encrypted with KMS/Key Vault"),
            ("Encryption in transit", "TLS 1.2+ enforced on all connections"),
            ("Secret management", "Secrets in Secrets Manager/Key Vault, not in code"),
            ("WAF", "Web Application Firewall on all public endpoints"),
            ("Vulnerability scanning", "SAST, SCA, container scanning in CI/CD"),
            ("Audit logging", "CloudTrail/Activity Log enabled, centralized SIEM"),
            ("DDoS protection", "Shield/DDoS Protection Standard enabled"),
            ("Supply chain security", "SBOM generated, images signed, dependencies scanned"),
        ],
    },
    "reliability": {
        "title": "Reliability",
        "items": [
            ("Multi-AZ deployment", "All production services span 3+ availability zones"),
            ("Health checks", "Liveness, readiness, and startup probes configured"),
            ("Auto-scaling", "HPA/ASG configured with appropriate metrics and thresholds"),
            ("Circuit breakers", "Implemented for all external service calls"),
            ("Backup strategy", "Automated backups with tested restore procedures"),
            ("Disaster recovery", "DR plan documented and tested (at least annually)"),
            ("Graceful degradation", "Service continues with reduced functionality on failures"),
            ("Queue-based buffering", "Async processing for non-real-time workloads"),
            ("Pod Disruption Budgets", "PDBs defined for all production deployments"),
            ("Dependency mapping", "All service dependencies documented and monitored"),
        ],
    },
    "performance": {
        "title": "Performance Efficiency",
        "items": [
            ("Right-sized instances", "CPU/memory utilization reviewed quarterly"),
            ("Caching strategy", "CDN, application cache, and DB query cache implemented"),
            ("Connection pooling", "DB connection pools or RDS Proxy configured"),
            ("Async processing", "Non-critical work offloaded to queues/events"),
            ("Read replicas", "Read traffic offloaded from primary database"),
            ("CDN", "Static content served via CloudFront/Front Door"),
            ("Performance testing", "Load tests run before major releases"),
            ("SLOs defined", "Latency and throughput targets documented and monitored"),
            ("ARM/Graviton instances", "Used where compatible for better price/performance"),
            ("Database indexing", "Query performance regularly reviewed, indexes optimized"),
        ],
    },
    "cost": {
        "title": "Cost Optimization",
        "items": [
            ("Tagging strategy", "All resources tagged: Environment, Team, Project, CostCenter"),
            ("Budget alerts", "Alerts at 50%, 80%, 100% of monthly budget"),
            ("Reserved capacity", "Savings Plans/RIs purchased for steady-state workloads"),
            ("Spot instances", "Used for fault-tolerant workloads (batch, CI/CD)"),
            ("Right-sizing", "Over-provisioned resources identified and downsized"),
            ("Unused resource cleanup", "Regular sweep for unattached volumes, old snapshots"),
            ("Storage lifecycle", "Auto-transition to cheaper tiers (IA, Cool, Archive)"),
            ("Dev environment scheduling", "Non-production turned off outside business hours"),
            ("Data transfer optimization", "VPC endpoints, CDN, compression used"),
            ("FinOps reviews", "Monthly cost review with engineering and finance"),
        ],
    },
    "sustainability": {
        "title": "Sustainability",
        "items": [
            ("Efficient instances", "ARM/Graviton used where possible"),
            ("Managed services", "Serverless and managed services preferred"),
            ("Storage cleanup", "Unused data deleted, lifecycle policies applied"),
            ("Region selection", "Carbon footprint considered in region choice"),
            ("Right-sizing", "Over-provisioning minimized"),
        ],
    },
}


def generate_review(provider, pillars_str, project, output):
    pillar_list = list(PILLARS.keys()) if pillars_str == "all" else pillars_str.split(",")
    date = datetime.now().strftime("%Y-%m-%d")

    content = f"""# Well-Architected Review: {project}

**Date:** {date}
**Provider:** {provider.upper()}
**Reviewer:** [Name]
**Status:** In Progress

---

## Summary

| Pillar | Score | Critical Issues | Action Items |
|--------|-------|----------------|-------------|
"""
    for key in pillar_list:
        pillar = PILLARS.get(key)
        if pillar:
            content += f"| {pillar['title']} | ☐ / {len(pillar['items'])} | | |\n"

    content += "\n---\n\n"

    for key in pillar_list:
        pillar = PILLARS.get(key)
        if not pillar:
            continue

        content += f"## {pillar['title']}\n\n"
        content += "| # | Check | Status | Notes |\n"
        content += "|---|-------|--------|-------|\n"
        for i, (check, description) in enumerate(pillar["items"], 1):
            content += f"| {i} | **{check}** — {description} | ☐ Pass / ☐ Fail / ☐ N/A | |\n"
        content += "\n"
        content += f"### {pillar['title']} — Action Items\n\n"
        content += "| Priority | Action | Owner | Due Date |\n"
        content += "|----------|--------|-------|----------|\n"
        content += "| | | | |\n\n"
        content += "---\n\n"

    content += """## Review Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Architect | | | |
| Engineering Lead | | | |
| Security | | | |
| Product | | | |
"""

    create_file(os.path.join(output, f"well-architected-review-{project}.md"), content)


def generate_adr(project, output):
    date = datetime.now().strftime("%Y-%m-%d")

    content = f"""# ADR-001: [Decision Title]

**Status:** Proposed | Accepted | Deprecated | Superseded
**Date:** {date}
**Project:** {project}
**Deciders:** [Names]
**Consulted:** [Names]

## Context

What is the issue that motivates this decision? What forces are at play?

## Decision

What is the change we're proposing and/or doing?

## Alternatives Considered

### Alternative 1: [Name]
- **Pros:** ...
- **Cons:** ...

### Alternative 2: [Name]
- **Pros:** ...
- **Cons:** ...

## Consequences

### Positive
- ...

### Negative
- ...

### Risks
- ...

## Compliance

- [ ] Security review completed
- [ ] Cost impact assessed
- [ ] Performance impact assessed
- [ ] DR implications reviewed

## Review Date

Review this decision by: {date} + 6 months
"""

    create_file(os.path.join(output, f"adr-001-template.md"), content)


def generate_dr_plan(provider, project, output):
    date = datetime.now().strftime("%Y-%m-%d")

    content = f"""# Disaster Recovery Plan: {project}

**Date:** {date}
**Provider:** {provider.upper()}
**Owner:** [Name]
**Last Tested:** [Date]
**Next Test:** [Date]

---

## Service Classification

| Service | Tier | RPO | RTO | DR Pattern | DR Region |
|---------|------|-----|-----|-----------|-----------|
| Core API | 1 | 0 | < 15 min | Warm Standby | |
| Web App | 2 | < 1h | < 1h | Pilot Light | |
| Admin Portal | 3 | < 4h | < 4h | Backup & Restore | |
| Batch Jobs | 4 | < 24h | < 24h | Backup & Restore | |

## Data Replication

| Data Store | Replication Method | RPO | Region |
|-----------|-------------------|-----|--------|
| Primary DB | Cross-region replica / Failover Group | < 1 min | |
| Object Storage | Cross-region replication / GRS | < 15 min | |
| Cache | Rebuild from DB on failover | N/A | |

## Failover Procedure

### Pre-Conditions
- [ ] DR infrastructure is running (pilot light / warm standby)
- [ ] DB replica is healthy and replication lag < 1 minute
- [ ] DNS TTL set to 60 seconds
- [ ] Monitoring active in DR region
- [ ] Communication plan activated

### Step 1: Assess
- [ ] Confirm primary region is down (not a false alarm)
- [ ] Verify impact scope (full outage vs partial)
- [ ] Initiate incident communication

### Step 2: Failover
- [ ] Scale up DR compute to production capacity
- [ ] Promote DB replica to primary
- [ ] Update DNS / enable failover routing
- [ ] Verify traffic flowing to DR region

### Step 3: Validate
- [ ] Run smoke tests against DR endpoints
- [ ] Verify data consistency
- [ ] Monitor error rates and latency
- [ ] Confirm all critical user journeys functional

### Step 4: Communicate
- [ ] Update status page
- [ ] Notify internal stakeholders
- [ ] Notify affected customers (if applicable)

## Failback Procedure

### Step 1: Restore Primary
- [ ] Rebuild primary region infrastructure
- [ ] Establish replication from DR → Primary
- [ ] Wait for full data sync

### Step 2: Failback
- [ ] Verify primary region is healthy
- [ ] Switch traffic back to primary
- [ ] Demote DR database back to replica

### Step 3: Verify
- [ ] Confirm all services running in primary
- [ ] Verify replication re-established
- [ ] Scale down DR to standby level

## Communication Plan

| Audience | Channel | Template | Owner |
|----------|---------|----------|-------|
| Engineering | Slack #incidents | Auto-notification | On-call |
| Management | Email + Slack | Incident brief | Engineering Manager |
| Customers | Status page + email | Customer notice | Support |

## Test Schedule

| Test Type | Frequency | Next Date | Owner |
|-----------|-----------|-----------|-------|
| Tabletop exercise | Quarterly | | |
| DB failover test | Semi-annual | | |
| Full failover test | Annual | | |
| Backup restore test | Monthly | | |
"""

    create_file(os.path.join(output, f"dr-plan-{project}.md"), content)


def generate_cost_report(provider, project, output):
    date = datetime.now().strftime("%Y-%m-%d")

    content = f"""# Cost Optimization Report: {project}

**Date:** {date}
**Provider:** {provider.upper()}
**Period:** [Month/Quarter]

---

## Executive Summary

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Monthly spend | $ | $ | ☐ On track / ☐ Over |
| Reserved coverage | % | > 70% | |
| Spot utilization | % | > 30% (eligible) | |
| Waste (unused) | $ | < 5% | |

## Top Cost Drivers

| # | Service/Resource | Monthly Cost | % of Total | Trend | Action |
|---|-----------------|-------------|-----------|-------|--------|
| 1 | | $ | % | ↑ ↓ → | |
| 2 | | $ | % | | |
| 3 | | $ | % | | |
| 4 | | $ | % | | |
| 5 | | $ | % | | |

## Optimization Opportunities

### Immediate (This Week)
| Opportunity | Estimated Savings | Effort | Owner |
|------------|------------------|--------|-------|
| Delete unused EBS volumes | $/mo | Low | |
| Release unattached Elastic IPs | $/mo | Low | |

### Short-Term (This Month)
| Opportunity | Estimated Savings | Effort | Owner |
|------------|------------------|--------|-------|
| Right-size over-provisioned instances | $/mo | Medium | |
| Schedule dev environments off-hours | $/mo | Medium | |

### Medium-Term (This Quarter)
| Opportunity | Estimated Savings | Effort | Owner |
|------------|------------------|--------|-------|
| Purchase Savings Plans/RIs | $/mo | Low (purchase) | |
| Migrate to Graviton/ARM | $/mo | Medium | |

## Reserved Capacity Analysis

| Resource Type | On-Demand | Reserved | Coverage | Recommendation |
|--------------|----------|----------|----------|---------------|
| EC2/VMs | instances | instances | % | |
| RDS/SQL | instances | instances | % | |
| ElastiCache/Redis | nodes | nodes | % | |

## Action Items

| # | Action | Savings | Owner | Due Date | Status |
|---|--------|---------|-------|----------|--------|
| 1 | | $/mo | | | ☐ |
| 2 | | $/mo | | | ☐ |
| 3 | | $/mo | | | ☐ |
"""

    create_file(os.path.join(output, f"cost-report-{project}.md"), content)


GENERATORS = {
    "review": generate_review,
    "adr": lambda p, pil, proj, out: generate_adr(proj, out),
    "cost-report": lambda p, pil, proj, out: generate_cost_report(p, proj, out),
    "dr-plan": lambda p, pil, proj, out: generate_dr_plan(p, proj, out),
}


def main():
    parser = argparse.ArgumentParser(description="Generate Architecture Documents")
    parser.add_argument("--type", choices=GENERATORS.keys(), required=True)
    parser.add_argument("--provider", choices=["aws", "azure", "multi-cloud"], default="aws")
    parser.add_argument("--pillars", default="all", help="Comma-separated or 'all'")
    parser.add_argument("--project", default="myapp")
    parser.add_argument("--output", default="./architecture")
    args = parser.parse_args()

    print(f"\n🏛️  Generating {args.type} for {args.project}\n")

    if args.type == "review":
        generate_review(args.provider, args.pillars, args.project, args.output)
    else:
        GENERATORS[args.type](args.provider, args.pillars, args.project, args.output)

    print(f"\n✅ Document generated at: {args.output}/")


if __name__ == "__main__":
    main()

```
