---
name: agile-metrics-tracker
description: >-
  Agile metrics, velocity tracking, flow metrics, and forecasting for Scrum and Kanban teams. Use when the user mentions velocity, burndown, burnup, cycle time, lead time, throughput, cumulative flow diagram, CFD, sprint metrics, flow efficiency, Monte Carlo forecasting, predictability, WIP aging, or asks to track, measure, or forecast Agile team performance.
---

# Agile Metrics Tracker

A production-grade skill for Agile performance measurement, visualization, and forecasting.
Produces interactive dashboards, Excel reports, and markdown summaries with Monte Carlo
predictive analytics.

## Quick Reference

| Metric Category | Key Metrics | Best For |
|-----------------|-------------|----------|
| Scrum Metrics | Velocity, burndown, burnup, commitment reliability | Sprint-based teams |
| Flow Metrics | Cycle time, lead time, throughput, WIP age | Kanban / continuous flow |
| Predictive | Monte Carlo, trend projection, confidence intervals | Release planning |
| Flow Visualization | Cumulative Flow Diagram (CFD) | Bottleneck identification |

## Output Formats

| Format | Use Case | Script |
|--------|----------|--------|
| Interactive HTML Dashboard | Team standups, stakeholder reviews | `scripts/generate_dashboard.py` |
| Excel Spreadsheet | Data analysis, offline tracking | `scripts/generate_metrics_xlsx.py` |
| Markdown Report | Sprint reviews, async communication | Generated inline |
| Monte Carlo Forecast | Release planning, "when will we finish" | `scripts/monte_carlo.py` |

## Core Workflow

1. **Identify what the user needs** — metrics report, dashboard, forecast, or analysis?
2. **Gather historical data** — sprint history, item-level flow data, or backlog size
3. **Read the relevant reference:**
   - Scrum metrics → `references/scrum-metrics.md`
   - Flow metrics → `references/flow-metrics.md`
   - Forecasting → `references/forecasting.md`
4. **Generate output** using the appropriate script or inline markdown

---

## Metric Definitions

### Scrum Metrics

**Velocity**
- Definition: Story points completed per sprint
- Calculation: Sum of story points for all items meeting Definition of Done
- Tracking: 3-sprint rolling average for planning, full history for trends
- Healthy signal: Low variance (±20% from average)

**Burndown Chart**
- Definition: Remaining work (story points) over time within a sprint
- Ideal line: Linear decrease from total committed to zero
- Actual line: Updated daily based on completed work
- Healthy signal: Actual line tracks near or below ideal line

**Burnup Chart**
- Definition: Cumulative work completed vs total scope over time
- Two lines: Scope line (total) and Done line (completed)
- Advantage over burndown: Shows scope changes explicitly
- Healthy signal: Done line converges toward scope line; scope line is stable

**Commitment Reliability**
- Definition: Percentage of sprints where the team completed all committed stories
- Calculation: (Sprints with 100% completion / Total sprints) × 100
- Target: ≥ 80% reliability indicates mature estimation
- Alternative: (Completed points / Committed points) × 100 per sprint

### Flow Metrics

**Lead Time**
- Definition: Time from item creation (or request) to delivery (Done)
- Includes: Wait time + active work time
- Track: Median and 85th percentile (not average — skewed by outliers)
- Healthy signal: Stable or decreasing over time

**Cycle Time**
- Definition: Time from work started (In Progress) to delivery (Done)
- Excludes: Queue/wait time before work begins
- Track: Median and 85th percentile
- Healthy signal: Low variance, consistent delivery pace

**Throughput**
- Definition: Number of items completed per unit of time (week, sprint, month)
- Track: By item type (feature, bug, tech debt) for richer insights
- Healthy signal: Stable or increasing without quality degradation

**WIP Age**
- Definition: How long current in-progress items have been in progress
- Alert threshold: Items exceeding 85th percentile historical cycle time
- Action: Swarm, split, or escalate aging items

**Flow Efficiency**
- Definition: (Active work time / Total lead time) × 100
- Typical range: 15-40% for most teams (lots of wait time)
- Target: Improvement over time, not a specific number

### Cumulative Flow Diagram (CFD)

- Definition: Stacked area chart showing item count in each workflow state over time
- X-axis: Time (days or weeks)
- Y-axis: Number of items
- Bands: One per workflow state (Backlog, Ready, In Progress, Review, Done)
- Insights:
  - Band width = average WIP in that state
  - Horizontal distance between bands = approximate lead time
  - Flat top band = no new items entering (starvation)
  - Widening band = bottleneck (items accumulating)
  - Parallel bands = smooth, stable flow

---

## Data Input Format

All scripts accept JSON data. Here's the unified schema:

```json
{
  "team_name": "Alpha Squad",
  "sprints": [
    {
      "number": 11,
      "start_date": "2024-12-02",
      "end_date": "2024-12-13",
      "committed_points": 34,
      "completed_points": 30,
      "stories_committed": 8,
      "stories_completed": 7,
      "bugs_found": 2,
      "bugs_fixed": 1
    }
  ],
  "items": [
    {
      "id": "PROJ-101",
      "type": "feature",
      "title": "Email login",
      "created_date": "2024-11-20",
      "started_date": "2024-12-03",
      "completed_date": "2024-12-06",
      "story_points": 5,
      "status": "Done"
    }
  ],
  "flow_snapshots": [
    {
      "date": "2024-12-02",
      "backlog": 45,
      "ready": 8,
      "in_progress": 5,
      "in_review": 2,
      "testing": 1,
      "done": 120
    }
  ],
  "remaining_backlog_points": 150,
  "target_date": "2025-03-31"
}
```

- `sprints`: Required for Scrum metrics (velocity, burndown)
- `items`: Required for flow metrics (cycle time, lead time, throughput)
- `flow_snapshots`: Required for CFD generation
- `remaining_backlog_points` + `target_date`: Required for Monte Carlo forecasting

---

## Sprint Report Template (Markdown)

When generating a markdown sprint report, use this structure:

```
# Sprint [N] Metrics Report — [Team Name]
**Period:** [Start] — [End]

## Sprint Summary
| Metric | Value | Trend |
|--------|-------|-------|
| Velocity | [X] points | [↑↓→] vs avg |
| Commitment | [X/Y] stories ([Z]%) | [↑↓→] |
| Points Committed vs Completed | [X] / [Y] | [↑↓→] |
| Bugs Found / Fixed | [X] / [Y] | [↑↓→] |
| Sprint Goal | [Achieved/Partial/Missed] | — |

## Velocity Trend (Last 6 Sprints)
[Table with sprint numbers, committed, completed, rolling avg]

## Cycle Time Summary
| Metric | Value |
|--------|-------|
| Median Cycle Time | [X] days |
| 85th Percentile | [X] days |
| Fastest Item | [X] days |
| Slowest Item | [X] days |

## Flow Health
- Items in Progress: [N] (WIP limit: [N])
- Aging Items (above 85th %ile): [list]
- Throughput this sprint: [N] items

## Forecast
- Remaining backlog: [N] points
- At current velocity: [X] sprints to complete
- Monte Carlo 85% confidence: [Date]

## Observations & Recommendations
1. [Insight based on data]
2. [Recommendation]
```

---

## Scripts Reference

### generate_dashboard.py
Interactive HTML dashboard with Chart.js. Includes velocity chart, burndown, cycle time
distribution, throughput trend, and CFD. All charts are interactive with tooltips and legends.

### generate_metrics_xlsx.py
Multi-sheet Excel workbook with: Velocity History, Cycle Time Data, Throughput Tracking,
CFD Data, and a Summary Dashboard sheet with charts.

### monte_carlo.py
Monte Carlo simulation for delivery forecasting. Uses historical throughput data to simulate
thousands of possible outcomes and provides probability-based delivery date ranges.

---

## Best Practices

1. Track metrics to learn and improve, never to punish
2. Use median over average for cycle time and lead time (less sensitive to outliers)
3. Need at least 5-6 sprints of data before velocity is reliable for forecasting
4. Present trends, not single data points — one sprint is noise, six sprints is a signal
5. CFDs should be reviewed weekly — they surface bottlenecks before they become crises
6. Monte Carlo forecasts should always present ranges, never single dates
7. Compare the team to its own past, never to other teams
8. When metrics conflict with team sentiment, investigate — the team may know something the numbers don't



---
