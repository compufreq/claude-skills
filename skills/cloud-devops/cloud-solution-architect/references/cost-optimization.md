# Cost Optimization Reference

## Table of Contents
1. FinOps Framework
2. AWS Cost Optimization
3. Azure Cost Optimization
4. Tagging Strategy
5. Cost Governance

---

## 1. FinOps Framework

### FinOps Lifecycle
```
Inform → Optimize → Operate
  ↓          ↓          ↓
Visibility  Action    Governance
```

| Phase | Activities | Tools |
|-------|-----------|-------|
| **Inform** | Cost visibility, allocation, forecasting | Cost Explorer, Cost Management, dashboards |
| **Optimize** | Right-sizing, reserved capacity, unused cleanup | Compute Optimizer, Advisor, custom scripts |
| **Operate** | Budgets, policies, continuous improvement | Budgets, alerts, FinOps reviews |

### FinOps Maturity Levels

| Level | Crawl | Walk | Run |
|-------|-------|------|-----|
| Visibility | Basic cost reports | Per-team cost allocation | Real-time cost per transaction |
| Optimization | Manual right-sizing | Automated recommendations | Auto-remediation |
| Governance | Monthly cost reviews | Budget alerts + anomaly detection | Policy-enforced guardrails |

---

## 2. AWS Cost Optimization

### Savings Hierarchy (Apply in Order)
```
1. Delete unused resources (EBS, EIPs, old snapshots, idle LBs)
2. Right-size (downsize over-provisioned instances)
3. Spot instances for fault-tolerant workloads
4. Reserved Instances / Savings Plans for steady-state
5. Architecture optimization (serverless, caching, CDN)
```

### AWS Savings Plans vs Reserved Instances

| Feature | Savings Plans | Reserved Instances |
|---------|-------------|-------------------|
| Flexibility | Across instance families | Specific instance type |
| Savings | 20-50% (compute), 30-60% (EC2) | 30-60% |
| Commitment | $/hour for 1 or 3 years | Instance count for 1/3 years |
| Recommendation | Preferred for most teams | Specific high-volume workloads |

### AWS Cost Optimization Terraform
```hcl
# Budget alert
resource "aws_budgets_budget" "monthly" {
  name         = "${var.project}-monthly-budget"
  budget_type  = "COST"
  limit_amount = var.monthly_budget
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filter {
    name   = "TagKeyValue"
    values = ["user:Project$${var.project}"]
  }

  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = [var.finance_email]
  }

  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 100
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = [var.finance_email, var.engineering_email]
  }

  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 100
    threshold_type            = "FORECASTED"
    notification_type         = "FORECASTED"
    subscriber_email_addresses = [var.finance_email]
  }
}

# Cost anomaly detection
resource "aws_ce_anomaly_monitor" "main" {
  name              = "${var.project}-anomaly-monitor"
  monitor_type      = "DIMENSIONAL"
  monitor_dimension = "SERVICE"
}

resource "aws_ce_anomaly_subscription" "main" {
  name = "${var.project}-anomaly-alerts"
  monitor_arn_list = [aws_ce_anomaly_monitor.main.arn]
  frequency        = "DAILY"

  threshold_expression {
    dimension {
      key           = "ANOMALY_TOTAL_IMPACT_ABSOLUTE"
      values        = ["100"]
      match_options = ["GREATER_THAN_OR_EQUAL"]
    }
  }

  subscriber {
    type    = "EMAIL"
    address = var.finance_email
  }
}
```

### Common AWS Cost Wastes

| Waste | Monthly Cost | Fix |
|-------|-------------|-----|
| Unattached EBS volumes | $10-100/vol | Delete or snapshot+delete |
| Idle NAT Gateways | $32/mo + data | Remove if unused |
| Over-provisioned RDS | $200-2000 | Downsize or Aurora Serverless |
| Unused Elastic IPs | $3.60/mo each | Release |
| Old EBS/RDS snapshots | $0.05/GB/mo | Lifecycle policy |
| Dev environments 24/7 | 70% waste | Schedule on/off (Lambda) |
| No Savings Plans | 30-60% waste | Purchase based on steady usage |

---

## 3. Azure Cost Optimization

### Azure Cost Management
```hcl
# Azure Budget
resource "azurerm_consumption_budget_resource_group" "main" {
  name              = "${var.project}-monthly-budget"
  resource_group_id = azurerm_resource_group.main.id
  amount            = var.monthly_budget
  time_grain        = "Monthly"

  time_period {
    start_date = "2025-01-01T00:00:00Z"
  }

  notification {
    enabled        = true
    threshold      = 80
    operator       = "GreaterThan"
    threshold_type = "Actual"
    contact_emails = [var.finance_email]
  }

  notification {
    enabled        = true
    threshold      = 100
    operator       = "GreaterThan"
    threshold_type = "Actual"
    contact_emails = [var.finance_email, var.engineering_email]
  }

  notification {
    enabled        = true
    threshold      = 110
    operator       = "GreaterThan"
    threshold_type = "Forecasted"
    contact_emails = [var.finance_email]
  }
}
```

### Azure-Specific Savings

| Strategy | Savings | How |
|----------|---------|-----|
| Azure Hybrid Benefit | 40-80% | Use existing Windows/SQL licenses |
| Reserved VMs (1yr) | 30-40% | Commit to instance type |
| Reserved VMs (3yr) | 50-60% | Longer commitment |
| Spot VMs | 60-90% | Evictable workloads |
| Dev/Test pricing | 40-60% | MSDN subscription discount |
| Auto-shutdown | 70% (dev) | Schedule VMs off at night |
| B-series VMs | 30-50% | Burstable for variable workloads |

---

## 4. Tagging Strategy

### Mandatory Tags

| Tag Key | Purpose | Example Values |
|---------|---------|---------------|
| `Environment` | Lifecycle stage | production, staging, development |
| `Project` | Business project | myapp, platform, data-pipeline |
| `Team` | Owning team | platform-eng, backend, data |
| `CostCenter` | Financial allocation | CC-1234, engineering, marketing |
| `ManagedBy` | How it's managed | terraform, cloudformation, manual |
| `Service` | Specific service | api, worker, database, cache |

### Tag Enforcement

**AWS:**
```hcl
# AWS Organizations SCP — deny untagged resources
resource "aws_organizations_policy" "require_tags" {
  name    = "require-tags"
  content = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "DenyUntaggedEC2"
      Effect    = "Deny"
      Action    = ["ec2:RunInstances"]
      Resource  = ["arn:aws:ec2:*:*:instance/*"]
      Condition = {
        "StringEquals" = { "aws:RequestTag/Environment" = "" }
      }
    }]
  })
}

# AWS Config rule — check for required tags
resource "aws_config_config_rule" "required_tags" {
  name = "required-tags"
  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }
  input_parameters = jsonencode({
    tag1Key = "Environment"
    tag2Key = "Project"
    tag3Key = "Team"
  })
}
```

**Azure:**
```hcl
resource "azurerm_resource_group_policy_assignment" "require_tags" {
  name                 = "require-tags"
  resource_group_id    = azurerm_resource_group.main.id
  policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/871b6d14-10aa-478d-b466-ef6f3cef3e50"

  parameters = jsonencode({
    tagName = { value = "Environment" }
  })
}
```

---

## 5. Cost Governance

### Monthly FinOps Review Agenda
1. **Total spend** vs budget (actual and forecast)
2. **Anomalies** — any unexpected cost spikes?
3. **Top 5 cost drivers** — what's growing fastest?
4. **Unused resources** — what can be deleted?
5. **Right-sizing opportunities** — over-provisioned resources
6. **Reserved capacity** — coverage vs utilization
7. **Action items** — assign owners and deadlines

### Cost Metrics to Track

| Metric | Target | Frequency |
|--------|--------|-----------|
| Monthly spend vs budget | < 100% | Weekly |
| Reserved capacity coverage | > 70% | Monthly |
| Spot utilization | > 30% of fault-tolerant | Monthly |
| Waste (unused resources) | < 5% of total | Monthly |
| Cost per transaction | Decreasing trend | Monthly |
| Unit economics | Improving | Quarterly |



---
