---
name: cloud-migration
description: >
  Comprehensive cloud migration skill covering the 6 Rs strategy, migration assessment, database
  migration, and cutover planning for AWS and Azure. Use this skill whenever the user mentions
  cloud migration, migration strategy, 6 Rs, rehost, lift and shift, replatform, refactor,
  repurchase, retire, retain, migration assessment, application discovery, dependency mapping,
  TCO analysis, total cost of ownership, migration wave, migration factory, AWS Migration Hub,
  AWS DMS, Database Migration Service, Schema Conversion Tool, SCT, Application Migration Service,
  Azure Migrate, Azure DMS, cutover, cutover planning, migration runbook, rollback plan, data
  migration, database migration, zero-downtime migration, blue-green migration, parallel run,
  migration testing, smoke test, validation checklist, or any request involving planning and
  executing migration of applications, databases, or infrastructure to the cloud.
---

# Cloud Migration

A production-grade skill for planning and executing cloud migrations, covering strategy
selection, assessment, database migration, and cutover execution.

## Quick Reference

| Phase | Key Activities | Reference |
|-------|---------------|-----------|
| Strategy | 6 Rs assessment, portfolio analysis | `references/strategy.md` |
| Assessment | Discovery, dependency mapping, TCO | `references/assessment.md` |
| Database Migration | DMS, schema conversion, zero-downtime | `references/database-migration.md` |
| Cutover | Runbooks, validation, rollback | `references/cutover-planning.md` |

## Migration Phases

```
Phase 1: Assess (2-6 weeks)
  → Discover applications and dependencies
  → Classify by 6 Rs strategy
  → Estimate TCO and build business case
  → Prioritize into migration waves

Phase 2: Mobilize (2-4 weeks)
  → Set up landing zone (VPC/VNet, IAM, networking)
  → Establish CI/CD for cloud deployments
  → Train teams on cloud services
  → Run proof-of-concept migrations

Phase 3: Migrate (ongoing, wave-based)
  → Execute migrations wave by wave
  → Each wave: Plan → Test → Cutover → Validate
  → Database migrations with DMS or native tools
  → Decommission source systems after validation

Phase 4: Optimize (post-migration)
  → Right-size resources
  → Implement auto-scaling
  → Modernize (containers, serverless)
  → Cost optimization (RI/SP, spot)
```

## Scripts

### generate_migration_plan.py
```bash
python scripts/generate_migration_plan.py \
  --type assessment|wave-plan|cutover-runbook|tcо-analysis \
  --provider aws|azure \
  --project myapp \
  --output ./migration/
```

---

## Best Practices

1. **Start with low-risk apps** — build confidence before migrating critical systems
2. **Migrate in waves** — 5-10 apps per wave, not big-bang
3. **Parallel run before cutover** — verify in cloud before decommissioning source
4. **Always have a rollback plan** — tested and documented
5. **Automate everything** — migration is repetitive; tooling pays off
6. **Don't migrate tech debt** — migration is an opportunity to modernize
7. **Test, test, test** — functional, performance, security, DR
8. **Communicate early and often** — stakeholders need visibility
9. **Track progress** — dashboard with wave status, blockers, risks
10. **Optimize post-migration** — don't just lift-and-shift and walk away



---
