# Container Compute Reference

## Table of Contents
1. AWS ECS Fargate
2. AWS App Runner
3. Azure Container Instances
4. Azure App Service
5. Container Compute Decision Guide

---

## 1. AWS ECS Fargate

### Production ECS Service
```hcl
resource "aws_ecs_cluster" "main" {
  name = "${var.project}-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_task_definition" "app" {
  family                   = "${var.project}-${var.environment}-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu       # 256, 512, 1024, 2048, 4096
  memory                   = var.task_memory    # 512 - 30720
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "app"
    image = "${aws_ecr_repository.app.repository_url}:${var.image_tag}"

    portMappings = [{
      containerPort = 8080
      protocol      = "tcp"
    }]

    environment = [
      { name = "ENVIRONMENT", value = var.environment },
      { name = "PORT", value = "8080" },
    ]

    secrets = [
      { name = "DATABASE_URL", valueFrom = aws_secretsmanager_secret.db_url.arn },
      { name = "API_KEY", valueFrom = "${aws_secretsmanager_secret.api.arn}:api_key::" },
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.app.name
        "awslogs-region"        = var.region
        "awslogs-stream-prefix" = "app"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }

    essential = true
  }])

  runtime_platform {
    cpu_architecture        = "ARM64"    # Graviton — 20% cheaper
    operating_system_family = "LINUX"
  }
}

resource "aws_ecs_service" "app" {
  name            = "${var.project}-app"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = module.vpc.private_subnets
    security_groups = [aws_security_group.app.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "app"
    container_port   = 8080
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  deployment_configuration {
    maximum_percent         = 200
    minimum_healthy_percent = 100
  }

  enable_execute_command = var.environment != "production"  # ECS Exec for debugging

  lifecycle {
    ignore_changes = [desired_count, task_definition]  # Managed by CI/CD + autoscaling
  }
}

# Auto-scaling
resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = var.max_count
  min_capacity       = var.min_count
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "ecs_cpu" {
  name               = "${var.project}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
```

---

## 2. AWS App Runner

Simplest way to run containers on AWS — no VPC, no cluster, no task definitions.

```hcl
resource "aws_apprunner_service" "app" {
  service_name = "${var.project}-${var.environment}"

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_ecr.arn
    }
    image_repository {
      image_identifier      = "${aws_ecr_repository.app.repository_url}:latest"
      image_repository_type = "ECR"
      image_configuration {
        port                          = "8080"
        runtime_environment_variables = {
          ENVIRONMENT = var.environment
        }
        runtime_environment_secrets = {
          DATABASE_URL = aws_secretsmanager_secret.db_url.arn
        }
      }
    }
    auto_deployments_enabled = true    # Auto-deploy on new image push
  }

  instance_configuration {
    cpu    = "1024"    # 0.25, 0.5, 1, 2, 4 vCPU
    memory = "2048"   # 0.5-12 GB
  }

  auto_scaling_configuration_arn = aws_apprunner_auto_scaling_configuration_version.app.arn

  health_check_configuration {
    protocol            = "HTTP"
    path                = "/health"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 1
    unhealthy_threshold = 5
  }
}

resource "aws_apprunner_auto_scaling_configuration_version" "app" {
  auto_scaling_configuration_name = "${var.project}-scaling"
  min_size                        = var.environment == "production" ? 2 : 1
  max_size                        = 10
  max_concurrency                 = 100    # Requests per instance before scaling
}
```

### App Runner vs ECS Fargate

| Factor | App Runner | ECS Fargate |
|--------|-----------|-------------|
| Complexity | Very low | Medium |
| VPC support | Optional | Required |
| Custom networking | Limited | Full control |
| Service mesh | No | Yes (App Mesh) |
| Cost (low traffic) | Lower (scale to 1) | Higher (min tasks) |
| Cost (high traffic) | Higher | Lower |
| GPU | No | No (use EC2) |
| Sidecar containers | No | Yes |
| Best for | Simple APIs, prototypes | Production microservices |

---

## 3. Azure Container Instances (ACI)

Serverless containers — no cluster management.

```hcl
resource "azurerm_container_group" "app" {
  name                = "${var.project}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  ip_address_type     = "Private"
  subnet_ids          = [azurerm_subnet.app.id]

  container {
    name   = "app"
    image  = "${azurerm_container_registry.main.login_server}/app:${var.image_tag}"
    cpu    = "1"
    memory = "2"

    ports {
      port     = 8080
      protocol = "TCP"
    }

    environment_variables = {
      ENVIRONMENT = var.environment
    }

    secure_environment_variables = {
      DATABASE_URL = var.database_url
    }

    liveness_probe {
      http_get {
        path   = "/health"
        port   = 8080
        scheme = "Http"
      }
      initial_delay_seconds = 15
      period_seconds        = 10
    }
  }

  identity {
    type = "SystemAssigned"
  }

  image_registry_credential {
    server   = azurerm_container_registry.main.login_server
    username = azurerm_container_registry.main.admin_username
    password = azurerm_container_registry.main.admin_password
  }
}
```

---

## 4. Azure App Service (Containers)

```hcl
resource "azurerm_service_plan" "main" {
  name                = "${var.project}-${var.environment}-plan"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = var.environment == "production" ? "P1v3" : "B1"
}

resource "azurerm_linux_web_app" "main" {
  name                = "${var.project}-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    always_on = true

    application_stack {
      docker_registry_url = "https://${azurerm_container_registry.main.login_server}"
      docker_image_name   = "app:${var.image_tag}"
      docker_registry_username = azurerm_container_registry.main.admin_username
      docker_registry_password = azurerm_container_registry.main.admin_password
    }

    health_check_path = "/health"
  }

  app_settings = {
    ENVIRONMENT                    = var.environment
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = "false"
    DOCKER_REGISTRY_SERVER_URL     = "https://${azurerm_container_registry.main.login_server}"
  }

  identity {
    type = "SystemAssigned"
  }
}

# Auto-scale
resource "azurerm_monitor_autoscale_setting" "app" {
  name                = "${var.project}-autoscale"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  target_resource_id  = azurerm_service_plan.main.id

  profile {
    name = "default"
    capacity {
      default = 2
      minimum = 2
      maximum = 10
    }

    rule {
      metric_trigger {
        metric_name        = "CpuPercentage"
        metric_resource_id = azurerm_service_plan.main.id
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
        value     = "1"
        cooldown  = "PT5M"
      }
    }

    rule {
      metric_trigger {
        metric_name        = "CpuPercentage"
        metric_resource_id = azurerm_service_plan.main.id
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
}
```

---

## 5. Container Compute Decision Guide

| Factor | ECS Fargate | App Runner | ACI | App Service |
|--------|-----------|-----------|-----|-------------|
| Cloud | AWS | AWS | Azure | Azure |
| Complexity | Medium | Low | Low | Low-Medium |
| Auto-scale | Yes (fine-grained) | Yes (simple) | Manual | Yes |
| VPC | Required | Optional | Optional | Optional (VNet integration) |
| Sidecars | Yes | No | Yes | No |
| GPU | No | No | Yes | No |
| Min cost | ~$10/mo | ~$5/mo | Per-second billing | ~$13/mo (B1) |
| Best for | Microservices, production | Simple APIs | Jobs, burst tasks | Web apps, APIs |



---
