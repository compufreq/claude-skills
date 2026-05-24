# Scrum Metrics Reference

## Table of Contents
1. Velocity Deep Dive
2. Burndown Charts
3. Burnup Charts
4. Commitment Reliability
5. Sprint Predictability
6. Interpreting Scrum Metrics

---

## 1. Velocity Deep Dive

### Calculating Velocity

```
Sprint Velocity = Σ(story points of items that meet Definition of Done)
```

Rules:
- Only count items that are FULLY Done (meet DoD)
- Partially completed items count ZERO — they carry over
- Bug fixes and tech debt count if they were estimated and on the board
- Don't count items completed but not planned (unless team practice includes this)

### Rolling Average

```
Rolling Average (3-sprint) = (V[n] + V[n-1] + V[n-2]) / 3
Rolling Average (5-sprint) = (V[n] + V[n-1] + ... + V[n-4]) / 5
```

Use 3-sprint for planning (responsive to recent changes).
Use 5-sprint for forecasting (smooths out noise).

### Velocity Range

```
Velocity Range = [Min(last 5 sprints), Max(last 5 sprints)]
Velocity Variance = (Max - Min) / Average × 100%
```

| Variance | Interpretation | Action |
|----------|---------------|--------|
| < 15% | Highly predictable | Trust velocity for planning |
| 15-25% | Normal variance | Use rolling average + buffer |
| 25-40% | Unstable | Investigate causes, use pessimistic estimates |
| > 40% | Unpredictable | Velocity is unreliable — fix root causes first |

### Velocity Influencing Factors

When velocity changes significantly, check these factors before concluding the team
is faster/slower:

| Factor | Impact |
|--------|--------|
| Team composition change | +/- 1 dev ≈ 10-20% velocity change |
| Estimation recalibration | Team may be sizing differently |
| Scope complexity shift | New domain, new tech = slower |
| Technical debt payoff | May increase future velocity |
| Reduced PTO/holidays | More available days = higher velocity |
| Process improvement | Genuine throughput increase |

### Velocity Anti-Patterns

- **Velocity as a performance metric**: Pressures inflation, destroys trust
- **Comparing velocity across teams**: Points are relative, not absolute
- **Velocity without quality**: Fast delivery of buggy code isn't fast
- **Demanding velocity increase**: Leads to gaming, not improvement
- **Sprint 1 velocity projection**: Need 3-5 sprints for reliable baseline

---

## 2. Burndown Charts

### Construction

```
X-axis: Sprint day (0 to N, where N = sprint days)
Y-axis: Story points remaining

Ideal Line: Straight line from (0, total_points) to (N, 0)
Actual Line: Updated daily: total_points - cumulative_completed
```

### Daily Update Process
1. At end of each day, sum points of all stories moved to Done
2. Remaining = Total committed - Cumulative completed
3. Plot the actual point for that day

### Reading Burndown Patterns

**Healthy Patterns:**
```
Actual line tracks close to ideal line
↘ Smooth, consistent descent
```

**Warning Patterns:**

| Pattern | Shape | Meaning | Action |
|---------|-------|---------|--------|
| Flat start | ▬▬▬↘ | No stories completing early | Check if stories are too large |
| Cliff | ▬▬▬▬↓ | Everything finishes last day | Team may be batch-completing, not incrementally delivering |
| Staircase | ┐┐┐┐ | Stories complete in bursts | Normal for some teams, but check WIP limits |
| Above ideal | Actual above ideal line | Behind schedule | Swarm on nearly-done items, reduce scope, or flag risk |
| Scope creep | Line goes UP | New work added mid-sprint | Sprint commitment isn't being protected |

### Burndown Data Table

| Sprint Day | Date | Ideal Remaining | Actual Remaining | Delta |
|-----------|------|-----------------|------------------|-------|
| 0 | [start] | [total] | [total] | 0 |
| 1 | [+1d] | [total - daily_ideal] | [actual] | [diff] |
| ... | ... | ... | ... | ... |

---

## 3. Burnup Charts

### Why Burnup Over Burndown

Burnup charts show TWO lines:
1. **Scope line** (top): Total work committed
2. **Done line** (bottom): Cumulative work completed

Advantage: Burnup explicitly shows scope changes. If the scope line moves up, you can
see new work was added. Burndown hides this — remaining work goes up, but you can't tell
if it's because new work was added or completed work was reverted.

### Construction

```
X-axis: Sprint day (or sprint number for multi-sprint burnup)
Y-axis: Story points

Scope Line: Total committed points (may change if stories added/removed)
Done Line: Cumulative completed points (only goes up or stays flat)
```

### Multi-Sprint Burnup (Release Burnup)

For tracking progress toward a release:

```
X-axis: Sprint number (Sprint 1, 2, 3, ...)
Y-axis: Story points

Scope Line: Total release backlog size (may grow as items are discovered)
Done Line: Cumulative points completed across all sprints
```

When Done line meets Scope line → release is complete.
If Scope line keeps growing faster than Done line → release date is at risk.

### Reading Burnup Patterns

| Pattern | Meaning |
|---------|---------|
| Lines converging | On track — completing faster than scope grows |
| Lines parallel | Scope and velocity match — check if target date is met |
| Lines diverging | Scope growing faster than delivery — release at risk |
| Scope line flat, done line rising | Ideal — fixed scope, steady delivery |
| Scope line stepping up | Scope additions — investigate if planned or creep |

---

## 4. Commitment Reliability

### Sprint-Level Reliability

```
Sprint Reliability = (Completed Points / Committed Points) × 100

OR (stricter):
Sprint Pass/Fail = 1 if ALL committed stories completed, else 0
Team Reliability Rate = (Passing Sprints / Total Sprints) × 100
```

### Tracking Table

| Sprint | Committed | Completed | % | Pass? |
|--------|-----------|-----------|---|-------|
| Sprint 11 | 34 | 30 | 88% | No |
| Sprint 12 | 32 | 33 | 103% | Yes |
| Sprint 13 | 35 | 31 | 89% | No |

### Interpreting Reliability

| Rate | Interpretation |
|------|---------------|
| > 95% | May be under-committing — try stretching |
| 80-95% | Healthy — good estimation maturity |
| 60-80% | Needs improvement — investigate causes |
| < 60% | Systemic issue — stories too large, too many unknowns, or external disruptions |

---

## 5. Sprint Predictability

### Predictability Score

Measures how consistent velocity is over time:

```
Standard Deviation = √(Σ(Vi - Vavg)² / (n-1))
Coefficient of Variation (CV) = (Std Dev / Average Velocity) × 100
Predictability Score = 100 - CV (higher = more predictable)
```

| Score | Rating |
|-------|--------|
| > 85 | Excellent predictability |
| 70-85 | Good — reliable for planning |
| 55-70 | Fair — use ranges, not point estimates |
| < 55 | Poor — focus on stabilization before forecasting |

---

## 6. Interpreting Scrum Metrics

### Healthy Team Signals
- Velocity variance < 20% over 5 sprints
- Commitment reliability > 80%
- Burndown tracks near ideal line
- Burnup shows converging scope and done lines
- No chronic scope creep (scope additions < 10% per sprint)

### Red Flags
- Velocity increasing but bugs also increasing → quality being sacrificed
- Velocity stable but team morale declining → unsustainable pace
- Perfect commitment every sprint → team may be sandbagging
- Velocity spikes after management pressure → gaming likely
- Stories frequently carry over → stories too large or scope unclear

### Metric Combinations for Diagnosis

| Symptom | Check These Metrics | Likely Cause |
|---------|-------------------|--------------|
| Missed commitments | Velocity variance, story size distribution | Estimation problems or stories too large |
| Slow delivery | Cycle time, WIP count, flow efficiency | Too much WIP, bottlenecks |
| Quality issues | Bug rate, velocity/bug correlation | Rushing to hit velocity targets |
| Unpredictable delivery | Predictability score, scope changes | Scope creep, external interruptions |



---

<!-- Script: scripts/generate_dashboard.py -->

# Script: generate_dashboard.py

```python
#!/usr/bin/env python3
"""
Generate an interactive HTML Agile metrics dashboard with Chart.js.

Includes: Velocity trend, burndown, cycle time distribution, throughput, and CFD.

Usage:
    python generate_dashboard.py --config metrics_data.json --output dashboard.html
"""

import json
import sys
import argparse
from datetime import datetime, timedelta
import math


def compute_cycle_times(items):
    """Calculate cycle times from item data."""
    cycle_times = []
    for item in items:
        if item.get("started_date") and item.get("completed_date"):
            start = datetime.strptime(item["started_date"], "%Y-%m-%d")
            end = datetime.strptime(item["completed_date"], "%Y-%m-%d")
            days = (end - start).days
            if days >= 0:
                cycle_times.append({
                    "id": item.get("id", ""),
                    "title": item.get("title", ""),
                    "type": item.get("type", "feature"),
                    "days": days,
                    "completed": item["completed_date"],
                })
    return cycle_times


def compute_lead_times(items):
    """Calculate lead times from item data."""
    lead_times = []
    for item in items:
        if item.get("created_date") and item.get("completed_date"):
            created = datetime.strptime(item["created_date"], "%Y-%m-%d")
            completed = datetime.strptime(item["completed_date"], "%Y-%m-%d")
            days = (completed - created).days
            if days >= 0:
                lead_times.append(days)
    return sorted(lead_times)


def percentile(sorted_data, pct):
    if not sorted_data:
        return 0
    idx = int(len(sorted_data) * pct / 100)
    return sorted_data[min(idx, len(sorted_data) - 1)]


def generate_dashboard(config, output_path):
    team = config.get("team_name", "Team")
    sprints = config.get("sprints", [])
    items = config.get("items", [])
    flow_snapshots = config.get("flow_snapshots", [])

    # Velocity data
    sprint_labels = [f"Sprint {s.get('number', i+1)}" for i, s in enumerate(sprints)]
    committed = [s.get("committed_points", 0) for s in sprints]
    completed = [s.get("completed_points", 0) for s in sprints]
    avg_velocity = sum(completed) / len(completed) if completed else 0

    # Rolling average (3-sprint)
    rolling_avg = []
    for i in range(len(completed)):
        if i >= 2:
            rolling_avg.append(round(sum(completed[i-2:i+1]) / 3, 1))
        else:
            rolling_avg.append(None)

    # Cycle time data
    ct_data = compute_cycle_times(items)
    ct_values = sorted([c["days"] for c in ct_data])
    ct_median = percentile(ct_values, 50) if ct_values else 0
    ct_85 = percentile(ct_values, 85) if ct_values else 0
    ct_95 = percentile(ct_values, 95) if ct_values else 0

    # Cycle time histogram
    if ct_values:
        max_ct = max(ct_values)
        ct_bins = list(range(0, max_ct + 2))
        ct_hist = [ct_values.count(d) for d in ct_bins]
    else:
        ct_bins, ct_hist = [], []

    # Lead time
    lt_values = compute_lead_times(items)
    lt_median = percentile(lt_values, 50) if lt_values else 0
    lt_85 = percentile(lt_values, 85) if lt_values else 0

    # Throughput (weekly from items)
    throughput_data = []
    if items:
        completed_items = [i for i in items if i.get("completed_date")]
        if completed_items:
            completed_items.sort(key=lambda x: x["completed_date"])
            start = datetime.strptime(completed_items[0]["completed_date"], "%Y-%m-%d")
            end = datetime.strptime(completed_items[-1]["completed_date"], "%Y-%m-%d")
            weeks = max(1, (end - start).days // 7 + 1)
            for w in range(weeks):
                w_start = start + timedelta(weeks=w)
                w_end = w_start + timedelta(days=7)
                count = sum(1 for i in completed_items
                            if w_start <= datetime.strptime(i["completed_date"], "%Y-%m-%d") < w_end)
                throughput_data.append({"week": f"W{w+1}", "count": count})

    tp_labels = [t["week"] for t in throughput_data]
    tp_values = [t["count"] for t in throughput_data]
    avg_tp = sum(tp_values) / len(tp_values) if tp_values else 0

    # CFD data
    cfd_dates = [s.get("date", "") for s in flow_snapshots]
    cfd_states = ["done", "testing", "in_review", "in_progress", "ready", "backlog"]
    cfd_colors = ["#4CAF50", "#00BCD4", "#9C27B0", "#FF9800", "#2196F3", "#78909C"]
    cfd_datasets = []
    for state, color in zip(cfd_states, cfd_colors):
        data = [s.get(state, 0) for s in flow_snapshots]
        cfd_datasets.append({"label": state.replace("_", " ").title(), "data": data, "color": color})

    # Pre-compute CFD datasets JSON for chart
    cfd_datasets_json = json.dumps([
        {"label": d["label"], "data": d["data"], "borderColor": d["color"],
         "backgroundColor": d["color"] + "33", "fill": True, "tension": 0.2, "pointRadius": 0}
        for d in cfd_datasets
    ])

    # Commitment reliability
    reliability_data = []
    for s in sprints:
        c = s.get("committed_points", 1)
        d = s.get("completed_points", 0)
        pct = round(d / c * 100, 1) if c > 0 else 0
        reliability_data.append(pct)
    avg_reliability = sum(reliability_data) / len(reliability_data) if reliability_data else 0

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agile Dashboard — {team}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0f0f23;
            color: #eee;
            padding: 1.5rem;
        }}
        h1 {{ color: #e94560; font-size: 1.4rem; margin-bottom: 0.3rem; }}
        .subtitle {{ color: #888; font-size: 0.85rem; margin-bottom: 1.5rem; }}
        .kpi-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        .kpi {{
            background: #1a1a2e;
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
            border: 1px solid #333;
        }}
        .kpi .value {{ font-size: 1.6rem; font-weight: 700; color: #e94560; }}
        .kpi .label {{ font-size: 0.75rem; color: #888; margin-top: 0.2rem; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; }}
        .card {{
            background: #1a1a2e;
            border-radius: 12px;
            padding: 1.25rem;
            border: 1px solid #333;
        }}
        .card h3 {{ color: #e94560; margin-bottom: 0.75rem; font-size: 0.95rem; }}
        .chart-container {{ position: relative; height: 260px; }}
        .full-width {{ grid-column: 1 / -1; }}
        @media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <h1>📊 Agile Metrics Dashboard — {team}</h1>
    <div class="subtitle">Generated {datetime.now().strftime("%B %d, %Y")} | {len(sprints)} sprints | {len(items)} items tracked</div>

    <div class="kpi-row">
        <div class="kpi"><div class="value">{avg_velocity:.1f}</div><div class="label">Avg Velocity</div></div>
        <div class="kpi"><div class="value">{ct_median}d</div><div class="label">Median Cycle Time</div></div>
        <div class="kpi"><div class="value">{ct_85}d</div><div class="label">85th %ile CT</div></div>
        <div class="kpi"><div class="value">{lt_median}d</div><div class="label">Median Lead Time</div></div>
        <div class="kpi"><div class="value">{avg_tp:.1f}</div><div class="label">Avg Throughput/Wk</div></div>
        <div class="kpi"><div class="value">{avg_reliability:.0f}%</div><div class="label">Commitment Reliability</div></div>
    </div>

    <div class="grid">
        <div class="card">
            <h3>📈 Velocity Trend</h3>
            <div class="chart-container"><canvas id="velocityChart"></canvas></div>
        </div>
        <div class="card">
            <h3>⏱️ Cycle Time Distribution</h3>
            <div class="chart-container"><canvas id="cycleTimeChart"></canvas></div>
        </div>
        <div class="card">
            <h3>🔄 Weekly Throughput</h3>
            <div class="chart-container"><canvas id="throughputChart"></canvas></div>
        </div>
        <div class="card">
            <h3>✅ Commitment Reliability</h3>
            <div class="chart-container"><canvas id="reliabilityChart"></canvas></div>
        </div>
        {"" if not flow_snapshots else '''
        <div class="card full-width">
            <h3>📊 Cumulative Flow Diagram</h3>
            <div class="chart-container" style="height:320px"><canvas id="cfdChart"></canvas></div>
        </div>
        '''}
    </div>

<script>
const chartDefaults = {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{ legend: {{ labels: {{ color: '#aaa', font: {{ size: 11 }} }} }} }},
    scales: {{
        y: {{ beginAtZero: true, ticks: {{ color: '#888' }}, grid: {{ color: '#222' }} }},
        x: {{ ticks: {{ color: '#888' }}, grid: {{ color: '#222' }} }}
    }}
}};

// Velocity
new Chart(document.getElementById('velocityChart'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(sprint_labels)},
        datasets: [
            {{ label: 'Committed', data: {json.dumps(committed)}, backgroundColor: 'rgba(33,150,243,0.4)', borderColor: '#2196F3', borderWidth: 1 }},
            {{ label: 'Completed', data: {json.dumps(completed)}, backgroundColor: 'rgba(233,69,96,0.6)', borderColor: '#e94560', borderWidth: 1 }},
            {{ label: '3-Sprint Avg', data: {json.dumps(rolling_avg)}, type: 'line', borderColor: '#4CAF50', borderDash: [5,5], pointRadius: 3, fill: false }}
        ]
    }},
    options: chartDefaults
}});

// Cycle Time
new Chart(document.getElementById('cycleTimeChart'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(ct_bins)},
        datasets: [{{
            label: 'Items',
            data: {json.dumps(ct_hist)},
            backgroundColor: 'rgba(233,69,96,0.5)',
            borderColor: '#e94560',
            borderWidth: 1
        }}]
    }},
    options: {{
        ...chartDefaults,
        plugins: {{
            ...chartDefaults.plugins,
            annotation: undefined
        }},
        scales: {{
            ...chartDefaults.scales,
            x: {{ ...chartDefaults.scales.x, title: {{ display: true, text: 'Days', color: '#888' }} }}
        }}
    }}
}});

// Throughput
new Chart(document.getElementById('throughputChart'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(tp_labels)},
        datasets: [
            {{ label: 'Items/Week', data: {json.dumps(tp_values)}, backgroundColor: 'rgba(233,69,96,0.5)', borderColor: '#e94560', borderWidth: 1 }},
            {{ label: 'Average', data: Array({len(tp_values)}).fill({avg_tp:.1f}), type: 'line', borderColor: '#4CAF50', borderDash: [5,5], pointRadius: 0, fill: false }}
        ]
    }},
    options: chartDefaults
}});

// Reliability
new Chart(document.getElementById('reliabilityChart'), {{
    type: 'line',
    data: {{
        labels: {json.dumps(sprint_labels)},
        datasets: [
            {{ label: 'Commitment %', data: {json.dumps(reliability_data)}, borderColor: '#e94560', backgroundColor: 'rgba(233,69,96,0.1)', fill: true, tension: 0.2 }},
            {{ label: '80% Target', data: Array({len(sprints)}).fill(80), borderColor: '#4CAF50', borderDash: [5,5], pointRadius: 0, fill: false }}
        ]
    }},
    options: {{ ...chartDefaults, scales: {{ ...chartDefaults.scales, y: {{ ...chartDefaults.scales.y, max: 120 }} }} }}
}});

// CFD
{"" if not flow_snapshots else f"""
new Chart(document.getElementById('cfdChart'), {{
    type: 'line',
    data: {{
        labels: {json.dumps(cfd_dates)},
        datasets: {cfd_datasets_json}
    }},
    options: {{
        ...chartDefaults,
        plugins: {{ ...chartDefaults.plugins, filler: {{ propagate: true }} }},
        scales: {{
            ...chartDefaults.scales,
            y: {{ ...chartDefaults.scales.y, stacked: true }},
            x: {{ ...chartDefaults.scales.x, ticks: {{ ...chartDefaults.scales.x.ticks, maxTicksLimit: 15 }} }}
        }}
    }}
}});
"""}
</script>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)
    print(f"Dashboard saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate Agile Metrics Dashboard")
    parser.add_argument("--config", help="Path to JSON config")
    parser.add_argument("--output", default="dashboard.html")
    args = parser.parse_args()

    if args.config:
        with open(args.config, "r") as f:
            config = json.load(f)
    else:
        config = json.load(sys.stdin)

    generate_dashboard(config, args.output)


if __name__ == "__main__":
    main()

```


---

<!-- Script: scripts/generate_metrics_xlsx.py -->

# Script: generate_metrics_xlsx.py

```python
#!/usr/bin/env python3
"""
Generate a multi-sheet Agile metrics Excel workbook.

Sheets: Summary, Velocity History, Cycle Time Data, Throughput, CFD Data

Usage:
    python generate_metrics_xlsx.py --config metrics_data.json --output metrics.xlsx
"""

import json
import sys
import argparse
from datetime import datetime
import math

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.chart import BarChart, LineChart, Reference
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl", "--break-system-packages", "-q"])
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.chart import BarChart, LineChart, Reference


HEADER_FONT = Font(name="Calibri", bold=True, size=11, color="FFFFFF")
HEADER_FILL = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
TITLE_FONT = Font(name="Calibri", bold=True, size=14, color="2F5496")
THIN_BORDER = Border(
    left=Side(style="thin", color="D9D9D9"),
    right=Side(style="thin", color="D9D9D9"),
    top=Side(style="thin", color="D9D9D9"),
    bottom=Side(style="thin", color="D9D9D9"),
)


def style_header(ws, row, cols):
    for c in range(1, cols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER


def auto_width(ws, min_w=10, max_w=35):
    for col in ws.columns:
        mx = max((len(str(c.value or "")) for c in col), default=0)
        ws.column_dimensions[get_column_letter(col[0].column)].width = max(min(mx + 3, max_w), min_w)


def percentile_val(sorted_list, pct):
    if not sorted_list:
        return 0
    idx = min(int(len(sorted_list) * pct / 100), len(sorted_list) - 1)
    return sorted_list[idx]


def create_summary_sheet(wb, config, sprints, items):
    ws = wb.active
    ws.title = "Summary"

    ws.merge_cells("A1:F1")
    ws["A1"] = f"Agile Metrics Summary — {config.get('team_name', 'Team')}"
    ws["A1"].font = TITLE_FONT

    ws.merge_cells("A2:F2")
    ws["A2"] = f"Generated: {datetime.now().strftime('%B %d, %Y')}"
    ws["A2"].font = Font(name="Calibri", italic=True, color="888888")

    # KPIs
    completed_pts = [s.get("completed_points", 0) for s in sprints]
    committed_pts = [s.get("committed_points", 1) for s in sprints]
    avg_vel = sum(completed_pts) / len(completed_pts) if completed_pts else 0
    vel_variance = (max(completed_pts) - min(completed_pts)) / avg_vel * 100 if avg_vel > 0 and completed_pts else 0

    # Cycle times
    ct_values = []
    for item in items:
        if item.get("started_date") and item.get("completed_date"):
            s = datetime.strptime(item["started_date"], "%Y-%m-%d")
            e = datetime.strptime(item["completed_date"], "%Y-%m-%d")
            d = (e - s).days
            if d >= 0:
                ct_values.append(d)
    ct_values.sort()

    # Lead times
    lt_values = []
    for item in items:
        if item.get("created_date") and item.get("completed_date"):
            c = datetime.strptime(item["created_date"], "%Y-%m-%d")
            e = datetime.strptime(item["completed_date"], "%Y-%m-%d")
            d = (e - c).days
            if d >= 0:
                lt_values.append(d)
    lt_values.sort()

    reliability = [round(c / m * 100, 1) if m > 0 else 0 for c, m in zip(completed_pts, committed_pts)]
    avg_rel = sum(reliability) / len(reliability) if reliability else 0

    kpis = [
        ("Scrum Metrics", "", ""),
        ("Average Velocity", f"{avg_vel:.1f} points/sprint", ""),
        ("Velocity Variance", f"{vel_variance:.0f}%", "< 20% = predictable"),
        ("Avg Commitment Reliability", f"{avg_rel:.0f}%", "> 80% = healthy"),
        ("Sprints Tracked", str(len(sprints)), ""),
        ("", "", ""),
        ("Flow Metrics", "", ""),
        ("Median Cycle Time", f"{percentile_val(ct_values, 50)} days", ""),
        ("85th %ile Cycle Time", f"{percentile_val(ct_values, 85)} days", "SLE threshold"),
        ("95th %ile Cycle Time", f"{percentile_val(ct_values, 95)} days", ""),
        ("Median Lead Time", f"{percentile_val(lt_values, 50)} days", ""),
        ("85th %ile Lead Time", f"{percentile_val(lt_values, 85)} days", ""),
        ("Items Tracked", str(len(items)), ""),
    ]

    row = 4
    headers = ["Metric", "Value", "Benchmark"]
    for c, h in enumerate(headers, 1):
        ws.cell(row=row, column=c, value=h)
    style_header(ws, row, len(headers))

    for i, (metric, value, note) in enumerate(kpis):
        r = row + 1 + i
        ws.cell(row=r, column=1, value=metric).border = THIN_BORDER
        ws.cell(row=r, column=2, value=value).border = THIN_BORDER
        ws.cell(row=r, column=3, value=note).border = THIN_BORDER
        if not metric or metric in ("Scrum Metrics", "Flow Metrics"):
            ws.cell(row=r, column=1).font = Font(bold=True, color="2F5496")

    auto_width(ws)
    ws.sheet_properties.tabColor = "2F5496"


def create_velocity_sheet(wb, sprints):
    ws = wb.create_sheet("Velocity History")

    ws.merge_cells("A1:H1")
    ws["A1"] = "Velocity History"
    ws["A1"].font = TITLE_FONT

    headers = ["Sprint #", "Start Date", "End Date", "Committed", "Completed",
               "Delta", "Reliability %", "Rolling Avg (3)"]
    row = 3
    for c, h in enumerate(headers, 1):
        ws.cell(row=row, column=c, value=h)
    style_header(ws, row, len(headers))

    completed_list = []
    for i, s in enumerate(sprints):
        r = row + 1 + i
        committed = s.get("committed_points", 0)
        completed = s.get("completed_points", 0)
        delta = completed - committed
        rel = round(completed / committed * 100, 1) if committed > 0 else 0
        completed_list.append(completed)

        ws.cell(row=r, column=1, value=s.get("number", i + 1)).border = THIN_BORDER
        ws.cell(row=r, column=2, value=s.get("start_date", "")).border = THIN_BORDER
        ws.cell(row=r, column=3, value=s.get("end_date", "")).border = THIN_BORDER
        ws.cell(row=r, column=4, value=committed).border = THIN_BORDER
        ws.cell(row=r, column=5, value=completed).border = THIN_BORDER

        delta_cell = ws.cell(row=r, column=6, value=delta)
        delta_cell.border = THIN_BORDER
        delta_cell.font = Font(color="FF0000" if delta < 0 else "008000")

        ws.cell(row=r, column=7, value=f"{rel}%").border = THIN_BORDER

        if i >= 2:
            ravg = round(sum(completed_list[i - 2:i + 1]) / 3, 1)
            ws.cell(row=r, column=8, value=ravg).border = THIN_BORDER

        for c in range(1, len(headers) + 1):
            ws.cell(row=r, column=c).alignment = Alignment(horizontal="center")

    # Chart
    if len(sprints) >= 2:
        chart = BarChart()
        chart.title = "Velocity Trend"
        chart.y_axis.title = "Story Points"
        chart.width = 20
        chart.height = 12
        data_end = row + len(sprints)
        committed_ref = Reference(ws, min_col=4, min_row=row, max_row=data_end)
        completed_ref = Reference(ws, min_col=5, min_row=row, max_row=data_end)
        labels = Reference(ws, min_col=1, min_row=row + 1, max_row=data_end)
        chart.add_data(committed_ref, titles_from_data=True)
        chart.add_data(completed_ref, titles_from_data=True)
        chart.set_categories(labels)
        ws.add_chart(chart, f"A{data_end + 2}")

    auto_width(ws)
    ws.sheet_properties.tabColor = "E94560"


def create_cycle_time_sheet(wb, items):
    ws = wb.create_sheet("Cycle Time Data")

    ws.merge_cells("A1:G1")
    ws["A1"] = "Cycle Time & Lead Time Data"
    ws["A1"].font = TITLE_FONT

    headers = ["Item ID", "Title", "Type", "Created", "Started",
               "Completed", "Cycle Time (days)", "Lead Time (days)"]
    row = 3
    for c, h in enumerate(headers, 1):
        ws.cell(row=row, column=c, value=h)
    style_header(ws, row, len(headers))

    for i, item in enumerate(items):
        r = row + 1 + i
        ct = lt = ""
        if item.get("started_date") and item.get("completed_date"):
            s = datetime.strptime(item["started_date"], "%Y-%m-%d")
            e = datetime.strptime(item["completed_date"], "%Y-%m-%d")
            ct = (e - s).days
        if item.get("created_date") and item.get("completed_date"):
            c_d = datetime.strptime(item["created_date"], "%Y-%m-%d")
            e = datetime.strptime(item["completed_date"], "%Y-%m-%d")
            lt = (e - c_d).days

        ws.cell(row=r, column=1, value=item.get("id", "")).border = THIN_BORDER
        ws.cell(row=r, column=2, value=item.get("title", "")).border = THIN_BORDER
        ws.cell(row=r, column=3, value=item.get("type", "")).border = THIN_BORDER
        ws.cell(row=r, column=4, value=item.get("created_date", "")).border = THIN_BORDER
        ws.cell(row=r, column=5, value=item.get("started_date", "")).border = THIN_BORDER
        ws.cell(row=r, column=6, value=item.get("completed_date", "")).border = THIN_BORDER
        ws.cell(row=r, column=7, value=ct).border = THIN_BORDER
        ws.cell(row=r, column=8, value=lt).border = THIN_BORDER

    auto_width(ws)
    ws.sheet_properties.tabColor = "4CAF50"


def create_throughput_sheet(wb, items):
    ws = wb.create_sheet("Throughput")

    ws.merge_cells("A1:E1")
    ws["A1"] = "Weekly Throughput"
    ws["A1"].font = TITLE_FONT

    completed = [i for i in items if i.get("completed_date")]
    if not completed:
        ws["A3"] = "No completed items to analyze."
        return

    completed.sort(key=lambda x: x["completed_date"])
    start = datetime.strptime(completed[0]["completed_date"], "%Y-%m-%d")
    end = datetime.strptime(completed[-1]["completed_date"], "%Y-%m-%d")
    weeks = max(1, (end - start).days // 7 + 1)

    headers = ["Week", "Start Date", "Items Completed", "Features", "Bugs", "Running Avg"]
    row = 3
    for c, h in enumerate(headers, 1):
        ws.cell(row=row, column=c, value=h)
    style_header(ws, row, len(headers))

    running_total = 0
    for w in range(weeks):
        r = row + 1 + w
        w_start = start + __import__("datetime").timedelta(weeks=w)
        w_end = w_start + __import__("datetime").timedelta(days=7)

        week_items = [i for i in completed
                      if w_start <= datetime.strptime(i["completed_date"], "%Y-%m-%d") < w_end]
        total = len(week_items)
        features = sum(1 for i in week_items if i.get("type") == "feature")
        bugs = sum(1 for i in week_items if i.get("type") == "bug")
        running_total += total
        ravg = round(running_total / (w + 1), 1)

        ws.cell(row=r, column=1, value=f"W{w + 1}").border = THIN_BORDER
        ws.cell(row=r, column=2, value=w_start.strftime("%Y-%m-%d")).border = THIN_BORDER
        ws.cell(row=r, column=3, value=total).border = THIN_BORDER
        ws.cell(row=r, column=4, value=features).border = THIN_BORDER
        ws.cell(row=r, column=5, value=bugs).border = THIN_BORDER
        ws.cell(row=r, column=6, value=ravg).border = THIN_BORDER

    auto_width(ws)
    ws.sheet_properties.tabColor = "FF9800"


def create_cfd_sheet(wb, snapshots):
    ws = wb.create_sheet("CFD Data")

    ws.merge_cells("A1:H1")
    ws["A1"] = "Cumulative Flow Diagram Data"
    ws["A1"].font = TITLE_FONT

    if not snapshots:
        ws["A3"] = "No flow snapshot data available."
        return

    headers = ["Date", "Backlog", "Ready", "In Progress", "In Review", "Testing", "Done"]
    row = 3
    for c, h in enumerate(headers, 1):
        ws.cell(row=row, column=c, value=h)
    style_header(ws, row, len(headers))

    for i, snap in enumerate(snapshots):
        r = row + 1 + i
        ws.cell(row=r, column=1, value=snap.get("date", "")).border = THIN_BORDER
        ws.cell(row=r, column=2, value=snap.get("backlog", 0)).border = THIN_BORDER
        ws.cell(row=r, column=3, value=snap.get("ready", 0)).border = THIN_BORDER
        ws.cell(row=r, column=4, value=snap.get("in_progress", 0)).border = THIN_BORDER
        ws.cell(row=r, column=5, value=snap.get("in_review", 0)).border = THIN_BORDER
        ws.cell(row=r, column=6, value=snap.get("testing", 0)).border = THIN_BORDER
        ws.cell(row=r, column=7, value=snap.get("done", 0)).border = THIN_BORDER

    auto_width(ws)
    ws.sheet_properties.tabColor = "9C27B0"


def generate_metrics_xlsx(config, output_path):
    wb = openpyxl.Workbook()
    sprints = config.get("sprints", [])
    items = config.get("items", [])
    snapshots = config.get("flow_snapshots", [])

    create_summary_sheet(wb, config, sprints, items)
    create_velocity_sheet(wb, sprints)
    create_cycle_time_sheet(wb, items)
    create_throughput_sheet(wb, items)
    create_cfd_sheet(wb, snapshots)

    wb.save(output_path)
    print(f"Metrics workbook saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate Agile Metrics Excel Workbook")
    parser.add_argument("--config", help="Path to JSON config")
    parser.add_argument("--output", default="agile_metrics.xlsx")
    args = parser.parse_args()

    if args.config:
        with open(args.config, "r") as f:
            config = json.load(f)
    else:
        config = json.load(sys.stdin)

    generate_metrics_xlsx(config, args.output)


if __name__ == "__main__":
    main()

```


---

<!-- Script: scripts/monte_carlo.py -->

# Script: monte_carlo.py

```python
#!/usr/bin/env python3
"""
Monte Carlo simulation for Agile delivery forecasting.

Supports two forecast modes:
1. "when" — When will N items be completed? (date forecasting)
2. "how_many" — How many items will be completed by date X? (scope forecasting)

Usage:
    python monte_carlo.py --config data.json --mode when --output forecast.html
    python monte_carlo.py --config data.json --mode how_many --target-date 2025-06-30 --output forecast.html

Config JSON should include:
{
    "team_name": "Alpha Squad",
    "remaining_items": 45,
    "target_date": "2025-06-30",  // optional, used for how_many mode
    "throughput_history": [6, 5, 7, 6, 4, 8, 7, 5, 6, 7, 8, 6],  // weekly throughput
    "simulations": 10000,  // optional, default 10000
    "start_date": "2025-01-13"  // optional, default today
}

OR provide sprint-level data and the script extracts throughput:
{
    "sprints": [
        {"number": 11, "stories_completed": 7, "sprint_weeks": 2},
        {"number": 12, "stories_completed": 8, "sprint_weeks": 2}
    ],
    "remaining_items": 45
}
"""

import json
import sys
import argparse
import random
from datetime import datetime, timedelta
from collections import Counter
import math


def extract_throughput(config):
    """Extract weekly throughput from config data."""
    if "throughput_history" in config:
        return config["throughput_history"]

    if "sprints" in config:
        weekly = []
        for sprint in config["sprints"]:
            weeks = sprint.get("sprint_weeks", 2)
            completed = sprint.get("stories_completed", sprint.get("completed_points", 0))
            per_week = completed / weeks if weeks > 0 else 0
            for _ in range(weeks):
                weekly.append(round(per_week))
        return weekly

    if "items" in config:
        items = [i for i in config["items"] if i.get("completed_date")]
        if not items:
            return []
        items.sort(key=lambda x: x["completed_date"])
        start = datetime.strptime(items[0]["completed_date"], "%Y-%m-%d")
        end = datetime.strptime(items[-1]["completed_date"], "%Y-%m-%d")
        total_weeks = max(1, (end - start).days // 7)
        week_counts = [0] * total_weeks
        for item in items:
            d = datetime.strptime(item["completed_date"], "%Y-%m-%d")
            week_idx = min((d - start).days // 7, total_weeks - 1)
            week_counts[week_idx] += 1
        return week_counts

    return []


def run_when_simulation(throughput, remaining, num_simulations=10000):
    """Simulate: when will we finish N items?"""
    results = []
    for _ in range(num_simulations):
        remaining_count = remaining
        weeks = 0
        max_weeks = 200  # Safety cap
        while remaining_count > 0 and weeks < max_weeks:
            sampled = random.choice(throughput)
            remaining_count -= sampled
            weeks += 1
        results.append(weeks)
    return sorted(results)


def run_how_many_simulation(throughput, weeks_available, num_simulations=10000):
    """Simulate: how many items will be done in N weeks?"""
    results = []
    for _ in range(num_simulations):
        total = 0
        for _ in range(weeks_available):
            total += random.choice(throughput)
        results.append(total)
    return sorted(results)


def get_percentile(sorted_data, pct):
    """Get percentile from sorted data."""
    idx = int(len(sorted_data) * pct / 100)
    idx = min(idx, len(sorted_data) - 1)
    return sorted_data[idx]


def generate_forecast_html(config, results, mode, throughput):
    """Generate interactive HTML forecast report."""
    team = config.get("team_name", "Team")
    remaining = config.get("remaining_items", 0)
    start_date_str = config.get("start_date", datetime.now().strftime("%Y-%m-%d"))
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    num_sims = len(results)

    # Statistics
    avg_throughput = sum(throughput) / len(throughput)
    std_throughput = math.sqrt(sum((t - avg_throughput) ** 2 for t in throughput) / len(throughput))
    min_tp, max_tp = min(throughput), max(throughput)

    if mode == "when":
        p50 = get_percentile(results, 50)
        p70 = get_percentile(results, 70)
        p85 = get_percentile(results, 85)
        p95 = get_percentile(results, 95)

        d50 = (start_date + timedelta(weeks=p50)).strftime("%b %d, %Y")
        d70 = (start_date + timedelta(weeks=p70)).strftime("%b %d, %Y")
        d85 = (start_date + timedelta(weeks=p85)).strftime("%b %d, %Y")
        d95 = (start_date + timedelta(weeks=p95)).strftime("%b %d, %Y")

        # Histogram data
        counter = Counter(results)
        max_weeks = max(results)
        hist_labels = list(range(min(results), max_weeks + 1))
        hist_data = [counter.get(w, 0) for w in hist_labels]
        # Convert to dates for display
        hist_date_labels = [(start_date + timedelta(weeks=w)).strftime("%b %d") for w in hist_labels]

        forecast_table = f"""
            <tr><td>50%</td><td>{d50}</td><td>{p50} weeks</td><td>Coin flip — not reliable</td></tr>
            <tr><td>70%</td><td>{d70}</td><td>{p70} weeks</td><td>Moderate confidence</td></tr>
            <tr class="highlight"><td>85%</td><td>{d85}</td><td>{p85} weeks</td><td>★ Recommended commitment</td></tr>
            <tr><td>95%</td><td>{d95}</td><td>{p95} weeks</td><td>Very conservative</td></tr>
        """
        title_text = f"When will {remaining} items be completed?"
        chart_title = "Probability Distribution — Completion Date"

    else:  # how_many
        p50 = get_percentile(results, 50)
        p70 = get_percentile(results, 70)
        p85 = get_percentile(results, 85)
        p95 = get_percentile(results, 95)

        target_date = config.get("target_date", "TBD")
        forecast_table = f"""
            <tr><td>50%</td><td>{p50} items</td><td>—</td><td>Coin flip</td></tr>
            <tr><td>70%</td><td>{p70} items</td><td>—</td><td>Moderate</td></tr>
            <tr class="highlight"><td>85%</td><td>{p85} items</td><td>—</td><td>★ Recommended</td></tr>
            <tr><td>95%</td><td>{p95} items</td><td>—</td><td>Very conservative (minimum)</td></tr>
        """
        title_text = f"How many items by {target_date}?"
        chart_title = "Probability Distribution — Items Completed"

        counter = Counter(results)
        hist_labels = list(range(min(results), max(results) + 1))
        hist_data = [counter.get(v, 0) for v in hist_labels]
        hist_date_labels = [str(v) for v in hist_labels]

    # Throughput history chart data
    tp_labels = [f"W{i+1}" for i in range(len(throughput))]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monte Carlo Forecast — {team}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0f0f23;
            color: #eee;
            padding: 2rem;
        }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        h1 {{ color: #e94560; margin-bottom: 0.3rem; font-size: 1.6rem; }}
        .subtitle {{ color: #888; margin-bottom: 2rem; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem; }}
        .card {{
            background: #1a1a2e;
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid #333;
        }}
        .card h3 {{ color: #e94560; margin-bottom: 1rem; font-size: 1rem; }}
        .full-width {{ grid-column: 1 / -1; }}
        .chart-container {{ position: relative; height: 300px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 0.6rem 1rem; text-align: left; border-bottom: 1px solid #333; }}
        th {{ color: #888; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; }}
        .highlight {{ background: rgba(233, 69, 96, 0.15); }}
        .highlight td {{ color: #e94560; font-weight: 600; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; }}
        .stat {{
            background: #1a1a2e;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            border: 1px solid #333;
        }}
        .stat .value {{ font-size: 1.8rem; font-weight: 700; color: #e94560; }}
        .stat .label {{ font-size: 0.8rem; color: #888; margin-top: 0.3rem; }}
        .assumptions {{
            background: #1a1a2e;
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid #333;
            margin-top: 1.5rem;
        }}
        .assumptions h3 {{ color: #e94560; margin-bottom: 0.75rem; }}
        .assumptions ul {{ list-style: none; }}
        .assumptions li {{ padding: 0.3rem 0; color: #aaa; }}
        .assumptions li::before {{ content: "⚠️ "; }}
    </style>
</head>
<body>
<div class="container">
    <h1>🎲 Monte Carlo Forecast — {team}</h1>
    <div class="subtitle">{title_text} | {num_sims:,} simulations | {len(throughput)} weeks of data</div>

    <div class="stats">
        <div class="stat">
            <div class="value">{remaining}</div>
            <div class="label">Items Remaining</div>
        </div>
        <div class="stat">
            <div class="value">{avg_throughput:.1f}</div>
            <div class="label">Avg Throughput/Week</div>
        </div>
        <div class="stat">
            <div class="value">{min_tp}–{max_tp}</div>
            <div class="label">Throughput Range</div>
        </div>
        <div class="stat">
            <div class="value">±{std_throughput:.1f}</div>
            <div class="label">Std Deviation</div>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <h3>📊 Forecast Results</h3>
            <table>
                <tr><th>Confidence</th><th>{"Date" if mode == "when" else "Items"}</th><th>{"Weeks" if mode == "when" else ""}</th><th>Interpretation</th></tr>
                {forecast_table}
            </table>
        </div>
        <div class="card">
            <h3>📈 Throughput History</h3>
            <div class="chart-container">
                <canvas id="throughputChart"></canvas>
            </div>
        </div>
        <div class="card full-width">
            <h3>🎲 {chart_title}</h3>
            <div class="chart-container">
                <canvas id="histogramChart"></canvas>
            </div>
        </div>
    </div>

    <div class="assumptions">
        <h3>Assumptions & Caveats</h3>
        <ul>
            <li>Team composition remains stable</li>
            <li>Historical throughput patterns continue</li>
            <li>No major scope additions beyond current backlog</li>
            <li>Does not account for specific known risks (holidays, departures)</li>
            <li>Based on {len(throughput)} weeks of data — more data = more accuracy</li>
        </ul>
    </div>
</div>

<script>
    new Chart(document.getElementById('throughputChart'), {{
        type: 'bar',
        data: {{
            labels: {json.dumps(tp_labels)},
            datasets: [{{
                label: 'Items/Week',
                data: {json.dumps(throughput)},
                backgroundColor: 'rgba(233, 69, 96, 0.6)',
                borderColor: '#e94560',
                borderWidth: 1
            }}, {{
                label: 'Average',
                data: Array({len(throughput)}).fill({avg_throughput:.1f}),
                type: 'line',
                borderColor: '#4CAF50',
                borderDash: [5, 5],
                pointRadius: 0,
                fill: false
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ labels: {{ color: '#aaa' }} }} }},
            scales: {{
                y: {{ beginAtZero: true, ticks: {{ color: '#888' }}, grid: {{ color: '#333' }} }},
                x: {{ ticks: {{ color: '#888' }}, grid: {{ color: '#333' }} }}
            }}
        }}
    }});

    const histCtx = document.getElementById('histogramChart');
    const histData = {json.dumps(hist_data)};
    const cumulative = [];
    let runningSum = 0;
    const total = histData.reduce((a, b) => a + b, 0);
    histData.forEach(v => {{ runningSum += v; cumulative.push((runningSum / total * 100).toFixed(1)); }});

    new Chart(histCtx, {{
        type: 'bar',
        data: {{
            labels: {json.dumps(hist_date_labels)},
            datasets: [{{
                label: 'Simulations',
                data: histData,
                backgroundColor: 'rgba(233, 69, 96, 0.5)',
                borderColor: '#e94560',
                borderWidth: 1,
                yAxisID: 'y'
            }}, {{
                label: 'Cumulative %',
                data: cumulative,
                type: 'line',
                borderColor: '#4CAF50',
                borderWidth: 2,
                pointRadius: 0,
                fill: false,
                yAxisID: 'y1'
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ labels: {{ color: '#aaa' }} }} }},
            scales: {{
                y: {{ beginAtZero: true, ticks: {{ color: '#888' }}, grid: {{ color: '#333' }}, title: {{ display: true, text: 'Simulation Count', color: '#888' }} }},
                y1: {{ position: 'right', min: 0, max: 100, ticks: {{ color: '#888', callback: v => v + '%' }}, grid: {{ display: false }}, title: {{ display: true, text: 'Cumulative %', color: '#888' }} }},
                x: {{ ticks: {{ color: '#888', maxRotation: 45 }}, grid: {{ color: '#333' }} }}
            }}
        }}
    }});
</script>
</body>
</html>"""
    return html


def generate_forecast_text(config, results, mode, throughput):
    """Generate markdown forecast report."""
    team = config.get("team_name", "Team")
    remaining = config.get("remaining_items", 0)
    start_date_str = config.get("start_date", datetime.now().strftime("%Y-%m-%d"))
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    avg_tp = sum(throughput) / len(throughput)

    p50 = get_percentile(results, 50)
    p70 = get_percentile(results, 70)
    p85 = get_percentile(results, 85)
    p95 = get_percentile(results, 95)

    if mode == "when":
        d50 = (start_date + timedelta(weeks=p50)).strftime("%B %d, %Y")
        d70 = (start_date + timedelta(weeks=p70)).strftime("%B %d, %Y")
        d85 = (start_date + timedelta(weeks=p85)).strftime("%B %d, %Y")
        d95 = (start_date + timedelta(weeks=p95)).strftime("%B %d, %Y")

        return f"""# Monte Carlo Forecast — {team}

## Question: When will {remaining} items be completed?

**Simulations:** {len(results):,} | **Data:** {len(throughput)} weeks | **Avg Throughput:** {avg_tp:.1f} items/week

## Forecast Results

| Confidence | Date | Weeks | Interpretation |
|------------|------|-------|----------------|
| 50% | {d50} | {p50} | Optimistic — coin flip odds |
| 70% | {d70} | {p70} | Moderate confidence |
| **85%** | **{d85}** | **{p85}** | **★ Recommended commitment** |
| 95% | {d95} | {p95} | Very conservative |

## Throughput Summary

| Metric | Value |
|--------|-------|
| Average | {avg_tp:.1f} items/week |
| Min | {min(throughput)} items/week |
| Max | {max(throughput)} items/week |
| Std Dev | {math.sqrt(sum((t - avg_tp)**2 for t in throughput) / len(throughput)):.1f} |
| Data Points | {len(throughput)} weeks |

## Recommendation

Commit to **{d85}** (85% confidence). This means there is an 85% probability
the team will complete all {remaining} items by this date, based on historical performance.
"""
    else:
        return f"""# Monte Carlo Forecast — {team}

## Question: How many items by {config.get("target_date", "target")}?

**Simulations:** {len(results):,} | **Data:** {len(throughput)} weeks

## Forecast Results

| Confidence | Items Completed | Interpretation |
|------------|----------------|----------------|
| 50% | {p50} items | Coin flip |
| 70% | {p70} items | Moderate |
| **85%** | **{p85} items** | **★ Recommended** |
| 95% | {p95} items | Conservative (minimum expected) |
"""


def main():
    parser = argparse.ArgumentParser(description="Monte Carlo Delivery Forecast")
    parser.add_argument("--config", help="Path to JSON config file")
    parser.add_argument("--mode", choices=["when", "how_many"], default="when")
    parser.add_argument("--target-date", help="Target date for how_many mode (YYYY-MM-DD)")
    parser.add_argument("--output", help="Output file (.html or .md)")
    parser.add_argument("--format", choices=["html", "markdown"], default="html")
    parser.add_argument("--simulations", type=int, default=10000)
    args = parser.parse_args()

    if args.config:
        with open(args.config, "r") as f:
            config = json.load(f)
    else:
        config = json.load(sys.stdin)

    throughput = extract_throughput(config)
    if not throughput or len(throughput) < 3:
        print("Error: Need at least 3 weeks of throughput data.", file=sys.stderr)
        sys.exit(1)

    # Filter out zero-throughput weeks (likely holidays/breaks)
    throughput = [t for t in throughput if t > 0] or throughput

    num_sims = config.get("simulations", args.simulations)
    remaining = config.get("remaining_items", 0)

    if args.mode == "when":
        if remaining <= 0:
            print("Error: remaining_items must be > 0 for 'when' mode.", file=sys.stderr)
            sys.exit(1)
        results = run_when_simulation(throughput, remaining, num_sims)
    else:
        target_date = args.target_date or config.get("target_date")
        if not target_date:
            print("Error: --target-date required for how_many mode.", file=sys.stderr)
            sys.exit(1)
        start = datetime.strptime(
            config.get("start_date", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d"
        )
        end = datetime.strptime(target_date, "%Y-%m-%d")
        weeks_available = max(1, (end - start).days // 7)
        results = run_how_many_simulation(throughput, weeks_available, num_sims)

    output_format = args.format
    if args.output and args.output.endswith(".md"):
        output_format = "markdown"
    elif args.output and args.output.endswith(".html"):
        output_format = "html"

    if output_format == "html":
        content = generate_forecast_html(config, results, args.mode, throughput)
    else:
        content = generate_forecast_text(config, results, args.mode, throughput)

    output_path = args.output or (f"forecast.{('html' if output_format == 'html' else 'md')}")
    with open(output_path, "w") as f:
        f.write(content)

    print(f"Forecast saved to: {output_path}")

    # Print summary to stdout
    p85 = get_percentile(results, 85)
    if args.mode == "when":
        start = datetime.strptime(
            config.get("start_date", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d"
        )
        d85 = (start + timedelta(weeks=p85)).strftime("%B %d, %Y")
        print(f"85% confidence: {remaining} items done by {d85} ({p85} weeks)")
    else:
        print(f"85% confidence: {p85} items completed by target date")


if __name__ == "__main__":
    main()

```
