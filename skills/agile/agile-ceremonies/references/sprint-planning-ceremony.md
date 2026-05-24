# Sprint Planning Ceremony — Full Reference

## Table of Contents
1. Full Facilitation Playbook
2. Agenda Templates
3. Notes Templates
4. Remote Planning Guide
5. Anti-Patterns & Fixes

---

## 1. Full Facilitation Playbook

### Time Box Calculation
| Sprint Length | Planning Time Box | Part 1 (What) | Part 2 (How) |
|--------------|-------------------|----------------|--------------|
| 1 week       | 2 hours           | 1 hour         | 1 hour       |
| 2 weeks      | 4 hours           | 2 hours        | 2 hours      |
| 3 weeks      | 6 hours           | 3 hours        | 3 hours      |
| 4 weeks      | 8 hours           | 4 hours        | 4 hours      |

### Pre-Meeting Checklist
- [ ] Backlog is refined — top items meet Definition of Ready
- [ ] PO has prepared the sprint goal and priority stories
- [ ] Previous sprint velocity is calculated and visible
- [ ] Team capacity is calculated (PTO, holidays, on-call)
- [ ] Previous retro action items are ready for review
- [ ] Room booked / video call set up with screen sharing
- [ ] Board/tool is accessible to all participants
- [ ] Snacks/drinks for long sessions (seriously — this matters)

### Facilitation Script

**Opening & Context Setting (10 min)**
⏱️ Timer: 10 minutes
🎤 Speaker: Scrum Master
📋 Script:
> "Welcome to Sprint [N] planning. Before we start, let's review where we are.
> Last sprint we completed [X] of [Y] committed points — velocity of [X].
> Our 3-sprint rolling average is [Z] points.
>
> Let me also check in on our retro action items from last sprint:
> - [Action 1]: [Status]
> - [Action 2]: [Status]
>
> Now I'll hand it over to [PO name] to share the sprint goal and priorities."

📝 Note: If retro actions aren't done, briefly discuss why. Don't let it derail planning.

---

**PART 1: WHAT — Sprint Goal & Story Selection**

**Sprint Goal Presentation (10-15 min)**
⏱️ Timer: 15 minutes
🎤 Speaker: Product Owner
📋 PO presents:
> "[PO Name], please share the sprint goal and walk us through the top priorities."

The PO should:
- State the sprint goal in one sentence
- Explain the business context and why this goal matters NOW
- Present the top 8-12 backlog items in priority order
- Flag any external dependencies or deadlines

📝 Facilitator note: The goal should pass the "so what?" test. If the team can't explain
why the goal matters to a stakeholder, it needs refinement.

**Story Discussion & Clarification (45-90 min, depending on sprint length)**
⏱️ Timer: 5-8 minutes per story
🎤 Speaker: PO + Team
📋 Facilitator guides:
> "Let's go through each candidate story. For each one, let's make sure we understand the
> acceptance criteria and can identify the technical approach. [PO], please present [STORY-ID]."

For EACH story:
1. PO reads the story and acceptance criteria
2. Team asks clarifying questions (time-box to 5 min)
3. Team does a quick confidence check: "Do we understand this well enough to commit?"
4. If yes → move to estimation
5. If no → flag for refinement, consider deferring to next sprint

⚠️ Watch-fors:
- "What does the PO mean by...?" → Acceptance criteria need work. Pause and clarify NOW.
- Story has no acceptance criteria → Cannot be committed. Send back for refinement.
- Team debates technical approach → "Let's note both options and decide in Part 2."
- PO tries to dictate HOW → "The team decides the how. Let's focus on the what."

**Estimation Round (15-30 min)**
⏱️ Timer: 3-5 minutes per story
🎤 Speaker: Team
📋 Facilitator:
> "Now let's estimate. Remember our reference story: [REFERENCE-STORY] was [X] points.
> Planning poker — everyone ready? Reveal."

Follow the estimation process from the agile-sprint-planner skill's estimation reference.

**Sprint Commitment (10-15 min)**
⏱️ Timer: 15 minutes
🎤 Speaker: Team + PO
📋 Facilitator:
> "Our capacity this sprint is approximately [X] points based on velocity and capacity planning.
> We've estimated the top [N] stories at a total of [Y] points.
>
> Team — are we confident we can deliver these [N] stories?
> Are there any we should swap out or add?
>
> [If yes]: Great. These are our committed stories.
> [If no]: Let's discuss which stories to adjust."

📝 Note: The team commits, not the PO. The PO sets priorities, the team sets capacity.

**Break (10-15 min)** — Essential for 4+ hour sessions.

---

**PART 2: HOW — Task Breakdown & Technical Approach**

**Task Decomposition (bulk of Part 2)**
⏱️ Timer: 10-15 minutes per story
🎤 Speaker: Team
📋 Facilitator:
> "Now let's break each committed story into tasks. For each story, identify:
> 1. What are the implementation tasks? (aim for 2-8 hour chunks)
> 2. What's the technical approach?
> 3. Who's picking it up? (or leave unassigned for now)
> 4. Any risks or unknowns?"

For EACH committed story:
- Team identifies tasks (dev, test, review, deploy)
- Tasks are added to the sprint board
- Dependencies between tasks are flagged
- Team members may self-assign or defer to standup

⚠️ Watch-fors:
- Tasks that are too large (>8 hours) → Break them down further
- Tasks that are too small (<30 min) → Merge them or they're overhead
- Only one person can do a task → Risk! Cross-train or pair program
- No testing tasks → Remind team that testing is part of "done"

**Risk & Dependency Review (10 min)**
⏱️ Timer: 10 minutes
📋 Facilitator:
> "Before we close, let's review risks and dependencies:
> - Any external dependencies? (other teams, third parties, approvals)
> - Any technical risks? (new technology, unfamiliar codebase)
> - Any team availability risks? (PTO, on-call, training)
>
> Let's document these and assign owners for each risk mitigation."

**Closing & Confirmation (5 min)**
⏱️ Timer: 5 minutes
📋 Facilitator:
> "To summarize:
> - Sprint Goal: [goal]
> - Committed stories: [N] stories, [X] total points
> - Key risks: [list]
> - First standup: [date/time]
>
> Team, final confirmation — are we committed? [Wait for verbal yes from team]
> 
> Great. Let's have a strong sprint. Thank you everyone."

### Post-Meeting Checklist
- [ ] Sprint backlog is entered in tracking tool
- [ ] Sprint board is set up / reset
- [ ] Sprint goal posted in team channel
- [ ] Calendar invites sent for all sprint ceremonies
- [ ] Risks documented with owners and mitigation plans
- [ ] Any deferred stories noted for next refinement

---

## 2. Agenda Templates

### Sprint Planning Agenda
```
# Sprint [N] Planning — [Date]
**Team:** [Name] | **Duration:** [X hours] | **Facilitator:** [SM Name]
**PO:** [Name] | **Location:** [Room/Link]

## Pre-Meeting
- Review: Previous sprint velocity and retro action items
- Ensure: Top backlog items meet Definition of Ready

## Part 1: WHAT (first half)
| Time | Activity | Owner | Duration |
|------|----------|-------|----------|
| [Start] | Opening & retro action review | SM | 10 min |
| +10 min | Sprint goal presentation | PO | 15 min |
| +25 min | Story walkthrough & clarification | PO + Team | 60 min |
| +85 min | Estimation | Team | 30 min |
| +115 min | Sprint commitment | Team | 15 min |

## Break (15 min)

## Part 2: HOW (second half)
| Time | Activity | Owner | Duration |
|------|----------|-------|----------|
| [Resume] | Task decomposition | Team | 75 min |
| +75 min | Risk & dependency review | SM | 10 min |
| +85 min | Final commitment & closing | SM | 5 min |

## Preparation for Attendees
- [ ] PO: Backlog prioritized, sprint goal drafted
- [ ] Devs: Review top 10 backlog items before the meeting
- [ ] SM: Velocity calculated, capacity plan ready
```

---

## 3. Notes Templates

### Sprint Planning Notes
```
# Sprint [N] Planning Notes — [Date]
**Attendees:** [Names]
**Absent:** [Names]

## Sprint Metadata
- Sprint Goal: [one sentence]
- Duration: [start date] — [end date]
- Team Velocity (3-sprint avg): [X] points
- Team Capacity This Sprint: [Y] points
- Committed Points: [Z] points

## Committed Stories
| ID | Title | Points | Assignee | Key Tasks |
|----|-------|--------|----------|-----------|

## Stretch Goals (if capacity allows)
| ID | Title | Points |
|----|-------|--------|

## Risks & Dependencies
| Risk | Likelihood | Impact | Mitigation | Owner |
|------|-----------|--------|------------|-------|

## Retro Action Item Status
| Action | Owner | Status |
|--------|-------|--------|

## Decisions Made
1. [Decision and context]

## Parking Lot
- [Items to address outside of planning]
```

---

## 4. Remote Planning Guide

- Use breakout rooms for Part 2 task decomposition (sub-teams per story)
- Async pre-work: PO records a 5-min video walking through priorities before the meeting
- Use digital estimation tools (PlanITPoker, Pointing Poker, Miro voting)
- 5-minute breaks every 50 minutes for remote fatigue
- Facilitator uses explicit call-outs: "I'd like to hear from everyone. [Name], your thoughts?"
- Have a shared document open for real-time note-taking visible to all

---

## 5. Anti-Patterns & Fixes

| Anti-Pattern | Fix |
|-------------|-----|
| PO absent or unprepared | Cancel or reschedule. Planning without the PO is a waste. |
| No sprint goal | Don't proceed without one. Ask PO: "What's the ONE thing we must achieve?" |
| Team doesn't understand stories | Stories aren't Ready. Send them back for refinement. |
| Manager assigns work | Redirect: "The team self-organizes. [Name], what would you like to pick up?" |
| Planning takes all day | Strict time-boxing. If backlog isn't refined, that's a refinement problem, not a planning problem. |
| Same velocity assumed for reduced team | Adjust! If 2 of 6 devs are on PTO, capacity drops ~33%. |
| No task breakdown | Part 2 is non-negotiable. Tasks surface hidden complexity. |



---
