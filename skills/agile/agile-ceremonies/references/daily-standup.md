# Daily Standup / Daily Kanban — Full Reference

## Table of Contents
1. Scrum Standup Playbook
2. Kanban Daily Meeting Playbook
3. Remote/Hybrid Standup Guide
4. Standup Agenda Templates
5. Notes Templates
6. Anti-Patterns & Fixes

---

## 1. Scrum Standup Playbook

### Pre-Meeting (2 min before)
- [ ] Board/tool is visible (projector, screen share, or physical board)
- [ ] Yesterday's parking lot items addressed or scheduled
- [ ] Sprint burndown visible

### Full Facilitation Script

**Opening (1 min)**
⏱️ Timer: 1 minute
🎤 Speaker: Scrum Master / Facilitator
📋 Script:
> "Good morning everyone. Let's get started with our daily standup. Quick reminder — we're
> focusing on what's moving toward our sprint goal and any blockers we need to surface.
> Please keep updates brief. If something needs a longer discussion, we'll take it to the
> parking lot. [Name], would you like to start?"

**Round Robin (10-12 min)**
⏱️ Timer: ~90 seconds per person
🎤 Speaker: Each team member
📋 Each person answers:
> 1. "Yesterday I completed [specific task/story progress]."
> 2. "Today I'm working on [specific task/story]."
> 3. "I'm blocked by [specific issue] / No blockers."

⚠️ **Facilitator watch-fors:**
- If someone is rambling → "Thanks [Name], let's take that to the parking lot so we can
  dig in after standup."
- If someone says "same as yesterday" → "Can you be more specific? Which story are you on
  and what's the next step?"
- If problem-solving starts → "Great topic — let's park that. [Name] and [Name], can you
  sync right after standup?"
- If someone reports TO you (the SM) → Redirect: "Tell the team, not me — I'm just facilitating."

**Parking Lot & Blockers (2 min)**
⏱️ Timer: 2 minutes
🎤 Speaker: Scrum Master
📋 Script:
> "Okay, we had a few items for the parking lot: [list]. Here's how we'll handle each:
> - [Item 1]: [Name] and [Name] will sync after this call.
> - [Item 2]: I'll follow up with [external person] by end of day.
> Any other blockers before we wrap?"

**Closing (30 sec)**
📋 Script:
> "Thanks everyone. Sprint burndown shows we're at [X] points remaining with [Y] days left.
> [On track / Slightly behind — any volunteers to swarm on [story]?]. Have a great day!"

---

## 2. Kanban Daily Meeting Playbook

### Pre-Meeting (2 min before)
- [ ] Kanban board is visible and up-to-date
- [ ] WIP limits are displayed
- [ ] Any aging items flagged (highlight items near or exceeding cycle time SLE)

### Full Facilitation Script

**Opening (1 min)**
⏱️ Timer: 1 minute
🎤 Speaker: Facilitator
📋 Script:
> "Good morning. Let's walk the board. Remember, we go right-to-left — focus on finishing
> before starting. I'll call out anything aging or blocked."

**Walk the Board — Right to Left (10-12 min)**

⏱️ Timer: 10-12 minutes total
🎤 Speaker: Facilitator leads, assignees respond

📋 **Step 1: Testing / QA column**
> "Starting from the right — Testing column. We have [N] items here. [Name], how's
> [ITEM-ID] looking? Any issues with the acceptance criteria?"

📋 **Step 2: In Review column**
> "In Review — [N] items. [ITEM-ID] has been here for [X] days. Who can pick up that review?
> Remember our WIP limit here is [N]."

📋 **Step 3: In Progress column**
> "In Progress — we're at [N] of our [WIP limit] WIP limit. [Name], any updates on [ITEM-ID]?
> Any items blocked?"

📋 **Step 4: Ready column**
> "Ready column has [N] items. Anyone with capacity to pull? Remember, only pull if you're
> below our WIP limit."

⚠️ **Facilitator watch-fors:**
- Items approaching SLE → "This item is at [X] days, our SLE is [Y]. What do we need to
  unblock it?"
- WIP limit hit → "We're at our limit in [column]. Let's finish something before pulling new work."
- Stale items → "This hasn't moved in [X] days. Is it blocked? Do we need to swarm?"

**Blocked Items (2 min)**
📋 Script:
> "We have [N] blocked items. Let me go through them:
> - [ITEM-ID]: Blocked on [reason]. [Name], any progress on unblocking?
> - [ITEM-ID]: Waiting on [external dependency]. I'll escalate today."

**Closing (30 sec)**
📋 Script:
> "Current throughput this week: [N] items completed. [N] items in progress. Let's keep
> the flow moving. Any last items? Great, thanks everyone."

---

## 3. Remote/Hybrid Standup Guide

### Async Standup Option (for distributed teams)

When synchronous standups don't work across time zones, use an async format:

**Daily async post (in Slack/Teams/chat):**
```
🟢 Done yesterday:
- [completed work]

🔵 Working on today:
- [planned work]

🔴 Blockers:
- [issues, or "None"]

⏰ Posted at: [local time]
```

**Rules for async standups:**
- Post by [agreed time] in your time zone
- Facilitator reviews all posts and flags conflicts/blockers within 1 hour
- If a blocker needs real-time discussion, facilitator schedules a 15-min sync
- Weekly video standup for team bonding (30 min, less structured)

### Hybrid Meeting Tips

- Remote participants speak first (they're easier to forget)
- Use a shared digital board, not a physical one
- Mute notifications during the standup
- If camera fatigue is an issue, cameras-optional is fine for standups
- Facilitator explicitly calls on remote people: "Before we move on — [Name], anything from your side?"

---

## 4. Standup Agenda Templates

### Scrum Standup Agenda
```
# Daily Standup — [Date]
**Sprint:** [N] | **Day:** [X of Y] | **Time:** 15 min | **Facilitator:** [Name]

## Format
Each person: Yesterday / Today / Blockers

## Sprint Status
- Burndown: [X] points remaining / [Y] total
- Days left: [N]
- Stories in progress: [list]

## Parking Lot (from yesterday)
- [ ] [Item — Owner — Status]

## Today's Parking Lot
- (captured during meeting)
```

### Kanban Daily Agenda
```
# Daily Kanban Meeting — [Date]
**Time:** 15 min | **Facilitator:** [Name]

## Board Walk (Right to Left)
- Testing: [N items]
- In Review: [N items]
- In Progress: [N items] / WIP limit: [N]
- Ready: [N items]

## Aging Items (approaching SLE)
- [ITEM-ID]: [X days] in [column] (SLE: [Y days])

## Blocked Items
- [ITEM-ID]: [reason] — Owner: [Name]

## Throughput This Week
- Completed: [N] items
- Average cycle time: [X] days
```

---

## 5. Notes Templates

### Standup Notes Template
```
# Standup Notes — [Date]
**Sprint:** [N] | **Attendees:** [Names] | **Absent:** [Names]

## Updates
| Person | Yesterday | Today | Blockers |
|--------|-----------|-------|----------|
| [Name] | [done]    | [plan]| [blocker or None] |

## Blockers Raised
| Blocker | Raised By | Owner | Resolution Plan | Due |
|---------|-----------|-------|-----------------|-----|

## Parking Lot Items
| Topic | Participants | Scheduled For |
|-------|-------------|---------------|

## Sprint Health
- Points remaining: [X] / [Total]
- On track: [Yes/No/At risk]
- Notes: [any concerns]
```

---

## 6. Anti-Patterns & Fixes

| Anti-Pattern | Symptom | Fix |
|-------------|---------|-----|
| Status report to manager | People face the SM/manager when talking | SM steps back physically; have team face the board |
| Problem-solving forum | One topic consumes 10+ minutes | Strict parking lot: "Great topic — after standup" |
| Monologue standup | One person talks for 5+ minutes | Use a token (physical object) with 90-sec timer |
| Ghost standup | People are disengaged, checking phones | Shorter + more energetic; try walk-the-board format |
| Skip-day standup | "Nothing to report" | Ask: "What did you learn?" or "What's your next commit?" |
| Late starts | Standup drifts 5-10 min past start time | Start on time regardless of who's there; latecomers catch up |
| Phantom blockers | Same blocker reported for days with no action | Track blockers on board with aging; escalate at 2 days |



---
