---
name: cloud-solution-architect
description: >-
  Well-Architected Framework, multi-tier patterns, FinOps, and disaster recovery for AWS and Azure. Use when the user mentions cloud architecture, Well-Architected, WAF review, operational excellence, reliability, cost optimization, microservices, CQRS, saga pattern, FinOps, reserved instances, right-sizing, DR, RPO, RTO, active-active, pilot light, warm standby, ADR, or designing/reviewing cloud solutions.
---

# Cloud Solution Architect

A production-grade skill for designing, reviewing, and optimizing cloud architectures
using the Well-Architected Framework, proven patterns, FinOps, and DR strategies.

## Quick Reference

| Area | Key Concepts | Reference |
|------|-------------|-----------|
| Well-Architected | 6 pillars, review checklists | `references/well-architected.md` |
| Architecture Patterns | Multi-tier, microservices, event-driven | `references/architecture-patterns.md` |
| Cost Optimization | FinOps, reserved capacity, right-sizing | `references/cost-optimization.md` |
| Disaster Recovery | RPO/RTO, DR patterns, BCP | `references/disaster-recovery.md` |

## Architecture Design Process

```
1. Requirements → Understand business needs, constraints, SLAs
        ↓
2. Trade-offs → Cost vs performance vs reliability vs complexity
        ↓
3. Pattern Selection → Choose architecture pattern(s)
        ↓
4. Component Design → Select services, define boundaries
        ↓
5. Well-Architected Review → Validate against 6 pillars
        ↓
6. Document → ADRs, diagrams, runbooks
        ↓
7. Iterate → Review quarterly, evolve with needs
```

## Architecture Decision Records (ADRs)

Every significant architecture decision should be documented:

```markdown
# ADR-001: Use ECS Fargate over EKS for API services

**Status:** Accepted
**Date:** 2025-01-15
**Context:** We need a container platform for 5 microservices with moderate traffic.
**Decision:** Use ECS Fargate instead of EKS.
**Rationale:** Simpler operations, lower cost for our scale, team has ECS experience.
**Alternatives:** EKS (more complex, better for 20+ services), App Runner (too limited).
**Consequences:** Limited to AWS, no service mesh, simpler autoscaling.
**Review:** Reassess when we exceed 15 services or need multi-cloud.
```

---

## Scripts

### generate_architecture_review.py
Generate Well-Architected review checklists and architecture assessment documents.

```bash
python scripts/generate_architecture_review.py \
  --type review|adr|cost-report \
  --provider aws|azure|multi-cloud \
  --pillars all|security,reliability,cost \
  --project myapp \
  --output ./architecture/
```

---

## Best Practices

1. **Design for failure** — everything fails; design so failures don't cascade
2. **Automate everything** — infrastructure, deployments, scaling, recovery
3. **Use managed services** — let the cloud provider handle undifferentiated heavy lifting
4. **Decouple components** — loose coupling enables independent scaling and deployment
5. **Design for observability** — you can't fix what you can't see
6. **Optimize costs continuously** — FinOps is a practice, not a one-time activity
7. **Document decisions** — ADRs preserve context for future teams
8. **Test your DR plan** — a plan that hasn't been tested is just a wish
9. **Start simple, evolve** — don't over-architect for problems you don't have yet
10. **Review quarterly** — architectures age; revisit assumptions regularly



---
