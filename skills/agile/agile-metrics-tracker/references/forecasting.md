# Forecasting Reference

## Table of Contents
1. Monte Carlo Simulation
2. Velocity-Based Forecasting
3. Throughput-Based Forecasting
4. Confidence Intervals
5. Presenting Forecasts to Stakeholders
6. Forecast Accuracy & Calibration

---

## 1. Monte Carlo Simulation

### What It Is
Monte Carlo simulation uses historical data to randomly sample possible future outcomes.
By running thousands of simulations, it produces a probability distribution of completion dates.

### How It Works

**For "When will we finish?" (date forecasting):**

1. Gather historical throughput data (items completed per week for last 8-12 weeks)
2. Count remaining items in the backlog
3. For each simulation (run 10,000 times):
   a. Start with remaining item count
   b. Randomly sample a weekly throughput from the historical data
   c. Subtract that throughput from the remaining count
   d. Repeat until remaining count reaches zero
   e. Record the total number of weeks taken
4. Aggregate all simulation results into a probability distribution
5. Extract percentiles for confidence levels

**For "How much will we finish by date X?" (scope forecasting):**

1. Gather historical throughput data
2. Calculate weeks remaining until target date
3. For each simulation:
   a. Start with 0 items completed
   b. For each remaining week, randomly sample a throughput
   c. Accumulate the total items completed
   d. Record the final count
4. Extract percentiles

### Input Requirements

- **Minimum data**: 6 weeks of throughput history (8-12 preferred)
- **Data quality**: Exclude anomalous weeks (team was half-size, holiday week) OR include them
  if they're representative of normal variation
- **Backlog size**: Must have a reasonably stable remaining item count
- **Item splitting**: If large items will be split, estimate the split count

### Output Format

```
Monte Carlo Forecast: When will 45 items be completed?
Based on 10,000 simulations using 12 weeks of historical throughput.

| Confidence | Completion Date | Weeks from Now |
|------------|----------------|----------------|
| 50% | March 7, 2025 | 8 weeks |
| 70% | March 21, 2025 | 10 weeks |
| 85% | April 4, 2025 | 12 weeks |
| 95% | April 25, 2025 | 15 weeks |

Recommendation: Commit to the 85% confidence date (April 4, 2025).
The 50% date is a coin flip — not reliable for commitments.
```

### Which Confidence Level to Use

| Context | Recommended Level |
|---------|-------------------|
| Internal team planning | 50-70% |
| Stakeholder commitment | 85% |
| Contractual deadline | 95% |
| Customer promise | 85-95% |

### Assumptions & Caveats

Always state these when presenting Monte Carlo results:

1. Assumes team composition remains stable
2. Assumes historical throughput patterns continue
3. Assumes no major scope additions (or state the assumed scope growth rate)
4. Does not account for specific known risks (holidays, departures)
5. Accuracy improves with more historical data
6. Large remaining backlogs are less accurate than small ones

---

## 2. Velocity-Based Forecasting

### Simple Forecast
```
Sprints Remaining = Remaining Points / Average Velocity
Completion Date = Today + (Sprints Remaining × Sprint Length)
```

### Range Forecast (Better)
```
Best Case = Remaining Points / Highest Historical Velocity
Likely Case = Remaining Points / Average Velocity
Worst Case = Remaining Points / Lowest Historical Velocity
```

### Example
```
Remaining: 150 story points
Velocity History: [28, 33, 30, 35, 31] (5 sprints, 2-week each)

Average: 31.4 points/sprint
Best: 35 points/sprint
Worst: 28 points/sprint

Best Case: 150 / 35 = 4.3 sprints ≈ 9 weeks
Likely: 150 / 31.4 = 4.8 sprints ≈ 10 weeks
Worst Case: 150 / 28 = 5.4 sprints ≈ 11 weeks

Forecast: 9-11 weeks (most likely 10 weeks)
```

### Limitations
- Assumes points-per-sprint stays consistent
- Doesn't handle scope changes well
- Treats velocity as fixed, not probabilistic
- Less accurate than Monte Carlo for complex backlogs

---

## 3. Throughput-Based Forecasting

### Simple Throughput Forecast
```
Weeks Remaining = Remaining Items / Average Weekly Throughput
```

### Advantages Over Velocity-Based
- Uses item count, not points (avoids estimation biases)
- Works with any framework (Scrum, Kanban, hybrid)
- Pairs naturally with Monte Carlo

### Throughput Data Collection

| Week | Items Completed | Running Avg | Std Dev |
|------|----------------|-------------|---------|
| W1 | 6 | 6.0 | — |
| W2 | 5 | 5.5 | 0.71 |
| W3 | 7 | 6.0 | 1.00 |
| W4 | 6 | 6.0 | 0.82 |
| W5 | 4 | 5.6 | 1.14 |
| W6 | 8 | 6.0 | 1.41 |

---

## 4. Confidence Intervals

### For Velocity

```
95% Confidence Interval = Average ± (1.96 × Std Dev / √n)

Where n = number of sprints in the sample
```

### For Cycle Time

Use percentile-based intervals:
```
50% of items complete within [median] days
85% of items complete within [85th percentile] days
95% of items complete within [95th percentile] days
```

### For Delivery Date

Monte Carlo naturally provides confidence intervals via percentiles.

Visualize as a probability density chart:
- X-axis: Completion date
- Y-axis: Probability
- Shade regions for 50%, 85%, 95% confidence

---

## 5. Presenting Forecasts to Stakeholders

### Do's
- Present ranges, never single dates: "Between March 7 and April 4"
- State the confidence level: "We're 85% confident we'll finish by April 4"
- Show the data behind the forecast: "Based on our last 12 weeks of delivery data"
- Update forecasts regularly (every 2 weeks minimum)
- Use visual probability charts — they communicate uncertainty better than tables

### Don'ts
- Don't present the 50% date as a commitment — it's a coin flip
- Don't hide uncertainty — stakeholders prefer honest ranges to false precision
- Don't forecast without data — wait for at least 6 sprints/weeks of history
- Don't adjust the model to match desired dates — that's wishful thinking
- Don't present forecasts as deterministic: "We WILL finish on March 15" → wrong

### Stakeholder Communication Template

```
## Delivery Forecast — [Project/Feature]
**Updated:** [Date] | **Based on:** [N] weeks of data

### Summary
We have [X] items remaining. Based on our historical delivery rate,
we expect to complete them by [85% confidence date] with high confidence.

### Confidence Levels
| Probability | Date | Interpretation |
|-------------|------|----------------|
| 50% | [date] | Optimistic — coin flip odds |
| 70% | [date] | Moderate confidence |
| 85% | [date] | **Recommended commitment** |
| 95% | [date] | Very conservative |

### Key Assumptions
1. Team of [N] remains stable
2. No major scope additions
3. Historical throughput continues ([avg] items/week)

### Risks to This Forecast
- [Risk 1]: Could delay by [X] weeks if realized
- [Risk 2]: Could delay by [X] weeks if realized

### Next Update
This forecast will be refreshed on [date] with updated throughput data.
```

---

## 6. Forecast Accuracy & Calibration

### Tracking Forecast Accuracy

After each delivery, compare forecast to actual:

| Project | 85% Forecast | Actual Date | Delta (days) | Accurate? |
|---------|-------------|-------------|-------------|-----------|
| Auth MVP | Mar 15 | Mar 12 | -3 | ✅ |
| Search v2 | Apr 1 | Apr 8 | +7 | ❌ (late) |
| Reports | May 10 | May 5 | -5 | ✅ |

### Calibration

If your 85% confidence forecasts are wrong more than 15% of the time,
the model needs calibration:

- **Consistently late** → throughput data may exclude slow periods, or scope grows
  during execution. Include wider historical range or add scope growth factor.
- **Consistently early** → team may be maturing (good!) or estimates are too conservative.
  Use more recent data (last 8 weeks vs last 16).
- **Inconsistent** → high variance in throughput. Use more data points or investigate
  special cause variation.



---
