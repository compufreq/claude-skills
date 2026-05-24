# Cutover Planning Reference

## Table of Contents
1. Cutover Types
2. Cutover Runbook Template
3. Rollback Planning
4. Validation Checklists
5. Communication Plan

---

## 1. Cutover Types

| Type | Downtime | Risk | Complexity | When |
|------|----------|------|-----------|------|
| **Big-bang** | Hours | High | Low | Simple apps, small data |
| **Blue-green** | Minutes | Low | Medium | Web apps with LB |
| **Canary/rolling** | None-minutes | Low | Medium | Microservices |
| **Parallel run** | None | Lowest | High | Critical systems, compliance |

### Big-Bang Cutover
```
Friday 10 PM: Start maintenance window
  1. Stop application (source)
  2. Final data sync / backup
  3. Migrate remaining data
  4. Validate data integrity
  5. Start application (target/cloud)
  6. Smoke test
  7. Update DNS
  8. Full validation
Saturday 6 AM: End maintenance window
```

### Blue-Green Cutover
```
Before cutover: Both environments running
  Source (blue): serving traffic
  Target (green): running, validated, ready

Cutover (5-10 minutes):
  1. Final data sync (DMS CDC caught up)
  2. Stop writes to source DB
  3. Promote target DB
  4. Switch DNS/LB to green
  5. Verify traffic flowing
  6. Monitor for 30 minutes
  
Rollback: Switch DNS/LB back to blue (< 5 minutes)
```

### Parallel Run
```
Week 1-2: Both systems active
  Source: primary (serving users)
  Target: shadow (receiving same inputs)
  Compare: outputs match?

Week 3: Switch primary
  Target: primary (serving users)
  Source: shadow (standby)
  
Week 4: Decommission source
  After validation period, shut down source
```

---

## 2. Cutover Runbook Template

```markdown
# Cutover Runbook: [Application Name]

## Overview
- **Application:** [Name]
- **Migration Type:** [Rehost/Replatform/Refactor]
- **Cutover Type:** [Big-bang/Blue-green/Parallel]
- **Scheduled:** [Date] [Time] - [Time] [Timezone]
- **Maintenance Window:** [Duration]
- **Rollback Deadline:** [Time] (if not complete by this time, roll back)

## Roles
| Role | Name | Contact |
|------|------|---------|
| Migration Lead | | Phone/Slack |
| DBA | | Phone/Slack |
| App Engineer | | Phone/Slack |
| QA | | Phone/Slack |
| Comms Lead | | Phone/Slack |
| Stakeholder | | Phone/Slack |

## Pre-Cutover (T-24 hours)
- [ ] Final dress rehearsal completed successfully
- [ ] All team members confirmed availability
- [ ] Rollback procedure tested
- [ ] Monitoring dashboards ready (source + target)
- [ ] Communication sent to stakeholders
- [ ] Maintenance page / banner prepared
- [ ] DNS TTL lowered to 60 seconds (T-48h)
- [ ] Backups verified

## Cutover Steps

### Phase 1: Preparation (T-0)
| Time | Step | Owner | Status |
|------|------|-------|--------|
| T+0 | Announce cutover start in #migrations channel | Comms | ☐ |
| T+2m | Enable maintenance page / read-only mode | App Eng | ☐ |
| T+5m | Verify no active write transactions | DBA | ☐ |

### Phase 2: Data Migration (T+5m)
| Time | Step | Owner | Status |
|------|------|-------|--------|
| T+5m | Wait for DMS CDC lag = 0 | DBA | ☐ |
| T+8m | Stop DMS replication task | DBA | ☐ |
| T+10m | Run data validation script | DBA | ☐ |
| T+15m | Confirm row counts match | DBA | ☐ |
| T+18m | Confirm checksums match | DBA | ☐ |

### Phase 3: Application Cutover (T+20m)
| Time | Step | Owner | Status |
|------|------|-------|--------|
| T+20m | Update application config to target DB | App Eng | ☐ |
| T+22m | Deploy application to cloud environment | App Eng | ☐ |
| T+25m | Verify application starts successfully | App Eng | ☐ |
| T+28m | Run smoke test suite (automated) | QA | ☐ |

### Phase 4: Traffic Switch (T+30m)
| Time | Step | Owner | Status |
|------|------|-------|--------|
| T+30m | Switch DNS / LB to cloud environment | Infra | ☐ |
| T+32m | Verify traffic flowing to cloud | Infra | ☐ |
| T+35m | Disable maintenance page | App Eng | ☐ |
| T+40m | Run full validation suite | QA | ☐ |

### Phase 5: Monitoring (T+40m to T+2h)
| Time | Step | Owner | Status |
|------|------|-------|--------|
| T+40m | Monitor error rates (target < 1%) | All | ☐ |
| T+50m | Monitor latency (within SLO) | All | ☐ |
| T+60m | Spot-check user journeys manually | QA | ☐ |
| T+90m | Confirm no data anomalies | DBA | ☐ |
| T+120m | **GO / NO-GO decision** | Lead | ☐ |

### Phase 6: Closure
| Time | Step | Owner | Status |
|------|------|-------|--------|
| T+120m | Announce cutover complete | Comms | ☐ |
| T+120m | Restore DNS TTL to normal (300s) | Infra | ☐ |
| T+120m | Update status page | Comms | ☐ |
| T+24h | Decommission source (after soak period) | Infra | ☐ |
```

---

## 3. Rollback Planning

### Rollback Decision Criteria

| Condition | Action |
|-----------|--------|
| Data validation fails | Rollback immediately |
| Application won't start in cloud | Rollback immediately |
| Error rate > 5% after switch | Rollback if not resolved in 15 min |
| Latency > 3x baseline | Investigate 15 min, then rollback |
| Critical user journey broken | Rollback immediately |
| Past rollback deadline | Rollback (no exceptions) |

### Rollback Procedure
```markdown
## Rollback Steps (Emergency)

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | Announce rollback in #migrations | Lead | 0 min |
| 2 | Switch DNS / LB back to source | Infra | 2 min |
| 3 | Verify traffic flowing to source | Infra | 3 min |
| 4 | Verify source application healthy | App Eng | 5 min |
| 5 | Disable cloud application | App Eng | 7 min |
| 6 | If data was written to cloud DB, sync back to source | DBA | 10-60 min |
| 7 | Announce rollback complete | Comms | +5 min |
| 8 | Schedule post-mortem | Lead | Next day |

**Total rollback time: 5-10 minutes (DNS) + data sync if needed**
```

### Rollback Prerequisites
- [ ] Source environment still running (don't decommission until soak period ends)
- [ ] Source DB accessible and up-to-date (or can be restored)
- [ ] DNS TTL lowered for fast propagation
- [ ] Rollback tested in dress rehearsal
- [ ] Team knows who makes the rollback call

---

## 4. Validation Checklists

### Functional Validation

| Category | Test | Pass/Fail |
|----------|------|-----------|
| **Authentication** | User can log in | ☐ |
| **Authentication** | SSO/OAuth works | ☐ |
| **Core workflow** | [Primary user journey 1] | ☐ |
| **Core workflow** | [Primary user journey 2] | ☐ |
| **Data access** | Read existing data correctly | ☐ |
| **Data access** | Create new records | ☐ |
| **Data access** | Update existing records | ☐ |
| **Data access** | Delete records (soft/hard) | ☐ |
| **Integrations** | [Integration 1] works | ☐ |
| **Integrations** | [Integration 2] works | ☐ |
| **Email/notifications** | Outbound messages sent | ☐ |
| **File operations** | Upload works | ☐ |
| **File operations** | Download works | ☐ |
| **Search** | Search returns correct results | ☐ |
| **Reports** | Reports generate correctly | ☐ |

### Infrastructure Validation

| Check | Expected | Actual | Pass |
|-------|---------|--------|------|
| DNS resolves to cloud LB | Cloud IP | | ☐ |
| TLS certificate valid | Valid, correct domain | | ☐ |
| Health check passing | 200 OK | | ☐ |
| Auto-scaling configured | Min/max set | | ☐ |
| Monitoring active | Dashboards showing data | | ☐ |
| Alerts configured | Test alert fires | | ☐ |
| Backups enabled | Backup schedule active | | ☐ |
| Logs flowing | CloudWatch/Log Analytics receiving | | ☐ |

### Performance Validation

| Metric | Baseline (Source) | Post-Migration | Acceptable? |
|--------|------------------|----------------|-------------|
| P50 latency | ms | ms | ☐ (within 20%) |
| P99 latency | ms | ms | ☐ (within 50%) |
| Error rate | % | % | ☐ (< 1%) |
| Throughput | RPS | RPS | ☐ (within 10%) |
| DB query time (avg) | ms | ms | ☐ (within 20%) |

---

## 5. Communication Plan

### Communication Timeline

| When | Audience | Channel | Message |
|------|---------|---------|---------|
| T-2 weeks | All stakeholders | Email | Migration scheduled, timeline, expected impact |
| T-1 week | Engineering + support | Slack | Detailed runbook shared, roles confirmed |
| T-1 day | All stakeholders | Email | Reminder: migration tomorrow, maintenance window |
| T-1 hour | Engineering | Slack #migrations | Go/no-go check, final confirmation |
| T-0 | All stakeholders | Status page + Slack | Migration started, expected completion time |
| T+30m | Engineering | Slack #migrations | Traffic switched, monitoring phase |
| T+2h | All stakeholders | Email + status page | Migration complete / rolled back |
| T+1 day | Engineering | Slack | Post-migration status, any issues |

### Status Page Updates
```
🔵 [Scheduled] Migration planned for [date] [time]
🟡 [In Progress] Migration underway, some features may be temporarily unavailable
🟢 [Completed] Migration complete, all systems operational
🔴 [Rolled Back] Migration rolled back, investigating issues, all systems operational on original infrastructure
```



---
