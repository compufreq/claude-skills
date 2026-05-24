# Auto-Scaling Reference

## Table of Contents
1. Scaling Strategies
2. AWS Auto Scaling
3. Azure Auto-Scale
4. Scaling Best Practices

---

## 1. Scaling Strategies

| Strategy | How It Works | Best For |
|----------|-------------|---------|
| **Target Tracking** | Maintain a metric at target value | Most workloads (CPU at 70%) |
| **Step Scaling** | Add/remove capacity at thresholds | Custom metrics, precise control |
| **Scheduled** | Scale at specific times | Predictable traffic patterns |
| **Predictive** | ML-based forecast | Recurring patterns (daily/weekly) |

### Target Tracking (Recommended Default)
```
Target: CPU = 70%
  - If CPU > 70% → add instances (scale out)
  - If CPU < 70% → remove instances (scale in)
  - Cooldown prevents thrashing
```

### Step Scaling (Fine-Grained)
```
CPU 0-40%   → 2 instances (minimum)
CPU 40-60%  → 3 instances
CPU 60-80%  → 5 instances
CPU 80-90%  → 8 instances
CPU 90%+    → 10 instances (maximum)
```

### Scheduled Scaling
```
Monday-Friday 8 AM  → Scale to 10 instances
Monday-Friday 8 PM  → Scale to 3 instances
Saturday-Sunday     → Scale to 2 instances
Black Friday        → Scale to 50 instances
```

---

## 2. AWS Auto Scaling

### EC2 Auto Scaling Group — Target Tracking
```hcl
resource "aws_autoscaling_policy" "cpu" {
  name                   = "${var.project}-cpu-target"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value     = 70.0
    disable_scale_in = false
  }
}

# Custom metric (requests per target from ALB)
resource "aws_autoscaling_policy" "requests" {
  name                   = "${var.project}-request-target"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.app.arn_suffix}/${aws_lb_target_group.app.arn_suffix}"
    }
    target_value = 1000    # 1000 requests per instance
  }
}
```

### EC2 Step Scaling
```hcl
resource "aws_autoscaling_policy" "scale_out" {
  name                   = "${var.project}-scale-out"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "StepScaling"
  adjustment_type        = "ChangeInCapacity"

  step_adjustment {
    scaling_adjustment          = 2
    metric_interval_lower_bound = 0
    metric_interval_upper_bound = 20
  }
  step_adjustment {
    scaling_adjustment          = 4
    metric_interval_lower_bound = 20
  }
}

resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "${var.project}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Average"
  threshold           = 70
  alarm_actions       = [aws_autoscaling_policy.scale_out.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.app.name
  }
}
```

### Scheduled Scaling
```hcl
resource "aws_autoscaling_schedule" "business_hours" {
  scheduled_action_name  = "business-hours"
  autoscaling_group_name = aws_autoscaling_group.app.name
  min_size               = 5
  max_size               = 20
  desired_capacity       = 10
  recurrence             = "0 8 * * MON-FRI"    # 8 AM weekdays
}

resource "aws_autoscaling_schedule" "off_hours" {
  scheduled_action_name  = "off-hours"
  autoscaling_group_name = aws_autoscaling_group.app.name
  min_size               = 2
  max_size               = 5
  desired_capacity       = 2
  recurrence             = "0 20 * * MON-FRI"   # 8 PM weekdays
}
```

### Predictive Scaling (ML-based)
```hcl
resource "aws_autoscaling_policy" "predictive" {
  name                   = "${var.project}-predictive"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "PredictiveScaling"

  predictive_scaling_configuration {
    metric_specification {
      target_value = 70

      predefined_scaling_metric_specification {
        predefined_metric_type = "ASGAverageCPUUtilization"
        resource_label         = ""
      }

      predefined_load_metric_specification {
        predefined_metric_type = "ASGTotalCPUUtilization"
        resource_label         = ""
      }
    }
    mode                         = "ForecastAndScale"
    scheduling_buffer_time       = 300    # Pre-scale 5 min before predicted need
  }
}
```

### Lambda Concurrency Scaling
```hcl
# Reserved concurrency (hard limit)
resource "aws_lambda_function" "api" {
  reserved_concurrent_executions = 100
}

# Provisioned concurrency (pre-warmed)
resource "aws_lambda_provisioned_concurrency_config" "api" {
  function_name                     = aws_lambda_function.api.function_name
  qualifier                         = aws_lambda_function.api.version
  provisioned_concurrent_executions = 10
}

# Auto-scale provisioned concurrency
resource "aws_appautoscaling_target" "lambda" {
  max_capacity       = 50
  min_capacity       = 5
  resource_id        = "function:${aws_lambda_function.api.function_name}:${aws_lambda_function.api.version}"
  scalable_dimension = "lambda:function:ProvisionedConcurrency"
  service_namespace  = "lambda"
}

resource "aws_appautoscaling_policy" "lambda" {
  name               = "lambda-scaling"
  resource_id        = aws_appautoscaling_target.lambda.resource_id
  scalable_dimension = aws_appautoscaling_target.lambda.scalable_dimension
  service_namespace  = aws_appautoscaling_target.lambda.service_namespace
  policy_type        = "TargetTrackingScaling"

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "LambdaProvisionedConcurrencyUtilization"
    }
    target_value = 0.7
  }
}
```

---

## 3. Azure Auto-Scale

### VMSS Auto-Scale
```hcl
resource "azurerm_monitor_autoscale_setting" "vmss" {
  name                = "${var.project}-autoscale"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  target_resource_id  = azurerm_linux_virtual_machine_scale_set.app.id

  profile {
    name = "default"
    capacity {
      default = 3
      minimum = 2
      maximum = 20
    }

    # Scale out on CPU
    rule {
      metric_trigger {
        metric_name        = "Percentage CPU"
        metric_resource_id = azurerm_linux_virtual_machine_scale_set.app.id
        time_grain         = "PT1M"
        statistic          = "Average"
        time_window        = "PT5M"
        time_aggregation   = "Average"
        operator           = "GreaterThan"
        threshold          = 70
      }
      scale_action {
        direction = "Increase"
        type      = "ChangeCount"
        value     = "2"
        cooldown  = "PT5M"
      }
    }

    # Scale in on CPU
    rule {
      metric_trigger {
        metric_name        = "Percentage CPU"
        metric_resource_id = azurerm_linux_virtual_machine_scale_set.app.id
        time_grain         = "PT1M"
        statistic          = "Average"
        time_window        = "PT10M"
        time_aggregation   = "Average"
        operator           = "LessThan"
        threshold          = 30
      }
      scale_action {
        direction = "Decrease"
        type      = "ChangeCount"
        value     = "1"
        cooldown  = "PT10M"
      }
    }
  }

  # Scheduled: business hours
  profile {
    name = "business-hours"
    capacity {
      default = 5
      minimum = 5
      maximum = 20
    }

    recurrence {
      timezone  = "Eastern Standard Time"
      days      = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
      hours     = [8]
      minutes   = [0]
    }

    rule {
      metric_trigger {
        metric_name        = "Percentage CPU"
        metric_resource_id = azurerm_linux_virtual_machine_scale_set.app.id
        time_grain         = "PT1M"
        statistic          = "Average"
        time_window        = "PT5M"
        time_aggregation   = "Average"
        operator           = "GreaterThan"
        threshold          = 70
      }
      scale_action {
        direction = "Increase"
        type      = "ChangeCount"
        value     = "2"
        cooldown  = "PT5M"
      }
    }
  }

  notification {
    email {
      send_to_subscription_administrator    = true
      send_to_subscription_co_administrator = false
      custom_emails                         = ["ops@example.com"]
    }
  }
}
```

---

## 4. Scaling Best Practices

### General
1. **Scale on the right metric** — request count > CPU for web apps
2. **Scale out fast, in slow** — 1 min scale-out, 5-10 min scale-in cooldown
3. **Set minimum for HA** — at least 2 instances in production (multi-AZ)
4. **Load test before launch** — know your scaling limits
5. **Monitor scaling events** — alert on repeated scale-out (may indicate a problem)

### Cooldown Configuration

| Direction | Recommended | Why |
|-----------|------------|-----|
| Scale-out | 60 seconds | Respond quickly to demand |
| Scale-in | 300-600 seconds | Avoid thrashing, ensure stability |

### Scaling Metrics Cheat Sheet

| Metric | Target | Good For |
|--------|--------|---------|
| CPU utilization | 60-70% | General workloads |
| Memory utilization | 70-80% | Memory-bound apps |
| Request count per target | App-specific | HTTP APIs |
| Queue depth | 0-10 messages | Queue workers |
| Custom (latency P99) | < 500ms | Latency-sensitive |
| Concurrent connections | App-specific | WebSocket servers |



---
