# Roadmap Styles Reference

## Table of Contents
1. Now / Next / Later Deep Dive
2. Timeline Roadmap Deep Dive
3. Theme-Based Roadmap Deep Dive
4. Feature-Based Roadmap Deep Dive
5. Choosing the Right Style
6. Roadmap Anti-Patterns

---

## 1. Now / Next / Later Deep Dive

### Philosophy
This format deliberately avoids dates. It communicates intent and direction without
creating false precision. Originated from lean/agile practitioners who found that
date-based roadmaps create harmful commitments too early.

### Column Definitions

**Now (Committed)**
- Items actively being worked on or starting within the current sprint
- Highest confidence — team has refined these, stories are written
- Detail level: individual stories or small epics with acceptance criteria
- Typical count: 3-5 items (what fits in current sprint capacity)

**Next (Planned)**
- Items the team expects to work on in the next 1-3 sprints
- Medium confidence — epics are defined but may not be fully refined
- Detail level: epics with rough scope and high-level acceptance criteria
- Typical count: 5-8 items
- Items here may be reordered based on learning from "Now" items

**Later (Exploring)**
- Items on the radar but not yet committed
- Low confidence — may change significantly or be dropped
- Detail level: themes or large epics, possibly just problem statements
- Typical count: 5-15 items
- Items here are explicitly "no promises" territory

### Transition Rules
```
Later → Next: When the team has enough information to size roughly
               and the PO has prioritized it above other "Later" items.

Next → Now:   When the item is refined, meets Definition of Ready,
               and the team has capacity in the upcoming sprint.

Now → Done:   When all stories meet Definition of Done.

Any → Dropped: Explicitly move deprioritized items to a "Dropped" section
                with a brief reason. Don't just delete them.
```

### Facilitation: Roadmap Review Meeting
Hold monthly (or every 2 sprints):
1. Review "Now" status (5 min) — What shipped? What's in progress?
2. Move items between columns (10 min) — Any promotions or demotions?
3. Review "Later" for new items (10 min) — What's changed in the landscape?
4. Stakeholder Q&A (5 min) — Address questions about priorities

---

## 2. Timeline Roadmap Deep Dive

### Structure
Organize by quarters or months. Each item spans a time range.

```
         Jan    Feb    Mar    Apr    May    Jun
Theme 1  |==Epic A==|
                |====Epic B=====|
Theme 2              |==Epic C==|
                                   |===Epic D===|
Milestones  ▼M1              ▼M2         ▼M3
```

### Confidence Visualization
- **High confidence** (committed, stories written): Solid bar
- **Medium confidence** (planned, rough scope): Dashed bar
- **Low confidence** (exploring): Dotted bar or lighter shade

### Time Granularity by Horizon

| Horizon | Granularity | Example |
|---------|------------|---------|
| This quarter | Month or sprint | "Sprint 14-16 (Feb)" |
| Next quarter | Month | "March 2025" |
| 2+ quarters out | Quarter | "Q3 2025" |

This reflects the cone of uncertainty — further out = less precise.

### Handling Uncertainty
- Use ranges, not point dates: "Q1-Q2" not "March 15"
- Show confidence visually (solid vs dashed vs dotted)
- Add a disclaimer: "Items beyond current quarter are directional, not committed"
- For external roadmaps, use "Early/Mid/Late [Quarter]" instead of specific months

### Milestone Types

| Type | Symbol | Example |
|------|--------|---------|
| Release | ▼ | "v2.0 Launch" |
| Decision Point | ◆ | "Go/No-Go Decision" |
| External Deadline | ⚠ | "SOC2 Audit" |
| Internal Target | ○ | "Feature Complete" |

---

## 3. Theme-Based Roadmap Deep Dive

### Structure
Organize by strategic themes or OKR objectives, not timelines.

```
🎯 Theme: User Growth (KR: +40% MAU)
├── [Now] Social Login ████████░░ 80%
├── [Next] Referral Program ███░░░░░░ 30%
└── [Later] Onboarding v2 ░░░░░░░░░░ 0%

🎯 Theme: Revenue (KR: +20% ARPU)
├── [Now] Premium Tier ██████████ 100% ✅
├── [Next] Usage Billing ████░░░░░ 40%
└── [Later] Enterprise Plan ░░░░░░░░░ 0%
```

### Theme Construction
Each theme should have:
- **Name**: Short, memorable label (2-4 words)
- **Objective**: What success looks like (measurable)
- **Key Result**: Specific metric and target
- **Epics**: The features/work items that drive this theme
- **Owner**: Who is accountable for the theme (usually a PM or product lead)

### Theme Prioritization
Use WSJF (Weighted Shortest Job First) or a simple priority matrix:

| Theme | Business Value | Time Criticality | Risk/Opportunity | Job Size | WSJF Score |
|-------|---------------|-----------------|------------------|----------|------------|
| User Growth | 8 | 7 | 6 | 5 | (8+7+6)/5 = 4.2 |
| Revenue | 9 | 5 | 4 | 8 | (9+5+4)/8 = 2.25 |

Higher WSJF = do it first.

---

## 4. Feature-Based Roadmap Deep Dive

### Structure
Detailed list of features with dates, owners, estimates, and status.

| Feature | Epic | Owner | Start | End | Points | Status | Confidence | Dependencies |
|---------|------|-------|-------|-----|--------|--------|-----------|-------------|

### When to Use
- Engineering teams need task-level visibility
- Release management requires feature-level tracking
- Contractual commitments need specific deliverables
- Large programs with multiple teams need coordination

### Capacity Allocation View

| Team | Q1 Capacity | Q1 Allocated | Q1 Available | Q2 Capacity | Q2 Allocated |
|------|------------|-------------|-------------|------------|-------------|
| Auth | 90 SP | 78 SP | 12 SP | 90 SP | 65 SP |
| Core | 120 SP | 115 SP | 5 SP | 120 SP | 95 SP |

Flag teams above 90% allocation — they have no buffer for unplanned work.

---

## 5. Choosing the Right Style

| Situation | Recommended Style | Why |
|-----------|-------------------|-----|
| Board presentation | Timeline | Execs want to see dates and milestones |
| Customer advisory board | Theme-based (external view) | Show value delivered, not internal details |
| Sprint planning horizon | Now/Next/Later | Focuses on what's actionable |
| Engineering all-hands | Feature-based + Timeline | Teams need detail and context |
| Investor update | Timeline + Theme-based | Strategy alignment + execution timeline |
| New product (< 6 months old) | Now/Next/Later | Too early for date commitments |
| Mature product | Timeline or Theme-based | Enough history for reliable forecasting |
| Multi-team program | Timeline + Dependency map | Cross-team coordination needs dates |

---

## 6. Roadmap Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Feature factory roadmap | List of features with no strategic context | Add themes/objectives: explain WHY |
| Over-committed roadmap | More work than capacity allows | Run capacity check; cut or defer |
| Stale roadmap | Not updated in 2+ months | Monthly review cadence; assign an owner |
| Hidden dependencies | Dependencies not visualized | Use dependency map; review cross-team |
| No confidence levels | Everything looks equally certain | Add High/Medium/Low; adjust date specificity |
| Date-driven roadmap | Dates set before scope is understood | Start with Now/Next/Later; add dates when confident |
| No stakeholder version | Internal detail shown to customers | Create external view with simplified language |
| Roadmap as contract | Treated as immutable commitment | Add explicit disclaimer; review cadence |
| Solution roadmap | Specifies HOW not WHAT | Focus on problems/outcomes, not implementations |
| Empty "Later" column | Team only plans 1-2 sprints ahead | Vision is unclear; run a roadmap workshop |



---

<!-- Script: scripts/generate_dependency_map.py -->

# Script: generate_dependency_map.py

```python
#!/usr/bin/env python3
"""
Generate an interactive dependency graph as HTML using SVG + JavaScript.

Renders epics as nodes and dependencies as directed edges.
Highlights the critical path and color-codes by team/theme.

Usage:
    python generate_dependency_map.py --config roadmap.json --output dependencies.html
"""

import json
import sys
import argparse
import math


def compute_layout(epics, width=900, height=600, padding=80):
    """Simple force-directed-ish layout using layered approach."""
    nodes = {}
    edges = []

    for e in epics:
        nodes[e["id"]] = {
            "id": e["id"],
            "title": e.get("title", e["id"]),
            "owner": e.get("owner", ""),
            "status": e.get("status", ""),
            "confidence": e.get("confidence", "Medium"),
            "theme_id": e.get("theme_id", ""),
            "story_points": e.get("story_points", 0),
            "quarter": e.get("quarter", ""),
            "deps": e.get("dependencies", []),
        }
        for dep in e.get("dependencies", []):
            edges.append({"from": dep, "to": e["id"]})

    # Layer assignment (topological sort by dependency depth)
    layers = {}
    visited = set()

    def get_depth(node_id, visiting=None):
        if visiting is None:
            visiting = set()
        if node_id in visiting:
            return 0  # Circular dependency — break cycle
        if node_id in layers:
            return layers[node_id]
        visiting.add(node_id)
        node = nodes.get(node_id)
        if not node or not node["deps"]:
            layers[node_id] = 0
            return 0
        max_dep = 0
        for d in node["deps"]:
            if d in nodes:
                max_dep = max(max_dep, get_depth(d, visiting) + 1)
        layers[node_id] = max_dep
        return max_dep

    for nid in nodes:
        get_depth(nid)

    # Position nodes by layer
    max_layer = max(layers.values()) if layers else 0
    layer_groups = {}
    for nid, layer in layers.items():
        if layer not in layer_groups:
            layer_groups[layer] = []
        layer_groups[layer].append(nid)

    positions = {}
    for layer, group in layer_groups.items():
        x = padding + (layer / max(max_layer, 1)) * (width - 2 * padding)
        for i, nid in enumerate(group):
            y = padding + ((i + 1) / (len(group) + 1)) * (height - 2 * padding)
            positions[nid] = {"x": x, "y": y}

    return nodes, edges, positions, layers


def find_critical_path(nodes, edges, layers):
    """Find the longest dependency chain."""
    if not layers:
        return set()

    max_depth = max(layers.values())
    # Find node(s) at max depth
    deepest = [nid for nid, d in layers.items() if d == max_depth]

    # Trace back through dependencies
    critical = set()
    queue = list(deepest)
    while queue:
        current = queue.pop(0)
        critical.add(current)
        node = nodes.get(current, {})
        for dep in node.get("deps", []):
            if dep in nodes and dep not in critical:
                queue.append(dep)

    return critical


def generate_dependency_map(config, output_path):
    epics = config.get("epics", [])
    themes = {t["id"]: t for t in config.get("themes", [])}
    product = config.get("product_name", "Product")

    if not epics:
        with open(output_path, "w") as f:
            f.write("<html><body><h1>No epics to map</h1></body></html>")
        print(f"No epics found. Empty map saved to: {output_path}")
        return

    # Only include epics that have dependencies or are depended upon
    dep_ids = set()
    for e in epics:
        if e.get("dependencies"):
            dep_ids.add(e["id"])
            dep_ids.update(e["dependencies"])

    relevant_epics = [e for e in epics if e["id"] in dep_ids] if dep_ids else epics

    w, h = 1000, max(400, len(relevant_epics) * 80)
    nodes, edges, positions, layers = compute_layout(relevant_epics, w, h)
    critical_path = find_critical_path(nodes, edges, layers)

    # Build SVG edges
    edges_svg = ""
    for edge in edges:
        if edge["from"] in positions and edge["to"] in positions:
            p1 = positions[edge["from"]]
            p2 = positions[edge["to"]]
            is_critical = edge["from"] in critical_path and edge["to"] in critical_path
            color = "#e94560" if is_critical else "#555"
            width = 3 if is_critical else 1.5
            # Arrow with marker
            mid_x = (p1["x"] + p2["x"]) / 2
            mid_y = (p1["y"] + p2["y"]) / 2
            edges_svg += f"""<line x1="{p1['x']}" y1="{p1['y']}" x2="{p2['x']}" y2="{p2['y']}"
                stroke="{color}" stroke-width="{width}" marker-end="url(#arrow{'Crit' if is_critical else ''})" />"""

    # Build SVG nodes
    nodes_svg = ""
    for nid, pos in positions.items():
        node = nodes.get(nid, {})
        theme = themes.get(node.get("theme_id", ""), {})
        color = theme.get("color", "#2196F3")
        is_critical = nid in critical_path
        stroke = "#e94560" if is_critical else color
        stroke_w = 3 if is_critical else 2

        status_color = {"Done": "#4CAF50", "In Progress": "#FF9800",
                       "In Review": "#9C27B0", "Testing": "#00BCD4"}.get(
            node.get("status", ""), "#555")

        nodes_svg += f"""
        <g class="node" transform="translate({pos['x']},{pos['y']})" data-id="{nid}">
            <rect x="-75" y="-30" width="150" height="60" rx="8"
                  fill="#1a1a2e" stroke="{stroke}" stroke-width="{stroke_w}" />
            <text x="0" y="-8" text-anchor="middle" fill="#eee" font-size="11" font-weight="600">
                {node.get('title', nid)[:18]}
            </text>
            <text x="0" y="8" text-anchor="middle" fill="{color}" font-size="9">
                {node.get('owner', '')}
            </text>
            <text x="0" y="22" text-anchor="middle" fill="{status_color}" font-size="9">
                {node.get('status', '')}
            </text>
        </g>"""

    # Stats
    total_nodes = len(nodes)
    total_edges = len(edges)
    cp_length = max(layers.values()) + 1 if layers else 0
    orphans = len([n for n in nodes if not nodes[n]["deps"] and
                   n not in {e["from"] for e in edges}])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{product} — Dependency Map</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, sans-serif; background: #0f0f23; color: #eee; padding: 1.5rem; }}
        h1 {{ color: #e94560; font-size: 1.4rem; margin-bottom: 0.3rem; }}
        .subtitle {{ color: #888; font-size: 0.85rem; margin-bottom: 1rem; }}
        .stats {{ display: flex; gap: 2rem; margin-bottom: 1rem; }}
        .stat {{ font-size: 0.85rem; color: #aaa; }}
        .stat strong {{ color: #e94560; }}
        .legend {{ display: flex; gap: 1.5rem; margin-bottom: 1rem; font-size: 0.8rem; color: #888; }}
        .legend-item {{ display: flex; align-items: center; gap: 0.3rem; }}
        .legend-color {{ width: 12px; height: 3px; }}
        svg {{ background: #1a1a2e; border-radius: 12px; border: 1px solid #333; }}
        .node {{ cursor: pointer; }}
        .node:hover rect {{ filter: brightness(1.3); }}
    </style>
</head>
<body>
    <h1>🔗 {product} — Dependency Map</h1>
    <div class="subtitle">Showing {total_edges} dependencies across {total_nodes} epics</div>
    <div class="stats">
        <div class="stat">Epics: <strong>{total_nodes}</strong></div>
        <div class="stat">Dependencies: <strong>{total_edges}</strong></div>
        <div class="stat">Critical Path Length: <strong>{cp_length} epics</strong></div>
        <div class="stat">Independent Epics: <strong>{orphans}</strong></div>
    </div>
    <div class="legend">
        <div class="legend-item"><div class="legend-color" style="background:#e94560;height:3px"></div> Critical Path</div>
        <div class="legend-item"><div class="legend-color" style="background:#555;height:2px"></div> Dependency</div>
        <div class="legend-item"><div class="legend-color" style="background:#e94560;width:14px;height:14px;border-radius:3px;border:2px solid #e94560;background:transparent"></div> On Critical Path</div>
    </div>
    <svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">
        <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5"
                    markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#555"/>
            </marker>
            <marker id="arrowCrit" viewBox="0 0 10 10" refX="10" refY="5"
                    markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#e94560"/>
            </marker>
        </defs>
        {edges_svg}
        {nodes_svg}
    </svg>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)
    print(f"Dependency map saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate Dependency Map")
    parser.add_argument("--config", help="JSON config path")
    parser.add_argument("--output", default="dependencies.html")
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = json.load(sys.stdin)

    generate_dependency_map(config, args.output)


if __name__ == "__main__":
    main()

```


---

<!-- Script: scripts/generate_release_xlsx.py -->

# Script: generate_release_xlsx.py

```python
#!/usr/bin/env python3
"""
Generate a release planning Excel spreadsheet with milestones, scope, capacity, and risk tracking.

Usage:
    python generate_release_xlsx.py --config roadmap.json --output release_plan.xlsx
"""

import json
import sys
import argparse

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl", "--break-system-packages", "-q"])
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter


HEADER_FONT = Font(name="Calibri", bold=True, size=11, color="FFFFFF")
HEADER_FILL = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
TITLE_FONT = Font(name="Calibri", bold=True, size=14, color="2F5496")
BORDER = Border(
    left=Side(style="thin", color="D9D9D9"), right=Side(style="thin", color="D9D9D9"),
    top=Side(style="thin", color="D9D9D9"), bottom=Side(style="thin", color="D9D9D9"),
)

PRIORITY_FILLS = {
    "Must": PatternFill(start_color="FCE4EC", end_color="FCE4EC", fill_type="solid"),
    "Should": PatternFill(start_color="FFF3E0", end_color="FFF3E0", fill_type="solid"),
    "Could": PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid"),
    "Won't": PatternFill(start_color="F5F5F5", end_color="F5F5F5", fill_type="solid"),
}

CONF_FILLS = {
    "High": PatternFill(start_color="C8E6C9", end_color="C8E6C9", fill_type="solid"),
    "Medium": PatternFill(start_color="FFF9C4", end_color="FFF9C4", fill_type="solid"),
    "Low": PatternFill(start_color="FFCDD2", end_color="FFCDD2", fill_type="solid"),
}


def style_header(ws, row, cols):
    for c in range(1, cols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER


def auto_width(ws, min_w=10, max_w=35):
    for col in ws.columns:
        mx = max((len(str(c.value or "")) for c in col), default=0)
        ws.column_dimensions[get_column_letter(col[0].column)].width = max(min(mx + 3, max_w), min_w)


def create_overview_sheet(wb, config):
    ws = wb.active
    ws.title = "Release Overview"
    product = config.get("product_name", "Product")
    timeframe = config.get("timeframe", "")

    ws.merge_cells("A1:F1")
    ws["A1"] = f"Release Plan — {product}"
    ws["A1"].font = TITLE_FONT

    ws.merge_cells("A2:F2")
    ws["A2"] = f"Timeframe: {timeframe} | Updated: {config.get('last_updated', '')}"
    ws["A2"].font = Font(italic=True, color="888888")

    # Summary stats
    epics = config.get("epics", [])
    total_pts = sum(e.get("story_points", 0) for e in epics)
    must = [e for e in epics if e.get("priority") == "Must"]
    should = [e for e in epics if e.get("priority") == "Should"]
    could = [e for e in epics if e.get("priority") == "Could"]

    stats = [
        ("Total Epics", len(epics)),
        ("Total Story Points", total_pts),
        ("Must Have", f"{len(must)} epics ({sum(e.get('story_points', 0) for e in must)} SP)"),
        ("Should Have", f"{len(should)} epics ({sum(e.get('story_points', 0) for e in should)} SP)"),
        ("Could Have", f"{len(could)} epics ({sum(e.get('story_points', 0) for e in could)} SP)"),
        ("Milestones", len(config.get("milestones", []))),
        ("Teams", len(config.get("teams", []))),
    ]

    row = 4
    ws.cell(row=row, column=1, value="Metric").font = Font(bold=True)
    ws.cell(row=row, column=2, value="Value").font = Font(bold=True)
    for i, (metric, value) in enumerate(stats):
        ws.cell(row=row + 1 + i, column=1, value=metric).border = BORDER
        ws.cell(row=row + 1 + i, column=2, value=str(value)).border = BORDER

    # Themes
    themes = config.get("themes", [])
    if themes:
        t_row = row + len(stats) + 3
        ws.cell(row=t_row, column=1, value="Strategic Themes").font = Font(bold=True, size=12, color="2F5496")
        for i, theme in enumerate(themes):
            ws.cell(row=t_row + 1 + i, column=1, value=f"🎯 {theme.get('name', '')}").border = BORDER
            ws.cell(row=t_row + 1 + i, column=2, value=theme.get("objective", "")).border = BORDER

    auto_width(ws)
    ws.sheet_properties.tabColor = "2F5496"


def create_scope_sheet(wb, config):
    ws = wb.create_sheet("Scope")
    themes = {t["id"]: t for t in config.get("themes", [])}

    ws.merge_cells("A1:K1")
    ws["A1"] = "Release Scope"
    ws["A1"].font = TITLE_FONT

    headers = ["ID", "Title", "Theme", "Owner", "Priority", "Story Points",
               "Quarter", "Status", "Confidence", "Dependencies", "Notes"]
    row = 3
    for c, h in enumerate(headers, 1):
        ws.cell(row=row, column=c, value=h)
    style_header(ws, row, len(headers))

    for i, e in enumerate(config.get("epics", [])):
        r = row + 1 + i
        theme = themes.get(e.get("theme_id", ""), {})
        priority = e.get("priority", "")
        confidence = e.get("confidence", "")
        deps = ", ".join(e.get("dependencies", [])) or "—"

        ws.cell(row=r, column=1, value=e.get("id", "")).border = BORDER
        ws.cell(row=r, column=2, value=e.get("title", "")).border = BORDER
        ws.cell(row=r, column=3, value=theme.get("name", "")).border = BORDER
        ws.cell(row=r, column=4, value=e.get("owner", "")).border = BORDER

        p_cell = ws.cell(row=r, column=5, value=priority)
        p_cell.border = BORDER
        if priority in PRIORITY_FILLS:
            p_cell.fill = PRIORITY_FILLS[priority]

        ws.cell(row=r, column=6, value=e.get("story_points", "")).border = BORDER
        ws.cell(row=r, column=7, value=e.get("quarter", "")).border = BORDER
        ws.cell(row=r, column=8, value=e.get("status", "")).border = BORDER

        c_cell = ws.cell(row=r, column=9, value=confidence)
        c_cell.border = BORDER
        if confidence in CONF_FILLS:
            c_cell.fill = CONF_FILLS[confidence]

        ws.cell(row=r, column=10, value=deps).border = BORDER
        ws.cell(row=r, column=11, value="").border = BORDER

    auto_width(ws)
    ws.column_dimensions["B"].width = 30
    ws.sheet_properties.tabColor = "E94560"


def create_milestones_sheet(wb, config):
    ws = wb.create_sheet("Milestones")

    ws.merge_cells("A1:F1")
    ws["A1"] = "Release Milestones"
    ws["A1"].font = TITLE_FONT

    headers = ["Milestone", "Date", "Type", "Owner", "Status", "Notes"]
    row = 3
    for c, h in enumerate(headers, 1):
        ws.cell(row=row, column=c, value=h)
    style_header(ws, row, len(headers))

    milestones = config.get("milestones", [])
    # Add standard release milestones if not present
    standard = [
        {"name": "Scope Freeze", "type": "internal", "date": ""},
        {"name": "Feature Complete", "type": "internal", "date": ""},
        {"name": "Code Freeze", "type": "internal", "date": ""},
        {"name": "QA Sign-off", "type": "internal", "date": ""},
        {"name": "Go/No-Go Decision", "type": "decision", "date": ""},
        {"name": "Production Release", "type": "release", "date": ""},
    ]
    existing_names = {m.get("name", "").lower() for m in milestones}
    for s in standard:
        if s["name"].lower() not in existing_names:
            milestones.append(s)

    for i, ms in enumerate(milestones):
        r = row + 1 + i
        ws.cell(row=r, column=1, value=ms.get("name", "")).border = BORDER
        ws.cell(row=r, column=2, value=ms.get("date", "")).border = BORDER
        ws.cell(row=r, column=3, value=ms.get("type", "")).border = BORDER
        ws.cell(row=r, column=4, value=ms.get("owner", "")).border = BORDER
        ws.cell(row=r, column=5, value=ms.get("status", "")).border = BORDER
        ws.cell(row=r, column=6, value="").border = BORDER

    auto_width(ws)
    ws.sheet_properties.tabColor = "4CAF50"


def create_capacity_sheet(wb, config):
    ws = wb.create_sheet("Capacity")

    ws.merge_cells("A1:G1")
    ws["A1"] = "Team Capacity Planning"
    ws["A1"].font = TITLE_FONT

    teams = config.get("teams", [])
    epics = config.get("epics", [])

    headers = ["Team", "Capacity/Sprint (SP)", "Total Sprints", "Total Capacity",
               "Allocated (SP)", "Available (SP)", "Utilization %"]
    row = 3
    for c, h in enumerate(headers, 1):
        ws.cell(row=row, column=c, value=h)
    style_header(ws, row, len(headers))

    # Estimate sprints from timeframe
    total_sprints = 6  # Default

    for i, team in enumerate(teams):
        r = row + 1 + i
        cap_per_sprint = team.get("capacity_per_sprint", 30)
        total_cap = cap_per_sprint * total_sprints

        # Calculate allocation for this team
        team_name = team.get("name", "")
        allocated = sum(e.get("story_points", 0) for e in epics if e.get("owner", "") == team_name)
        available = total_cap - allocated
        util = round(allocated / total_cap * 100, 1) if total_cap > 0 else 0

        ws.cell(row=r, column=1, value=team_name).border = BORDER
        ws.cell(row=r, column=2, value=cap_per_sprint).border = BORDER
        ws.cell(row=r, column=3, value=total_sprints).border = BORDER
        ws.cell(row=r, column=4, value=total_cap).border = BORDER
        ws.cell(row=r, column=5, value=allocated).border = BORDER
        ws.cell(row=r, column=6, value=available).border = BORDER

        util_cell = ws.cell(row=r, column=7, value=f"{util}%")
        util_cell.border = BORDER
        if util > 90:
            util_cell.fill = PatternFill(start_color="FFCDD2", end_color="FFCDD2", fill_type="solid")
        elif util > 75:
            util_cell.fill = PatternFill(start_color="FFF9C4", end_color="FFF9C4", fill_type="solid")

        for c in range(1, len(headers) + 1):
            ws.cell(row=r, column=c).alignment = Alignment(horizontal="center")

    auto_width(ws)
    ws.sheet_properties.tabColor = "FF9800"


def create_risks_sheet(wb, config):
    ws = wb.create_sheet("Risks")

    ws.merge_cells("A1:G1")
    ws["A1"] = "Risk Register"
    ws["A1"].font = TITLE_FONT

    headers = ["Risk", "Category", "Probability", "Impact", "Risk Level",
               "Mitigation", "Owner"]
    row = 3
    for c, h in enumerate(headers, 1):
        ws.cell(row=row, column=c, value=h)
    style_header(ws, row, len(headers))

    # Pre-populate with common risks based on data
    epics = config.get("epics", [])
    risks = []

    # Dependency risks
    dep_count = sum(len(e.get("dependencies", [])) for e in epics)
    if dep_count > 3:
        risks.append({
            "risk": f"Cross-epic dependencies ({dep_count} total)",
            "category": "Dependency",
            "probability": "Medium",
            "impact": "High",
            "mitigation": "Weekly dependency review, API contract-first development",
        })

    # Capacity risks
    low_conf = [e for e in epics if e.get("confidence") == "Low"]
    if low_conf:
        risks.append({
            "risk": f"{len(low_conf)} epics with Low confidence estimates",
            "category": "Estimation",
            "probability": "High",
            "impact": "Medium",
            "mitigation": "Run spikes for unknowns, use PERT estimation, add buffer",
        })

    # Scope risks
    must_pts = sum(e.get("story_points", 0) for e in epics if e.get("priority") == "Must")
    could_pts = sum(e.get("story_points", 0) for e in epics if e.get("priority") == "Could")
    if could_pts > must_pts * 0.5:
        risks.append({
            "risk": "Significant 'Could Have' scope may cause overcommitment",
            "category": "Scope",
            "probability": "Medium",
            "impact": "Medium",
            "mitigation": "Scope freeze date, MoSCoW discipline, cut 'Could' items first",
        })

    # Add blank rows for manual entry
    for _ in range(5):
        risks.append({"risk": "", "category": "", "probability": "", "impact": "", "mitigation": ""})

    risk_level_map = {
        ("High", "High"): "Critical",
        ("High", "Medium"): "High",
        ("Medium", "High"): "High",
        ("Medium", "Medium"): "Medium",
        ("Low", "High"): "Medium",
        ("High", "Low"): "Medium",
        ("Medium", "Low"): "Low",
        ("Low", "Medium"): "Low",
        ("Low", "Low"): "Low",
    }

    for i, risk in enumerate(risks):
        r = row + 1 + i
        ws.cell(row=r, column=1, value=risk.get("risk", "")).border = BORDER
        ws.cell(row=r, column=2, value=risk.get("category", "")).border = BORDER
        ws.cell(row=r, column=3, value=risk.get("probability", "")).border = BORDER
        ws.cell(row=r, column=4, value=risk.get("impact", "")).border = BORDER

        prob = risk.get("probability", "")
        imp = risk.get("impact", "")
        level = risk_level_map.get((prob, imp), "")
        level_cell = ws.cell(row=r, column=5, value=level)
        level_cell.border = BORDER
        if level == "Critical":
            level_cell.fill = PatternFill(start_color="FFCDD2", end_color="FFCDD2", fill_type="solid")
        elif level == "High":
            level_cell.fill = PatternFill(start_color="FFE0B2", end_color="FFE0B2", fill_type="solid")

        ws.cell(row=r, column=6, value=risk.get("mitigation", "")).border = BORDER
        ws.cell(row=r, column=7, value=risk.get("owner", "")).border = BORDER

    auto_width(ws)
    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["F"].width = 45
    ws.sheet_properties.tabColor = "F44336"


def create_dependencies_sheet(wb, config):
    ws = wb.create_sheet("Dependencies")

    ws.merge_cells("A1:G1")
    ws["A1"] = "Dependency Register"
    ws["A1"].font = TITLE_FONT

    headers = ["From (Dependent)", "To (Provider)", "Type", "Description",
               "Status", "Risk Level", "Owner"]
    row = 3
    for c, h in enumerate(headers, 1):
        ws.cell(row=row, column=c, value=h)
    style_header(ws, row, len(headers))

    epic_map = {e["id"]: e for e in config.get("epics", [])}
    dep_row = row + 1
    for e in config.get("epics", []):
        for dep_id in e.get("dependencies", []):
            dep_epic = epic_map.get(dep_id, {})
            ws.cell(row=dep_row, column=1, value=f"{e['id']}: {e.get('title', '')}").border = BORDER
            ws.cell(row=dep_row, column=2, value=f"{dep_id}: {dep_epic.get('title', dep_id)}").border = BORDER
            ws.cell(row=dep_row, column=3, value="Technical").border = BORDER
            ws.cell(row=dep_row, column=4, value="").border = BORDER
            ws.cell(row=dep_row, column=5, value="").border = BORDER
            ws.cell(row=dep_row, column=6, value="").border = BORDER
            ws.cell(row=dep_row, column=7, value="").border = BORDER
            dep_row += 1

    # Blank rows for manual entry
    for _ in range(5):
        for c in range(1, len(headers) + 1):
            ws.cell(row=dep_row, column=c, value="").border = BORDER
        dep_row += 1

    auto_width(ws)
    ws.sheet_properties.tabColor = "9C27B0"


def generate_release_xlsx(config, output_path):
    wb = openpyxl.Workbook()
    create_overview_sheet(wb, config)
    create_scope_sheet(wb, config)
    create_milestones_sheet(wb, config)
    create_capacity_sheet(wb, config)
    create_risks_sheet(wb, config)
    create_dependencies_sheet(wb, config)
    wb.save(output_path)
    print(f"Release plan saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate Release Planning Spreadsheet")
    parser.add_argument("--config", help="JSON config path")
    parser.add_argument("--output", default="release_plan.xlsx")
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = json.load(sys.stdin)

    generate_release_xlsx(config, args.output)


if __name__ == "__main__":
    main()

```


---

<!-- Script: scripts/generate_roadmap_html.py -->

# Script: generate_roadmap_html.py

```python
#!/usr/bin/env python3
"""
Generate interactive HTML roadmap visualizations.

Supports 4 styles: now-next-later, timeline, theme, feature
Supports 2 views: internal (full detail), external (stakeholder-friendly)

Usage:
    python generate_roadmap_html.py \
        --config roadmap.json \
        --style now-next-later|timeline|theme|feature \
        --view internal|external \
        --output roadmap.html
"""

import json
import sys
import argparse
from datetime import datetime


STATUS_MAP_EXTERNAL = {
    "Backlog": "Planned",
    "Refined": "Planned",
    "Ready": "Planned",
    "In Progress": "In Development",
    "In Review": "Coming Soon",
    "Testing": "Coming Soon",
    "Done": "Available",
    "Released": "Available",
}

CONFIDENCE_STYLES = {
    "High": {"opacity": "1", "border": "solid", "badge_color": "#4CAF50"},
    "Medium": {"opacity": "0.85", "border": "dashed", "badge_color": "#FF9800"},
    "Low": {"opacity": "0.65", "border": "dotted", "badge_color": "#f44336"},
}

PRIORITY_COLORS = {
    "Must": "#e94560",
    "Should": "#FF9800",
    "Could": "#2196F3",
    "Won't": "#78909C",
}


def filter_for_external(epics):
    """Filter and transform epics for external/stakeholder view."""
    external = []
    for e in epics:
        if not e.get("external_visible", True):
            continue
        ext = {
            "id": e.get("id", ""),
            "title": e.get("external_title", e.get("title", "")),
            "description": e.get("external_description", e.get("description", "")),
            "theme_id": e.get("theme_id", ""),
            "status": STATUS_MAP_EXTERNAL.get(e.get("status", ""), e.get("status", "")),
            "timeframe": e.get("timeframe", ""),
            "quarter": e.get("quarter", ""),
            "confidence": e.get("confidence", "Medium"),
        }
        # Broaden time specificity for external
        q = e.get("quarter", "")
        if q:
            ext["quarter"] = q  # Keep quarter-level for external
        external.append(ext)
    return external


def generate_now_next_later(config, view):
    """Generate Now/Next/Later board."""
    product = config.get("product_name", "Product")
    epics = config.get("epics", [])
    themes = {t["id"]: t for t in config.get("themes", [])}
    is_external = view == "external"

    if is_external:
        epics = filter_for_external(epics)

    columns = {
        "now": {"label": "Now", "subtitle": "In Progress", "color": "#4CAF50", "items": []},
        "next": {"label": "Next", "subtitle": "1-3 Sprints", "color": "#FF9800", "items": []},
        "later": {"label": "Later", "subtitle": "Exploring", "color": "#2196F3", "items": []},
    }

    for e in epics:
        tf = e.get("timeframe", "later").lower()
        if tf in columns:
            columns[tf]["items"].append(e)

    title = f"{product} Roadmap" + (" — Stakeholder View" if is_external else "")
    subtitle = f"Last updated: {config.get('last_updated', datetime.now().strftime('%Y-%m-%d'))}"

    cols_html = ""
    for key, col in columns.items():
        items_html = ""
        for e in col["items"]:
            theme = themes.get(e.get("theme_id", ""), {})
            theme_name = theme.get("name", "")
            theme_color = theme.get("color", "#666")
            conf = e.get("confidence", "Medium")
            conf_style = CONFIDENCE_STYLES.get(conf, CONFIDENCE_STYLES["Medium"])

            detail_html = ""
            if not is_external:
                owner = e.get("owner", "")
                points = e.get("story_points", "")
                detail_html = f"""
                    <div class="epic-meta">
                        {"<span>👤 " + owner + "</span>" if owner else ""}
                        {"<span>📊 " + str(points) + " SP</span>" if points else ""}
                        <span style="color:{conf_style['badge_color']}">● {conf}</span>
                    </div>"""

            deps = e.get("dependencies", [])
            deps_html = ""
            if deps and not is_external:
                deps_html = f'<div class="epic-deps">🔗 Depends on: {", ".join(deps)}</div>'

            items_html += f"""
            <div class="epic-card" style="opacity:{conf_style['opacity']}; border-left: 4px {conf_style['border']} {col['color']}">
                {"<div class='theme-badge' style='background:" + theme_color + "22; color:" + theme_color + "'>" + theme_name + "</div>" if theme_name else ""}
                <div class="epic-title">{e.get('title', '')}</div>
                <div class="epic-desc">{e.get('description', '')}</div>
                {detail_html}
                {deps_html}
                <div class="epic-status">{e.get('status', '')}</div>
            </div>"""

        cols_html += f"""
        <div class="roadmap-column">
            <div class="column-header" style="background:{col['color']}20; border-bottom: 3px solid {col['color']}">
                <div class="col-title" style="color:{col['color']}">{col['label']}</div>
                <div class="col-subtitle">{col['subtitle']}</div>
                <div class="col-count">{len(col['items'])} items</div>
            </div>
            <div class="column-items">{items_html}</div>
        </div>"""

    return _wrap_html(title, subtitle, f'<div class="nnl-board">{cols_html}</div>',
                      is_external, config)


def generate_timeline(config, view):
    """Generate timeline/Gantt roadmap."""
    product = config.get("product_name", "Product")
    epics = config.get("epics", [])
    themes = {t["id"]: t for t in config.get("themes", [])}
    milestones = config.get("milestones", [])
    is_external = view == "external"

    if is_external:
        epics = filter_for_external(epics)

    title = f"{product} Timeline" + (" — Stakeholder View" if is_external else "")
    subtitle = f"{config.get('timeframe', '')} | Updated: {config.get('last_updated', '')}"

    # Group by quarter
    quarters = {}
    for e in epics:
        q = e.get("quarter", "Unscheduled")
        if q not in quarters:
            quarters[q] = []
        quarters[q].append(e)

    timeline_html = ""
    for q, items in sorted(quarters.items()):
        items_html = ""
        for e in items:
            theme = themes.get(e.get("theme_id", ""), {})
            conf = e.get("confidence", "Medium")
            conf_style = CONFIDENCE_STYLES.get(conf, CONFIDENCE_STYLES["Medium"])
            priority = e.get("priority", "Should")
            p_color = PRIORITY_COLORS.get(priority, "#666")

            meta = ""
            if not is_external:
                meta = f"""<span class="meta-item">👤 {e.get('owner', 'TBD')}</span>
                          <span class="meta-item">📊 {e.get('story_points', '?')} SP</span>
                          <span class="meta-item" style="color:{p_color}">● {priority}</span>"""

            items_html += f"""
            <div class="timeline-item" style="opacity:{conf_style['opacity']}; border-left: 4px solid {theme.get('color', '#666')}">
                <div class="tl-header">
                    <span class="tl-title">{e.get('title', '')}</span>
                    <span class="tl-conf" style="color:{conf_style['badge_color']}">{conf}</span>
                </div>
                <div class="tl-desc">{e.get('description', '')}</div>
                <div class="tl-meta">{meta}</div>
                <div class="tl-status">{e.get('status', '')}</div>
            </div>"""

        timeline_html += f"""
        <div class="quarter-section">
            <div class="quarter-header">{q}</div>
            <div class="quarter-items">{items_html}</div>
        </div>"""

    # Milestones
    if milestones:
        ms_html = "".join(
            f'<div class="milestone"><span class="ms-icon">{"▼" if m.get("type") == "release" else "◆"}</span>'
            f'<span class="ms-name">{m.get("name", "")}</span>'
            f'<span class="ms-date">{m.get("date", "")}</span></div>'
            for m in milestones
        )
        timeline_html += f'<div class="milestones-section"><h3>Key Milestones</h3>{ms_html}</div>'

    return _wrap_html(title, subtitle, f'<div class="timeline-board">{timeline_html}</div>',
                      is_external, config)


def generate_theme_based(config, view):
    """Generate theme-based roadmap."""
    product = config.get("product_name", "Product")
    epics = config.get("epics", [])
    themes_list = config.get("themes", [])
    is_external = view == "external"

    if is_external:
        epics = filter_for_external(epics)

    title = f"{product} Strategic Roadmap" + (" — Stakeholder View" if is_external else "")
    subtitle = f"{config.get('timeframe', '')} | Updated: {config.get('last_updated', '')}"

    themes_html = ""
    for theme in themes_list:
        theme_epics = [e for e in epics if e.get("theme_id") == theme["id"]]
        if not theme_epics and is_external:
            continue

        items_html = ""
        for e in theme_epics:
            conf = e.get("confidence", "Medium")
            conf_style = CONFIDENCE_STYLES.get(conf, CONFIDENCE_STYLES["Medium"])
            tf = e.get("timeframe", "")
            tf_badge = {"now": "🟢 Now", "next": "🟡 Next", "later": "🔵 Later"}.get(tf, tf)

            meta = ""
            if not is_external:
                meta = f"""<span>{e.get('owner', '')}</span> · <span>{e.get('story_points', '?')} SP</span>"""

            items_html += f"""
            <div class="theme-epic" style="opacity:{conf_style['opacity']}">
                <div class="te-header">
                    <span class="te-title">{e.get('title', '')}</span>
                    <span class="te-horizon">{tf_badge}</span>
                </div>
                <div class="te-desc">{e.get('description', '')}</div>
                {"<div class='te-meta'>" + meta + "</div>" if meta else ""}
                <div class="te-status">{e.get('status', '')} · {e.get('quarter', '')}</div>
            </div>"""

        themes_html += f"""
        <div class="theme-block" style="border-left: 4px solid {theme.get('color', '#666')}">
            <div class="theme-header" style="background:{theme.get('color', '#666')}15">
                <div class="th-title" style="color:{theme.get('color', '#666')}">🎯 {theme.get('name', '')}</div>
                <div class="th-objective">{theme.get('objective', '')}</div>
            </div>
            <div class="theme-items">{items_html}</div>
        </div>"""

    return _wrap_html(title, subtitle, f'<div class="theme-board">{themes_html}</div>',
                      is_external, config)


def generate_feature_based(config, view):
    """Generate feature-based detailed roadmap."""
    product = config.get("product_name", "Product")
    epics = config.get("epics", [])
    themes = {t["id"]: t for t in config.get("themes", [])}
    is_external = view == "external"

    if is_external:
        epics = filter_for_external(epics)

    title = f"{product} Feature Roadmap" + (" — Stakeholder View" if is_external else "")
    subtitle = f"{config.get('timeframe', '')} | {len(epics)} features"

    # Build table
    if is_external:
        headers = ["Feature", "Category", "Status", "Timeline"]
    else:
        headers = ["ID", "Feature", "Theme", "Owner", "Priority", "Points", "Quarter",
                    "Status", "Confidence", "Dependencies"]

    rows_html = ""
    for e in epics:
        theme = themes.get(e.get("theme_id", ""), {})
        conf = e.get("confidence", "Medium")
        conf_style = CONFIDENCE_STYLES.get(conf, CONFIDENCE_STYLES["Medium"])
        p_color = PRIORITY_COLORS.get(e.get("priority", ""), "#666")

        if is_external:
            rows_html += f"""
            <tr style="opacity:{conf_style['opacity']}">
                <td><strong>{e.get('title', '')}</strong><br><small>{e.get('description', '')}</small></td>
                <td>{theme.get('name', '')}</td>
                <td><span class="status-badge">{e.get('status', '')}</span></td>
                <td>{e.get('quarter', '')}</td>
            </tr>"""
        else:
            deps = ", ".join(e.get("dependencies", [])) or "—"
            rows_html += f"""
            <tr style="opacity:{conf_style['opacity']}">
                <td><code>{e.get('id', '')}</code></td>
                <td><strong>{e.get('title', '')}</strong></td>
                <td style="color:{theme.get('color', '#666')}">{theme.get('name', '')}</td>
                <td>{e.get('owner', '')}</td>
                <td style="color:{p_color}">{e.get('priority', '')}</td>
                <td>{e.get('story_points', '')}</td>
                <td>{e.get('quarter', '')}</td>
                <td><span class="status-badge">{e.get('status', '')}</span></td>
                <td style="color:{conf_style['badge_color']}">{conf}</td>
                <td>{deps}</td>
            </tr>"""

    th_html = "".join(f"<th>{h}</th>" for h in headers)
    table_html = f"""
    <div class="feature-table-wrap">
        <table class="feature-table">
            <thead><tr>{th_html}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>"""

    return _wrap_html(title, subtitle, table_html, is_external, config)


def _wrap_html(title, subtitle, content, is_external, config):
    """Wrap content in the standard HTML template."""
    disclaimer = ""
    if is_external:
        disclaimer = """<div class="disclaimer">
            This roadmap represents our current direction. Timelines and features are subject
            to change. Items marked "Planned" are under consideration but not yet committed.
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0f0f23;
            color: #eee;
            padding: 2rem;
        }}
        h1 {{ color: #e94560; font-size: 1.5rem; margin-bottom: 0.3rem; }}
        .subtitle {{ color: #888; font-size: 0.85rem; margin-bottom: 1.5rem; }}
        .disclaimer {{
            background: #1a1a2e;
            border: 1px solid #e9456033;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            color: #aaa;
            font-size: 0.8rem;
            margin-bottom: 1.5rem;
            font-style: italic;
        }}
        /* Now/Next/Later */
        .nnl-board {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }}
        .roadmap-column {{ background: #1a1a2e; border-radius: 12px; border: 1px solid #333; overflow: hidden; }}
        .column-header {{ padding: 1rem; text-align: center; }}
        .col-title {{ font-size: 1.2rem; font-weight: 700; }}
        .col-subtitle {{ font-size: 0.8rem; color: #888; }}
        .col-count {{ font-size: 0.75rem; color: #666; margin-top: 0.2rem; }}
        .column-items {{ padding: 0.75rem; display: flex; flex-direction: column; gap: 0.75rem; }}
        .epic-card {{ background: #16213e; border-radius: 8px; padding: 0.75rem; }}
        .theme-badge {{ font-size: 0.7rem; padding: 0.15rem 0.5rem; border-radius: 10px; display: inline-block; margin-bottom: 0.4rem; }}
        .epic-title {{ font-weight: 600; font-size: 0.95rem; margin-bottom: 0.3rem; }}
        .epic-desc {{ font-size: 0.8rem; color: #aaa; margin-bottom: 0.4rem; }}
        .epic-meta {{ display: flex; gap: 0.75rem; font-size: 0.75rem; color: #888; margin-bottom: 0.3rem; }}
        .epic-deps {{ font-size: 0.7rem; color: #FF9800; margin-bottom: 0.3rem; }}
        .epic-status {{ font-size: 0.7rem; color: #4CAF50; }}
        /* Timeline */
        .timeline-board {{ display: flex; flex-direction: column; gap: 1.5rem; }}
        .quarter-section {{ background: #1a1a2e; border-radius: 12px; border: 1px solid #333; overflow: hidden; }}
        .quarter-header {{ background: #16213e; padding: 0.75rem 1rem; font-weight: 700; font-size: 1.1rem; color: #e94560; }}
        .quarter-items {{ padding: 0.75rem; display: flex; flex-direction: column; gap: 0.5rem; }}
        .timeline-item {{ background: #16213e; border-radius: 8px; padding: 0.75rem; }}
        .tl-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .tl-title {{ font-weight: 600; }}
        .tl-conf {{ font-size: 0.8rem; }}
        .tl-desc {{ font-size: 0.8rem; color: #aaa; margin: 0.3rem 0; }}
        .tl-meta {{ font-size: 0.75rem; color: #888; display: flex; gap: 0.5rem; }}
        .tl-status {{ font-size: 0.7rem; color: #4CAF50; margin-top: 0.3rem; }}
        .meta-item {{ display: inline; }}
        .milestones-section {{ background: #1a1a2e; border-radius: 12px; border: 1px solid #333; padding: 1rem; }}
        .milestones-section h3 {{ color: #e94560; margin-bottom: 0.75rem; font-size: 1rem; }}
        .milestone {{ display: flex; gap: 1rem; padding: 0.4rem 0; align-items: center; border-bottom: 1px solid #222; }}
        .ms-icon {{ font-size: 1rem; }}
        .ms-name {{ flex: 1; }}
        .ms-date {{ color: #888; font-size: 0.85rem; }}
        /* Theme-based */
        .theme-board {{ display: flex; flex-direction: column; gap: 1.5rem; }}
        .theme-block {{ background: #1a1a2e; border-radius: 12px; overflow: hidden; }}
        .theme-header {{ padding: 1rem; }}
        .th-title {{ font-size: 1.1rem; font-weight: 700; }}
        .th-objective {{ font-size: 0.85rem; color: #aaa; margin-top: 0.2rem; }}
        .theme-items {{ padding: 0.75rem; display: flex; flex-direction: column; gap: 0.5rem; }}
        .theme-epic {{ background: #16213e; border-radius: 8px; padding: 0.75rem; }}
        .te-header {{ display: flex; justify-content: space-between; }}
        .te-title {{ font-weight: 600; }}
        .te-horizon {{ font-size: 0.8rem; }}
        .te-desc {{ font-size: 0.8rem; color: #aaa; margin: 0.3rem 0; }}
        .te-meta {{ font-size: 0.75rem; color: #888; }}
        .te-status {{ font-size: 0.7rem; color: #4CAF50; margin-top: 0.3rem; }}
        /* Feature table */
        .feature-table-wrap {{ overflow-x: auto; }}
        .feature-table {{ width: 100%; border-collapse: collapse; background: #1a1a2e; border-radius: 12px; overflow: hidden; }}
        .feature-table th {{ background: #16213e; color: #e94560; padding: 0.75rem; text-align: left; font-size: 0.8rem; text-transform: uppercase; }}
        .feature-table td {{ padding: 0.6rem 0.75rem; border-bottom: 1px solid #222; font-size: 0.85rem; }}
        .feature-table tr:hover {{ background: #16213e88; }}
        .status-badge {{ font-size: 0.75rem; padding: 0.15rem 0.5rem; background: #4CAF5022; color: #4CAF50; border-radius: 10px; }}
        @media (max-width: 900px) {{ .nnl-board {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="subtitle">{subtitle}</div>
    {disclaimer}
    {content}
</body>
</html>"""


GENERATORS = {
    "now-next-later": generate_now_next_later,
    "timeline": generate_timeline,
    "theme": generate_theme_based,
    "feature": generate_feature_based,
}


def main():
    parser = argparse.ArgumentParser(description="Generate Roadmap HTML")
    parser.add_argument("--config", help="JSON config path")
    parser.add_argument("--style", choices=GENERATORS.keys(), default="now-next-later")
    parser.add_argument("--view", choices=["internal", "external"], default="internal")
    parser.add_argument("--output", default="roadmap.html")
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = json.load(sys.stdin)

    html = GENERATORS[args.style](config, args.view)

    with open(args.output, "w") as f:
        f.write(html)
    print(f"Roadmap ({args.style}, {args.view}) saved to: {args.output}")


if __name__ == "__main__":
    main()

```
