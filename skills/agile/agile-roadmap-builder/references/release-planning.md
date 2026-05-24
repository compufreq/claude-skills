# Release Planning Reference

## Table of Contents
1. Release Planning Process
2. Release Plan Structure
3. Scope Management
4. Risk & Contingency
5. Go/No-Go Criteria
6. Release Communication

---

## 1. Release Planning Process

### Inputs
- Product roadmap (themes, epics, priorities)
- Team capacity (per sprint, per team)
- Historical velocity / throughput
- External constraints (compliance deadlines, events, contracts)
- Dependency map (cross-team, cross-system)

### Steps

1. **Define the release goal** — What is this release about? What problem does it solve?
2. **Identify candidate features** — Which epics/features are in scope?
3. **Size and estimate** — How much work? How many sprints?
4. **Capacity check** — Does the team have enough capacity?
5. **Dependency analysis** — What depends on what? What's the critical path?
6. **Risk assessment** — What could go wrong? What's the contingency?
7. **Milestone planning** — Key dates, decision points, reviews
8. **Communication plan** — Who needs to know what, when?

### Release Cadence Models

| Model | Cadence | Best For |
|-------|---------|----------|
| Sprint-aligned | Every sprint (2 weeks) | SaaS, continuous delivery |
| Monthly | Every 4 weeks | B2B SaaS, internal tools |
| Quarterly | Every 12-13 weeks | Enterprise, regulated industries |
| Feature-driven | When a feature set is ready | Mobile apps, consumer products |
| Date-driven | Fixed date (event, contract) | Marketing launches, compliance |

---

## 2. Release Plan Structure

### Release Plan Document Template

```
# Release Plan: [Release Name / Version]
**Release Date:** [Target date or range]
**Release Owner:** [Name]
**Status:** Planning | In Progress | Feature Complete | Testing | Released

## Release Goal
[One paragraph: what this release achieves for users/business]

## Scope

### Must Have (Release blockers)
| Feature | Epic | Owner | Est. | Status | Sprint Target |
|---------|------|-------|------|--------|--------------|

### Should Have (High value, not blocking)
| Feature | Epic | Owner | Est. | Status | Sprint Target |
|---------|------|-------|------|--------|--------------|

### Could Have (Nice to have, cut first)
| Feature | Epic | Owner | Est. | Status | Sprint Target |
|---------|------|-------|------|--------|--------------|

### Won't Have (Explicitly out of scope)
| Feature | Reason | Deferred To |
|---------|--------|-------------|

## Milestones
| Milestone | Date | Owner | Status |
|-----------|------|-------|--------|
| Scope Freeze | [date] | PM | |
| Feature Complete | [date] | Eng Lead | |
| Code Freeze | [date] | Eng Lead | |
| QA Sign-off | [date] | QA Lead | |
| Staging Deploy | [date] | DevOps | |
| Go/No-Go Decision | [date] | Release Owner | |
| Production Release | [date] | DevOps | |
| Post-Release Review | [date +1 week] | PM | |

## Capacity
| Team | Available Sprints | Total Capacity (SP) | Allocated (SP) | Buffer |
|------|-----------------|--------------------|--------------|---------| 

## Dependencies
| From | To | Type | Status | Risk |
|------|----|------|--------|------|

## Risks
| Risk | Probability | Impact | Mitigation | Owner |
|------|------------|--------|------------|-------|

## Communication Plan
| Audience | What | When | Channel | Owner |
|----------|------|------|---------|-------|
```

---

## 3. Scope Management

### MoSCoW for Releases

| Priority | Meaning | Release Implication |
|----------|---------|-------------------|
| **Must** | Release fails without this | Cannot ship if not done |
| **Should** | Important but not blocking | Ship without if needed, fast-follow |
| **Could** | Nice to have | Cut without guilt if behind |
| **Won't** | Explicitly excluded | Prevents scope creep by naming what's out |

### Scope Freeze
- Set a date after which no new features enter the release
- Only bug fixes and polish after scope freeze
- Any scope additions after freeze require release owner approval + trade-off

### Scope Tracking

Track scope changes over time:

| Date | Change | Type | Impact | Approved By |
|------|--------|------|--------|-------------|
| Jan 15 | Added SSO support | Addition | +13 SP, +1 sprint | PM |
| Jan 22 | Removed dark mode | Removal | -8 SP | PM |
| Feb 1 | Bug: auth regression | Bug fix | +3 SP | Auto-approved |

Net scope change: +8 SP (flag if > 15% of original scope)

---

## 4. Risk & Contingency

### Risk Assessment Matrix

| Probability ↓ / Impact → | Low | Medium | High |
|---------------------------|-----|--------|------|
| High | Monitor | Mitigate | Escalate |
| Medium | Accept | Mitigate | Mitigate |
| Low | Accept | Monitor | Monitor |

### Common Release Risks

| Risk Category | Example | Mitigation |
|--------------|---------|------------|
| Scope creep | New requirements mid-release | Scope freeze date, change control |
| Technical | Integration with legacy system fails | Spike early, have fallback |
| Resource | Key developer leaves mid-release | Cross-training, documentation |
| Dependency | External API not ready | Mock/stub, contract testing |
| Quality | Insufficient test coverage | QA involved from sprint 1 |
| Timeline | Underestimated complexity | Buffer sprints, cut "Could Have" |

### Contingency Planning

For each "Must Have" feature, define:
1. **Fallback scope** — Minimum viable version if behind schedule
2. **Cut candidates** — Which "Should Have" items get cut first?
3. **Date flexibility** — Can the release date slip? By how much?
4. **Team flexibility** — Can resources be added? From where?

---

## 5. Go/No-Go Criteria

### Go/No-Go Checklist

| Category | Criterion | Status |
|----------|-----------|--------|
| **Scope** | All "Must Have" features complete | ☐ |
| **Quality** | No P0/P1 bugs open | ☐ |
| **Quality** | Test coverage > [X]% | ☐ |
| **Quality** | Performance benchmarks met | ☐ |
| **Security** | Security review passed | ☐ |
| **Operations** | Monitoring & alerting configured | ☐ |
| **Operations** | Rollback plan documented and tested | ☐ |
| **Operations** | On-call schedule confirmed | ☐ |
| **Documentation** | User-facing docs updated | ☐ |
| **Documentation** | Release notes drafted | ☐ |
| **Communication** | Stakeholders notified | ☐ |
| **Communication** | Support team briefed | ☐ |

### Decision Framework
- **All green** → Go
- **1-2 amber (non-blocking)** → Go with monitoring plan
- **Any red (blocking)** → No-Go, set new target, communicate delay
- **No-Go** is always a valid outcome — shipping broken software is worse than delaying

---

## 6. Release Communication

### Internal Communication Timeline

| When | What | Audience | Channel |
|------|------|----------|---------|
| Release planning | Scope & timeline shared | Engineering + Product | All-hands / Wiki |
| Weekly | Progress update | Stakeholders | Email / Slack |
| Scope freeze | Scope locked announcement | Engineering | Standup + Slack |
| Feature complete | Feature complete status | PM + Leadership | Email |
| Go/No-Go | Decision communicated | All stakeholders | Meeting + Email |
| Release day | Release notes | All | Email + Slack + Wiki |
| +1 week | Post-release review | Engineering + Product | Retro meeting |

### External Communication

| When | What | Audience | Channel |
|------|------|----------|---------|
| 4-6 weeks before | Preview / coming soon | Customers | Blog / Newsletter |
| 1-2 weeks before | Detailed announcement | Customers | Email + In-app |
| Release day | Release notes + changelog | Public | Blog + Docs |
| +1 week | "What's new" walkthrough | Customers | Webinar / Video |

### Release Notes Template

```
# [Product] [Version] — [Release Name]
**Release Date:** [Date]

## Highlights
- 🚀 [Major feature 1]: [One-sentence benefit]
- 🚀 [Major feature 2]: [One-sentence benefit]

## What's New
### [Feature 1 Name]
[2-3 sentences describing the feature and its benefit to users]

### [Feature 2 Name]
[2-3 sentences]

## Improvements
- [Improvement 1]
- [Improvement 2]

## Bug Fixes
- Fixed: [Bug description]

## Known Issues
- [Issue]: [Workaround]

## Breaking Changes
- [Change]: [Migration guide link]
```



---
