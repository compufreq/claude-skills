# Estimation Methods Reference

## Table of Contents
1. Story Points (Fibonacci)
2. T-Shirt Sizing
3. Time-Based Estimates (PERT)
4. Estimation Facilitation
5. Velocity & Forecasting
6. Estimation Anti-Patterns

---

## 1. Story Points (Fibonacci)

Story points measure relative complexity, effort, and uncertainty — not time.

### The Fibonacci Scale

| Points | Complexity | Uncertainty | Typical Characteristics |
|--------|-----------|-------------|------------------------|
| 1 | Trivial | None | Config change, copy update, well-known pattern |
| 2 | Low | Minimal | Small feature, one component, clear requirements |
| 3 | Moderate | Low | Multiple components, some integration work |
| 5 | Significant | Some | Cross-cutting concern, new pattern needed |
| 8 | High | Moderate | Multiple systems, research needed, some unknowns |
| 13 | Very High | High | Large scope, significant unknowns, consider splitting |
| 21 | Epic-level | Very High | Too large for a sprint. MUST be split. |

### Reference Story Technique

Anchor estimates to a well-understood reference story:

1. Pick a completed story the whole team understands (ideally a 3 or 5)
2. This becomes the "reference story"
3. For each new story, ask: "Is this bigger, smaller, or about the same as the reference?"
4. Size relative to the reference, not in absolute terms

### Planning Poker Process

1. PO presents the story and answers questions
2. Each team member privately selects a card (1, 2, 3, 5, 8, 13, 21)
3. All cards revealed simultaneously
4. If consensus (all within 1 step): accept the estimate
5. If divergence: highest and lowest explain their reasoning
6. Re-vote (max 3 rounds, then use the higher estimate or the median)

---

## 2. T-Shirt Sizing

T-shirt sizing is faster and less precise than story points. Best for early backlog
grooming, roadmap planning, or teams new to estimation.

### Size Definitions

| Size | Description | SP Equivalent | Time Analogy |
|------|-------------|---------------|-------------|
| XS | Trivial, could do it in your sleep | 1 | < 2 hours |
| S | Small, well-understood, one component | 2-3 | Half day to 1 day |
| M | Medium, some complexity, maybe 2 components | 5 | 1-2 days |
| L | Large, cross-cutting, some unknowns | 8 | 3-5 days |
| XL | Very large, significant unknowns | 13+ | > 1 week — SPLIT IT |

### When to Use T-Shirt Sizing
- Initial backlog grooming before detailed refinement
- Roadmap-level planning (quarterly, yearly)
- When the team is new to estimation and story points feel intimidating
- Quick triage of incoming requests
- Executive-level capacity discussions

### Converting T-Shirt to Story Points
When transitioning from t-shirt to story points, use this mapping as a starting point
and adjust based on team experience:

```
XS → 1 SP
S  → 2-3 SP (default to 2 for well-known, 3 for slight unknowns)
M  → 5 SP
L  → 8 SP
XL → 13 SP (but seriously, split it first)
```

---

## 3. Time-Based Estimates (PERT)

Time-based estimation is useful when stakeholders need calendar-based forecasts
or when the team works in a non-Agile context that requires time tracking.

### Three-Point Estimation (PERT)

For each task, provide three estimates:

| Estimate | Symbol | Meaning |
|----------|--------|---------|
| Optimistic | O | Best case — everything goes right, no blockers |
| Most Likely | M | Realistic — normal conditions, typical interruptions |
| Pessimistic | P | Worst case — complications, dependencies, rework |

### PERT Formula
```
Expected Duration = (O + 4M + P) / 6
Standard Deviation = (P - O) / 6
```

### Example
```
Task: Implement user search API endpoint
Optimistic (O): 4 hours
Most Likely (M): 8 hours
Pessimistic (P): 20 hours

Expected = (4 + 4×8 + 20) / 6 = 56/6 ≈ 9.3 hours
Std Dev = (20 - 4) / 6 ≈ 2.7 hours

Estimate: ~9 hours (range: 7-12 hours at 1 standard deviation)
```

### Confidence Levels
- 68% confidence: Expected ± 1 std dev
- 95% confidence: Expected ± 2 std dev
- 99.7% confidence: Expected ± 3 std dev

For project commitments, use the 95% confidence level (Expected + 2 × Std Dev).

### Time Estimate Spreadsheet Columns

| Task | Optimistic (h) | Most Likely (h) | Pessimistic (h) | PERT (h) | Std Dev | 95% Upper (h) |
|------|----------------|-----------------|-----------------|----------|---------|----------------|

---

## 4. Estimation Facilitation

### Facilitator Guide

**Before the session:**
- Ensure stories are refined and have acceptance criteria
- Prepare the reference story for story points
- Set up the estimation tool (physical cards, digital tool)
- Time-box the session (2 hours max for a full backlog)

**During the session:**
- PO reads each story and answers clarifying questions (max 5 min/story)
- If questions exceed 5 minutes, the story isn't ready — send it back for refinement
- After questions, team estimates silently (no anchoring bias)
- Reveal estimates simultaneously
- Discuss outliers (30 seconds each for high/low to explain)
- Re-estimate if needed (max 2 re-votes)
- If no consensus after 2 re-votes, take the higher estimate and note the uncertainty
- Record the estimate and any assumptions or risks

**After the session:**
- Update the backlog with estimates
- Flag any stories that need more refinement
- Calculate updated velocity projections

### Common Estimation Biases

| Bias | Description | Mitigation |
|------|-------------|------------|
| Anchoring | First estimate influences others | Simultaneous reveal (Planning Poker) |
| Optimism | Underestimating complexity | Use historical data, PERT pessimistic |
| HiPPO | Highest Paid Person's Opinion dominates | Anonymous voting, Scrum Master facilitates |
| Groupthink | Team converges without critical thinking | Require silent individual estimates first |
| Recency | Last sprint's experience biases current estimates | Use reference stories across multiple sprints |

---

## 5. Velocity & Forecasting

### Calculating Velocity

```
Sprint Velocity = Total Story Points completed (Done) in one sprint
Average Velocity = Sum of last 3-5 sprints' velocity / Number of sprints
Velocity Range = [Lowest sprint, Highest sprint] over last 5 sprints
```

Only count stories that are fully Done (meet Definition of Done). Partially completed
stories carry over and are counted in the sprint where they finish.

### Forecasting with Velocity

**Simple forecast:**
```
Sprints to complete backlog = Total Backlog Points / Average Velocity
```

**Range forecast (recommended):**
```
Best case = Total Backlog Points / Highest Velocity
Likely case = Total Backlog Points / Average Velocity
Worst case = Total Backlog Points / Lowest Velocity
```

### Velocity Stabilization

- Sprint 1-2: Velocity is unreliable. Don't make commitments based on it.
- Sprint 3-5: Velocity is emerging. Use with wide confidence intervals.
- Sprint 6+: Velocity should stabilize. Use rolling 3-sprint average.
- If velocity variance > 25% after 6 sprints, investigate root causes
  (scope creep, team changes, unclear requirements, technical debt).

---

## 6. Estimation Anti-Patterns

| Anti-Pattern | Why It's Harmful | Better Approach |
|-------------|------------------|-----------------|
| Estimating in isolation | Individual estimates miss team knowledge | Collaborative estimation (Planning Poker) |
| Treating estimates as commitments | Creates pressure to game the system | Estimates are forecasts, not promises |
| Not re-estimating after learning | Stale estimates mislead planning | Re-estimate when scope or understanding changes |
| Estimating during sprint | Disrupts flow, incomplete information | Estimate during refinement/planning |
| Points = hours conversion | Defeats the purpose of relative sizing | Keep them separate; use velocity for forecasting |
| Padding estimates | Erodes trust, inflates projections | Use explicit risk buffers instead |
| Skipping estimation | No data for forecasting or capacity planning | Even rough t-shirt sizing is better than nothing |



---
