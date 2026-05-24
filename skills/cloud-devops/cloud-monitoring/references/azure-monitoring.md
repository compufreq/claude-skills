# Azure Monitoring Reference

## Table of Contents
1. Azure Monitor & Application Insights
2. Log Analytics & KQL
3. Alerts & Action Groups
4. Dashboards

---

## 1. Azure Monitor & Application Insights

### Application Insights (Terraform)
```hcl
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.project}-${var.environment}-law"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = var.environment == "production" ? 90 : 30
}

resource "azurerm_application_insights" "main" {
  name                = "${var.project}-${var.environment}-ai"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  retention_in_days   = var.environment == "production" ? 90 : 30
  sampling_percentage = var.environment == "production" ? 50 : 100
}

# Availability test (synthetic monitoring)
resource "azurerm_application_insights_standard_web_test" "health" {
  name                    = "${var.project}-health-check"
  resource_group_name     = azurerm_resource_group.main.name
  location                = azurerm_resource_group.main.location
  application_insights_id = azurerm_application_insights.main.id
  geo_locations           = ["us-tx-sn1-azr", "us-il-ch1-azr", "emea-gb-db3-azr"]
  frequency               = 300

  request {
    url = "https://app.example.com/health"
    header {
      name  = "Accept"
      value = "application/json"
    }
  }

  validation_rules {
    expected_status_code = 200
    ssl_check_enabled    = true
    ssl_cert_remaining_lifetime = 30
  }
}
```

### Diagnostic Settings (Terraform)
```hcl
# Send resource metrics/logs to Log Analytics
resource "azurerm_monitor_diagnostic_setting" "app_service" {
  name                       = "diag-to-law"
  target_resource_id         = azurerm_linux_web_app.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "AppServiceHTTPLogs"
  }
  enabled_log {
    category = "AppServiceConsoleLogs"
  }
  enabled_log {
    category = "AppServiceAppLogs"
  }

  metric {
    category = "AllMetrics"
  }
}

resource "azurerm_monitor_diagnostic_setting" "sql" {
  name                       = "sql-diag"
  target_resource_id         = azurerm_mssql_database.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log { category = "SQLSecurityAuditEvents" }
  enabled_log { category = "QueryStoreRuntimeStatistics" }
  enabled_log { category = "Errors" }
  metric { category = "AllMetrics" }
}
```

---

## 2. Log Analytics & KQL

### Common KQL Queries
```kusto
// Request performance (App Insights)
requests
| where timestamp > ago(1h)
| summarize avg(duration), percentile(duration, 95), percentile(duration, 99),
            count(), countif(success == false)
  by bin(timestamp, 5m)
| render timechart

// Error details
exceptions
| where timestamp > ago(24h)
| summarize count() by type, outerMessage
| sort by count_ desc
| take 20

// Dependency performance (DB, HTTP, etc.)
dependencies
| where timestamp > ago(1h)
| summarize avg(duration), count(), countif(success == false)
  by name, type
| sort by avg_duration desc

// Slow requests by endpoint
requests
| where timestamp > ago(1h) and duration > 1000
| summarize count(), avg(duration) by name
| sort by avg_duration desc
| take 10

// Custom events with dimensions
customEvents
| where timestamp > ago(24h) and name == "OrderPlaced"
| extend orderTotal = todouble(customDimensions.total)
| summarize totalRevenue = sum(orderTotal), orderCount = count()
  by bin(timestamp, 1h)

// Infrastructure: VM CPU
Perf
| where TimeGenerated > ago(1h)
| where ObjectName == "Processor" and CounterName == "% Processor Time"
| summarize avg(CounterValue) by Computer, bin(TimeGenerated, 5m)
| render timechart

// Container logs (AKS)
ContainerLogV2
| where TimeGenerated > ago(1h)
| where LogMessage contains "error"
| project TimeGenerated, PodName, ContainerName, LogMessage
| sort by TimeGenerated desc
| take 50
```

---

## 3. Alerts & Action Groups

### Action Group (Terraform)
```hcl
resource "azurerm_monitor_action_group" "critical" {
  name                = "${var.project}-critical"
  resource_group_name = azurerm_resource_group.main.name
  short_name          = "critical"

  email_receiver {
    name          = "oncall-email"
    email_address = var.oncall_email
  }

  webhook_receiver {
    name = "slack-webhook"
    uri  = var.slack_webhook_url
  }

  webhook_receiver {
    name = "pagerduty"
    uri  = var.pagerduty_webhook_url
  }
}

resource "azurerm_monitor_action_group" "warning" {
  name                = "${var.project}-warning"
  resource_group_name = azurerm_resource_group.main.name
  short_name          = "warning"

  email_receiver {
    name          = "team-email"
    email_address = var.team_email
  }
}
```

### Metric Alert
```hcl
resource "azurerm_monitor_metric_alert" "high_cpu" {
  name                = "${var.project}-high-cpu"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_service_plan.main.id]
  description         = "CPU > 85% for 15 minutes"
  severity            = 2
  frequency           = "PT5M"
  window_size         = "PT15M"

  criteria {
    metric_namespace = "Microsoft.Web/serverfarms"
    metric_name      = "CpuPercentage"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 85
  }

  action { action_group_id = azurerm_monitor_action_group.critical.id }
}

# Log-based alert (KQL)
resource "azurerm_monitor_scheduled_query_rules_alert_v2" "error_rate" {
  name                = "${var.project}-error-rate"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  scopes              = [azurerm_application_insights.main.id]
  description         = "Error rate > 5% in 5 minutes"
  severity            = 1
  enabled             = true
  evaluation_frequency = "PT5M"
  window_duration      = "PT5M"

  criteria {
    query = <<-KQL
      requests
      | where timestamp > ago(5m)
      | summarize total = count(), errors = countif(success == false)
      | extend error_pct = (errors * 100.0) / total
      | where error_pct > 5
    KQL
    time_aggregation_method = "Count"
    operator                = "GreaterThan"
    threshold               = 0

    failing_periods {
      minimum_failing_periods_to_trigger_alert = 1
      number_of_evaluation_periods             = 1
    }
  }

  action { action_groups = [azurerm_monitor_action_group.critical.id] }
}
```

---

## 4. Dashboards

### Azure Dashboard (Terraform)
```hcl
resource "azurerm_portal_dashboard" "main" {
  name                = "${var.project}-${var.environment}-dashboard"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  dashboard_properties = templatefile("${path.module}/dashboard.tpl.json", {
    app_insights_id = azurerm_application_insights.main.id
    subscription_id = data.azurerm_subscription.current.subscription_id
    resource_group  = azurerm_resource_group.main.name
  })
}
```

### Azure Workbook
Workbooks provide interactive dashboards with KQL queries. Use the Azure Portal to create them, then export as ARM/Terraform for version control.

Key panels for a service workbook:
- Request rate and error rate (time chart)
- Latency percentiles (p50, p95, p99)
- Top errors by type
- Dependency performance
- Infrastructure metrics (CPU, memory)
- Active users / sessions



---
