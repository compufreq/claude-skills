---
name: agile-roadmap-builder
description: >-
  Agile roadmap creation, release planning, and dependency mapping. Use when the user mentions product roadmap, release plan, now-next-later, timeline roadmap, outcome-based roadmap, dependency mapping, cross-team dependencies, milestone planning, quarterly planning, PI planning, or asks to build roadmaps, plan releases, or map dependencies.
---

# Agile Roadmap Builder

A production-grade skill for building product roadmaps, release plans, and dependency maps.
Supports four roadmap styles with dual internal/external views for stakeholder management.

## Quick Reference

| Roadmap Style | Best For | Outputs |
|---------------|----------|---------|
| Now / Next / Later | Lean teams, early-stage products | HTML board, Markdown doc |
| Timeline (quarters/months) | Executive communication, program planning | Interactive HTML, XLSX |
| Theme-based | Strategy alignment, OKR-driven teams | HTML, Markdown, XLSX |
| Feature-based | Detailed planning, engineering teams | XLSX, Markdown |

| Additional Outputs | Description |
|--------------------|-------------|
| Dependency Map | Interactive graph showing epic/team dependencies |
| Release Plan | Spreadsheet with milestones, dates, scope, risks |
| Stakeholder View | Simplified external roadmap without estimates |

## Core Workflow

1. **Identify roadmap style** — Ask if not stated. Use context clues:
   - "What's coming" → Now/Next/Later
   - "Q1/Q2 plan" → Timeline
   - "Strategic pillars" → Theme-based
   - "Feature list with dates" → Feature-based

2. **Identify the audience** — Internal (team/engineering) or external (stakeholders/customers)?
   If both, produce dual views.

3. **Gather roadmap data** — Features/epics, priorities, timeframes, dependencies, owners.

4. **Read relevant references:**
   - Roadmap styles → `references/roadmap-styles.md`
   - Release planning → `references/release-planning.md`
   - Dependency mapping → `references/dependency-mapping.md`

5. **Generate outputs** using scripts or inline markdown.

---

## Data Input Schema

All scripts accept this unified JSON format:

```json
{
  "product_name": "Acme Platform",
  "team_name": "Product Engineering",
  "timeframe": "Q1-Q3 2025",
  "last_updated": "2025-01-15",
  "themes": [
    {
      "id": "T1",
      "name": "User Growth",
      "objective": "Increase MAU by 40%",
      "color": "#4CAF50"
    }
  ],
  "epics": [
    {
      "id": "E1",
      "title": "Social Login",
      "theme_id": "T1",
      "description": "OAuth login via Google, GitHub, Apple",
      "owner": "Auth Team",
      "priority": "Must",
      "timeframe": "now",
      "quarter": "Q1 2025",
      "start_month": "2025-01",
      "end_month": "2025-02",
      "status": "In Progress",
      "confidence": "High",
      "story_points": 34,
      "dependencies": ["E3"],
      "milestones": [
        {"name": "Google OAuth live", "date": "2025-01-31"}
      ],
      "external_visible": true,
      "external_title": "More sign-in options",
      "external_description": "Sign in with your existing accounts"
    }
  ],
  "milestones": [
    {
      "name": "Beta Launch",
      "date": "2025-03-15",
      "type": "release"
    }
  ],
  "teams": [
    {"id": "auth", "name": "Auth Team", "capacity_per_sprint": 30}
  ]
}
```

### Field Notes
- `timeframe`: "now" | "next" | "later" for lean roadmaps; "Q1 2025" etc. for timeline
- `confidence`: "High" | "Medium" | "Low" — affects how items display
- `external_visible`: Whether this epic appears on the stakeholder roadmap
- `external_title` / `external_description`: Simplified language for external view
- `dependencies`: Array of epic IDs this epic depends on

---

## Roadmap Styles

### 1. Now / Next / Later (Lean Roadmap)

The simplest, most Agile-friendly roadmap. No dates — just horizons.

| Horizon | Meaning | Confidence | Detail Level |
|---------|---------|-----------|-------------|
| **Now** | Currently in progress or starting this sprint | High | Full stories, assigned |
| **Next** | Coming in 1-3 sprints | Medium | Epics with rough sizing |
| **Later** | On the radar, 3+ sprints out | Low | Themes or large epics |

Best when:
- Stakeholders push for dates but the team isn't ready to commit
- Product discovery is ongoing
- Early-stage product with shifting priorities

### 2. Timeline (Quarters / Months)

Classic Gantt-style roadmap with items placed on a calendar.

Structure:
```
Q1 2025          Q2 2025          Q3 2025
|---- Epic 1 ----|
     |---- Epic 2 --------|
                  |---- Epic 3 ----|
▼ Milestone 1    ▼ Milestone 2
```

Best when:
- Reporting to executives or board
- Coordinating across multiple teams
- External commitments require date ranges

### 3. Theme-Based

Groups features under strategic themes or OKR objectives.

Structure:
```
🎯 Theme: User Growth (Increase MAU by 40%)
  ├── Epic: Social Login [Q1] [High Confidence]
  ├── Epic: Referral Program [Q1-Q2] [Medium]
  └── Epic: Onboarding Redesign [Q2] [Low]

🎯 Theme: Revenue (Increase ARPU by 20%)
  ├── Epic: Premium Tier [Q1] [High]
  └── Epic: Usage-Based Billing [Q2-Q3] [Medium]
```

Best when:
- Aligning product work to company strategy/OKRs
- Communicating "why" not just "what"
- Multiple stakeholders care about different themes

### 4. Feature-Based

Detailed feature list with dates, owners, and estimates.

Best when:
- Engineering teams need granular planning
- Release coordination requires feature-level tracking
- Teams need to see capacity allocation

---

## Internal vs External Views

### Internal Roadmap (Engineering/Team)
Includes:
- Story point estimates and capacity data
- Technical dependencies and architecture notes
- Confidence levels with reasoning
- Risk assessments and mitigation plans
- Individual team/person assignments
- Sprint-level granularity for "Now" items

### External Roadmap (Stakeholders/Customers)
Excludes:
- All estimates (points, hours, capacity)
- Internal team names and assignments
- Technical dependencies and architecture details
- Confidence levels and risk data
- Sprint-level detail

Uses instead:
- `external_title` (simplified, benefit-focused language)
- `external_description` (user value, not technical detail)
- Broader timeframes ("Early 2025" not "Sprint 14")
- Status indicators (Planned, In Development, Coming Soon, Available)

### Status Mapping (Internal → External)

| Internal Status | External Status |
|----------------|-----------------|
| Backlog | Planned |
| Refined / Ready | Planned |
| In Progress | In Development |
| In Review / Testing | Coming Soon |
| Done / Released | Available |

---

## Scripts

### generate_roadmap_html.py

Generates interactive HTML roadmap visualizations. Supports all 4 styles.

```bash
python scripts/generate_roadmap_html.py \
  --config roadmap.json \
  --style now-next-later|timeline|theme|feature \
  --view internal|external \
  --output roadmap.html
```

### generate_dependency_map.py

Generates an interactive dependency graph showing relationships between epics/teams.

```bash
python scripts/generate_dependency_map.py \
  --config roadmap.json \
  --output dependencies.html
```

### generate_release_xlsx.py

Generates a release planning spreadsheet with milestones, scope, capacity, and risk tracking.

```bash
python scripts/generate_release_xlsx.py \
  --config roadmap.json \
  --output release_plan.xlsx
```

---

## Roadmap Document Template (Markdown)

For inline markdown generation:

```
# Product Roadmap — [Product Name]
**Last Updated:** [Date] | **Owner:** [Name] | **Period:** [Timeframe]

## Vision
[One-paragraph product vision]

## Strategic Themes
### 🎯 [Theme 1]: [Objective]
[Why this matters]

### 🎯 [Theme 2]: [Objective]
[Why this matters]

## Roadmap

### Now (In Progress)
| Epic | Theme | Owner | Status | Confidence |
|------|-------|-------|--------|-----------|

### Next (1-3 Sprints)
| Epic | Theme | Target | Confidence |
|------|-------|--------|-----------|

### Later (3+ Sprints)
| Epic | Theme | Rough Estimate |
|------|-------|---------------|

## Key Milestones
| Milestone | Date | Dependencies |
|-----------|------|-------------|

## Dependencies & Risks
| Dependency | From | To | Status | Risk Level |
|-----------|------|-----|--------|-----------|

## Assumptions
1. [Key assumption underlying this roadmap]
```

---

## Best Practices

1. Roadmaps are communication tools, not contracts — update them frequently
2. Lower confidence items should have less date specificity (quarter, not week)
3. Always show the "why" (theme/objective), not just the "what" (feature list)
4. External roadmaps should never include dates you aren't confident about
5. Dependencies are the #1 risk to roadmap delivery — visualize them explicitly
6. Review and update the roadmap at least monthly (or every 2 sprints)
7. Include a "dropped/deferred" section to show what was deprioritized and why
8. Capacity > ambition — don't roadmap more than your teams can deliver



---
