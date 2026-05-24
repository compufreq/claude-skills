# Scrum Sprint Planning Reference

## Table of Contents
1. Sprint Planning Ceremony
2. Capacity Planning
3. Sprint Goal Crafting
4. Commitment vs Forecast
5. Sprint Planning Checklist
6. Anti-Patterns

---

## 1. Sprint Planning Ceremony

Sprint Planning is a time-boxed event that kicks off each sprint. The entire Scrum team
collaborates to define what can be delivered and how the work will be achieved.

### Time Box
- 2-week sprint → 4 hours max
- 1-week sprint → 2 hours max
- 3-week sprint → 6 hours max
- 4-week sprint → 8 hours max

### Participants
- **Product Owner** — Presents prioritized backlog, clarifies requirements, answers questions
- **Scrum Master** — Facilitates, ensures time box, removes impediments
- **Development Team** — Selects work, breaks stories into tasks, commits to delivery

### Two-Part Structure

**Part 1: What can be done?** (First half of time box)
- PO presents the sprint goal and top-priority backlog items
- Team discusses each item for clarity
- Team selects items they believe they can complete
- Selection is based on velocity, capacity, and complexity

**Part 2: How will it be done?** (Second half of time box)
- Team breaks selected stories into tasks (2-8 hours each)
- Team identifies technical approach for each story
- Team identifies dependencies and risks
- Team confirms or adjusts the sprint commitment

### Inputs to Sprint Planning
- Refined product backlog (top items should be "Ready")
- Team velocity (3-sprint rolling average)
- Team capacity (accounting for PTO, holidays, ceremonies)
- Previous sprint's retrospective action items
- Technical debt items flagged for attention

### Outputs of Sprint Planning
- Sprint goal (one sentence, measurable)
- Sprint backlog (committed stories + tasks)
- Capacity plan (per team member)
- Risk register (identified risks with mitigations)

---

## 2. Capacity Planning

Capacity planning ensures the team doesn't overcommit. Use this formula:

### Per-Person Capacity
```
Available Days = Sprint Days - PTO Days - Holiday Days
Ceremony Overhead = Sprint Days × 0.15 (standups, retro, review, planning)
Focus Days = Available Days - Ceremony Overhead
Capacity (hours) = Focus Days × Productive Hours Per Day (typically 5-6)
```

### Team Capacity
```
Total Team Capacity = Sum of all members' Focus Days
Capacity in Points = Total Team Capacity × (Historical Velocity / Historical Capacity)
Safe Commitment = Capacity in Points × 0.85
```

### Capacity Table Template

| Team Member | Role | Sprint Days | PTO | Holidays | Ceremony OH | Net Days | Allocated SP |
|-------------|------|-------------|-----|----------|-------------|----------|--------------|
| [Name]      | Dev  | 10          | 0   | 0        | 1.5         | 8.5      | [calc]       |

---

## 3. Sprint Goal Crafting

A good sprint goal follows the SMART framework adapted for sprints:

- **Specific** — Names the feature area or user problem being addressed
- **Measurable** — Has a clear definition of "achieved" vs "not achieved"
- **Achievable** — Realistic given team capacity and velocity
- **Relevant** — Aligns with product roadmap and stakeholder priorities
- **Time-bound** — Completable within the sprint duration

### Sprint Goal Formula
```
"By the end of this sprint, [target users] will be able to [key capability],
enabling [business value]."
```

### Examples

Good: "By the end of this sprint, registered users will be able to reset their
passwords via email, reducing support ticket volume by an estimated 30%."

Bad: "Work on authentication stuff."

Good: "Complete the checkout flow for credit card payments so that beta users can
make purchases, unblocking the May 15 soft launch."

Bad: "Make progress on the payment epic."

---

## 4. Commitment vs Forecast

Modern Scrum uses "forecast" rather than "commitment" to acknowledge uncertainty.

### Forecast Guidelines
- Select stories totaling 80-90% of average velocity
- Ensure all selected stories are "Ready" (meet Definition of Ready)
- If velocity is unstable (variance > 20%), use the lower bound
- New teams without velocity history: start conservatively (estimate 60% of theoretical capacity)
- Account for sprint-specific factors (holidays, training, on-call rotations)

### Stretch Goals
- Identify 1-2 additional stories as stretch goals
- Stretch goals are only pulled in if committed work finishes early
- Never report stretch goals as committed work
- Mark stretch goals clearly in the sprint backlog

---

## 5. Sprint Planning Checklist

### Before Planning (PO + SM)
- [ ] Backlog is refined (top 2 sprints worth of items)
- [ ] Top items meet Definition of Ready
- [ ] Acceptance criteria are written in Given/When/Then
- [ ] Dependencies are identified and flagged
- [ ] Previous sprint's metrics are available (velocity, burndown)
- [ ] Team capacity is calculated (PTO, holidays accounted for)

### During Planning (Full Team)
- [ ] Sprint goal is articulated and agreed upon
- [ ] Each candidate story is discussed and understood
- [ ] Stories are estimated (or re-estimated if needed)
- [ ] Stories are selected based on priority and capacity
- [ ] Stories are broken into tasks
- [ ] Risks and dependencies are documented
- [ ] Sprint backlog is finalized

### After Planning (SM)
- [ ] Sprint backlog is entered into tracking tool
- [ ] Sprint board is set up / reset
- [ ] Sprint goal is posted visibly
- [ ] First standup is scheduled
- [ ] Calendar invites for sprint ceremonies are sent

---

## 6. Anti-Patterns to Avoid

### Planning Anti-Patterns
- **No sprint goal** — Stories become a disconnected shopping list
- **Over-commitment** — Consistently planning above velocity
- **Absent PO** — Team guesses at requirements, rework follows
- **No task breakdown** — Stories stay abstract, surprises emerge mid-sprint
- **Ignoring tech debt** — Quality degrades sprint over sprint
- **Planning by fiat** — Manager assigns work instead of team self-selecting

### Velocity Anti-Patterns
- **Gaming points** — Inflating estimates to look productive
- **Using velocity for individual performance** — Destroys team trust
- **Comparing velocity across teams** — Points are relative, not absolute
- **Projecting velocity from sprint 1** — Need 3-5 sprints for reliable data

### Capacity Anti-Patterns
- **100% allocation** — No buffer for meetings, support, unplanned work
- **Ignoring specialization** — All work can't go to any team member
- **Not accounting for ramp-up** — New team members need onboarding time



---
