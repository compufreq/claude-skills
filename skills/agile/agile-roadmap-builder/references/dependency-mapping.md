# Dependency Mapping Reference

## Table of Contents
1. Types of Dependencies
2. Dependency Identification
3. Dependency Visualization
4. Managing Dependencies
5. Cross-Team Coordination

---

## 1. Types of Dependencies

### Technical Dependencies
One feature requires another to be built first.
```
Epic A (Auth API) ──→ Epic B (User Dashboard)
                       "B needs A's API to function"
```

### Resource Dependencies
Same person/skill needed for multiple items.
```
Epic A (iOS Login) ──→ Epic B (iOS Settings)
                       "Same iOS developer needed"
```

### External Dependencies
Waiting on something outside the team's control.
```
Epic A (Payment Processing) ──→ [External: Stripe API v3]
                                 "Waiting on Stripe release"
```

### Cross-Team Dependencies
Another team must deliver something first.
```
[Platform Team: Epic A (API Gateway)] ──→ [Product Team: Epic B (Mobile App)]
```

### Organizational Dependencies
Approvals, legal review, compliance checks.
```
Epic A (Data Export) ──→ [Legal: Privacy Review]
                         ──→ [Security: Penetration Test]
```

---

## 2. Dependency Identification

### Questions to Surface Dependencies

For each epic/feature, ask:
1. Does this need an API/service that doesn't exist yet? → Technical dependency
2. Does this need another team to build or change something? → Cross-team
3. Does this need an external service, vendor, or partner? → External
4. Does this need a specific person who's also needed elsewhere? → Resource
5. Does this need approval, legal review, or compliance sign-off? → Organizational

### Dependency Matrix

A matrix showing which epics depend on which:

|  | E1 | E2 | E3 | E4 | E5 |
|--|----|----|----|----|-----|
| E1 | — | | ← | | |
| E2 | | — | | ← | |
| E3 | → | | — | | |
| E4 | | → | | — | ← |
| E5 | | | | → | — |

→ means "this row depends on this column"
← means "this column depends on this row"

### Dependency Register

| ID | From (Dependent) | To (Provider) | Type | Description | Status | Risk | Owner |
|----|-----------------|---------------|------|-------------|--------|------|-------|
| D1 | E3: Dashboard | E1: Auth API | Technical | Dashboard needs auth tokens | Green | Low | Alice |
| D2 | E4: Mobile App | E2: API Gateway | Cross-team | Mobile needs gateway endpoints | Amber | Medium | Bob |
| D3 | E5: Payments | Stripe API v3 | External | Need v3 for subscriptions | Red | High | Carol |

---

## 3. Dependency Visualization

### Directed Acyclic Graph (DAG)

The standard visualization for dependencies. Nodes are epics, edges are dependencies.

```
[E1: Auth API] ──→ [E3: Dashboard] ──→ [E5: Analytics]
                                    ↗
[E2: Data API] ──→ [E4: Reports] ──┘
```

### Critical Path

The longest chain of dependencies determines the minimum delivery time.

```
Critical Path: E1 → E3 → E5 (total: 8 + 5 + 3 = 16 sprints)
```

Any delay on the critical path delays the entire release.

### Visualization Best Practices
- Color-code by status: Green (on track), Amber (at risk), Red (blocked)
- Color-code by team to show cross-team dependencies
- Show direction with arrows (from dependent to provider)
- Highlight the critical path with a distinct color/thickness
- Flag circular dependencies as errors (A needs B, B needs A)

---

## 4. Managing Dependencies

### Dependency Resolution Strategies

| Strategy | When to Use | Example |
|----------|------------|---------|
| **Eliminate** | Can we remove the dependency? | Build the feature without the dependency |
| **Internalize** | Can we own both sides? | Move the dependent work to the providing team |
| **Decouple** | Can we use interfaces/contracts? | Define API contract, build in parallel with mocks |
| **Sequence** | Must one truly come first? | Plan the dependency first in the schedule |
| **Buffer** | How much slack do we need? | Add a sprint buffer between dependent items |

### Dependency Meetings

For programs with significant cross-team dependencies:

**Scrum of Scrums** (weekly, 30 min)
- One representative per team
- Focus: "What does your team need from other teams?"
- Track dependency status (Green/Amber/Red)
- Escalate blocked items

**Dependency Board Review** (bi-weekly, 45 min)
- Review the dependency graph/board
- Update statuses
- Identify new dependencies
- Coordinate timeline changes

### Dependency Risk Levels

| Level | Criteria | Action |
|-------|----------|--------|
| Green | Provider is on track, no blockers | Monitor weekly |
| Amber | Provider has risks or may slip | Daily coordination, create fallback plan |
| Red | Provider is blocked or significantly delayed | Escalate, activate contingency, consider descoping |

---

## 5. Cross-Team Coordination

### API Contract-First Development

When two teams are dependent on an API:
1. Define the API contract together (OpenAPI/Swagger spec)
2. Both teams agree on the contract before building
3. Consumer team builds against mocks that match the contract
4. Provider team implements the actual API
5. Integration testing when both sides are ready

This allows parallel development despite the dependency.

### Dependency SLAs

For recurring cross-team dependencies, establish SLAs:

| Dependency Type | SLA | Escalation |
|----------------|-----|------------|
| API endpoint request | 2 sprints from agreement | Team lead after 1 sprint |
| Data schema change | 1 sprint | Architect after 3 days |
| Infrastructure request | 1 sprint | DevOps lead after 3 days |
| Security review | 5 business days | Security lead after 3 days |
| Design review | 3 business days | Design lead after 2 days |

### Coordination Tools

| Tool | Use |
|------|-----|
| Dependency board (physical or digital) | Visual tracking |
| Shared Slack channel | Real-time coordination |
| Scrum of Scrums | Weekly sync |
| API contract repo | Technical contracts |
| Dependency register spreadsheet | Formal tracking |



---
