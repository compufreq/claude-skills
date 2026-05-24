# Flow Metrics Reference

## Table of Contents
1. Cycle Time
2. Lead Time
3. Throughput
4. WIP & WIP Age
5. Flow Efficiency
6. Cumulative Flow Diagram (CFD)
7. Using Flow Metrics Together

---

## 1. Cycle Time

### Definition
Time from when work actively begins (moved to "In Progress") to when it's delivered ("Done").

```
Cycle Time = Completed Date - Started Date (in business days)
```

### Statistical Measures

Always use percentiles, not averages. Cycle time distributions are typically right-skewed
(a few items take much longer than the rest).

| Measure | Formula | Use |
|---------|---------|-----|
| Median (50th %ile) | Middle value when sorted | "Typical" item delivery time |
| 85th Percentile | 85% of items finish within this | Service Level Expectation (SLE) |
| 95th Percentile | 95% of items finish within this | Worst-case planning |
| Mean (Average) | Sum / Count | Avoid for planning — distorted by outliers |

### Cycle Time Scatter Plot

Plot each completed item:
- X-axis: Completion date
- Y-axis: Cycle time (days)
- Add horizontal lines for 50th, 85th, 95th percentiles

Insights:
- Dots clustering near the median = predictable
- Dots scattered widely = unpredictable
- Dots trending upward over time = slowing down
- Outliers far above 95th = investigate specific blockers

### Cycle Time by Work Type

Track separately for different work types:

| Work Type | Median CT | 85th %ile CT | Count |
|-----------|-----------|-------------|-------|
| Feature | 4 days | 8 days | 12 |
| Bug Fix | 1 day | 3 days | 8 |
| Tech Debt | 3 days | 6 days | 5 |
| Spike | 2 days | 4 days | 3 |

---

## 2. Lead Time

### Definition
Time from when an item is created/requested to when it's delivered.

```
Lead Time = Completed Date - Created Date (in business days)
```

Lead Time = Queue Time + Cycle Time

### Lead Time vs Cycle Time

```
Timeline: |-- Queue Time --|-- Cycle Time --|
          Created    Started        Completed
          |_____ Lead Time ________________________|
```

- Lead Time includes waiting in the backlog
- Cycle Time only measures active work
- The gap between them reveals queue/wait time

### Service Level Expectations (SLEs)

Based on historical lead time data, set expectations:

```
"85% of [work type] items will be delivered within [X] business days."
```

Example SLE Table:

| Work Type | Priority | SLE (85th %ile) |
|-----------|----------|-----------------|
| Bug Fix | Critical | 1 day |
| Bug Fix | High | 3 days |
| Feature | Standard | 12 days |
| Tech Debt | Standard | 15 days |

---

## 3. Throughput

### Definition
Number of items completed per unit of time.

```
Weekly Throughput = Items completed in 1 week
Sprint Throughput = Items completed in 1 sprint
Monthly Throughput = Items completed in 1 month
```

### Throughput vs Velocity

| | Throughput | Velocity |
|--|-----------|----------|
| Unit | Item count | Story points |
| Use | Flow metrics, forecasting | Sprint planning |
| Best for | Kanban, Monte Carlo | Scrum commitment |

### Throughput Tracking Table

| Week | Features | Bugs | Tech Debt | Total | Running Avg (4wk) |
|------|----------|------|-----------|-------|--------------------|
| W1 | 3 | 2 | 1 | 6 | — |
| W2 | 4 | 1 | 0 | 5 | — |
| W3 | 2 | 3 | 2 | 7 | — |
| W4 | 3 | 2 | 1 | 6 | 6.0 |
| W5 | 5 | 1 | 1 | 7 | 6.25 |

### Throughput Run Chart

Plot weekly throughput over time:
- X-axis: Week number
- Y-axis: Items completed
- Add average line and ±1 standard deviation bands
- Points outside the bands indicate special cause variation

---

## 4. WIP & WIP Age

### Work in Progress (WIP)

```
Current WIP = Count of items in all "active" columns
             (In Progress + In Review + Testing, etc.)
```

### WIP Age

For each item currently in progress:
```
WIP Age = Today - Started Date (in business days)
```

### WIP Aging Chart

A scatter plot of current WIP items:
- X-axis: Workflow state (In Progress, In Review, Testing)
- Y-axis: WIP Age (days in current state)
- Horizontal lines: 50th, 85th, 95th percentile of historical cycle time

Items above the 85th percentile line are AT RISK.
Items above the 95th percentile line need IMMEDIATE attention.

### WIP Age Report Table

| Item ID | Title | State | Age (days) | 85th %ile CT | Status |
|---------|-------|-------|------------|-------------|--------|
| PROJ-101 | Login flow | In Progress | 3 | 8 | ✅ OK |
| PROJ-98 | Search API | In Review | 7 | 8 | ⚠️ Approaching |
| PROJ-92 | Reports | Testing | 12 | 8 | 🔴 At Risk |

---

## 5. Flow Efficiency

### Definition

```
Flow Efficiency = (Active Work Time / Total Lead Time) × 100%
```

Where:
- Active Work Time = Time spent actually working (hands on keyboard)
- Total Lead Time = End-to-end time including all waiting

### Industry Benchmarks

| Efficiency | Rating |
|------------|--------|
| < 5% | Very inefficient — mostly waiting |
| 5-15% | Typical for many organizations |
| 15-40% | Good — team has reasonable flow |
| > 40% | Excellent — highly optimized process |

### Improving Flow Efficiency

The biggest lever is reducing wait time, not working faster:

| Wait Type | Example | Improvement |
|-----------|---------|-------------|
| Queue time | Waiting in backlog for prioritization | More frequent replenishment |
| Handoff wait | Waiting for code review | Reduce WIP, prioritize reviews |
| External dependency | Waiting for another team | Decouple, plan ahead |
| Approval wait | Waiting for sign-off | Automate or delegate approvals |
| Environment wait | Waiting for test environment | Infrastructure automation |

---

## 6. Cumulative Flow Diagram (CFD)

### Construction

Data: Daily snapshot of item counts in each workflow state.

```
Date       | Backlog | Ready | In Progress | In Review | Testing | Done
2024-12-01 | 45      | 8     | 5           | 2         | 1       | 120
2024-12-02 | 44      | 7     | 6           | 2         | 1       | 121
2024-12-03 | 44      | 6     | 5           | 3         | 2       | 121
...
```

Visualization: Stacked area chart where each state is a band.
- Bottom band: Done (grows over time)
- Top band: Backlog (shrinks or grows)
- Middle bands: Active states

### Reading the CFD

**Band Width = Average WIP in that state**
- Wide "In Progress" band → too much WIP
- Narrow "In Review" band → reviews happening quickly

**Horizontal Distance = Approximate Lead Time**
- Measure horizontal gap between "In Progress" left edge and "Done" right edge
- Wider gap = longer lead time

**Band Behavior Patterns:**

| Pattern | Visual | Meaning | Action |
|---------|--------|---------|--------|
| Parallel, steady bands | ═══ | Smooth flow | Maintain current process |
| Widening band | /═══\ | Bottleneck forming | Reduce WIP, add capacity, or simplify |
| Narrowing band | \═══/ | Draining faster than filling | Check if upstream is starving |
| Flat top (Backlog) | ─── | No new items entering | Replenish the backlog |
| All bands converging | ╲╲╲ | Project completing | Expected near end of project |
| Stair-steps in Done | ┘┘┘ | Batch releases | Consider more continuous delivery |

### CFD Health Checks

Run these weekly:

1. **Is the Done band growing steadily?** → Team is delivering
2. **Is any middle band widening?** → Bottleneck — investigate that state
3. **Is the Backlog band stable?** → Work is entering and leaving at similar rates
4. **Are bands parallel?** → System is in steady state — predictable delivery

---

## 7. Using Flow Metrics Together

### The Four Flow Metrics (Actionable Agile)

Daniel Vacanti's four key metrics work together:

1. **WIP** — How much is in flight right now?
2. **Throughput** — How many items do we finish per time period?
3. **Cycle Time** — How long does each item take?
4. **WIP Age** — How long have current items been in progress?

### Little's Law

```
Average Cycle Time = Average WIP / Average Throughput
```

This means:
- To reduce cycle time → reduce WIP (easiest lever)
- To increase throughput → reduce WIP or reduce cycle time
- WIP is the primary control — it affects both other metrics

### Diagnostic Framework

| Observation | Root Cause | Recommendation |
|-------------|-----------|----------------|
| High cycle time, high WIP | Too much work in progress | Lower WIP limits |
| High cycle time, low WIP | Blockers or external dependencies | Address blockers, improve handoffs |
| Low throughput, high WIP | Context switching, multitasking | Stricter WIP limits, focus |
| Low throughput, low WIP | Insufficient work entering system | Replenish backlog, check team capacity |
| Increasing lead time, stable cycle time | Queue time growing | More frequent prioritization/replenishment |
| Erratic throughput | Special cause variation | Investigate specific weeks for events |



---
