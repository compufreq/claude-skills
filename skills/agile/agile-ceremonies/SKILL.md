---
name: agile-ceremonies
description: >
  Complete Agile ceremony facilitation toolkit covering daily standups, sprint planning, sprint
  reviews, and retrospectives for Scrum and Kanban teams. Use this skill whenever the user mentions
  standup, daily scrum, daily Kanban, sprint review, sprint demo, retrospective, retro, sprint
  planning meeting, ceremony facilitation, meeting agenda, meeting notes, facilitation guide,
  facilitation script, retrospective activities, Start/Stop/Continue, 4Ls, sailboat retro, mad/sad/glad,
  dot voting, or any Agile meeting format. Also trigger when the user asks to run a retro, plan a
  sprint review, create meeting minutes, facilitate a standup, write a meeting playbook, or produce
  any ceremony-related document. Trigger even if the user doesn't say "Agile" but describes
  recurring team meetings with demos, reflections, or daily check-ins. This skill complements
  agile-sprint-planner — use both when sprint planning involves ceremony setup.
---

# Agile Ceremonies

A production-grade facilitation toolkit for all Agile ceremonies. Produces full playbooks with
timing, speaker cues, and facilitator notes, plus meeting agendas, minutes templates, and
retrospective activity guides.

## Quick Reference

| Ceremony | Cadence | Time Box | Output Formats |
|----------|---------|----------|----------------|
| Daily Standup | Daily | 15 min | Agenda (md), Notes template (md/docx) |
| Sprint Planning | Per sprint | 2-8 hrs | Playbook (md/docx), Agenda (md/docx) |
| Sprint Review | Per sprint | 1-4 hrs | Playbook (md/docx), Demo script (md), Minutes (md/docx) |
| Retrospective | Per sprint | 1-3 hrs | Playbook (md/docx), Activity guide (md), Action items (xlsx) |

## Core Workflow

1. **Identify the ceremony** — Which meeting is the user preparing for?
2. **Identify the need** — Do they want a facilitation playbook, agenda, notes template, or retro activity?
3. **Gather context** — Team size, sprint duration, any specific concerns or themes.
4. **Read the relevant reference file:**
   - Daily standup → `references/daily-standup.md`
   - Sprint planning → `references/sprint-planning-ceremony.md`
   - Sprint review → `references/sprint-review.md`
   - Retrospective → `references/retrospective.md`
5. **Generate the output** — Use scripts for formatted documents, or produce markdown directly.

---

## Output Types

### 1. Facilitation Playbook

A full step-by-step script the facilitator (usually the Scrum Master) follows during the meeting.
Includes timing for each segment, speaker cues, facilitator notes, and transition phrases.

Structure:
```
# [Ceremony Name] Facilitation Playbook
## Meeting Metadata
- Date, Sprint, Team, Duration, Facilitator

## Pre-Meeting Checklist
- [ ] Preparation items

## Playbook

### Segment 1: Opening (X min)
⏱️ Timer: X minutes
🎤 Speaker: [Role]
📋 Facilitator says: "[Opening script]"
📝 Notes: [What to watch for]

### Segment 2: [Main Activity] (X min)
⏱️ Timer: X minutes
🎤 Speaker: [Role]
📋 Facilitator says: "[Transition script]"
🔄 Activity: [What happens]
⚠️ Watch for: [Common problems and how to redirect]

[...more segments...]

### Closing (X min)
📋 Facilitator says: "[Closing script]"
📝 Action items captured: [Template]

## Post-Meeting Checklist
- [ ] Follow-up items
```

### 2. Meeting Agenda

A concise agenda document suitable for sharing with the team before the meeting.

Structure:
```
# [Ceremony] Agenda — [Date]
**Sprint:** [N] | **Team:** [Name] | **Duration:** [X min] | **Facilitator:** [Name]

## Objectives
1. [What we'll accomplish]

## Agenda Items
| Time | Item | Owner | Notes |
|------|------|-------|-------|

## Pre-Read / Preparation
- [What attendees should prepare]

## Standing Rules
- [Meeting norms]
```

### 3. Meeting Notes / Minutes Template

A template for capturing what happened during the ceremony.

Structure:
```
# [Ceremony] Notes — [Date]
**Sprint:** [N] | **Attendees:** [Names] | **Absent:** [Names]

## Decisions Made
1. [Decision and rationale]

## Action Items
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|

## Key Discussion Points
- [Topic: Summary]

## Parking Lot (deferred items)
- [Item for later discussion]
```

### 4. Retrospective Activity Guide

A detailed guide for running a specific retro format, with instructions, materials needed,
timing, and facilitation tips.

---

## Ceremony Details

### Daily Standup / Daily Kanban

Read `references/daily-standup.md` for the full playbook.

**Key principles:**
- 15 minutes, same time every day, everyone stands (if in-person)
- Focus on the work, not status reporting to a manager
- Three questions (Scrum) or walk-the-board (Kanban)
- Blockers get flagged, not solved — take them offline
- The team owns the standup, not the Scrum Master

**Scrum format (person-focused):**
1. What did I complete yesterday?
2. What will I work on today?
3. What's blocking me?

**Kanban format (board-focused):**
1. Walk the board right-to-left (starting from "almost done")
2. Focus on blocked and aging items
3. Discuss items at WIP limit
4. Pull new work only if capacity exists

**Anti-patterns to flag:**
- Standup becomes a status report to the manager
- One person dominates, others disengage
- Exceeds 15 minutes regularly
- Problem-solving happens during standup instead of being taken offline
- People give vague updates ("working on stuff")
- Remote team members are afterthoughts

---

### Sprint Planning

Read `references/sprint-planning-ceremony.md` for the full playbook.

**Time box:** 2 hours per sprint week (e.g., 4 hours for a 2-week sprint)

**Two-part structure:**
- Part 1 — WHAT: PO presents goal + priorities, team selects stories
- Part 2 — HOW: Team breaks stories into tasks, identifies approach

This ceremony overlaps with the `agile-sprint-planner` skill. Use this skill for the ceremony
facilitation (playbook, agenda, timing) and `agile-sprint-planner` for the sprint artifacts
(backlog spreadsheet, capacity plan, estimation).

---

### Sprint Review / Demo

Read `references/sprint-review.md` for the full playbook.

**Time box:** 1 hour per sprint week (e.g., 2 hours for a 2-week sprint)

**Structure:**
1. Sprint goal recap (5 min)
2. Demo of completed work (bulk of time)
3. Stakeholder feedback (inline or after demos)
4. Backlog impact discussion (what changes based on feedback)
5. Next sprint preview (5 min)

**Key principles:**
- Demo working software, not slides
- Encourage stakeholder interaction and questions
- Capture feedback as actionable backlog items
- Be honest about what wasn't completed and why
- Celebrate team achievements

---

### Sprint Retrospective

Read `references/retrospective.md` for the full playbook and all activity formats.

**Time box:** 45 min per sprint week (e.g., 1.5 hours for a 2-week sprint)

**Core structure (regardless of activity):**
1. Set the stage (5-10 min) — Check-in, ground rules, safety check
2. Gather data (15-25 min) — The main retro activity
3. Generate insights (10-15 min) — Identify patterns and root causes
4. Decide what to do (10-15 min) — Pick 1-3 action items with owners
5. Close the retro (5 min) — Appreciation, feedback on the retro itself

**Available retro formats** (detailed in `references/retrospective.md`):
- Start / Stop / Continue
- Mad / Sad / Glad
- 4Ls (Liked, Learned, Lacked, Longed For)
- Sailboat (Wind, Anchor, Rocks, Island)
- Starfish (Keep, More, Less, Stop, Start)
- Timeline / Sprint Journey
- Happiness Radar
- Hot Air Balloon
- DAKI (Drop, Add, Keep, Improve)
- Lean Coffee
- Fishbone / Ishikawa (for root cause analysis)
- Circles of Control (for teams feeling stuck)

---

## Scripts

### generate_ceremony_doc.py

Located at `scripts/generate_ceremony_doc.py`. Generates formatted ceremony documents
(playbook, agenda, or notes) as markdown or docx.

Usage: Run with ceremony type, document type, and configuration JSON.

```bash
python scripts/generate_ceremony_doc.py \
  --ceremony standup|planning|review|retro \
  --type playbook|agenda|notes \
  --config ceremony_config.json \
  --output ceremony_doc.md
```

### generate_retro_board.py

Located at `scripts/generate_retro_board.py`. Generates an interactive HTML retrospective
board with sticky notes, voting, and export.

```bash
python scripts/generate_retro_board.py \
  --format start-stop-continue|4ls|sailboat|mad-sad-glad|starfish \
  --team-size 6 \
  --output retro_board.html
```

---

## Best Practices Embedded in All Outputs

1. Always include a safety check at retro start — people won't be honest if they don't feel safe
2. Rotate facilitation — it shouldn't always be the Scrum Master
3. Time-box ruthlessly — ceremonies that run over lose the team's trust
4. Action items need owners and due dates, or they won't happen
5. Review previous retro action items at the start of each retro
6. Remote ceremonies need explicit facilitation for equity — call on people, use async input
7. The Sprint Review is NOT a demo rehearsal — it's an inspection and adaptation event
8. Standups are for the team, not for managers — redirect status-reporting behavior



---
