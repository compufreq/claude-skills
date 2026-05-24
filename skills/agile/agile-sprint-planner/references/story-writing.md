# User Story Writing Reference

## Table of Contents
1. Story Format & Structure
2. Acceptance Criteria Patterns
3. INVEST Criteria
4. Story Splitting Techniques
5. Epic Decomposition
6. Common Personas
7. Anti-Patterns

---

## 1. Story Format & Structure

### The Canonical Format
```
As a [persona/role],
I want [goal/action],
So that [benefit/business value].
```

Every part matters:
- **As a** — Identifies WHO benefits. Use specific personas, not generic "user."
- **I want** — States WHAT they want to accomplish. Focus on the goal, not the solution.
- **So that** — Explains WHY it matters. This is the value proposition. If you can't
  articulate the "so that," the story may not be worth building.

### Story Card Layout
```
┌──────────────────────────────────────────────────┐
│ [STORY-ID]  [Priority: Must/Should/Could/Won't]  │
│ [Epic Name]                                       │
├──────────────────────────────────────────────────┤
│                                                   │
│ As a [persona],                                   │
│ I want [goal],                                    │
│ So that [value].                                  │
│                                                   │
├──────────────────────────────────────────────────┤
│ Acceptance Criteria:                              │
│ ☐ Given... When... Then...                        │
│ ☐ Given... When... Then...                        │
│                                                   │
├──────────────────────────────────────────────────┤
│ Estimate: [SP] [T-shirt] [Hours]                  │
│ Assignee: [Name]          Sprint: [N]             │
└──────────────────────────────────────────────────┘
```

---

## 2. Acceptance Criteria Patterns

### Given-When-Then (Gherkin Syntax)

This is the preferred format because it's unambiguous, testable, and maps directly to
automated test cases.

```
Given [precondition / initial state]
When [action / trigger]
Then [expected outcome / observable result]
```

**Multiple scenarios per story:**
```
Scenario 1: Successful login
Given a registered user with valid credentials
When they enter their email and password and click "Log In"
Then they are redirected to the dashboard
And a session token is stored

Scenario 2: Failed login — wrong password
Given a registered user with valid email
When they enter a wrong password and click "Log In"
Then an error message "Invalid email or password" is displayed
And no session token is created
And the password field is cleared

Scenario 3: Failed login — account locked
Given a user who has failed login 5 times in 10 minutes
When they attempt another login
Then the message "Account temporarily locked. Try again in 30 minutes." is displayed
And no login attempt is processed
```

### Acceptance Criteria Checklist (Alternative Format)

When Given/When/Then feels too heavy, use a checklist — but be specific:

```
Acceptance Criteria:
- [ ] User can upload files up to 10MB in size
- [ ] Supported formats: PDF, PNG, JPG, DOCX
- [ ] Upload progress bar is displayed during upload
- [ ] Error message shown for unsupported file types
- [ ] Uploaded files appear in the user's file list within 5 seconds
- [ ] Duplicate filenames are auto-renamed with a suffix (e.g., "report (1).pdf")
```

---

## 3. INVEST Criteria

Every user story should meet INVEST:

| Letter | Criterion | What It Means | Red Flag |
|--------|-----------|---------------|----------|
| **I** | Independent | Can be developed without requiring other stories to be done first | "This story depends on STORY-42 being completed" |
| **N** | Negotiable | Details can be discussed and adjusted | Extremely rigid requirements that can't flex |
| **V** | Valuable | Delivers value to the end user or business | "Refactor the database schema" (no user value stated) |
| **E** | Estimable | Team can estimate the effort required | Too vague or too many unknowns to size |
| **S** | Small | Can be completed in one sprint | Estimated at 21+ story points |
| **T** | Testable | Has clear criteria for "done" | "The UI should feel intuitive" (subjective) |

---

## 4. Story Splitting Techniques

When a story is too large (>13 SP, >XL, >5 days), split it using these techniques:

### By Workflow Steps
Original: "As a customer, I want to purchase a product online"
Split into:
1. "As a customer, I want to add products to my cart"
2. "As a customer, I want to enter my shipping address"
3. "As a customer, I want to pay with a credit card"
4. "As a customer, I want to receive an order confirmation email"

### By Business Rules
Original: "As an admin, I want to configure discount rules"
Split into:
1. "...configure percentage-based discounts"
2. "...configure fixed-amount discounts"
3. "...configure buy-one-get-one discounts"
4. "...set expiration dates on discounts"

### By Happy Path vs Edge Cases
Original: "As a user, I want to upload my profile photo"
Split into:
1. "...upload a JPG/PNG profile photo under 5MB" (happy path)
2. "...see an error when uploading unsupported formats" (edge case)
3. "...crop and resize my photo before saving" (enhancement)

### By Data Variations
Original: "As an analyst, I want to export reports"
Split into:
1. "...export reports as CSV"
2. "...export reports as PDF"
3. "...export reports as Excel"

### By Interface / Platform
Original: "As a user, I want to receive notifications"
Split into:
1. "...receive email notifications"
2. "...receive push notifications on mobile"
3. "...see in-app notification badges"

### By Operations (CRUD)
Original: "As an admin, I want to manage user accounts"
Split into:
1. "...create new user accounts"
2. "...view user account details"
3. "...edit user account information"
4. "...deactivate user accounts"

---

## 5. Epic Decomposition

Epics are large bodies of work that span multiple sprints. Decompose them systematically:

### Epic → Feature → Story Hierarchy
```
Epic: User Authentication System
├── Feature: Registration
│   ├── Story: Email registration with validation
│   ├── Story: Social login (Google)
│   ├── Story: Social login (GitHub)
│   └── Story: Email verification flow
├── Feature: Login
│   ├── Story: Email/password login
│   ├── Story: Remember me functionality
│   └── Story: Account lockout after failed attempts
├── Feature: Password Management
│   ├── Story: Forgot password flow
│   ├── Story: Password reset via email
│   └── Story: Password strength requirements
└── Feature: Session Management
    ├── Story: JWT token issuance
    ├── Story: Token refresh flow
    └── Story: Logout and session invalidation
```

### Epic Sizing
- If an epic has > 20 stories, consider breaking it into multiple epics
- Each epic should have a clear business objective
- Epics should be completable within 1-3 months (2-6 sprints)

---

## 6. Common Personas

When writing stories, use specific personas rather than generic "user":

| Persona | Description | Typical Goals |
|---------|-------------|---------------|
| End User | The primary consumer of the product | Complete tasks efficiently, find information |
| Admin | System administrator | Configure settings, manage users, monitor health |
| Power User | Experienced user with advanced needs | Automation, bulk operations, customization |
| New User | First-time or infrequent user | Onboarding, learning, getting started |
| API Consumer | Developer integrating with the system | Reliable API, good docs, predictable behavior |
| Support Agent | Customer support representative | Resolve tickets, access user data, escalate |

Encourage teams to develop their own persona library specific to their product.

---

## 7. Anti-Patterns

### Story Writing Anti-Patterns
- **Technical stories without user value**: "As a developer, I want to upgrade to React 18"
  → Better: "As a user, I want faster page loads, so that I can complete tasks more quickly"
  (with a technical note that this involves a React 18 upgrade)
- **Solution-prescriptive stories**: "As a user, I want a dropdown menu with..."
  → Better: "As a user, I want to select my country from a list..." (let the team decide the UI)
- **Compound stories (and-stories)**: "As a user, I want to log in AND manage my profile"
  → Split into two stories
- **No acceptance criteria**: A story without AC is just a wish
- **Vague acceptance criteria**: "It should work properly" → Define "properly" with specifics

### Persona Anti-Patterns
- **"As a user"** — Too vague. Which user? With what context?
- **"As a product owner"** — PO is a role, not a user of the product
- **"As a system"** — Systems don't have wants. Rephrase as the person who benefits.



---

<!-- Script: scripts/export_to_tools.py -->

# Script: export_to_tools.py

```python
#!/usr/bin/env python3
"""
Export sprint backlog data to various project management tool formats.

Supported formats:
- Jira CSV (for Jira import)
- Asana CSV (for Asana import)
- Trello JSON (for Trello import)
- Linear CSV (for Linear import)
- Generic CSV (universal format)

Usage:
    python export_to_tools.py --config sprint_config.json --format jira --output backlog_jira.csv
    python export_to_tools.py --config sprint_config.json --format asana --output backlog_asana.csv
    python export_to_tools.py --config sprint_config.json --format trello --output backlog_trello.json
    python export_to_tools.py --config sprint_config.json --format linear --output backlog_linear.csv
"""

import json
import csv
import sys
import argparse


def export_jira_csv(stories, config, output_path):
    """Export to Jira-compatible CSV format."""
    headers = [
        "Summary", "Issue Type", "Priority", "Story Points",
        "Description", "Acceptance Criteria", "Epic Link",
        "Sprint", "Labels", "Components", "Assignee"
    ]

    priority_map = {
        "Must": "Highest",
        "Should": "High",
        "Could": "Medium",
        "Won't": "Low"
    }

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for story in stories:
            writer.writerow([
                story.get("title", ""),
                "Story",
                priority_map.get(story.get("priority", ""), "Medium"),
                story.get("story_points", ""),
                story.get("description", ""),
                story.get("acceptance_criteria", ""),
                story.get("epic", ""),
                config.get("sprint_name", ""),
                "",  # Labels
                "",  # Components
                story.get("assignee", ""),
            ])

    print(f"Jira CSV exported to: {output_path}")


def export_asana_csv(stories, config, output_path):
    """Export to Asana-compatible CSV format."""
    headers = [
        "Name", "Section", "Priority", "Description",
        "Due Date", "Assignee", "Tags"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for story in stories:
            tags = []
            if story.get("epic"):
                tags.append(story["epic"])
            if story.get("story_points"):
                tags.append(f"{story['story_points']}SP")
            if story.get("tshirt_size"):
                tags.append(story["tshirt_size"])

            writer.writerow([
                f"[{story.get('id', '')}] {story.get('title', '')}",
                config.get("sprint_name", "Backlog"),
                story.get("priority", ""),
                story.get("description", ""),
                config.get("end_date", ""),
                story.get("assignee", ""),
                ",".join(tags),
            ])

    print(f"Asana CSV exported to: {output_path}")


def export_trello_json(stories, config, output_path):
    """Export to Trello-compatible JSON format."""
    # Group stories by status
    lists_map = {}
    for story in stories:
        status = story.get("status", "To Do")
        if status not in lists_map:
            lists_map[status] = []
        lists_map[status].append(story)

    trello_data = {
        "name": config.get("sprint_name", "Sprint Board"),
        "desc": config.get("sprint_goal", ""),
        "lists": []
    }

    for list_name, list_stories in lists_map.items():
        trello_list = {
            "name": list_name,
            "cards": []
        }
        for story in list_stories:
            card = {
                "name": f"[{story.get('id', '')}] {story.get('title', '')}",
                "desc": story.get("description", ""),
                "labels": [],
                "checklists": []
            }

            if story.get("priority"):
                card["labels"].append({"name": story["priority"], "color": "red"})
            if story.get("story_points"):
                card["labels"].append({"name": f"{story['story_points']} SP", "color": "blue"})

            if story.get("acceptance_criteria"):
                card["checklists"].append({
                    "name": "Acceptance Criteria",
                    "items": [
                        {"name": ac, "checked": False}
                        for ac in story["acceptance_criteria"]
                    ] if isinstance(story["acceptance_criteria"], list) else [
                        {"name": story["acceptance_criteria"], "checked": False}
                    ]
                })

            trello_list["cards"].append(card)

        trello_data["lists"].append(trello_list)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(trello_data, f, indent=2)

    print(f"Trello JSON exported to: {output_path}")


def export_linear_csv(stories, config, output_path):
    """Export to Linear-compatible CSV format."""
    headers = [
        "Title", "Description", "Priority", "Estimate",
        "Team", "Project", "Label"
    ]

    priority_map = {
        "Must": "Urgent",
        "Should": "High",
        "Could": "Medium",
        "Won't": "Low"
    }

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for story in stories:
            writer.writerow([
                story.get("title", ""),
                story.get("description", ""),
                priority_map.get(story.get("priority", ""), "Medium"),
                story.get("story_points", ""),
                "",  # Team
                config.get("sprint_name", ""),
                story.get("epic", ""),
            ])

    print(f"Linear CSV exported to: {output_path}")


def export_generic_csv(stories, config, output_path):
    """Export to a universal CSV format."""
    headers = [
        "ID", "Epic", "Title", "Description", "Priority",
        "Story Points", "T-Shirt Size", "Time Estimate (hrs)",
        "Assignee", "Status", "Sprint", "Acceptance Criteria"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for story in stories:
            ac = story.get("acceptance_criteria", "")
            if isinstance(ac, list):
                ac = "; ".join(ac)

            writer.writerow([
                story.get("id", ""),
                story.get("epic", ""),
                story.get("title", ""),
                story.get("description", ""),
                story.get("priority", ""),
                story.get("story_points", ""),
                story.get("tshirt_size", ""),
                story.get("time_estimate_hours", ""),
                story.get("assignee", ""),
                story.get("status", "To Do"),
                config.get("sprint_name", ""),
                ac,
            ])

    print(f"Generic CSV exported to: {output_path}")


EXPORTERS = {
    "jira": export_jira_csv,
    "asana": export_asana_csv,
    "trello": export_trello_json,
    "linear": export_linear_csv,
    "csv": export_generic_csv,
}


def main():
    parser = argparse.ArgumentParser(description="Export backlog to PM tool format")
    parser.add_argument("--config", help="Path to JSON config file")
    parser.add_argument("--format", choices=EXPORTERS.keys(), default="csv",
                        help="Export format")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()

    if args.config:
        with open(args.config, "r") as f:
            config = json.load(f)
    else:
        config = json.load(sys.stdin)

    stories = config.get("stories", [])

    if not args.output:
        ext = "json" if args.format == "trello" else "csv"
        args.output = f"backlog_{args.format}.{ext}"

    EXPORTERS[args.format](stories, config, args.output)


if __name__ == "__main__":
    main()

```


---

<!-- Script: scripts/generate_burndown_chart.py -->

# Script: generate_burndown_chart.py

```python
#!/usr/bin/env python3
"""
Generate a sprint burndown chart as a standalone HTML file with interactive Chart.js visualization.

Usage:
    python generate_burndown_chart.py --config sprint_config.json --output burndown.html

The config JSON should follow the same schema as generate_sprint_xlsx.py, with an additional
optional "daily_actuals" array for tracking actual progress:

{
    "sprint_name": "Sprint 14",
    "sprint_duration_weeks": 2,
    "stories": [...],
    "daily_actuals": [
        {"day": 0, "remaining": 35},
        {"day": 1, "remaining": 33},
        {"day": 2, "remaining": 28},
        ...
    ]
}
"""

import json
import sys
import argparse


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Burndown Chart</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f8f9fa;
            padding: 2rem;
            color: #333;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            padding: 2rem;
        }}
        h1 {{
            color: #2f5496;
            margin-bottom: 0.5rem;
            font-size: 1.5rem;
        }}
        .subtitle {{
            color: #888;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
        }}
        .chart-wrapper {{
            position: relative;
            height: 400px;
            margin-bottom: 1.5rem;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }}
        .stat-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }}
        .stat-card .value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #2f5496;
        }}
        .stat-card .label {{
            font-size: 0.8rem;
            color: #888;
            margin-top: 0.25rem;
        }}
        .on-track {{ color: #28a745 !important; }}
        .at-risk {{ color: #ffc107 !important; }}
        .behind {{ color: #dc3545 !important; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="subtitle">{subtitle}</div>
        <div class="chart-wrapper">
            <canvas id="burndownChart"></canvas>
        </div>
        <div class="stats">
            <div class="stat-card">
                <div class="value">{total_points}</div>
                <div class="label">Total Points</div>
            </div>
            <div class="stat-card">
                <div class="value">{remaining_points}</div>
                <div class="label">Remaining</div>
            </div>
            <div class="stat-card">
                <div class="value">{completed_points}</div>
                <div class="label">Completed</div>
            </div>
            <div class="stat-card">
                <div class="value {status_class}">{completion_pct}%</div>
                <div class="label">Complete</div>
            </div>
        </div>
    </div>
    <script>
        const ctx = document.getElementById('burndownChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {day_labels},
                datasets: [
                    {{
                        label: 'Ideal Burndown',
                        data: {ideal_data},
                        borderColor: '#2f5496',
                        borderDash: [8, 4],
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 3,
                        tension: 0
                    }},
                    {{
                        label: 'Actual Burndown',
                        data: {actual_data},
                        borderColor: '#e74c3c',
                        borderWidth: 3,
                        fill: false,
                        pointRadius: 5,
                        pointBackgroundColor: '#e74c3c',
                        tension: 0.1
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'top' }},
                    title: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: 'Story Points Remaining' }}
                    }},
                    x: {{
                        title: {{ display: true, text: 'Sprint Day' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""


def generate_burndown_html(config, output_path):
    """Generate an interactive burndown chart as HTML."""
    sprint_name = config.get("sprint_name", "Sprint")
    duration_weeks = config.get("sprint_duration_weeks", 2)
    total_days = duration_weeks * 5
    stories = config.get("stories", [])
    total_points = sum(
        s.get("story_points", 0) for s in stories
        if isinstance(s.get("story_points"), (int, float))
    )

    # Ideal burndown
    ideal_per_day = total_points / total_days if total_days > 0 else 0
    ideal_data = [round(total_points - (ideal_per_day * d), 1) for d in range(total_days + 1)]
    day_labels = [f"Day {d}" for d in range(total_days + 1)]

    # Actual data
    daily_actuals = config.get("daily_actuals", [])
    if daily_actuals:
        actual_data = [None] * (total_days + 1)
        for entry in daily_actuals:
            day = entry.get("day", 0)
            if 0 <= day <= total_days:
                actual_data[day] = entry.get("remaining", None)
        remaining = actual_data[-1] if actual_data[-1] is not None else (
            next((v for v in reversed(actual_data) if v is not None), total_points)
        )
    else:
        actual_data = [total_points]  # Only day 0
        remaining = total_points

    completed = total_points - remaining
    pct = round((completed / total_points * 100), 1) if total_points > 0 else 0

    if pct >= 80:
        status_class = "on-track"
    elif pct >= 50:
        status_class = "at-risk"
    else:
        status_class = "behind"

    start = config.get("start_date", "")
    end = config.get("end_date", "")
    subtitle = f"{duration_weeks}-week sprint"
    if start and end:
        subtitle += f" ({start} — {end})"

    html = HTML_TEMPLATE.format(
        title=f"{sprint_name} Burndown",
        subtitle=subtitle,
        total_points=total_points,
        remaining_points=remaining,
        completed_points=completed,
        completion_pct=pct,
        status_class=status_class,
        day_labels=json.dumps(day_labels),
        ideal_data=json.dumps(ideal_data),
        actual_data=json.dumps(actual_data),
    )

    with open(output_path, "w") as f:
        f.write(html)

    print(f"Burndown chart saved to: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate Sprint Burndown Chart")
    parser.add_argument("--config", help="Path to JSON config file")
    parser.add_argument("--output", default="burndown.html", help="Output .html path")
    args = parser.parse_args()

    if args.config:
        with open(args.config, "r") as f:
            config = json.load(f)
    else:
        config = json.load(sys.stdin)

    generate_burndown_html(config, args.output)


if __name__ == "__main__":
    main()

```


---

<!-- Script: scripts/generate_sprint_xlsx.py -->

# Script: generate_sprint_xlsx.py

```python
#!/usr/bin/env python3
"""
Generate a full sprint tracking spreadsheet (.xlsx) with multiple sheets:
- Sprint Backlog
- Capacity Plan
- Burndown Data
- Velocity History

Usage:
    python generate_sprint_xlsx.py --config sprint_config.json --output sprint_tracker.xlsx
    OR
    echo '{"sprint_name": "Sprint 1", ...}' | python generate_sprint_xlsx.py --output sprint_tracker.xlsx

Config JSON Schema:
{
    "sprint_name": "Sprint 14",
    "sprint_number": 14,
    "sprint_duration_weeks": 2,
    "start_date": "2025-01-13",
    "end_date": "2025-01-24",
    "sprint_goal": "Complete user authentication flow for beta launch",
    "team": [
        {"name": "Alice", "role": "Developer", "total_days": 10, "pto_days": 0},
        {"name": "Bob", "role": "Developer", "total_days": 10, "pto_days": 1},
        {"name": "Carol", "role": "QA", "total_days": 10, "pto_days": 0}
    ],
    "stories": [
        {
            "id": "PROJ-101",
            "epic": "Authentication",
            "title": "Email/password login",
            "description": "User can log in with email and password",
            "priority": "Must",
            "story_points": 5,
            "tshirt_size": "M",
            "time_estimate_hours": 16,
            "assignee": "Alice",
            "status": "To Do"
        }
    ],
    "velocity_history": [
        {"sprint": 11, "committed": 34, "completed": 30},
        {"sprint": 12, "committed": 32, "completed": 33},
        {"sprint": 13, "committed": 35, "completed": 31}
    ],
    "estimation_method": "story_points"
}
"""

import json
import sys
import argparse
from datetime import datetime, timedelta

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.chart import BarChart, LineChart, Reference
    from openpyxl.formatting.rule import CellIsRule, DataBarRule
except ImportError:
    print("Installing openpyxl...", file=sys.stderr)
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl", "--break-system-packages", "-q"])
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.chart import BarChart, LineChart, Reference
    from openpyxl.formatting.rule import CellIsRule, DataBarRule


# ── Style Constants ──────────────────────────────────────────────────────────
HEADER_FONT = Font(name="Calibri", bold=True, size=11, color="FFFFFF")
HEADER_FILL = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
TITLE_FONT = Font(name="Calibri", bold=True, size=14, color="2F5496")
SUBTITLE_FONT = Font(name="Calibri", bold=True, size=12, color="2F5496")
THIN_BORDER = Border(
    left=Side(style="thin", color="D9D9D9"),
    right=Side(style="thin", color="D9D9D9"),
    top=Side(style="thin", color="D9D9D9"),
    bottom=Side(style="thin", color="D9D9D9"),
)

PRIORITY_COLORS = {
    "Must": PatternFill(start_color="FCE4EC", end_color="FCE4EC", fill_type="solid"),
    "Should": PatternFill(start_color="FFF3E0", end_color="FFF3E0", fill_type="solid"),
    "Could": PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid"),
    "Won't": PatternFill(start_color="F5F5F5", end_color="F5F5F5", fill_type="solid"),
}

STATUS_COLORS = {
    "To Do": PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid"),
    "In Progress": PatternFill(start_color="FFF9C4", end_color="FFF9C4", fill_type="solid"),
    "In Review": PatternFill(start_color="F3E5F5", end_color="F3E5F5", fill_type="solid"),
    "Testing": PatternFill(start_color="E0F7FA", end_color="E0F7FA", fill_type="solid"),
    "Done": PatternFill(start_color="C8E6C9", end_color="C8E6C9", fill_type="solid"),
    "Blocked": PatternFill(start_color="FFCDD2", end_color="FFCDD2", fill_type="solid"),
}


def apply_header_style(ws, row, max_col):
    """Apply header styling to a row."""
    for col in range(1, max_col + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER


def auto_width(ws, min_width=10, max_width=40):
    """Auto-fit column widths based on content."""
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = max(min(max_len + 2, max_width), min_width)


def create_sprint_backlog_sheet(wb, config):
    """Create the Sprint Backlog sheet."""
    ws = wb.active
    ws.title = "Sprint Backlog"

    # Title
    ws.merge_cells("A1:L1")
    ws["A1"] = f"Sprint Backlog: {config.get('sprint_name', 'Sprint')}"
    ws["A1"].font = TITLE_FONT

    ws.merge_cells("A2:L2")
    ws["A2"] = f"Goal: {config.get('sprint_goal', 'N/A')}"
    ws["A2"].font = Font(name="Calibri", italic=True, size=11, color="666666")

    ws.merge_cells("A3:L3")
    start = config.get("start_date", "TBD")
    end = config.get("end_date", "TBD")
    ws["A3"] = f"Duration: {config.get('sprint_duration_weeks', 2)} weeks ({start} — {end})"
    ws["A3"].font = Font(name="Calibri", size=10, color="888888")

    # Headers
    headers = [
        "Story ID", "Epic", "Title", "Description", "Priority (MoSCoW)",
        "Story Points", "T-Shirt Size", "Time Est. (hrs)", "Assignee",
        "Status", "Blocked?", "Notes"
    ]
    header_row = 5
    for col, header in enumerate(headers, 1):
        ws.cell(row=header_row, column=col, value=header)
    apply_header_style(ws, header_row, len(headers))

    # Data rows
    stories = config.get("stories", [])
    for i, story in enumerate(stories):
        row = header_row + 1 + i
        ws.cell(row=row, column=1, value=story.get("id", "")).border = THIN_BORDER
        ws.cell(row=row, column=2, value=story.get("epic", "")).border = THIN_BORDER
        ws.cell(row=row, column=3, value=story.get("title", "")).border = THIN_BORDER
        ws.cell(row=row, column=4, value=story.get("description", "")).border = THIN_BORDER

        priority_cell = ws.cell(row=row, column=5, value=story.get("priority", ""))
        priority_cell.border = THIN_BORDER
        priority = story.get("priority", "")
        if priority in PRIORITY_COLORS:
            priority_cell.fill = PRIORITY_COLORS[priority]

        ws.cell(row=row, column=6, value=story.get("story_points", "")).border = THIN_BORDER
        ws.cell(row=row, column=7, value=story.get("tshirt_size", "")).border = THIN_BORDER
        ws.cell(row=row, column=8, value=story.get("time_estimate_hours", "")).border = THIN_BORDER
        ws.cell(row=row, column=9, value=story.get("assignee", "")).border = THIN_BORDER

        status_cell = ws.cell(row=row, column=10, value=story.get("status", "To Do"))
        status_cell.border = THIN_BORDER
        status = story.get("status", "To Do")
        if status in STATUS_COLORS:
            status_cell.fill = STATUS_COLORS[status]

        ws.cell(row=row, column=11, value="").border = THIN_BORDER
        ws.cell(row=row, column=12, value=story.get("notes", "")).border = THIN_BORDER

        for col in range(1, len(headers) + 1):
            ws.cell(row=row, column=col).alignment = Alignment(vertical="top", wrap_text=True)

    # Summary row
    summary_row = header_row + len(stories) + 2
    ws.cell(row=summary_row, column=5, value="TOTALS:").font = Font(bold=True)
    sp_total = sum(s.get("story_points", 0) for s in stories if isinstance(s.get("story_points"), (int, float)))
    hrs_total = sum(s.get("time_estimate_hours", 0) for s in stories if isinstance(s.get("time_estimate_hours"), (int, float)))
    ws.cell(row=summary_row, column=6, value=sp_total).font = Font(bold=True)
    ws.cell(row=summary_row, column=8, value=hrs_total).font = Font(bold=True)

    auto_width(ws)
    ws.column_dimensions["D"].width = 35  # Description wider
    ws.sheet_properties.tabColor = "2F5496"

    return ws


def create_capacity_plan_sheet(wb, config):
    """Create the Capacity Plan sheet."""
    ws = wb.create_sheet("Capacity Plan")

    ws.merge_cells("A1:H1")
    ws["A1"] = f"Capacity Plan: {config.get('sprint_name', 'Sprint')}"
    ws["A1"].font = TITLE_FONT

    headers = [
        "Team Member", "Role", "Total Days", "PTO Days", "Holiday Days",
        "Ceremony OH (15%)", "Net Available Days", "Allocated SP"
    ]
    header_row = 3
    for col, header in enumerate(headers, 1):
        ws.cell(row=header_row, column=col, value=header)
    apply_header_style(ws, header_row, len(headers))

    team = config.get("team", [])
    for i, member in enumerate(team):
        row = header_row + 1 + i
        total_days = member.get("total_days", 10)
        pto = member.get("pto_days", 0)
        holidays = member.get("holiday_days", 0)
        ceremony_oh = round((total_days - pto - holidays) * 0.15, 1)
        net_days = round(total_days - pto - holidays - ceremony_oh, 1)

        ws.cell(row=row, column=1, value=member.get("name", "")).border = THIN_BORDER
        ws.cell(row=row, column=2, value=member.get("role", "")).border = THIN_BORDER
        ws.cell(row=row, column=3, value=total_days).border = THIN_BORDER
        ws.cell(row=row, column=4, value=pto).border = THIN_BORDER
        ws.cell(row=row, column=5, value=holidays).border = THIN_BORDER
        ws.cell(row=row, column=6, value=ceremony_oh).border = THIN_BORDER
        ws.cell(row=row, column=7, value=net_days).border = THIN_BORDER
        ws.cell(row=row, column=8, value="").border = THIN_BORDER

        for col in range(1, len(headers) + 1):
            ws.cell(row=row, column=col).alignment = Alignment(horizontal="center")

    # Totals
    total_row = header_row + len(team) + 1
    ws.cell(row=total_row, column=1, value="TOTALS").font = Font(bold=True)
    for col in [3, 4, 5, 6, 7]:
        col_letter = get_column_letter(col)
        start_row = header_row + 1
        end_row = header_row + len(team)
        ws.cell(row=total_row, column=col).value = f"=SUM({col_letter}{start_row}:{col_letter}{end_row})"
        ws.cell(row=total_row, column=col).font = Font(bold=True)

    # Team capacity summary
    summary_row = total_row + 2
    ws.cell(row=summary_row, column=1, value="Team Capacity Summary").font = SUBTITLE_FONT
    ws.merge_cells(f"A{summary_row}:D{summary_row}")

    velocity_history = config.get("velocity_history", [])
    if velocity_history:
        avg_velocity = sum(v.get("completed", 0) for v in velocity_history) / len(velocity_history)
        ws.cell(row=summary_row + 1, column=1, value="Historical Avg Velocity:")
        ws.cell(row=summary_row + 1, column=3, value=round(avg_velocity, 1))
        ws.cell(row=summary_row + 2, column=1, value="Safe Commitment (85%):")
        ws.cell(row=summary_row + 2, column=3, value=round(avg_velocity * 0.85, 1))
        ws.cell(row=summary_row + 3, column=1, value="Stretch Target (100%):")
        ws.cell(row=summary_row + 3, column=3, value=round(avg_velocity, 1))

    auto_width(ws)
    ws.sheet_properties.tabColor = "548235"


def create_burndown_sheet(wb, config):
    """Create the Burndown Data sheet."""
    ws = wb.create_sheet("Burndown Data")

    ws.merge_cells("A1:F1")
    ws["A1"] = f"Sprint Burndown: {config.get('sprint_name', 'Sprint')}"
    ws["A1"].font = TITLE_FONT

    headers = ["Sprint Day", "Date", "Ideal Remaining", "Actual Remaining",
               "Stories Completed", "Cumulative Points"]
    header_row = 3
    for col, header in enumerate(headers, 1):
        ws.cell(row=header_row, column=col, value=header)
    apply_header_style(ws, header_row, len(headers))

    duration_weeks = config.get("sprint_duration_weeks", 2)
    total_days = duration_weeks * 5  # Weekdays only
    total_points = sum(
        s.get("story_points", 0) for s in config.get("stories", [])
        if isinstance(s.get("story_points"), (int, float))
    )
    ideal_per_day = total_points / total_days if total_days > 0 else 0

    start_date = None
    if config.get("start_date"):
        try:
            start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
        except ValueError:
            start_date = None

    for day in range(total_days + 1):
        row = header_row + 1 + day
        ws.cell(row=row, column=1, value=day).border = THIN_BORDER
        ws.cell(row=row, column=1).alignment = Alignment(horizontal="center")

        if start_date:
            current_date = start_date + timedelta(days=day)
            # Skip weekends
            while current_date.weekday() >= 5:
                current_date += timedelta(days=1)
            ws.cell(row=row, column=2, value=current_date.strftime("%Y-%m-%d")).border = THIN_BORDER
        else:
            ws.cell(row=row, column=2, value=f"Day {day}").border = THIN_BORDER

        ideal_remaining = round(total_points - (ideal_per_day * day), 1)
        ws.cell(row=row, column=3, value=ideal_remaining).border = THIN_BORDER

        # Actual remaining starts same as ideal, user fills in daily
        if day == 0:
            ws.cell(row=row, column=4, value=total_points).border = THIN_BORDER
            ws.cell(row=row, column=5, value=0).border = THIN_BORDER
            ws.cell(row=row, column=6, value=0).border = THIN_BORDER
        else:
            ws.cell(row=row, column=4, value="").border = THIN_BORDER
            ws.cell(row=row, column=5, value="").border = THIN_BORDER
            ws.cell(row=row, column=6, value="").border = THIN_BORDER

    # Add burndown chart
    chart = LineChart()
    chart.title = "Sprint Burndown Chart"
    chart.x_axis.title = "Sprint Day"
    chart.y_axis.title = "Story Points Remaining"
    chart.style = 10
    chart.width = 20
    chart.height = 12

    data_end_row = header_row + total_days + 1
    ideal_data = Reference(ws, min_col=3, min_row=header_row, max_row=data_end_row)
    actual_data = Reference(ws, min_col=4, min_row=header_row, max_row=data_end_row)
    days_labels = Reference(ws, min_col=1, min_row=header_row + 1, max_row=data_end_row)

    chart.add_data(ideal_data, titles_from_data=True)
    chart.add_data(actual_data, titles_from_data=True)
    chart.set_categories(days_labels)

    chart.series[0].graphicalProperties.line.dashStyle = "dash"

    chart_row = data_end_row + 2
    ws.add_chart(chart, f"A{chart_row}")

    auto_width(ws)
    ws.sheet_properties.tabColor = "BF8F00"


def create_velocity_sheet(wb, config):
    """Create the Velocity History sheet."""
    ws = wb.create_sheet("Velocity History")

    ws.merge_cells("A1:G1")
    ws["A1"] = "Velocity History & Trends"
    ws["A1"].font = TITLE_FONT

    headers = ["Sprint #", "Committed Points", "Completed Points",
               "Delta", "Completion %", "Rolling Avg (3)", "Notes"]
    header_row = 3
    for col, header in enumerate(headers, 1):
        ws.cell(row=header_row, column=col, value=header)
    apply_header_style(ws, header_row, len(headers))

    velocity_history = config.get("velocity_history", [])
    for i, sprint in enumerate(velocity_history):
        row = header_row + 1 + i
        committed = sprint.get("committed", 0)
        completed = sprint.get("completed", 0)
        delta = completed - committed
        pct = round((completed / committed * 100), 1) if committed > 0 else 0

        ws.cell(row=row, column=1, value=sprint.get("sprint", i + 1)).border = THIN_BORDER
        ws.cell(row=row, column=2, value=committed).border = THIN_BORDER
        ws.cell(row=row, column=3, value=completed).border = THIN_BORDER

        delta_cell = ws.cell(row=row, column=4, value=delta)
        delta_cell.border = THIN_BORDER
        if delta < 0:
            delta_cell.font = Font(color="FF0000")
        elif delta > 0:
            delta_cell.font = Font(color="008000")

        pct_cell = ws.cell(row=row, column=5, value=f"{pct}%")
        pct_cell.border = THIN_BORDER

        # Rolling 3-sprint average
        if i >= 2:
            rolling = round(sum(
                velocity_history[j].get("completed", 0) for j in range(i - 2, i + 1)
            ) / 3, 1)
            ws.cell(row=row, column=6, value=rolling).border = THIN_BORDER
        else:
            ws.cell(row=row, column=6, value="—").border = THIN_BORDER

        ws.cell(row=row, column=7, value=sprint.get("notes", "")).border = THIN_BORDER

        for col in range(1, len(headers) + 1):
            ws.cell(row=row, column=col).alignment = Alignment(horizontal="center")

    # Add placeholder rows for future sprints
    for j in range(3):
        row = header_row + len(velocity_history) + 1 + j
        for col in range(1, len(headers) + 1):
            ws.cell(row=row, column=col, value="").border = THIN_BORDER

    # Velocity chart
    if len(velocity_history) >= 2:
        chart = BarChart()
        chart.type = "col"
        chart.title = "Velocity Trend"
        chart.y_axis.title = "Story Points"
        chart.style = 10
        chart.width = 18
        chart.height = 10

        data_end = header_row + len(velocity_history)
        committed_ref = Reference(ws, min_col=2, min_row=header_row, max_row=data_end)
        completed_ref = Reference(ws, min_col=3, min_row=header_row, max_row=data_end)
        sprint_labels = Reference(ws, min_col=1, min_row=header_row + 1, max_row=data_end)

        chart.add_data(committed_ref, titles_from_data=True)
        chart.add_data(completed_ref, titles_from_data=True)
        chart.set_categories(sprint_labels)

        chart_row = data_end + 3
        ws.add_chart(chart, f"A{chart_row}")

    auto_width(ws)
    ws.sheet_properties.tabColor = "7030A0"


def generate_spreadsheet(config, output_path):
    """Generate the complete sprint tracking spreadsheet."""
    wb = openpyxl.Workbook()

    create_sprint_backlog_sheet(wb, config)
    create_capacity_plan_sheet(wb, config)
    create_burndown_sheet(wb, config)
    create_velocity_sheet(wb, config)

    wb.save(output_path)
    print(f"Sprint tracker saved to: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate Sprint Tracking Spreadsheet")
    parser.add_argument("--config", help="Path to JSON config file")
    parser.add_argument("--output", default="sprint_tracker.xlsx", help="Output .xlsx path")
    args = parser.parse_args()

    if args.config:
        with open(args.config, "r") as f:
            config = json.load(f)
    else:
        config = json.load(sys.stdin)

    generate_spreadsheet(config, args.output)


if __name__ == "__main__":
    main()

```
