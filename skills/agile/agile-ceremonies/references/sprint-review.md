# Sprint Review / Demo — Full Reference

## Table of Contents
1. Full Facilitation Playbook
2. Demo Script Template
3. Agenda & Notes Templates
4. Stakeholder Management
5. Anti-Patterns & Fixes

---

## 1. Full Facilitation Playbook

### Time Box
| Sprint Length | Review Time Box |
|--------------|-----------------|
| 1 week       | 1 hour          |
| 2 weeks      | 2 hours         |
| 3 weeks      | 3 hours         |
| 4 weeks      | 4 hours         |

### Pre-Meeting Checklist
- [ ] Demo environment is working and seeded with realistic data
- [ ] Each completed story has a designated demo-er
- [ ] Demo order is planned (most impactful first)
- [ ] Stakeholders are invited and confirmed
- [ ] Previous sprint review action items are reviewed
- [ ] Burndown / sprint metrics are prepared
- [ ] Backup plan if demo environment breaks (screenshots, recordings)
- [ ] "Not completed" items list prepared with reasons

### Facilitation Script

**Opening & Sprint Recap (5-10 min)**
⏱️ Timer: 10 minutes
🎤 Speaker: Scrum Master
📋 Script:
> "Welcome to the Sprint [N] Review. Thank you [stakeholder names] for joining us.
>
> Quick recap: Our sprint goal was '[sprint goal].'
> We committed to [X] stories totaling [Y] story points.
> We completed [A] stories ([B] points) — that's [C]% of our commitment.
>
> [If stories were not completed]:
> We carried over [N] stories to next sprint. The main reasons were [brief explanation].
>
> Now let's show you what we built. We'll demo each completed feature and I encourage
> you to ask questions and share feedback as we go."

📝 Note: Be transparent about what wasn't completed. Don't hide or spin it.

**Demo Walkthrough (bulk of time — 60-80% of meeting)**
⏱️ Timer: 5-10 minutes per story
🎤 Speaker: Developer/team member who built it

For EACH completed story:

📋 Facilitator introduces:
> "[Name] will demo [STORY-ID]: [Story title]. This addresses [user need/business value].
> [Name], take it away."

📋 Demo-er presents:
> "This story was about [brief context]. Let me show you how it works..."
> [Live demo of working software]
> "The acceptance criteria were [X, Y, Z] — let me show each one being met..."

📋 After each demo, facilitator opens for feedback:
> "Questions or feedback on this feature? [Stakeholder name], does this meet your expectations?
> Any changes you'd like to see?"

⚠️ Watch-fors:
- Demo breaks → Don't panic. Have backup screenshots. Say: "Let me show you via screenshots
  while we troubleshoot. The key functionality is [X]."
- Stakeholder requests new features during demo → Capture as backlog items, not sprint changes:
  "Great idea. I'm noting that for the backlog. [PO], can we prioritize it in refinement?"
- Demo-er goes too deep into technical details → Redirect: "Great technical work. For our
  stakeholders, can you show what the user sees?"
- Stakeholder is disengaged → Direct question: "[Name], how does this impact your team's workflow?"

**Incomplete Work Discussion (5 min)**
⏱️ Timer: 5 minutes
🎤 Speaker: Scrum Master + PO
📋 Script:
> "We have [N] stories that didn't complete this sprint:
> - [STORY-ID]: [reason — blocked on X / underestimated / scope discovered]
> - [STORY-ID]: [reason]
>
> These are carrying over to Sprint [N+1] and are top priority.
> [PO], any reprioritization needed based on what we've learned?"

**Backlog & Roadmap Impact (10-15 min)**
⏱️ Timer: 15 minutes
🎤 Speaker: Product Owner
📋 PO discusses:
> "Based on what we've delivered and the feedback today, here's what I'm thinking for
> the upcoming sprints:
> - Next sprint focus: [theme/goal]
> - Feedback items added to backlog: [list]
> - Any priority shifts: [explain]
>
> Stakeholders — does this alignment work for your timelines and priorities?"

📝 Note: This is where the PO adapts the plan based on real feedback. It's the "inspect
and adapt" moment for the product, not just the process.

**Metrics & Health (5 min)**
⏱️ Timer: 5 minutes
🎤 Speaker: Scrum Master
📋 Script:
> "Quick health check on our delivery:
> - Velocity this sprint: [X] (average: [Y])
> - Sprint goal achieved: [Yes/Partially/No]
> - Quality: [Bug count, test coverage, incidents]
> - Team happiness: [if tracked]
>
> Any questions about our process or delivery health?"

**Closing & Next Steps (5 min)**
📋 Script:
> "Thank you everyone. To summarize:
> - Completed: [N] stories demonstrating [key value delivered]
> - Feedback captured: [N] items added to backlog
> - Next sprint goal: [preview]
> - Next sprint review: [date/time]
>
> Thanks especially to [stakeholders] for your time and feedback."

### Post-Meeting Checklist
- [ ] Feedback items entered in backlog with "Sprint Review" tag
- [ ] Meeting notes shared with all attendees within 24 hours
- [ ] Any priority changes reflected in backlog ordering
- [ ] Demo recordings saved (if applicable)
- [ ] Action items assigned and tracked

---

## 2. Demo Script Template

For each story being demoed:

```
## Demo: [STORY-ID] — [Title]
**Demo-er:** [Name]
**Time:** ~[X] minutes

### Context (30 sec)
"This story addresses [user need]. Previously, users had to [old way]. Now they can [new way]."

### Demo Steps
1. Navigate to [starting point]
2. Show [initial state]
3. Perform [action that demonstrates the feature]
4. Point out [key UI elements, feedback messages]
5. Show [edge case handling]
6. Show [acceptance criterion 1 being met]
7. Show [acceptance criterion 2 being met]

### Talking Points
- Business value: [what this enables]
- Technical highlight: [interesting implementation detail — keep brief]
- Known limitations: [any caveats to mention]

### Anticipated Questions
- Q: [Likely stakeholder question]
  A: [Prepared answer]
```

---

## 3. Agenda & Notes Templates

### Sprint Review Agenda
```
# Sprint [N] Review — [Date]
**Time:** [Duration] | **Facilitator:** [SM] | **PO:** [Name]
**Stakeholders:** [Names]

## Agenda
| Time | Activity | Presenter | Duration |
|------|----------|-----------|----------|
| [Start] | Sprint recap & goal review | SM | 10 min |
| +10 | Demo: [Story 1 title] | [Name] | 10 min |
| +20 | Demo: [Story 2 title] | [Name] | 10 min |
| +30 | Demo: [Story 3 title] | [Name] | 10 min |
| +40 | Incomplete work discussion | SM + PO | 5 min |
| +45 | Backlog & roadmap impact | PO | 15 min |
| +60 | Metrics & health | SM | 5 min |
| +65 | Q&A and closing | SM | 10 min |

## Demo Environment
- URL: [staging URL]
- Credentials: [test account]
- Data: [description of test data]
```

### Sprint Review Notes
```
# Sprint [N] Review Notes — [Date]
**Attendees:** [Names] | **Absent:** [Names]

## Sprint Summary
- Goal: [sprint goal]
- Committed: [X] stories / [Y] points
- Completed: [A] stories / [B] points
- Velocity: [B] points (avg: [C])
- Goal achieved: [Yes/Partial/No]

## Demos Presented
| Story | Demo-er | Stakeholder Reaction | Feedback |
|-------|---------|---------------------|----------|

## Feedback & New Backlog Items
| Feedback | Source | Priority | Added as |
|----------|--------|----------|----------|

## Incomplete Stories (Carried Over)
| Story | Reason | Expected Completion |
|-------|--------|-------------------|

## Decisions Made
1. [Decision and rationale]

## Action Items
| Action | Owner | Due Date |
|--------|-------|----------|
```

---

## 4. Stakeholder Management

### Who Should Attend
- Product Owner (required)
- Scrum Master (required)
- Development Team (required)
- Direct stakeholders (business owners, sponsors)
- Adjacent team leads (when there are dependencies)
- UX/Design (when UI changes are demoed)
- Optional: End users, customer representatives

### Stakeholder Engagement Tips
- Send a 1-paragraph preview email the day before: "Tomorrow we'll demo [X, Y, Z]."
- Assign a "stakeholder buddy" on the team — someone who proactively seeks their input
- Ask specific questions: "Does this workflow match how your team operates?" not "Any feedback?"
- If stakeholders consistently don't attend, ask PO to address it — this is a product ownership issue
- Record demos for stakeholders who can't attend

### Handling Difficult Feedback
- "This isn't what we asked for" → "Help me understand what you expected. Let's capture
  the gap as a backlog item and prioritize it."
- "Can you add X by next week?" → "Let me note that. [PO] will prioritize it against the
  current backlog and we'll discuss it at refinement."
- "Why isn't this done yet?" → Be honest: "[Specific reason]. We've adjusted our plan to
  address it in the next sprint."

---

## 5. Anti-Patterns & Fixes

| Anti-Pattern | Fix |
|-------------|-----|
| Slide deck instead of demo | Show working software. Slides are for the sprint recap only. |
| No stakeholders attend | PO must champion attendance. Escalate if consistently absent. |
| Demo on dev machine | Use a stable staging environment. Dev machines have surprises. |
| Only PO gives feedback | Directly ask each stakeholder: "[Name], thoughts on this for your area?" |
| Feature is "demoed" but not Done | Only demo Done items. In-progress work goes in the "not completed" section. |
| Team doesn't celebrate | Acknowledge effort. Even a brief "great work on [X]" matters. |
| No backlog impact discussion | This IS the inspect-and-adapt moment. Skip it and the review is just show-and-tell. |
| Review becomes a gate/approval | Clarify: review is for feedback and transparency, not sign-off. PO has already accepted. |



---

<!-- Script: scripts/generate_ceremony_doc.py -->

# Script: generate_ceremony_doc.py

```python
#!/usr/bin/env python3
"""
Generate formatted Agile ceremony documents (playbook, agenda, or notes) as markdown.

Usage:
    python generate_ceremony_doc.py \
        --ceremony standup|planning|review|retro \
        --type playbook|agenda|notes \
        --config ceremony_config.json \
        --output ceremony_doc.md

Config JSON Schema:
{
    "team_name": "Alpha Squad",
    "sprint_number": 14,
    "sprint_goal": "Complete user auth flow",
    "start_date": "2025-01-13",
    "end_date": "2025-01-24",
    "facilitator": "Jane Smith",
    "product_owner": "John Doe",
    "team_members": ["Alice", "Bob", "Carol", "Dave"],
    "meeting_date": "2025-01-13",
    "meeting_time": "10:00 AM",
    "duration_minutes": 90,
    "location": "Room 3B / Zoom link",
    "retro_format": "sailboat",
    "sprint_duration_weeks": 2,
    "velocity_last_sprint": 28,
    "velocity_average": 31,
    "committed_points": 30,
    "stories_committed": 6,
    "stories_completed": 5,
    "previous_action_items": [
        {"action": "Set up PR template", "owner": "Alice", "status": "Done"},
        {"action": "Reduce flaky tests", "owner": "Bob", "status": "In Progress"}
    ],
    "stories": [
        {"id": "AUTH-101", "title": "Email login", "assignee": "Alice", "points": 5}
    ]
}
"""

import json
import sys
import argparse
from datetime import datetime


def generate_standup_playbook(config):
    team = ", ".join(config.get("team_members", ["Team"]))
    return f"""# Daily Standup Facilitation Playbook

## Meeting Metadata
- **Team:** {config.get("team_name", "Team")}
- **Sprint:** {config.get("sprint_number", "N")}
- **Facilitator:** {config.get("facilitator", "Scrum Master")}
- **Duration:** 15 minutes
- **Time:** {config.get("meeting_time", "9:00 AM")} daily
- **Location:** {config.get("location", "TBD")}
- **Participants:** {team}

---

## Pre-Meeting Checklist
- [ ] Sprint board is visible (projector / screen share)
- [ ] Burndown chart is current
- [ ] Yesterday's parking lot items addressed or scheduled

---

## Playbook

### Opening (1 min)
⏱️ Timer: 1 minute
🎤 Speaker: Facilitator
📋 Say:
> "Good morning everyone. Let's run through our standup. Focus on what's moving
> toward our sprint goal: *{config.get("sprint_goal", "TBD")}*. Keep it brief —
> parking lot for anything that needs discussion. Who wants to start?"

---

### Round Robin (~90 sec per person, {len(config.get("team_members", []))} people = {len(config.get("team_members", [])) * 2} min)
⏱️ Timer: ~90 seconds per person
🎤 Speaker: Each team member

Each person answers:
1. What I completed yesterday
2. What I'm working on today
3. Any blockers

**Facilitator prompts if needed:**
- Too vague → "Can you be more specific about which story?"
- Problem-solving starts → "Let's park that — sync after standup."
- Running long → "Thanks — let's take the details offline."

---

### Parking Lot & Blockers (2 min)
⏱️ Timer: 2 minutes
🎤 Speaker: Facilitator
📋 Say:
> "Parking lot items today: [list items captured].
> Here's how we'll handle each: [assign pairs/owners].
> Any other blockers before we wrap?"

---

### Closing (30 sec)
📋 Say:
> "Thanks everyone. Sprint burndown: [X] points remaining, [Y] days left.
> [Status check]. Have a great day!"

---

## Post-Standup
- [ ] Follow up on blocker owners
- [ ] Update board if anything changed during standup
- [ ] Schedule parking lot discussions
"""


def generate_standup_agenda(config):
    return f"""# Daily Standup Agenda — {config.get("meeting_date", "[Date]")}

**Sprint:** {config.get("sprint_number", "N")} | **Team:** {config.get("team_name", "Team")} | **Duration:** 15 min | **Facilitator:** {config.get("facilitator", "SM")}

## Sprint Goal
{config.get("sprint_goal", "TBD")}

## Format
Each person: Yesterday / Today / Blockers (90 sec max)

## Sprint Status
- Points remaining: TBD / {config.get("committed_points", "TBD")} total
- Days left: TBD
- Sprint goal on track: TBD

## Yesterday's Parking Lot
{_format_action_items(config.get("previous_action_items", []))}

## Today's Parking Lot
_(captured during meeting)_
"""


def generate_standup_notes(config):
    members = config.get("team_members", [])
    rows = "\n".join(f"| {m} |  |  |  |" for m in members)
    return f"""# Standup Notes — {config.get("meeting_date", "[Date]")}

**Sprint:** {config.get("sprint_number", "N")} | **Team:** {config.get("team_name", "Team")}
**Attendees:** {", ".join(members)} | **Absent:** _none_

## Updates
| Person | Yesterday | Today | Blockers |
|--------|-----------|-------|----------|
{rows}

## Blockers Raised
| Blocker | Raised By | Owner | Resolution Plan | Due |
|---------|-----------|-------|-----------------|-----|
|  |  |  |  |  |

## Parking Lot Items
| Topic | Participants | Scheduled For |
|-------|-------------|---------------|
|  |  |  |

## Sprint Health
- Points remaining: ___ / {config.get("committed_points", "___")}
- On track: ☐ Yes  ☐ At risk  ☐ Behind
"""


def generate_planning_playbook(config):
    duration = config.get("sprint_duration_weeks", 2) * 2
    half = duration // 2
    team = ", ".join(config.get("team_members", []))
    stories_table = _format_stories(config.get("stories", []))

    return f"""# Sprint {config.get("sprint_number", "N")} Planning — Facilitation Playbook

## Meeting Metadata
- **Team:** {config.get("team_name", "Team")}
- **Sprint:** {config.get("sprint_number", "N")}
- **Date:** {config.get("meeting_date", "TBD")}
- **Duration:** {duration} hours ({half}h What + {half}h How)
- **Facilitator:** {config.get("facilitator", "SM")}
- **Product Owner:** {config.get("product_owner", "PO")}
- **Participants:** {team}
- **Location:** {config.get("location", "TBD")}

---

## Pre-Meeting Checklist
- [ ] Backlog refined — top items meet Definition of Ready
- [ ] PO has sprint goal and priority stories prepared
- [ ] Velocity calculated: Last sprint = {config.get("velocity_last_sprint", "N/A")}, Average = {config.get("velocity_average", "N/A")}
- [ ] Team capacity calculated (PTO, holidays accounted)
- [ ] Previous retro action items reviewed
- [ ] Room/call setup with screen sharing

---

## PART 1: WHAT — Sprint Goal & Story Selection ({half} hours)

### Opening & Context (10 min)
⏱️ Timer: 10 minutes
🎤 Speaker: Facilitator
📋 Say:
> "Welcome to Sprint {config.get("sprint_number", "N")} planning. Quick context:
> Last sprint velocity: {config.get("velocity_last_sprint", "N/A")} points.
> Rolling average: {config.get("velocity_average", "N/A")} points.
>
> Previous retro actions:
{_format_action_items_inline(config.get("previous_action_items", []))}
>
> [PO Name], please share the sprint goal and priorities."

### Sprint Goal (15 min)
🎤 Speaker: Product Owner
📋 Sprint Goal: _{config.get("sprint_goal", "TBD")}_

### Story Walkthrough (60 min)
🎤 Speaker: PO + Team — 5-8 min per story

Candidate Stories:
{stories_table}

### Estimation (30 min)
🎤 Speaker: Team — Planning Poker / T-shirt sizing

### Commitment (15 min)
📋 Say:
> "Capacity: ~{config.get("velocity_average", "N/A")} points. Safe commitment (85%): ~{int(config.get("velocity_average", 0) * 0.85)} points.
> Team — are we confident in this selection?"

---

## ☕ BREAK (15 min)

---

## PART 2: HOW — Task Breakdown ({half} hours)

### Task Decomposition (bulk of Part 2)
For each committed story: identify tasks (2-8 hr chunks), technical approach, assignee, risks.

### Risk & Dependency Review (10 min)
📋 Say:
> "Any external dependencies? Technical risks? Availability risks?"

### Closing (5 min)
📋 Say:
> "Sprint Goal: {config.get("sprint_goal", "TBD")}
> Committed: [N] stories, [X] points.
> Team — final confirmation. Are we committed?"

---

## Post-Meeting
- [ ] Sprint backlog entered in tool
- [ ] Board set up / reset
- [ ] Sprint goal posted in team channel
- [ ] Ceremony calendar invites sent
"""


def generate_planning_agenda(config):
    duration = config.get("sprint_duration_weeks", 2) * 2
    stories_table = _format_stories(config.get("stories", []))
    return f"""# Sprint {config.get("sprint_number", "N")} Planning Agenda — {config.get("meeting_date", "[Date]")}

**Team:** {config.get("team_name", "Team")} | **Duration:** {duration} hours | **Facilitator:** {config.get("facilitator", "SM")}
**PO:** {config.get("product_owner", "PO")} | **Location:** {config.get("location", "TBD")}

## Sprint Goal (Draft)
{config.get("sprint_goal", "TBD")}

## Part 1: WHAT ({duration // 2}h)
| Time | Activity | Owner | Duration |
|------|----------|-------|----------|
| Start | Opening & retro action review | SM | 10 min |
| +10 | Sprint goal presentation | PO | 15 min |
| +25 | Story walkthrough & clarification | PO + Team | 60 min |
| +85 | Estimation | Team | 30 min |
| +115 | Sprint commitment | Team | 15 min |

## Break (15 min)

## Part 2: HOW ({duration // 2}h)
| Time | Activity | Owner | Duration |
|------|----------|-------|----------|
| Resume | Task decomposition | Team | {(duration // 2 * 60) - 15} min |
| -15 | Risk review + closing | SM | 15 min |

## Candidate Stories
{stories_table}

## Preparation
- [ ] PO: Backlog prioritized, goal drafted
- [ ] Devs: Review top 10 backlog items
- [ ] SM: Velocity + capacity plan ready
"""


def generate_planning_notes(config):
    stories_table = _format_stories(config.get("stories", []))
    return f"""# Sprint {config.get("sprint_number", "N")} Planning Notes — {config.get("meeting_date", "[Date]")}

**Attendees:** {", ".join(config.get("team_members", []))}
**Absent:** _none_

## Sprint Metadata
- Sprint Goal: {config.get("sprint_goal", "TBD")}
- Duration: {config.get("start_date", "TBD")} — {config.get("end_date", "TBD")}
- Velocity (3-sprint avg): {config.get("velocity_average", "N/A")}
- Committed Points: ___

## Committed Stories
{stories_table}

## Stretch Goals
| ID | Title | Points |
|----|-------|--------|
|  |  |  |

## Risks & Dependencies
| Risk | Likelihood | Impact | Mitigation | Owner |
|------|-----------|--------|------------|-------|
|  |  |  |  |  |

## Previous Retro Actions
{_format_action_items(config.get("previous_action_items", []))}

## Decisions Made
1.

## Parking Lot
-
"""


def generate_review_playbook(config):
    duration_hrs = config.get("sprint_duration_weeks", 2)
    team = ", ".join(config.get("team_members", []))
    demos = ""
    for s in config.get("stories", []):
        demos += f"""
### Demo: {s.get("id", "???")} — {s.get("title", "Untitled")}
⏱️ Timer: 8-10 minutes
🎤 Speaker: {s.get("assignee", "TBD")}
📋 Facilitator introduces:
> "{s.get("assignee", "A team member")} will demo {s.get("id", "this story")}: {s.get("title", "")}."
📋 After demo:
> "Questions or feedback? Does this meet expectations?"

"""
    return f"""# Sprint {config.get("sprint_number", "N")} Review — Facilitation Playbook

## Meeting Metadata
- **Team:** {config.get("team_name", "Team")}
- **Sprint:** {config.get("sprint_number", "N")}
- **Date:** {config.get("meeting_date", "TBD")}
- **Duration:** {duration_hrs} hours
- **Facilitator:** {config.get("facilitator", "SM")}
- **PO:** {config.get("product_owner", "PO")}
- **Participants:** {team}

## Pre-Meeting Checklist
- [ ] Demo environment working with realistic test data
- [ ] Each story has a designated demo-er
- [ ] Stakeholders confirmed attendance
- [ ] Sprint metrics prepared

---

## Playbook

### Opening (10 min)
📋 Say:
> "Welcome to Sprint {config.get("sprint_number", "N")} Review.
> Sprint goal: *{config.get("sprint_goal", "TBD")}*
> Committed: {config.get("stories_committed", "N")} stories / {config.get("committed_points", "N")} points.
> Completed: {config.get("stories_completed", "N")} stories.
> Let's demo what we built."

---

## Demos
{demos}

### Incomplete Work (5 min)
📋 Say:
> "Stories not completed this sprint: [list with reasons].
> These carry to Sprint {config.get("sprint_number", 0) + 1}."

### Backlog Impact (15 min)
🎤 Speaker: Product Owner
> Feedback items, priority shifts, upcoming focus.

### Closing (5 min)
📋 Say:
> "Thank you everyone. Next review: [date]. Next sprint focus: [preview]."
"""


def generate_review_agenda(config):
    duration_hrs = config.get("sprint_duration_weeks", 2)
    demos = "\n".join(
        f"| +{10 + i*10} | Demo: {s.get('title', 'Story')} | {s.get('assignee', 'TBD')} | 10 min |"
        for i, s in enumerate(config.get("stories", []))
    )
    return f"""# Sprint {config.get("sprint_number", "N")} Review Agenda — {config.get("meeting_date", "[Date]")}

**Duration:** {duration_hrs}h | **Facilitator:** {config.get("facilitator", "SM")} | **PO:** {config.get("product_owner", "PO")}

## Sprint Goal
{config.get("sprint_goal", "TBD")}

## Agenda
| Time | Activity | Presenter | Duration |
|------|----------|-----------|----------|
| Start | Sprint recap | SM | 10 min |
{demos}
| | Incomplete work | SM + PO | 5 min |
| | Backlog impact | PO | 15 min |
| | Q&A + closing | SM | 10 min |
"""


def generate_review_notes(config):
    story_rows = "\n".join(
        f"| {s.get('id', '')} | {s.get('assignee', '')} |  |  |"
        for s in config.get("stories", [])
    )
    return f"""# Sprint {config.get("sprint_number", "N")} Review Notes — {config.get("meeting_date", "[Date]")}

**Attendees:** {", ".join(config.get("team_members", []))}

## Sprint Summary
- Goal: {config.get("sprint_goal", "TBD")}
- Committed: {config.get("stories_committed", "N")} stories / {config.get("committed_points", "N")} pts
- Completed: {config.get("stories_completed", "N")} stories
- Goal achieved: ☐ Yes  ☐ Partial  ☐ No

## Demos
| Story | Demo-er | Stakeholder Reaction | Feedback |
|-------|---------|---------------------|----------|
{story_rows}

## New Backlog Items from Feedback
| Feedback | Source | Priority | Backlog ID |
|----------|--------|----------|------------|
|  |  |  |  |

## Action Items
| Action | Owner | Due |
|--------|-------|-----|
|  |  |  |
"""


def generate_retro_playbook(config):
    fmt = config.get("retro_format", "start-stop-continue")
    duration = config.get("duration_minutes", 90)
    team = ", ".join(config.get("team_members", []))

    format_instructions = _get_retro_format_instructions(fmt)

    return f"""# Sprint {config.get("sprint_number", "N")} Retrospective — Facilitation Playbook

## Meeting Metadata
- **Team:** {config.get("team_name", "Team")}
- **Sprint:** {config.get("sprint_number", "N")}
- **Date:** {config.get("meeting_date", "TBD")}
- **Duration:** {duration} minutes
- **Facilitator:** {config.get("facilitator", "SM")}
- **Format:** {fmt.replace("-", " ").title()}
- **Participants:** {team}

## Pre-Meeting Checklist
- [ ] Retro format materials ready (sticky notes / digital board)
- [ ] Previous action items reviewed
- [ ] Sprint metrics available
- [ ] Room / call set up

---

## Phase 1: Set the Stage (10 min)

📋 Ground Rules:
> "Welcome to our retro. Ground rules:
> 1. Vegas rule — what's said stays here.
> 2. Prime Directive — everyone did their best with what they knew.
> 3. Process, not people.
> 4. We leave with 1-3 action items."

📋 Previous Action Items:
{_format_action_items_inline(config.get("previous_action_items", []))}

📋 Safety Check:
> "Scale of 1-5, how safe do you feel sharing honestly? Show fingers."

📋 Check-in:
> "One word that describes this sprint for you."

---

## Phase 2: Gather Data — {fmt.replace("-", " ").title()} ({int(duration * 0.3)} min)

{format_instructions}

---

## Phase 3: Generate Insights ({int(duration * 0.25)} min)

📋 Say:
> "Let's find patterns. Help me group similar items."

1. Cluster sticky notes into themes (5 min)
2. Name each theme (2 min)
3. Dot vote: 3 votes per person (3 min)
4. Discuss top 2-3 themes — ask "Why?" to find root causes (remaining time)

---

## Phase 4: Decide What to Do ({int(duration * 0.25)} min)

📋 Say:
> "For each top theme, what's ONE concrete thing we can do next sprint?"

Rules:
- 1-3 actions maximum
- Each needs an owner (a person, not "the team")
- Each needs a due date
- Must be within our control

---

## Phase 5: Close ({int(duration * 0.1)} min)

📋 Appreciation Round:
> "Who would you like to thank for something this sprint?"

📋 Meta-Retro:
> "Rate this retro 1-5. What should I change next time?"

📋 Close:
> "Our action items: [list]. I'll post these in our channel. Great sprint, team."
"""


def generate_retro_agenda(config):
    fmt = config.get("retro_format", "start-stop-continue")
    duration = config.get("duration_minutes", 90)
    return f"""# Sprint {config.get("sprint_number", "N")} Retrospective Agenda — {config.get("meeting_date", "[Date]")}

**Duration:** {duration} min | **Facilitator:** {config.get("facilitator", "SM")} | **Format:** {fmt.replace("-", " ").title()}

## Agenda
| Time | Phase | Activity | Duration |
|------|-------|----------|----------|
| Start | Set the Stage | Check-in + safety check | {int(duration * 0.1)} min |
| +{int(duration * 0.1)} | Gather Data | {fmt.replace("-", " ").title()} activity | {int(duration * 0.3)} min |
| +{int(duration * 0.4)} | Generate Insights | Clustering + dot voting | {int(duration * 0.25)} min |
| +{int(duration * 0.65)} | Decide What to Do | SMART action items | {int(duration * 0.25)} min |
| +{int(duration * 0.9)} | Close | Appreciation + meta-retro | {int(duration * 0.1)} min |

## Previous Action Items
{_format_action_items(config.get("previous_action_items", []))}

## Ground Rules
- Vegas rule: what's said here stays here
- Prime Directive: assume best intent
- Focus on process, not people
- Leave with 1-3 concrete actions
"""


def generate_retro_notes(config):
    return f"""# Sprint {config.get("sprint_number", "N")} Retrospective Notes — {config.get("meeting_date", "[Date]")}

**Attendees:** {", ".join(config.get("team_members", []))}
**Facilitator:** {config.get("facilitator", "SM")}
**Format:** {config.get("retro_format", "start-stop-continue").replace("-", " ").title()}

## Safety Check Score: ___/5

## Previous Action Items
{_format_action_items(config.get("previous_action_items", []))}

## Themes Identified
| Theme | Votes | Key Points |
|-------|-------|------------|
|  |  |  |

## New Action Items
| Action | Owner | Due | Success Criteria |
|--------|-------|-----|------------------|
|  |  |  |  |

## Appreciation Highlights
-

## Meta-Retro Score: ___/5
"""


# ── Helper Functions ─────────────────────────────────────────────────

def _format_action_items(items):
    if not items:
        return "- _(none)_"
    return "\n".join(
        f"- {'☑' if i.get('status','').lower() == 'done' else '☐'} {i.get('action', '')} — {i.get('owner', '??')} — {i.get('status', 'Open')}"
        for i in items
    )


def _format_action_items_inline(items):
    if not items:
        return "> - _(none)_"
    return "\n".join(
        f"> - {i.get('action', '')}: {i.get('status', 'Open')}"
        for i in items
    )


def _format_stories(stories):
    if not stories:
        return "| — | — | — | — |\n"
    header = "| ID | Title | Points | Assignee |\n|---|---|---|---|\n"
    rows = "\n".join(
        f"| {s.get('id', '')} | {s.get('title', '')} | {s.get('points', s.get('story_points', ''))} | {s.get('assignee', '')} |"
        for s in stories
    )
    return header + rows


def _get_retro_format_instructions(fmt):
    formats = {
        "start-stop-continue": """### Start / Stop / Continue

**Columns:** Start | Stop | Continue

📋 Say:
> "You have 7 minutes of silent writing. For each column:
> **Start** — Things we should begin doing.
> **Stop** — Things we should stop doing.
> **Continue** — Things working well, keep doing.
> One idea per sticky note. Go."

1. ⏱️ Silent writing: 7 min
2. ⏱️ Share & cluster: 8 min (each person places notes, 30 sec explanation)
3. ⏱️ Dot vote: 3 min (3 votes per person)
4. ⏱️ Discuss top items: 7 min""",

        "mad-sad-glad": """### Mad / Sad / Glad

**Columns:** Mad 😡 | Sad 😢 | Glad 😊

📋 Say:
> "Think about this sprint emotionally.
> **Mad** — What frustrated or angered you?
> **Sad** — What disappointed you?
> **Glad** — What made you happy or proud?
> Let's start with Glad to set a positive tone."

1. ⏱️ Silent writing: 7 min
2. ⏱️ Share (start with Glad): 8 min
3. ⏱️ Dot vote: 3 min
4. ⏱️ Discuss Mad/Sad items: 7 min""",

        "4ls": """### 4Ls — Liked, Learned, Lacked, Longed For

**Quadrants:** Liked | Learned | Lacked | Longed For

📋 Say:
> "Four quadrants:
> **Liked** — What went well?
> **Learned** — What did you learn?
> **Lacked** — What was missing?
> **Longed For** — What do you wish you had?"

1. ⏱️ Silent writing: 8 min
2. ⏱️ Share & cluster: 8 min
3. ⏱️ Dot vote: 3 min
4. ⏱️ Discuss Lacked + Longed For: 6 min""",

        "sailboat": """### Sailboat ⛵

**Elements:** Island 🏝️ | Wind 💨 | Anchors ⚓ | Rocks 🪨

📋 Say:
> "Picture our team as a sailboat:
> **Island** — Our destination / goal.
> **Wind** — What's propelling us forward.
> **Anchors** — What's slowing us down.
> **Rocks** — Risks we see ahead."

1. ⏱️ Explain metaphor: 2 min
2. ⏱️ Silent writing: 8 min
3. ⏱️ Share: 10 min
4. ⏱️ Dot vote on Anchors + Rocks: 3 min
5. ⏱️ Discuss: 7 min""",

        "starfish": """### Starfish ⭐

**Sections:** Keep Doing | More Of | Less Of | Stop Doing | Start Doing

📋 Say:
> "Five categories — more nuanced than Start/Stop/Continue:
> **Keep** — Don't change. **More** — Good, want more.
> **Less** — Too much. **Stop** — Not valuable. **Start** — New ideas."

1. ⏱️ Silent writing: 8 min
2. ⏱️ Share & cluster: 8 min
3. ⏱️ Dot vote: 3 min
4. ⏱️ Discuss: 6 min""",

        "daki": """### DAKI — Drop, Add, Keep, Improve

**Quadrants:** Drop | Add | Keep | Improve

📋 Say:
> "Action-oriented retro:
> **Drop** — Stop entirely. **Add** — Start something new.
> **Keep** — Working, don't touch. **Improve** — Exists but needs work."

1. ⏱️ Silent writing: 8 min
2. ⏱️ Share & cluster: 8 min
3. ⏱️ Dot vote: 3 min
4. ⏱️ Convert to SMART actions: 6 min""",
    }
    return formats.get(fmt, formats["start-stop-continue"])


# ── Generator Registry ───────────────────────────────────────────────

GENERATORS = {
    ("standup", "playbook"): generate_standup_playbook,
    ("standup", "agenda"): generate_standup_agenda,
    ("standup", "notes"): generate_standup_notes,
    ("planning", "playbook"): generate_planning_playbook,
    ("planning", "agenda"): generate_planning_agenda,
    ("planning", "notes"): generate_planning_notes,
    ("review", "playbook"): generate_review_playbook,
    ("review", "agenda"): generate_review_agenda,
    ("review", "notes"): generate_review_notes,
    ("retro", "playbook"): generate_retro_playbook,
    ("retro", "agenda"): generate_retro_agenda,
    ("retro", "notes"): generate_retro_notes,
}


def main():
    parser = argparse.ArgumentParser(description="Generate Agile ceremony documents")
    parser.add_argument("--ceremony", choices=["standup", "planning", "review", "retro"], required=True)
    parser.add_argument("--type", choices=["playbook", "agenda", "notes"], required=True, dest="doc_type")
    parser.add_argument("--config", help="Path to JSON config")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()

    if args.config:
        with open(args.config, "r") as f:
            config = json.load(f)
    else:
        config = json.load(sys.stdin)

    generator = GENERATORS.get((args.ceremony, args.doc_type))
    if not generator:
        print(f"No generator for {args.ceremony}/{args.doc_type}", file=sys.stderr)
        sys.exit(1)

    content = generator(config)

    output = args.output or f"{args.ceremony}_{args.doc_type}.md"
    with open(output, "w") as f:
        f.write(content)

    print(f"Generated: {output}")


if __name__ == "__main__":
    main()

```


---

<!-- Script: scripts/generate_retro_board.py -->

# Script: generate_retro_board.py

```python
#!/usr/bin/env python3
"""
Generate an interactive HTML retrospective board with columns, sticky notes,
voting, and CSV export.

Usage:
    python generate_retro_board.py \
        --format start-stop-continue|4ls|sailboat|mad-sad-glad|starfish|daki \
        --team-size 6 \
        --sprint "Sprint 14" \
        --output retro_board.html
"""

import argparse
import json

FORMATS = {
    "start-stop-continue": {
        "title": "Start / Stop / Continue",
        "columns": [
            {"id": "start", "label": "🚀 Start", "color": "#4CAF50", "desc": "Things we should begin doing"},
            {"id": "stop", "label": "🛑 Stop", "color": "#f44336", "desc": "Things we should stop doing"},
            {"id": "continue", "label": "✅ Continue", "color": "#2196F3", "desc": "Things working well"},
        ]
    },
    "mad-sad-glad": {
        "title": "Mad / Sad / Glad",
        "columns": [
            {"id": "mad", "label": "😡 Mad", "color": "#f44336", "desc": "What frustrated you?"},
            {"id": "sad", "label": "😢 Sad", "color": "#9C27B0", "desc": "What disappointed you?"},
            {"id": "glad", "label": "😊 Glad", "color": "#4CAF50", "desc": "What made you happy?"},
        ]
    },
    "4ls": {
        "title": "4Ls",
        "columns": [
            {"id": "liked", "label": "👍 Liked", "color": "#4CAF50", "desc": "What went well?"},
            {"id": "learned", "label": "🧠 Learned", "color": "#2196F3", "desc": "What did you learn?"},
            {"id": "lacked", "label": "❌ Lacked", "color": "#FF9800", "desc": "What was missing?"},
            {"id": "longed", "label": "💭 Longed For", "color": "#9C27B0", "desc": "What do you wish you had?"},
        ]
    },
    "sailboat": {
        "title": "Sailboat ⛵",
        "columns": [
            {"id": "island", "label": "🏝️ Island (Goal)", "color": "#4CAF50", "desc": "Where are we heading?"},
            {"id": "wind", "label": "💨 Wind", "color": "#2196F3", "desc": "What propels us forward?"},
            {"id": "anchor", "label": "⚓ Anchors", "color": "#FF9800", "desc": "What slows us down?"},
            {"id": "rocks", "label": "🪨 Rocks", "color": "#f44336", "desc": "What risks lie ahead?"},
        ]
    },
    "starfish": {
        "title": "Starfish ⭐",
        "columns": [
            {"id": "keep", "label": "✅ Keep", "color": "#4CAF50", "desc": "Don't change"},
            {"id": "more", "label": "⬆️ More Of", "color": "#2196F3", "desc": "Good, want more"},
            {"id": "less", "label": "⬇️ Less Of", "color": "#FF9800", "desc": "Doing too much"},
            {"id": "stop", "label": "🛑 Stop", "color": "#f44336", "desc": "Not valuable"},
            {"id": "start", "label": "🚀 Start", "color": "#9C27B0", "desc": "New ideas"},
        ]
    },
    "daki": {
        "title": "DAKI",
        "columns": [
            {"id": "drop", "label": "🗑️ Drop", "color": "#f44336", "desc": "Stop entirely"},
            {"id": "add", "label": "➕ Add", "color": "#4CAF50", "desc": "Start something new"},
            {"id": "keep", "label": "✅ Keep", "color": "#2196F3", "desc": "Working, don't touch"},
            {"id": "improve", "label": "🔧 Improve", "color": "#FF9800", "desc": "Exists but needs work"},
        ]
    },
}


def generate_retro_board(fmt_key, team_size, sprint_name, output_path):
    fmt = FORMATS.get(fmt_key, FORMATS["start-stop-continue"])

    columns_json = json.dumps(fmt["columns"])
    num_cols = len(fmt["columns"])
    col_width = f"minmax(250px, 1fr)"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{sprint_name} Retrospective — {fmt["title"]}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            min-height: 100vh;
        }}
        .header {{
            background: #16213e;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #0f3460;
        }}
        .header h1 {{ font-size: 1.3rem; color: #e94560; }}
        .header .meta {{ color: #aaa; font-size: 0.85rem; }}
        .toolbar {{
            background: #16213e;
            padding: 0.5rem 2rem;
            display: flex;
            gap: 0.5rem;
            border-bottom: 1px solid #0f3460;
        }}
        .toolbar button {{
            background: #0f3460;
            color: #fff;
            border: none;
            padding: 0.4rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: background 0.2s;
        }}
        .toolbar button:hover {{ background: #e94560; }}
        .board {{
            display: grid;
            grid-template-columns: repeat({num_cols}, {col_width});
            gap: 1rem;
            padding: 1rem;
            min-height: calc(100vh - 120px);
        }}
        .column {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        .column-header {{
            text-align: center;
            padding: 0.75rem;
            border-radius: 8px;
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 0.5rem;
        }}
        .column-desc {{
            text-align: center;
            color: #888;
            font-size: 0.8rem;
            margin-bottom: 0.5rem;
        }}
        .add-btn {{
            width: 100%;
            padding: 0.5rem;
            background: rgba(255,255,255,0.08);
            border: 2px dashed rgba(255,255,255,0.15);
            border-radius: 8px;
            color: #888;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
        }}
        .add-btn:hover {{ border-color: #e94560; color: #e94560; }}
        .note {{
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 0.75rem;
            position: relative;
            border-left: 4px solid;
            animation: slideIn 0.2s ease-out;
        }}
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(-10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .note-text {{
            font-size: 0.9rem;
            line-height: 1.4;
            margin-bottom: 0.5rem;
        }}
        .note-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .note-author {{ font-size: 0.75rem; color: #888; }}
        .vote-btn {{
            background: none;
            border: 1px solid #555;
            color: #ccc;
            padding: 0.2rem 0.6rem;
            border-radius: 12px;
            cursor: pointer;
            font-size: 0.8rem;
            transition: all 0.2s;
        }}
        .vote-btn:hover {{ border-color: #e94560; color: #e94560; }}
        .vote-btn.voted {{ background: #e94560; border-color: #e94560; color: #fff; }}
        .delete-btn {{
            position: absolute;
            top: 4px;
            right: 8px;
            background: none;
            border: none;
            color: #666;
            cursor: pointer;
            font-size: 0.8rem;
        }}
        .delete-btn:hover {{ color: #f44336; }}
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.7);
            z-index: 100;
            justify-content: center;
            align-items: center;
        }}
        .modal-overlay.active {{ display: flex; }}
        .modal {{
            background: #16213e;
            border-radius: 12px;
            padding: 1.5rem;
            width: 400px;
            max-width: 90vw;
        }}
        .modal h3 {{ margin-bottom: 1rem; color: #e94560; }}
        .modal textarea {{
            width: 100%;
            height: 80px;
            background: #0f3460;
            border: 1px solid #333;
            color: #eee;
            border-radius: 8px;
            padding: 0.75rem;
            font-family: inherit;
            font-size: 0.9rem;
            resize: vertical;
        }}
        .modal input {{
            width: 100%;
            background: #0f3460;
            border: 1px solid #333;
            color: #eee;
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
            font-family: inherit;
            margin-top: 0.5rem;
        }}
        .modal-actions {{
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
            justify-content: flex-end;
        }}
        .modal-actions button {{
            padding: 0.5rem 1.2rem;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
        }}
        .btn-primary {{ background: #e94560; color: #fff; }}
        .btn-secondary {{ background: #333; color: #ccc; }}
        .stats {{
            display: flex;
            gap: 2rem;
            padding: 0 2rem;
            margin-top: 0.5rem;
        }}
        .stat {{ font-size: 0.8rem; color: #888; }}
        .stat strong {{ color: #e94560; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🔄 {sprint_name} — {fmt["title"]} Retrospective</h1>
            <div class="meta">Team size: {team_size} | Votes per person: 3</div>
        </div>
        <div class="stats">
            <div class="stat">Notes: <strong id="noteCount">0</strong></div>
            <div class="stat">Votes used: <strong id="voteCount">0</strong> / <strong>{team_size * 3}</strong></div>
        </div>
    </div>
    <div class="toolbar">
        <button onclick="exportCSV()">📥 Export CSV</button>
        <button onclick="exportJSON()">📥 Export JSON</button>
        <button onclick="sortByVotes()">🔢 Sort by Votes</button>
        <button onclick="clearAll()">🗑️ Clear All</button>
    </div>
    <div class="board" id="board"></div>

    <div class="modal-overlay" id="modal">
        <div class="modal">
            <h3 id="modalTitle">Add Note</h3>
            <textarea id="noteInput" placeholder="What's on your mind?"></textarea>
            <input id="authorInput" placeholder="Your name (optional)" />
            <div class="modal-actions">
                <button class="btn-secondary" onclick="closeModal()">Cancel</button>
                <button class="btn-primary" onclick="saveNote()">Add Note</button>
            </div>
        </div>
    </div>

    <script>
        const columns = {columns_json};
        const maxVotes = {team_size * 3};
        let notes = {{}};
        let votesUsed = 0;
        let currentColumn = null;

        function init() {{
            const board = document.getElementById('board');
            columns.forEach(col => {{
                notes[col.id] = [];
                const div = document.createElement('div');
                div.className = 'column';
                div.id = 'col-' + col.id;
                div.innerHTML = `
                    <div class="column-header" style="background: ${{col.color}}20; color: ${{col.color}}">
                        ${{col.label}}
                    </div>
                    <div class="column-desc">${{col.desc}}</div>
                    <button class="add-btn" onclick="openModal('${{col.id}}')">+ Add Note</button>
                    <div class="notes-container" id="notes-${{col.id}}"></div>
                `;
                board.appendChild(div);
            }});
        }}

        function openModal(colId) {{
            currentColumn = colId;
            const col = columns.find(c => c.id === colId);
            document.getElementById('modalTitle').textContent = 'Add to ' + col.label;
            document.getElementById('noteInput').value = '';
            document.getElementById('modal').classList.add('active');
            document.getElementById('noteInput').focus();
        }}

        function closeModal() {{
            document.getElementById('modal').classList.remove('active');
            currentColumn = null;
        }}

        function saveNote() {{
            const text = document.getElementById('noteInput').value.trim();
            const author = document.getElementById('authorInput').value.trim() || 'Anonymous';
            if (!text || !currentColumn) return;

            const note = {{ id: Date.now(), text, author, votes: 0, voted: false }};
            notes[currentColumn].push(note);
            renderNotes(currentColumn);
            updateStats();
            closeModal();
        }}

        function renderNotes(colId) {{
            const container = document.getElementById('notes-' + colId);
            const col = columns.find(c => c.id === colId);
            container.innerHTML = notes[colId].map(note => `
                <div class="note" style="border-left-color: ${{col.color}}">
                    <button class="delete-btn" onclick="deleteNote('${{colId}}', ${{note.id}})">&times;</button>
                    <div class="note-text">${{note.text}}</div>
                    <div class="note-footer">
                        <span class="note-author">${{note.author}}</span>
                        <button class="vote-btn ${{note.voted ? 'voted' : ''}}"
                                onclick="toggleVote('${{colId}}', ${{note.id}})">
                            👍 ${{note.votes}}
                        </button>
                    </div>
                </div>
            `).join('');
        }}

        function toggleVote(colId, noteId) {{
            const note = notes[colId].find(n => n.id === noteId);
            if (!note) return;
            if (note.voted) {{
                note.votes--;
                note.voted = false;
                votesUsed--;
            }} else if (votesUsed < maxVotes) {{
                note.votes++;
                note.voted = true;
                votesUsed++;
            }}
            renderNotes(colId);
            updateStats();
        }}

        function deleteNote(colId, noteId) {{
            const note = notes[colId].find(n => n.id === noteId);
            if (note && note.voted) votesUsed--;
            notes[colId] = notes[colId].filter(n => n.id !== noteId);
            renderNotes(colId);
            updateStats();
        }}

        function updateStats() {{
            const total = Object.values(notes).reduce((s, arr) => s + arr.length, 0);
            document.getElementById('noteCount').textContent = total;
            document.getElementById('voteCount').textContent = votesUsed;
        }}

        function sortByVotes() {{
            columns.forEach(col => {{
                notes[col.id].sort((a, b) => b.votes - a.votes);
                renderNotes(col.id);
            }});
        }}

        function exportCSV() {{
            let csv = 'Column,Text,Author,Votes\\n';
            columns.forEach(col => {{
                notes[col.id].forEach(note => {{
                    csv += `"${{col.label}}","${{note.text.replace(/"/g, '""')}}","${{note.author}}",${{note.votes}}\\n`;
                }});
            }});
            download(csv, 'retro_results.csv', 'text/csv');
        }}

        function exportJSON() {{
            const data = {{ sprint: '{sprint_name}', format: '{fmt["title"]}', columns: {{}} }};
            columns.forEach(col => {{ data.columns[col.id] = notes[col.id]; }});
            download(JSON.stringify(data, null, 2), 'retro_results.json', 'application/json');
        }}

        function download(content, filename, type) {{
            const blob = new Blob([content], {{ type }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url; a.download = filename; a.click();
            URL.revokeObjectURL(url);
        }}

        function clearAll() {{
            if (!confirm('Clear all notes? This cannot be undone.')) return;
            columns.forEach(col => {{ notes[col.id] = []; renderNotes(col.id); }});
            votesUsed = 0;
            updateStats();
        }}

        document.addEventListener('keydown', e => {{
            if (e.key === 'Escape') closeModal();
            if (e.key === 'Enter' && e.ctrlKey && currentColumn) saveNote();
        }});

        init();
    </script>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)

    print(f"Retro board saved to: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate Interactive Retro Board")
    parser.add_argument("--format", choices=FORMATS.keys(), default="start-stop-continue")
    parser.add_argument("--team-size", type=int, default=6)
    parser.add_argument("--sprint", default="Sprint N")
    parser.add_argument("--output", default="retro_board.html")
    args = parser.parse_args()

    generate_retro_board(args.format, args.team_size, args.sprint, args.output)


if __name__ == "__main__":
    main()

```
