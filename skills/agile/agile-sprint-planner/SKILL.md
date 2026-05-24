---
name: agile-sprint-planner
description: >
  Comprehensive Agile sprint planning, backlog grooming, user story writing, and estimation skill
  for Scrum and Kanban teams. Use this skill whenever the user mentions sprint planning, backlog
  refinement, story writing, user stories, acceptance criteria, sprint goals, estimation, story
  points, t-shirt sizing, velocity, sprint capacity, backlog prioritization, product backlog,
  sprint backlog, Definition of Done, Definition of Ready, Kanban board setup, WIP limits,
  swimlanes, or any Agile planning artifact. Also trigger when the user asks to create a sprint
  plan document, estimate work, break down epics into stories, write acceptance criteria, plan a
  release, or produce any sprint-related spreadsheet or tracking document. Trigger even if the user
  doesn't say "Agile" explicitly but describes planning work in iterative cycles or asks for task
  breakdowns with priorities and estimates.
---

# Agile Sprint Planner

A production-grade skill for Agile sprint planning, backlog management, story writing, and
estimation. Supports both Scrum and Kanban frameworks with multiple estimation methods.

## Quick Reference

| Capability | Output Format |
|---|---|
| Sprint plan narratives | Markdown (.md) or Word (.docx) |
| Sprint/backlog tracking | Excel (.xlsx) |
| User stories & acceptance criteria | Markdown (.md) or Word (.docx) |
| Estimation worksheets | Excel (.xlsx) |
| Sprint reports & retrospectives | Markdown (.md) or Word (.docx) |

## Core Workflow

When this skill triggers, follow this decision flow:

1. **Identify the request type** — Is the user asking for:
   - Sprint planning (new sprint setup, goal setting, capacity planning)?
   - Backlog grooming (refinement, prioritization, splitting stories)?
   - Story writing (user stories, acceptance criteria, tasks)?
   - Estimation (story points, t-shirt sizing, time-based)?
   - Reporting (velocity, burndown, sprint review)?
   - Board setup (Kanban board, WIP limits, swimlanes)?

2. **Identify the framework** — Scrum or Kanban? If not stated, ask. Default to Scrum for
   sprint-based requests and Kanban for flow-based/continuous requests.

3. **Identify the output** — Does the user want a document (narrative), a spreadsheet (tracking),
   or both? If not stated, produce both for sprint plans and estimation; docs only for stories.

4. **Read the relevant reference file** before generating output:
   - For sprint planning → read `references/scrum-planning.md`
   - For Kanban setup → read `references/kanban-planning.md`
   - For story writing → read `references/story-writing.md`
   - For estimation → read `references/estimation-methods.md`

5. **Generate the output** using the templates and scripts in this skill.

---

## Sprint Planning (Scrum)

When creating a sprint plan, gather the following from the user (ask if not provided):

- **Team size & roles** — Number of developers, testers, designers
- **Sprint duration** — Typically 1-4 weeks (default: 2 weeks)
- **Team velocity** — Historical average story points per sprint (if available)
- **Sprint goal** — What the team aims to achieve
- **Candidate stories** — Backlog items under consideration

### Sprint Plan Document Structure

Produce a Markdown or Word document with this structure:

```
# Sprint Plan: [Sprint Name/Number]
## Sprint Goal
[One clear, measurable objective]

## Sprint Metadata
- Duration: [X weeks] ([Start Date] — [End Date])
- Team Capacity: [X story points / hours]
- Committed Velocity: [X story points]

## Committed Stories
| ID | Story Title | Priority | Estimate | Assignee | Status |
|----|-------------|----------|----------|----------|--------|

## Sprint Risks & Dependencies
- [Risk 1]: Mitigation strategy
- [Dependency 1]: Owner & status

## Definition of Done (Sprint Level)
- [ ] All committed stories meet story-level DoD
- [ ] No critical bugs remain open
- [ ] Sprint demo prepared
- [ ] Retrospective scheduled

## Capacity Planning
[Breakdown by team member with available days, ceremonies overhead, net capacity]
```

### Sprint Tracking Spreadsheet

Use the xlsx skill to produce a spreadsheet with these sheets:

1. **Sprint Backlog** — Columns: Story ID, Epic, Title, Description, Priority (MoSCoW),
   Story Points, T-shirt Size, Time Estimate (hours), Assignee, Status, Sprint Day columns
   for daily tracking, Notes
2. **Capacity Plan** — Columns: Team Member, Role, Total Days, Ceremony Days, PTO Days,
   Net Available Days, Allocated Points, Utilization %
3. **Burndown Data** — Columns: Sprint Day, Ideal Remaining, Actual Remaining, Stories
   Completed, Cumulative Points
4. **Velocity History** — Columns: Sprint Number, Committed Points, Completed Points,
   Velocity Delta, Rolling Average (3-sprint), Notes

Run `scripts/generate_sprint_xlsx.py` to produce the spreadsheet. The script accepts JSON
input with sprint configuration.

---

## Backlog Grooming & Prioritization

When grooming a backlog:

1. Help the user structure items using MoSCoW prioritization (Must, Should, Could, Won't)
   or Weighted Shortest Job First (WSJF) for SAFe-influenced teams.
2. Ensure each item has: Title, Description, Acceptance Criteria, Priority, Rough Estimate.
3. Identify stories that need splitting (anything estimated > 13 story points or XL).
4. Flag dependencies between stories.
5. Output a prioritized backlog as both a document and spreadsheet.

### Story Splitting Patterns

When a story is too large, apply these splitting strategies:
- **By workflow step** — Split along the user's journey
- **By business rule** — Each rule variation becomes a story
- **By data type** — Handle different data separately
- **By interface** — API, UI, admin panel as separate stories
- **By operation** — CRUD operations as individual stories
- **Happy path / edge cases** — Core flow first, exceptions later
- **By platform** — iOS, Android, Web as separate stories

---

## User Story Writing

Follow the canonical format. Read `references/story-writing.md` for full guidance.

### Story Template

```
## [STORY-ID] [Story Title]

**As a** [type of user/persona],
**I want** [goal/desire],
**So that** [benefit/value].

### Acceptance Criteria
Given [precondition]
When [action]
Then [expected result]

### Technical Notes
- [Implementation considerations]
- [API contracts, data models]

### Definition of Ready Checklist
- [ ] Acceptance criteria defined and reviewed
- [ ] Dependencies identified
- [ ] Estimated by the team
- [ ] Small enough to complete in one sprint
- [ ] UI/UX mockups attached (if applicable)

### Definition of Done Checklist
- [ ] Code complete and peer-reviewed
- [ ] Unit tests written and passing (≥80% coverage)
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Deployed to staging
- [ ] PO acceptance verified
```

---

## Estimation Methods

This skill supports three estimation methods. Read `references/estimation-methods.md` for
detailed facilitation guides.

### 1. Story Points (Fibonacci)

Use the Fibonacci sequence: 1, 2, 3, 5, 8, 13, 21.

- **1 point** — Trivial change, well-understood, < 2 hours
- **2 points** — Small, straightforward, minimal unknowns
- **3 points** — Moderate effort, some complexity
- **5 points** — Significant work, multiple components
- **8 points** — Large, complex, some unknowns
- **13 points** — Very large, consider splitting
- **21 points** — Epic-sized, must be split before sprint commitment

### 2. T-Shirt Sizing

| Size | Relative Effort | Typical SP Equivalent | Time Range |
|------|-----------------|----------------------|------------|
| XS   | Trivial         | 1                    | < 2 hours  |
| S    | Small           | 2-3                  | 2-8 hours  |
| M    | Medium          | 5                    | 1-2 days   |
| L    | Large           | 8                    | 3-5 days   |
| XL   | Very Large      | 13+                  | > 5 days (split!) |

### 3. Time-Based Estimates

When using hours/days, always include:
- **Optimistic estimate** — Best case with no blockers
- **Most likely estimate** — Realistic with normal interruptions
- **Pessimistic estimate** — Worst case with complications
- **PERT estimate** — (Optimistic + 4×Most Likely + Pessimistic) / 6

---

## Kanban Board Setup

When setting up a Kanban board, read `references/kanban-planning.md` first.

Default column structure:
```
Backlog → Ready → In Progress → In Review → Testing → Done
```

Include in the output:
- Column definitions with entry/exit criteria
- WIP limits per column (recommend: team size ÷ 2, rounded up)
- Swimlane structure (by priority, by team, by work type)
- Policies for blocked items
- Cadence for replenishment and review meetings

---

## Scripts

### generate_sprint_xlsx.py

Located at `scripts/generate_sprint_xlsx.py`. Generates a full sprint tracking spreadsheet.

Usage: Read the script, then run it with appropriate parameters. It accepts JSON configuration
via stdin or file path and produces a formatted .xlsx with all tracking sheets, conditional
formatting, and formulas.

### generate_burndown_chart.py

Located at `scripts/generate_burndown_chart.py`. Generates a burndown chart as an image or
embeds it in an HTML report.

---

## Integration Formats

When the user mentions Jira, Asana, Trello, Linear, or Shortcut, produce CSV exports that
match their import formats:

- **Jira CSV** — Summary, Issue Type, Priority, Story Points, Description, Acceptance Criteria,
  Epic Link, Sprint, Labels, Components
- **Asana CSV** — Name, Section, Priority, Description, Due Date, Assignee, Tags
- **Trello JSON** — Lists with cards containing name, desc, labels, checklists
- **Linear CSV** — Title, Description, Priority, Estimate, Team, Project, Label

---

## Best Practices to Embed in All Outputs

1. Sprint goals should be specific, measurable, and achievable within the sprint
2. Never commit to more than 85% of historical velocity for a new sprint
3. Include a 10-20% buffer for unplanned work and tech debt
4. Every story must have at least one acceptance criterion in Given/When/Then format
5. Stories in a sprint should collectively map to the sprint goal
6. Flag any story without a clear "so that" — the value prop is essential
7. Encourage vertical slicing over horizontal (deliver end-to-end value, not layers)



---
