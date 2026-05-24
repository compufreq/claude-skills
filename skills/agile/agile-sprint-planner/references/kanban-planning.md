# Kanban Planning Reference

## Table of Contents
1. Kanban Fundamentals
2. Board Design
3. WIP Limits
4. Flow Metrics
5. Cadences
6. Policies & Service Level Expectations

---

## 1. Kanban Fundamentals

Kanban is a flow-based method that focuses on continuous delivery rather than time-boxed sprints.
The core principles are:

1. **Visualize the workflow** — Make all work visible on a board
2. **Limit Work in Progress (WIP)** — Reduce context switching, increase throughput
3. **Manage flow** — Optimize for smooth, predictable delivery
4. **Make policies explicit** — Everyone knows the rules
5. **Implement feedback loops** — Regular cadences for inspection
6. **Improve collaboratively** — Evolve the process incrementally

---

## 2. Board Design

### Default Column Structure

```
┌──────────┬───────┬─────────────┬───────────┬─────────┬──────┐
│ Backlog  │ Ready │ In Progress │ In Review │ Testing │ Done │
│          │       │ WIP: 4      │ WIP: 2    │ WIP: 2  │      │
└──────────┴───────┴─────────────┴───────────┴─────────┴──────┘
```

### Column Definitions

| Column | Purpose | Entry Criteria | Exit Criteria |
|--------|---------|---------------|---------------|
| Backlog | Unrefined ideas, requests | Any new item | Refined with acceptance criteria |
| Ready | Refined, estimated, ready to pull | Meets Definition of Ready | Developer pulls the item |
| In Progress | Actively being worked on | Developer has started | Code complete, PR opened |
| In Review | Code review in progress | PR submitted | Approved, no blocking comments |
| Testing | QA verification | Code merged to staging | All acceptance criteria verified |
| Done | Delivered to production | Deployed and verified | N/A |

### Swimlane Configurations

**By Priority:**
```
┌─────────────────────────────────────────────────┐
│ Expedite (WIP: 1)          │ For production issues │
├─────────────────────────────────────────────────┤
│ Standard                   │ Normal priority work   │
├─────────────────────────────────────────────────┤
│ Low Priority / Nice-to-have│ When capacity allows   │
└─────────────────────────────────────────────────┘
```

**By Work Type:**
```
┌─────────────────────────────────────────────────┐
│ Features          │ User-facing functionality     │
├─────────────────────────────────────────────────┤
│ Bugs              │ Defect fixes                  │
├─────────────────────────────────────────────────┤
│ Tech Debt         │ Refactoring, upgrades         │
├─────────────────────────────────────────────────┤
│ Ops / Maintenance │ Infrastructure, monitoring    │
└─────────────────────────────────────────────────┘
```

### Blocked Items Policy
- Blocked items get a red flag/tag and a note explaining the blocker
- Blocked items do NOT count against WIP limits (they're waiting, not being worked)
- If an item is blocked for > 2 days, escalate to team lead
- If blocked for > 5 days, escalate to management
- Daily standup should surface all blocked items

---

## 3. WIP Limits

WIP limits are the most important Kanban practice. They prevent overloading and improve flow.

### Setting Initial WIP Limits

**Formula:** `WIP Limit = Team Members working in column ÷ 2 (rounded up), minimum 1`

For a team of 6 developers:
- In Progress: 4 (allows pairing and some parallel work)
- In Review: 2 (encourages quick reviews)
- Testing: 2 (prevents QA bottleneck)

### WIP Limit Guidelines
- Start with limits that feel slightly uncomfortable — they should create tension
- If the team never hits the limit, it's too high
- If work is constantly blocked by limits, they may be too low
- Adjust in small increments (±1) after 2-4 weeks of data
- The Expedite swimlane should have WIP limit of 1 — only one emergency at a time

### Signs WIP Limits Are Working
- Lead time is decreasing or stable
- Team members help each other more (swarming on stuck items)
- Less context switching
- More predictable delivery

### Signs WIP Limits Need Adjustment
- Items aging in columns without progress → limits may be too high
- Developers idle because of limits → limits may be too low or there's a process issue
- Constant "emergency" bypasses → the process isn't trusted

---

## 4. Flow Metrics

### Lead Time
Time from when a request enters the board (Backlog) to when it's Done.
- Track the median, not the average (less affected by outliers)
- Use percentiles: "85% of items complete in ≤ X days"

### Cycle Time
Time from when work begins (In Progress) to when it's Done.
- This is the team's primary controllable metric
- Target: consistent cycle time with low variance

### Throughput
Number of items completed per unit of time (week or month).
- Track by work type (features vs bugs vs tech debt)
- Use for forecasting: "At current throughput, we'll finish the backlog in X weeks"

### Cumulative Flow Diagram (CFD)
Visualizes the quantity of items in each workflow state over time.
- Flat bands = smooth flow
- Widening bands = bottleneck (WIP accumulating)
- Narrowing bands = items draining faster than entering

### Aging Work in Progress
Items currently in progress, plotted by how long they've been in progress.
- Items above the 85th percentile cycle time → at risk, needs attention
- Helps identify stuck items before they become chronic blockers

---

## 5. Cadences

Kanban uses regular meetings (cadences) instead of sprint ceremonies:

### Daily Standup (15 min)
- Walk the board right-to-left (focus on finishing, not starting)
- Focus on blocked items and aging work
- Not a status report — focus on flow

### Replenishment Meeting (weekly, 30 min)
- Pull new items from Backlog to Ready
- Ensure Ready column has enough items for the team
- Prioritize incoming requests
- Equivalent to Scrum's backlog refinement

### Delivery Planning (bi-weekly, 1 hour)
- Review what was delivered since last meeting
- Discuss upcoming delivery commitments
- Coordinate with stakeholders on expectations
- Set Service Level Expectations for new work

### Service Delivery Review (monthly, 1 hour)
- Review flow metrics (lead time, cycle time, throughput)
- Identify bottlenecks and improvement opportunities
- Adjust WIP limits, policies, or board structure
- Equivalent to Scrum's retrospective + review combined

---

## 6. Policies & Service Level Expectations (SLEs)

### Service Level Expectations
SLEs are forecasts, not commitments. They communicate expected delivery timelines.

| Work Type | Priority | SLE (85th percentile) |
|-----------|----------|-----------------------|
| Bug Fix | Critical | 1 business day |
| Bug Fix | High | 3 business days |
| Bug Fix | Medium | 5 business days |
| Feature | High | 10 business days |
| Feature | Standard | 15 business days |
| Tech Debt | Standard | 20 business days |

### Pull Policies
- Team members pull work (never push/assign)
- Pull from the rightmost column first (finish before starting)
- When pulling new work, consider: priority, aging, skill match
- If at WIP limit, help a colleague finish before starting new work

### Escalation Policies
- Item exceeds SLE → Notify team lead
- Item exceeds 1.5× SLE → Notify product owner
- Item exceeds 2× SLE → Management escalation + root cause analysis



---
