# AWS Monitoring Reference

## Table of Contents
1. CloudWatch Metrics & Alarms
2. CloudWatch Dashboards
3. CloudWatch Logs & Insights
4. X-Ray Tracing
5. Common Alarms (Terraform)

---

## 1. CloudWatch Metrics & Alarms

### Alarm (Terraform)
```hcl
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "${var.project}-${var.environment}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "CPU > 85% for 15 minutes. Runbook: https://wiki.example.com/runbooks/high-cpu"
  treat_missing_data  = "notBreaching"

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.app.name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]
}

# Composite alarm (multiple conditions)
resource "aws_cloudwatch_composite_alarm" "service_degraded" {
  alarm_name = "${var.project}-service-degraded"
  alarm_rule = "ALARM(${aws_cloudwatch_metric_alarm.high_cpu.alarm_name}) AND ALARM(${aws_cloudwatch_metric_alarm.high_errors.alarm_name})"
  alarm_actions = [aws_sns_topic.critical.arn]
}

# Anomaly detection alarm
resource "aws_cloudwatch_metric_alarm" "request_anomaly" {
  alarm_name          = "${var.project}-request-anomaly"
  comparison_operator = "LessThanLowerOrGreaterThanUpperThreshold"
  evaluation_periods  = 2
  threshold_metric_id = "ad1"
  treat_missing_data  = "notBreaching"

  metric_query {
    id          = "m1"
    return_data = true
    metric {
      metric_name = "RequestCount"
      namespace   = "AWS/ApplicationELB"
      period      = 300
      stat        = "Sum"
      dimensions  = { LoadBalancer = aws_lb.app.arn_suffix }
    }
  }

  metric_query {
    id          = "ad1"
    expression  = "ANOMALY_DETECTION_BAND(m1, 2)"
    label       = "RequestCount (expected)"
    return_data = true
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}
```

### Custom Metrics (Application)
```python
import boto3

cloudwatch = boto3.client('cloudwatch')

# Publish custom metric
cloudwatch.put_metric_data(
    Namespace='MyApp',
    MetricData=[{
        'MetricName': 'OrderProcessingTime',
        'Value': 1.5,
        'Unit': 'Seconds',
        'Dimensions': [
            {'Name': 'Environment', 'Value': 'production'},
            {'Name': 'Service', 'Value': 'order-api'},
        ],
    }]
)
```

### Embedded Metric Format (Lambda/ECS — zero-config custom metrics)
```javascript
// Log this JSON and CloudWatch auto-creates metrics
console.log(JSON.stringify({
  "_aws": {
    "Timestamp": Date.now(),
    "CloudWatchMetrics": [{
      "Namespace": "MyApp",
      "Dimensions": [["Service", "Environment"]],
      "Metrics": [
        { "Name": "RequestDuration", "Unit": "Milliseconds" },
        { "Name": "ErrorCount", "Unit": "Count" }
      ]
    }]
  },
  "Service": "order-api",
  "Environment": "production",
  "RequestDuration": 145,
  "ErrorCount": 0,
  "requestId": "abc-123",
  "path": "/api/orders"
}));
```

---

## 2. CloudWatch Dashboards

### Dashboard (Terraform)
```hcl
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project}-${var.environment}"
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x = 0; y = 0; width = 12; height = 6
        properties = {
          title   = "Request Rate & Errors"
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", aws_lb.app.arn_suffix, { stat = "Sum", period = 60, label = "Requests" }],
            ["AWS/ApplicationELB", "HTTPCode_ELB_5XX_Count", "LoadBalancer", aws_lb.app.arn_suffix, { stat = "Sum", period = 60, label = "5xx Errors", color = "#d62728" }],
          ]
          view    = "timeSeries"
          stacked = false
          period  = 60
          region  = var.region
        }
      },
      {
        type   = "metric"
        x = 12; y = 0; width = 12; height = 6
        properties = {
          title   = "Latency (p50, p95, p99)"
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", aws_lb.app.arn_suffix, { stat = "p50", label = "p50" }],
            ["...", { stat = "p95", label = "p95" }],
            ["...", { stat = "p99", label = "p99", color = "#d62728" }],
          ]
          period = 60
        }
      },
      {
        type   = "metric"
        x = 0; y = 6; width = 8; height = 6
        properties = {
          title   = "CPU Utilization"
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", aws_ecs_cluster.main.name, "ServiceName", aws_ecs_service.app.name],
          ]
          period = 60
          annotations = {
            horizontal = [{ label = "Alarm Threshold", value = 85, color = "#d62728" }]
          }
        }
      },
      {
        type   = "log"
        x = 0; y = 12; width = 24; height = 6
        properties = {
          title  = "Recent Errors"
          query  = "SOURCE '${aws_cloudwatch_log_group.app.name}' | filter @message like /error|ERROR/ | sort @timestamp desc | limit 20"
          region = var.region
          view   = "table"
        }
      }
    ]
  })
}
```

---

## 3. CloudWatch Logs & Insights

### Log Group Configuration
```hcl
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.project}-${var.environment}"
  retention_in_days = var.environment == "production" ? 90 : 14
  kms_key_id        = aws_kms_key.logs.arn

  tags = { Name = "${var.project}-${var.environment}-logs" }
}

# Metric filter (create metrics from log patterns)
resource "aws_cloudwatch_log_metric_filter" "errors" {
  name           = "${var.project}-error-count"
  log_group_name = aws_cloudwatch_log_group.app.name
  pattern        = "{ $.level = \"error\" }"

  metric_transformation {
    name      = "ErrorCount"
    namespace = "MyApp/${var.environment}"
    value     = "1"
    default_value = "0"
  }
}

# Subscription filter (stream to Lambda/Kinesis/Elasticsearch)
resource "aws_cloudwatch_log_subscription_filter" "to_elasticsearch" {
  name            = "to-elasticsearch"
  log_group_name  = aws_cloudwatch_log_group.app.name
  filter_pattern  = ""
  destination_arn = aws_lambda_function.log_shipper.arn
}
```

### CloudWatch Logs Insights Queries
```sql
-- Top 10 errors in the last hour
fields @timestamp, @message, level, errorType
| filter level = "error"
| sort @timestamp desc
| limit 10

-- Request latency percentiles
fields @timestamp, duration_ms
| filter ispresent(duration_ms)
| stats avg(duration_ms) as avg_ms,
        pct(duration_ms, 50) as p50,
        pct(duration_ms, 95) as p95,
        pct(duration_ms, 99) as p99
  by bin(5m)

-- Error rate over time
fields @timestamp
| stats count(*) as total,
        sum(level = "error") as errors,
        (sum(level = "error") / count(*)) * 100 as error_pct
  by bin(5m)

-- Slowest endpoints
fields @timestamp, path, method, duration_ms
| filter ispresent(duration_ms)
| stats avg(duration_ms) as avg_ms, count(*) as requests
  by path, method
| sort avg_ms desc
| limit 10

-- Unique users in the last 24h
fields userId
| filter ispresent(userId)
| stats count_distinct(userId) as unique_users
  by bin(1h)
```

---

## 4. X-Ray Tracing

```hcl
# Enable X-Ray on Lambda
resource "aws_lambda_function" "api" {
  tracing_config { mode = "Active" }
}

# Enable X-Ray on API Gateway
resource "aws_apigatewayv2_stage" "main" {
  default_route_settings {
    detailed_metrics_enabled = true
    throttling_burst_limit   = 5000
    throttling_rate_limit    = 10000
  }
  # X-Ray tracing
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.apigw.arn
  }
}

# X-Ray sampling rule
resource "aws_xray_sampling_rule" "main" {
  rule_name      = "${var.project}-sampling"
  priority       = 1000
  reservoir_size = 5
  fixed_rate     = 0.05    # Sample 5% of requests
  url_path       = "*"
  host           = "*"
  http_method    = "*"
  service_type   = "*"
  service_name   = "*"
  resource_arn   = "*"
  version        = 1
}
```

---

## 5. Common Alarms (Terraform)

```hcl
# ALB 5xx error rate > 5%
resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "${var.project}-alb-5xx-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 5
  treat_missing_data  = "notBreaching"

  metric_query {
    id          = "error_rate"
    expression  = "(errors / requests) * 100"
    label       = "Error Rate %"
    return_data = true
  }
  metric_query {
    id = "errors"
    metric {
      metric_name = "HTTPCode_ELB_5XX_Count"
      namespace   = "AWS/ApplicationELB"
      period      = 300
      stat        = "Sum"
      dimensions  = { LoadBalancer = var.alb_arn_suffix }
    }
  }
  metric_query {
    id = "requests"
    metric {
      metric_name = "RequestCount"
      namespace   = "AWS/ApplicationELB"
      period      = 300
      stat        = "Sum"
      dimensions  = { LoadBalancer = var.alb_arn_suffix }
    }
  }
  alarm_actions = [var.sns_topic_arn]
}

# RDS high connections
resource "aws_cloudwatch_metric_alarm" "rds_connections" {
  alarm_name          = "${var.project}-rds-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 150
  dimensions          = { DBInstanceIdentifier = var.rds_identifier }
  alarm_actions       = [var.sns_topic_arn]
}

# ECS service running tasks
resource "aws_cloudwatch_metric_alarm" "ecs_running" {
  alarm_name          = "${var.project}-ecs-low-tasks"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "RunningTaskCount"
  namespace           = "ECS/ContainerInsights"
  period              = 60
  statistic           = "Average"
  threshold           = 2
  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }
  alarm_actions = [var.sns_topic_arn]
}

# Lambda errors
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${var.project}-lambda-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 5
  dimensions          = { FunctionName = var.lambda_function_name }
  alarm_actions       = [var.sns_topic_arn]
}

# DynamoDB throttling
resource "aws_cloudwatch_metric_alarm" "dynamodb_throttle" {
  alarm_name          = "${var.project}-dynamodb-throttles"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ReadThrottleEvents"
  namespace           = "AWS/DynamoDB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  dimensions          = { TableName = var.dynamodb_table_name }
  alarm_actions       = [var.sns_topic_arn]
}

# SNS Topic for alerts
resource "aws_sns_topic" "alerts" {
  name = "${var.project}-${var.environment}-alerts"
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_sns_topic_subscription" "slack" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.slack_notifier.arn
}
```



---
