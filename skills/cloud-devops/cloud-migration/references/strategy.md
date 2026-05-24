# Migration Strategy Reference

## Table of Contents
1. The 6 Rs Framework
2. Decision Matrix
3. Migration Patterns by App Type
4. Wave Planning

---

## 1. The 6 Rs Framework

| R | Strategy | What | Effort | Risk | When |
|---|---------|------|--------|------|------|
| **Rehost** | Lift & shift | Move as-is to cloud VMs | Low | Low | Quick wins, legacy apps |
| **Replatform** | Lift, tinker & shift | Minor optimizations (managed DB, containers) | Medium | Low-Med | Apps that benefit from managed services |
| **Refactor** | Re-architect | Rewrite for cloud-native (microservices, serverless) | High | Medium | Strategic apps, long-term investment |
| **Repurchase** | Replace | Switch to SaaS (Salesforce, Workday) | Medium | Medium | Commodity functions (HR, CRM, email) |
| **Retire** | Decommission | Turn off apps no longer needed | Low | Low | Redundant, unused applications |
| **Retain** | Keep on-premises | Not ready or not worth migrating | None | None | Compliance, latency, end-of-life apps |

### Detailed Decision Guide

**Rehost (Lift & Shift)**
```
When: Need to migrate fast, app works fine, no time for redesign
How:  AWS Application Migration Service / Azure Migrate
      Copy VMs, maintain same OS/config, update networking
Pros: Fast (days-weeks per app), low risk, minimal code changes
Cons: No cloud optimization, same ops burden, may cost more
Next: Optimize after migration (right-size, auto-scale)
```

**Replatform (Lift, Tinker & Shift)**
```
When: Easy wins available (managed DB, containers, LB)
How:  Move app to containers (ECS/AKS), DB to RDS/Azure SQL
      Use managed services where drop-in replacement exists
Pros: Better reliability, less ops, moderate effort
Cons: Some code/config changes needed, testing required
Examples:
  - Self-managed PostgreSQL → RDS / Azure PostgreSQL
  - VM-based app → ECS Fargate / Azure Container Apps
  - Self-managed Redis → ElastiCache / Azure Cache
  - Apache/Nginx LB → ALB / Azure App Gateway
```

**Refactor (Re-architect)**
```
When: App is strategic, needs to scale, or is too monolithic
How:  Break into microservices, adopt serverless, event-driven
      May involve significant code rewrite
Pros: Best cloud utilization, scalability, agility
Cons: High effort (months), risk of scope creep, needs skilled team
When NOT to: App is near end-of-life, team lacks cloud skills, tight deadline
```

**Repurchase (Replace with SaaS)**
```
When: Commercial SaaS does it better than custom-built
How:  Evaluate SaaS options, migrate data, train users
Examples:
  - Custom CRM → Salesforce / HubSpot
  - Custom email → Google Workspace / Microsoft 365
  - Custom HR system → Workday / BambooHR
  - Custom monitoring → Datadog / New Relic
Pros: No maintenance, vendor handles upgrades, often better features
Cons: Ongoing license cost, vendor lock-in, data migration complexity
```

---

## 2. Decision Matrix

```
                    ┌─────────────────────────────────────┐
                    │        Business Value                │
                    │   Low              High              │
        ┌───────────┼──────────────┬──────────────────────┤
        │   Low     │   RETIRE     │    REHOST /          │
 Effort │           │   or RETAIN  │    REPLATFORM        │
  to    │           │              │                      │
Migrate ├───────────┼──────────────┼──────────────────────┤
        │   High    │   RETIRE     │    REFACTOR /        │
        │           │   or         │    REPURCHASE        │
        │           │   REPURCHASE │                      │
        └───────────┴──────────────┴──────────────────────┘
```

### Quick Classification Questions

| Question | If Yes → | If No → |
|----------|---------|---------|
| Is the app still used? | Continue assessment | **Retire** |
| Does a SaaS replacement exist? | Consider **Repurchase** | Continue |
| Must it stay on-premises? | **Retain** | Continue |
| Can it move as-is to VMs? | **Rehost** (quick win) | Continue |
| Can it use managed services easily? | **Replatform** | Continue |
| Is it strategic and needs modernization? | **Refactor** | **Rehost** |

---

## 3. Migration Patterns by App Type

| App Type | Recommended R | Target Architecture |
|----------|-------------|-------------------|
| Static website | Replatform | S3/Blob + CloudFront/CDN |
| Simple web app (LAMP) | Replatform | App Service / ECS + RDS |
| Monolithic Java/Spring | Rehost → Replatform | EC2 → ECS/AKS + RDS |
| Microservices | Replatform | ECS Fargate / AKS |
| Batch/ETL jobs | Replatform | Lambda/Functions + Step Functions |
| Custom CRM/HR | Repurchase | SaaS (Salesforce, Workday) |
| Legacy mainframe | Retain or Rehost | Retain or specialized migration |
| Data warehouse | Replatform | Redshift / Synapse |
| File server | Replatform | EFS/FSx / Azure Files |

---

## 4. Wave Planning

### Wave Structure
```
Wave 0 (Foundation): Landing zone, networking, IAM, CI/CD
Wave 1 (Pilot): 2-3 low-risk, non-critical apps
Wave 2 (Early adoption): 5-10 apps, mix of Rehost + Replatform
Wave 3-N (Scale): 10-20 apps per wave, parallel execution
Final Wave: Remaining apps, complex migrations, database cutovers
```

### Wave Prioritization Criteria

| Factor | Weight | Score (1-5) |
|--------|--------|-------------|
| Business criticality | 20% | |
| Technical complexity | 20% | |
| Dependencies (fewer = easier) | 15% | |
| Data sensitivity / compliance | 15% | |
| Team readiness | 15% | |
| Business urgency | 15% | |

### Wave Sizing
- **Wave 0**: 0 apps (infrastructure only) — 2-4 weeks
- **Wave 1**: 2-3 apps (learning) — 2-3 weeks
- **Wave 2-3**: 5-10 apps (building confidence) — 3-4 weeks each
- **Wave 4+**: 10-20 apps (factory mode) — 2-3 weeks each
- Apps with shared dependencies should be in the same wave



---

<!-- Script: scripts/generate_migration_plan.py -->

# Script: generate_migration_plan.py

```python
#!/usr/bin/env python3
"""
Generate migration planning documents.

Usage:
    python generate_migration_plan.py \
        --type assessment|wave-plan|cutover-runbook|tco-analysis \
        --provider aws|azure \
        --project myapp \
        --output ./migration/
"""

import argparse
import os
from datetime import datetime, timedelta


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


def gen_assessment(project, provider, output):
    date = datetime.now().strftime("%Y-%m-%d")
    content = f"""# Migration Assessment: {project}

**Date:** {date}
**Target Cloud:** {provider.upper()}
**Assessment Lead:** [Name]

---

## Application Portfolio

| # | App Name | Owner | Criticality | Strategy | Complexity | Wave | Est. Effort |
|---|---------|-------|-------------|----------|-----------|------|-------------|
| 1 | | | Tier ☐1 ☐2 ☐3 ☐4 | ☐Rehost ☐Replatform ☐Refactor ☐Repurchase ☐Retire ☐Retain | ☐Low ☐Med ☐High | | weeks |
| 2 | | | | | | | |
| 3 | | | | | | | |
| 4 | | | | | | | |
| 5 | | | | | | | |
| 6 | | | | | | | |
| 7 | | | | | | | |
| 8 | | | | | | | |
| 9 | | | | | | | |
| 10 | | | | | | | |

## Portfolio Summary

| Strategy | Count | % |
|----------|-------|---|
| Rehost | | |
| Replatform | | |
| Refactor | | |
| Repurchase | | |
| Retire | | |
| Retain | | |
| **Total** | | **100%** |

## Server Inventory

| Hostname | OS | vCPU | RAM | Disk | Avg CPU% | Apps | Target Instance |
|----------|------|------|-----|------|----------|------|----------------|
| | | | | | | | |

## Database Inventory

| Name | Engine | Version | Size | HA? | Migration Method | Target Service |
|------|--------|---------|------|-----|-----------------|---------------|
| | PostgreSQL | 15 | GB | ☐Y ☐N | ☐DMS ☐Native ☐Dump/Restore | {"RDS" if provider == "aws" else "Azure SQL"} |
| | | | | | | |

## Dependency Map

```
[Draw or describe key dependencies between applications]

App A ──→ App B ──→ Database 1
  │                    ↑
  └──→ App C ──────────┘
```

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Data loss during migration | Low | Critical | DMS validation, parallel run |
| Extended downtime | Medium | High | Blue-green cutover, rollback plan |
| Performance degradation | Medium | Medium | Load testing, right-sizing |
| Compliance gap | Low | High | Security review, policy mapping |
| Team skill gap | Medium | Medium | Training, cloud partner support |

## Next Steps

1. [ ] Complete application inventory
2. [ ] Install discovery agents / deploy assessment tools
3. [ ] Conduct dependency mapping workshops
4. [ ] Complete TCO analysis
5. [ ] Define migration waves
6. [ ] Set up landing zone (VPC, IAM, networking)
7. [ ] Execute Wave 0 (foundation)
8. [ ] Execute Wave 1 (pilot)
"""
    create_file(os.path.join(output, f"migration-assessment-{project}.md"), content)


def gen_wave_plan(project, provider, output):
    date = datetime.now().strftime("%Y-%m-%d")
    w0_start = datetime.now() + timedelta(weeks=1)

    content = f"""# Migration Wave Plan: {project}

**Date:** {date}
**Target Cloud:** {provider.upper()}

---

## Wave Timeline

```
{w0_start.strftime("%b %d")}          {(w0_start + timedelta(weeks=3)).strftime("%b %d")}     {(w0_start + timedelta(weeks=6)).strftime("%b %d")}      {(w0_start + timedelta(weeks=9)).strftime("%b %d")}
  │               │              │               │
  ▼               ▼              ▼               ▼
  Wave 0          Wave 1         Wave 2          Wave 3
  Foundation      Pilot          Early Adopt     Scale
  (2 weeks)       (3 weeks)      (3 weeks)       (3 weeks)
```

## Wave 0: Foundation ({w0_start.strftime("%b %d")} — {(w0_start + timedelta(weeks=2)).strftime("%b %d")})

**Goal:** Set up cloud landing zone and migration tooling

| Task | Owner | Status | Due |
|------|-------|--------|-----|
| Create {"VPC" if provider == "aws" else "VNet"} with public/private subnets | Infra | ☐ | |
| Configure IAM roles and policies | Security | ☐ | |
| Set up VPN / Direct Connect | Network | ☐ | |
| Deploy CI/CD pipelines | DevOps | ☐ | |
| Set up monitoring ({"CloudWatch" if provider == "aws" else "Azure Monitor"}) | SRE | ☐ | |
| Configure {"DMS" if provider == "aws" else "Azure DMS"} replication instance | DBA | ☐ | |
| Deploy migration assessment tools | Migration Lead | ☐ | |
| Security baseline (WAF, NACLs, encryption) | Security | ☐ | |

## Wave 1: Pilot ({(w0_start + timedelta(weeks=2)).strftime("%b %d")} — {(w0_start + timedelta(weeks=5)).strftime("%b %d")})

**Goal:** Migrate 2-3 low-risk applications to validate process

| App | Strategy | Complexity | Dependencies | Owner | Status |
|-----|---------|-----------|-------------|-------|--------|
| [Low-risk app 1] | Rehost | Low | None | | ☐ |
| [Low-risk app 2] | Replatform | Low | Shared DB | | ☐ |
| [Internal tool] | Rehost | Low | None | | ☐ |

### Wave 1 Success Criteria
- [ ] Apps running in cloud with < 1% error rate
- [ ] Performance within 20% of on-premises baseline
- [ ] Monitoring and alerting functional
- [ ] Cutover process validated
- [ ] Rollback tested successfully
- [ ] Lessons learned documented

## Wave 2: Early Adoption ({(w0_start + timedelta(weeks=5)).strftime("%b %d")} — {(w0_start + timedelta(weeks=8)).strftime("%b %d")})

**Goal:** Migrate 5-10 applications, including first Tier 2 app

| App | Strategy | Complexity | Dependencies | Owner | Status |
|-----|---------|-----------|-------------|-------|--------|
| | | | | | ☐ |
| | | | | | ☐ |
| | | | | | ☐ |
| | | | | | ☐ |
| | | | | | ☐ |

## Wave 3+: Scale ({(w0_start + timedelta(weeks=8)).strftime("%b %d")}+)

**Goal:** Migrate remaining applications at scale (10-20 per wave)

[Define waves based on dependency mapping and team capacity]

---

## Migration Metrics Dashboard

| Metric | Target | Current |
|--------|--------|---------|
| Apps migrated | [total] | 0 |
| % complete | 100% | 0% |
| On schedule | Yes | |
| Rollbacks | 0 | 0 |
| Incidents during migration | 0 | 0 |
| Avg cutover time | < 2 hours | |
| Cost savings (monthly) | $[target] | $0 |
"""
    create_file(os.path.join(output, f"wave-plan-{project}.md"), content)


def gen_cutover_runbook(project, provider, output):
    date = datetime.now().strftime("%Y-%m-%d")
    content = f"""# Cutover Runbook: [Application Name]

**Project:** {project}
**Target Cloud:** {provider.upper()}
**Date:** {date}
**Cutover Type:** ☐ Big-bang  ☐ Blue-green  ☐ Parallel Run
**Scheduled:** [Date] [Start Time] — [End Time] [Timezone]
**Rollback Deadline:** [Time] (if not complete, MUST roll back)

---

## Team

| Role | Name | Phone | Slack |
|------|------|-------|-------|
| Migration Lead | | | |
| DBA | | | |
| App Engineer | | | |
| QA / Validation | | | |
| Infrastructure | | | |
| Communications | | | |

## Pre-Cutover Checklist (T-24h)

- [ ] Dress rehearsal completed successfully on [date]
- [ ] All team members confirmed availability
- [ ] Rollback procedure tested
- [ ] Cloud environment validated (compute, DB, networking)
- [ ] DNS TTL lowered to 60s (done T-48h)
- [ ] Stakeholder notification sent
- [ ] Maintenance page ready
- [ ] Backups taken and verified
- [ ] DMS replication running, lag < 5 seconds
- [ ] Monitoring dashboards ready (source + target)

## Cutover Steps

### Phase 1: Freeze (T+0 to T+5m)
| Step | Action | Owner | Status | Time |
|------|--------|-------|--------|------|
| 1.1 | Post in #migrations: "Cutover starting" | Comms | ☐ | |
| 1.2 | Enable maintenance page | App Eng | ☐ | |
| 1.3 | Stop application processes on source | App Eng | ☐ | |
| 1.4 | Verify no active DB transactions | DBA | ☐ | |

### Phase 2: Data Sync (T+5m to T+20m)
| Step | Action | Owner | Status | Time |
|------|--------|-------|--------|------|
| 2.1 | Wait for DMS CDC lag = 0 | DBA | ☐ | |
| 2.2 | Stop DMS task | DBA | ☐ | |
| 2.3 | Run validation script (row counts) | DBA | ☐ | |
| 2.4 | Verify checksums on key tables | DBA | ☐ | |
| 2.5 | **GO/NO-GO: Data validated?** | Lead | ☐ | |

### Phase 3: Application Switch (T+20m to T+35m)
| Step | Action | Owner | Status | Time |
|------|--------|-------|--------|------|
| 3.1 | Start application in cloud | App Eng | ☐ | |
| 3.2 | Verify health endpoint returns 200 | App Eng | ☐ | |
| 3.3 | Run automated smoke tests | QA | ☐ | |
| 3.4 | Switch DNS to cloud LB | Infra | ☐ | |
| 3.5 | Verify traffic flowing to cloud | Infra | ☐ | |
| 3.6 | Disable maintenance page | App Eng | ☐ | |

### Phase 4: Validate (T+35m to T+120m)
| Step | Action | Owner | Status | Time |
|------|--------|-------|--------|------|
| 4.1 | Monitor error rate (< 1%) | SRE | ☐ | |
| 4.2 | Monitor latency (within SLO) | SRE | ☐ | |
| 4.3 | Verify core user journeys | QA | ☐ | |
| 4.4 | Check integrations working | App Eng | ☐ | |
| 4.5 | Verify logs flowing to {"CloudWatch" if provider == "aws" else "Log Analytics"} | SRE | ☐ | |
| 4.6 | **GO/NO-GO: Accept migration?** | Lead | ☐ | |

### Phase 5: Close
| Step | Action | Owner | Status | Time |
|------|--------|-------|--------|------|
| 5.1 | Post: "Migration complete" | Comms | ☐ | |
| 5.2 | Update status page | Comms | ☐ | |
| 5.3 | Restore DNS TTL to 300s | Infra | ☐ | |
| 5.4 | Keep source running for [7] days (soak) | Infra | ☐ | |
| 5.5 | Schedule source decommission | Lead | ☐ | |

---

## Rollback Procedure

**Trigger:** Any GO/NO-GO fails, or error rate > 5%, or critical journey broken

| Step | Action | Owner | Time |
|------|--------|-------|------|
| R.1 | Announce rollback in #migrations | Lead | 0m |
| R.2 | Switch DNS back to source | Infra | 2m |
| R.3 | Stop cloud application | App Eng | 3m |
| R.4 | Verify traffic on source | Infra | 5m |
| R.5 | If writes hit cloud DB: sync data back | DBA | 10-60m |
| R.6 | Verify source app healthy | QA | 5m |
| R.7 | Announce rollback complete | Comms | +2m |
| R.8 | Schedule post-mortem | Lead | Next day |

---

## Post-Cutover (Day 1-7)

- [ ] Monitor performance daily (compare to baseline)
- [ ] Address any P1/P2 issues immediately
- [ ] Gather user feedback
- [ ] Right-size cloud resources based on actual usage
- [ ] Enable auto-scaling
- [ ] Decommission source systems (after soak period)
- [ ] Update architecture documentation
- [ ] Write migration retrospective
"""
    create_file(os.path.join(output, f"cutover-runbook-{project}.md"), content)


def gen_tco(project, provider, output):
    date = datetime.now().strftime("%Y-%m-%d")
    content = f"""# TCO Analysis: {project}

**Date:** {date}
**Comparison:** On-Premises vs {provider.upper()}
**Period:** 3-Year Analysis

---

## Cost Summary (3-Year)

| Category | On-Premises | {provider.upper()} Cloud | Savings |
|----------|------------|-------------|---------|
| Compute | $ | $ | $ |
| Storage | $ | $ | $ |
| Database | $ | $ | $ |
| Networking | $ | $ | $ |
| Licensing | $ | $ | $ |
| Data Center | $ | $ | $ |
| Personnel | $ | $ | $ |
| **Total (3yr)** | **$** | **$** | **$** |
| **Monthly** | **$** | **$** | **$** |

## Compute Comparison

| Server | On-Prem Spec | Monthly Cost | Cloud Instance | Monthly Cost |
|--------|-------------|-------------|---------------|-------------|
| Web-1 | 8 vCPU, 16GB | $ | {"m6i.xlarge" if provider == "aws" else "D4s_v5"} | $ |
| Web-2 | 8 vCPU, 16GB | $ | {"m6i.xlarge" if provider == "aws" else "D4s_v5"} | $ |
| App-1 | 16 vCPU, 32GB | $ | {"m6i.2xlarge" if provider == "aws" else "D8s_v5"} | $ |
| DB-1 | 16 vCPU, 64GB | $ | {"db.r6g.2xlarge" if provider == "aws" else "GP_Gen5_8"} | $ |

## Cost Optimization Scenarios

| Scenario | Monthly Cost | vs On-Demand | vs On-Prem |
|----------|-------------|-------------|-----------|
| On-Demand (baseline) | $ | — | $ |
| + Right-sizing | $ | -20% | $ |
| + 1yr Reserved/SP | $ | -40% | $ |
| + Spot (eligible) | $ | -50% | $ |
| + 3yr Reserved | $ | -55% | $ |

## Migration Costs (One-Time)

| Item | Cost |
|------|------|
| Cloud landing zone setup | $ |
| Application migration labor | $ |
| Database migration (DMS) | $ |
| Testing and validation | $ |
| Training | $ |
| Parallel running period | $ |
| **Total migration cost** | **$** |
| **Payback period** | **months** |

## Assumptions

1. On-premises costs include depreciation over 5-year hardware lifecycle
2. Cloud costs assume {provider.upper()} {"us-east-1" if provider == "aws" else "East US"} pricing
3. Personnel costs based on [X] FTE admins at $[Y]/year
4. Data center costs include power, cooling, rent, security
5. Licensing includes OS, database, virtualization, backup software
"""
    create_file(os.path.join(output, f"tco-analysis-{project}.md"), content)


GENERATORS = {
    "assessment": gen_assessment,
    "wave-plan": gen_wave_plan,
    "cutover-runbook": gen_cutover_runbook,
    "tco-analysis": gen_tco,
}


def main():
    parser = argparse.ArgumentParser(description="Generate Migration Documents")
    parser.add_argument("--type", choices=GENERATORS.keys(), required=True)
    parser.add_argument("--provider", choices=["aws", "azure"], default="aws")
    parser.add_argument("--project", default="myapp")
    parser.add_argument("--output", default="./migration")
    args = parser.parse_args()

    print(f"\n🚀 Generating {args.type} for {args.project} ({args.provider.upper()})\n")
    GENERATORS[args.type](args.project, args.provider, args.output)
    print(f"\n✅ Document generated at: {args.output}/")


if __name__ == "__main__":
    main()

```
