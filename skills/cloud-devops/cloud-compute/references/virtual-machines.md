# Virtual Machines Reference

## Table of Contents
1. AWS EC2
2. Azure Virtual Machines
3. Instance Type Selection
4. Spot Instances
5. Launch Templates & VM Images

---

## 1. AWS EC2

### Production EC2 with Launch Template
```hcl
resource "aws_launch_template" "app" {
  name_prefix   = "${var.project}-${var.environment}-"
  image_id      = data.aws_ami.app.id
  instance_type = var.instance_type

  # Networking
  vpc_security_group_ids = [aws_security_group.app.id]

  # Metadata service v2 (required for security)
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"     # IMDSv2 only
    http_put_response_hop_limit = 1
  }

  # EBS
  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size           = var.root_volume_size
      volume_type           = "gp3"
      iops                  = 3000
      throughput            = 125
      encrypted             = true
      delete_on_termination = true
    }
  }

  # IAM
  iam_instance_profile {
    name = aws_iam_instance_profile.app.name
  }

  # User data (cloud-init)
  user_data = base64encode(templatefile("${path.module}/userdata.sh", {
    environment = var.environment
    region      = var.region
  }))

  monitoring { enabled = true }  # Detailed monitoring

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name        = "${var.project}-${var.environment}-app"
      Environment = var.environment
    }
  }

  tag_specifications {
    resource_type = "volume"
    tags = {
      Name = "${var.project}-${var.environment}-app-volume"
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "app" {
  name                = "${var.project}-${var.environment}-app"
  desired_capacity    = var.desired_capacity
  min_size            = var.min_size
  max_size            = var.max_size
  vpc_zone_identifier = module.vpc.private_subnets
  health_check_type   = "ELB"
  health_check_grace_period = 300

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  # Mixed instances (on-demand + spot)
  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = var.on_demand_base   # Minimum on-demand
      on_demand_percentage_above_base_capacity = 30                   # 30% on-demand above base
      spot_allocation_strategy                 = "capacity-optimized"
    }
    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.app.id
        version            = "$Latest"
      }
      override {
        instance_type     = "m6i.xlarge"
        weighted_capacity = "1"
      }
      override {
        instance_type     = "m6a.xlarge"
        weighted_capacity = "1"
      }
      override {
        instance_type     = "m5.xlarge"
        weighted_capacity = "1"
      }
    }
  }

  target_group_arns = [aws_lb_target_group.app.arn]

  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 90
      instance_warmup        = 300
    }
  }

  tag {
    key                 = "Name"
    value               = "${var.project}-${var.environment}-app"
    propagate_at_launch = true
  }

  lifecycle {
    ignore_changes = [desired_capacity]  # Let auto-scaling manage
  }
}
```

### AMI Lookup
```hcl
data "aws_ami" "app" {
  most_recent = true
  owners      = ["self"]   # Or "amazon" for official AMIs

  filter {
    name   = "name"
    values = ["${var.project}-app-*"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }
}

# Amazon Linux 2023
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# Ubuntu 24.04
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}
```

---

## 2. Azure Virtual Machines

### Production VM with Scale Set
```hcl
resource "azurerm_linux_virtual_machine_scale_set" "app" {
  name                = "${var.project}-${var.environment}-vmss"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = var.vm_size
  instances           = var.desired_capacity

  admin_username                  = "adminuser"
  disable_password_authentication = true
  admin_ssh_key {
    username   = "adminuser"
    public_key = var.ssh_public_key
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "ubuntu-24_04-lts"
    sku       = "server"
    version   = "latest"
  }

  os_disk {
    storage_account_type = "Premium_LRS"
    caching              = "ReadWrite"
    disk_size_gb         = 100
  }

  network_interface {
    name    = "primary"
    primary = true

    ip_configuration {
      name                                   = "internal"
      primary                                = true
      subnet_id                              = azurerm_subnet.app.id
      load_balancer_backend_address_pool_ids = [azurerm_lb_backend_address_pool.app.id]
    }
  }

  custom_data = base64encode(file("cloud-init.yaml"))

  identity {
    type = "SystemAssigned"
  }

  automatic_os_upgrade_policy {
    disable_automatic_rollback  = false
    enable_automatic_os_upgrade = true
  }

  rolling_upgrade_policy {
    max_batch_instance_percent              = 20
    max_unhealthy_instance_percent          = 20
    max_unhealthy_upgraded_instance_percent = 5
    pause_time_between_batches              = "PT5M"
  }

  upgrade_mode = "Rolling"

  health_probe_id = azurerm_lb_probe.app.id

  zones = [1, 2, 3]

  tags = {
    Environment = var.environment
    Project     = var.project
  }
}

# Azure Spot VMSS
resource "azurerm_linux_virtual_machine_scale_set" "workers" {
  name     = "${var.project}-workers-vmss"
  priority = "Spot"
  eviction_policy = "Delete"
  max_bid_price   = -1    # Pay up to on-demand price

  # ... rest of config same as above
}
```

---

## 3. Instance Type Selection

### AWS Instance Families

| Family | Optimized For | Use Case | Example |
|--------|-------------|---------|---------|
| **t3/t4g** | Burstable | Dev, low-traffic, bastion | t4g.medium |
| **m6i/m7i** | General purpose | APIs, web servers | m6i.xlarge |
| **m6g/m7g** | ARM (Graviton) | Same + 20% cheaper | m7g.xlarge |
| **c6i/c7i** | Compute | CPU-intensive, batch | c7i.2xlarge |
| **r6i/r7i** | Memory | Caches, in-memory DB | r7i.2xlarge |
| **i3/i4i** | Storage IOPS | Databases, Elasticsearch | i4i.xlarge |
| **p4/p5** | GPU | ML training/inference | p4d.24xlarge |
| **g5** | Graphics/ML | Inference, rendering | g5.xlarge |

### Azure VM Series

| Series | Optimized For | Equivalent AWS |
|--------|-------------|---------------|
| **B** | Burstable | t3/t4g |
| **D** | General purpose | m6i |
| **Dpds v6** | ARM | m7g (Graviton) |
| **F** | Compute | c6i |
| **E** | Memory | r6i |
| **L** | Storage | i3/i4i |
| **NC/ND** | GPU | p4/g5 |

### Selection Checklist
1. **CPU-bound?** → C-series / F-series
2. **Memory-bound?** → R-series / E-series
3. **Balanced?** → M-series / D-series
4. **Budget-conscious?** → Graviton / ARM (m7g, Dpds v6)
5. **Variable load?** → Burstable (t4g / B-series)
6. **GPU needed?** → P/G-series / NC/ND-series

---

## 4. Spot Instances

### AWS Spot Best Practices
```hcl
# Spot Fleet for batch processing
resource "aws_spot_fleet_request" "batch" {
  iam_fleet_role  = aws_iam_role.spot_fleet.arn
  target_capacity = var.batch_workers
  allocation_strategy = "capacityOptimized"
  instance_interruption_behaviour = "terminate"

  launch_template_config {
    launch_template_specification {
      id      = aws_launch_template.batch.id
      version = "$Latest"
    }
    overrides { instance_type = "m6i.xlarge"; availability_zone = "us-east-1a" }
    overrides { instance_type = "m6a.xlarge"; availability_zone = "us-east-1b" }
    overrides { instance_type = "m5.xlarge";  availability_zone = "us-east-1c" }
    overrides { instance_type = "c6i.xlarge"; availability_zone = "us-east-1a" }
  }
}
```

### Spot Survival Guide
1. **Diversify** — use 4+ instance types across 3+ AZs
2. **Handle interruptions** — use 2-minute warning to drain gracefully
3. **Checkpointing** — save progress for long-running jobs
4. **Use capacity-optimized** — allocation strategy reduces interruptions
5. **Mix on-demand + spot** — baseline on-demand, burst with spot

---

## 5. Launch Templates & VM Images

### Cloud-Init User Data
```yaml
#cloud-config
package_update: true
packages:
  - docker.io
  - awscli
  - jq
  - curl

write_files:
  - path: /etc/app/config.yaml
    content: |
      environment: ${environment}
      region: ${region}
      log_level: info

runcmd:
  - systemctl enable docker
  - systemctl start docker
  - aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${ecr_url}
  - docker pull ${ecr_url}/${image}:${tag}
  - docker run -d --restart always -p 8080:8080 ${ecr_url}/${image}:${tag}
```

### Golden AMI Pipeline
```
Base AMI (Amazon Linux / Ubuntu)
  → Packer build
    → Install common packages
    → Harden (CIS benchmark)
    → Install monitoring agent
    → Install app runtime
  → Test with InSpec / Goss
  → Publish AMI
  → Tag with version + date
```

```hcl
# Packer template (HCL)
source "amazon-ebs" "app" {
  ami_name      = "${var.project}-app-${formatdate("YYYYMMDD", timestamp())}"
  instance_type = "t3.medium"
  region        = "us-east-1"
  source_ami_filter {
    filters = { "name" = "al2023-ami-*-x86_64" }
    owners  = ["amazon"]
    most_recent = true
  }
  ssh_username = "ec2-user"
}

build {
  sources = ["source.amazon-ebs.app"]
  provisioner "shell" {
    scripts = ["scripts/install-base.sh", "scripts/harden.sh", "scripts/install-app.sh"]
  }
}
```



---

<!-- Script: scripts/generate_compute_terraform.py -->

# Script: generate_compute_terraform.py

```python
#!/usr/bin/env python3
"""
Generate Terraform compute configurations for AWS or Azure.

Usage:
    python generate_compute_terraform.py \
        --provider aws|azure \
        --compute-type vm|serverless|container \
        --environment production \
        --project myapp \
        --output ./compute/
"""

import argparse
import os


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


def aws_vm(env, project, output):
    is_prod = env == "production"
    main = f'''terraform {{
  required_version = ">= 1.7.0"
  required_providers {{
    aws = {{ source = "hashicorp/aws"; version = "~> 5.0" }}
  }}
}}

provider "aws" {{
  region = var.region
  default_tags {{
    tags = {{ Environment = "{env}", Project = "{project}", ManagedBy = "terraform" }}
  }}
}}

data "aws_ami" "al2023" {{
  most_recent = true
  owners      = ["amazon"]
  filter {{
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }}
}}

resource "aws_launch_template" "app" {{
  name_prefix   = "{project}-{env}-"
  image_id      = data.aws_ami.al2023.id
  instance_type = var.instance_type

  metadata_options {{
    http_tokens = "required"
    http_endpoint = "enabled"
  }}

  block_device_mappings {{
    device_name = "/dev/xvda"
    ebs {{
      volume_size = var.root_volume_size
      volume_type = "gp3"
      encrypted   = true
    }}
  }}

  iam_instance_profile {{ name = aws_iam_instance_profile.app.name }}

  monitoring {{ enabled = true }}

  tag_specifications {{
    resource_type = "instance"
    tags = {{ Name = "{project}-{env}-app" }}
  }}

  lifecycle {{ create_before_destroy = true }}
}}

resource "aws_autoscaling_group" "app" {{
  name                = "{project}-{env}-app"
  desired_capacity    = var.desired_capacity
  min_size            = var.min_size
  max_size            = var.max_size
  vpc_zone_identifier = var.private_subnet_ids
  health_check_type   = "ELB"
  health_check_grace_period = 300

  launch_template {{
    id      = aws_launch_template.app.id
    version = "$Latest"
  }}

  instance_refresh {{
    strategy = "Rolling"
    preferences {{
      min_healthy_percentage = 90
    }}
  }}

  lifecycle {{ ignore_changes = [desired_capacity] }}
}}

resource "aws_autoscaling_policy" "cpu" {{
  name                   = "{project}-cpu-target"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {{
    predefined_metric_specification {{
      predefined_metric_type = "ASGAverageCPUUtilization"
    }}
    target_value = 70.0
  }}
}}

resource "aws_iam_role" "app" {{
  name = "{project}-{env}-app-role"
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{ Action = "sts:AssumeRole", Effect = "Allow", Principal = {{ Service = "ec2.amazonaws.com" }} }}]
  }})
}}

resource "aws_iam_instance_profile" "app" {{
  name = "{project}-{env}-app-profile"
  role = aws_iam_role.app.name
}}
'''

    variables = f'''variable "region" {{ default = "us-east-1" }}
variable "instance_type" {{ default = "{"m6i.xlarge" if is_prod else "t3.medium"}" }}
variable "root_volume_size" {{ default = {"100" if is_prod else "30"} }}
variable "desired_capacity" {{ default = {"3" if is_prod else "1"} }}
variable "min_size" {{ default = {"2" if is_prod else "1"} }}
variable "max_size" {{ default = {"10" if is_prod else "3"} }}
variable "private_subnet_ids" {{ type = list(string) }}
'''

    create_file(os.path.join(output, "main.tf"), main)
    create_file(os.path.join(output, "variables.tf"), variables)


def aws_serverless(env, project, output):
    main = f'''terraform {{
  required_version = ">= 1.7.0"
  required_providers {{
    aws = {{ source = "hashicorp/aws"; version = "~> 5.0" }}
  }}
}}

provider "aws" {{
  region = var.region
  default_tags {{
    tags = {{ Environment = "{env}", Project = "{project}", ManagedBy = "terraform" }}
  }}
}}

resource "aws_lambda_function" "api" {{
  function_name = "{project}-{env}-api"
  role          = aws_iam_role.lambda.arn
  handler       = "index.handler"
  runtime       = "nodejs20.x"
  architectures = ["arm64"]
  memory_size   = var.lambda_memory
  timeout       = var.lambda_timeout
  publish       = true

  filename         = "${{path.module}}/lambda.zip"
  source_code_hash = filebase64sha256("${{path.module}}/lambda.zip")

  environment {{
    variables = {{
      ENVIRONMENT = "{env}"
      LOG_LEVEL   = "info"
    }}
  }}

  tracing_config {{ mode = "Active" }}

  dead_letter_config {{
    target_arn = aws_sqs_queue.dlq.arn
  }}

  reserved_concurrent_executions = {"100" if env == "production" else "10"}
}}

# API Gateway HTTP API
resource "aws_apigatewayv2_api" "main" {{
  name          = "{project}-{env}"
  protocol_type = "HTTP"

  cors_configuration {{
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
    max_age       = 3600
  }}
}}

resource "aws_apigatewayv2_integration" "lambda" {{
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}}

resource "aws_apigatewayv2_route" "default" {{
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "$default"
  target    = "integrations/${{aws_apigatewayv2_integration.lambda.id}}"
}}

resource "aws_apigatewayv2_stage" "default" {{
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true
}}

resource "aws_lambda_permission" "apigw" {{
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${{aws_apigatewayv2_api.main.execution_arn}}/*/*"
}}

# DLQ
resource "aws_sqs_queue" "dlq" {{
  name = "{project}-{env}-dlq"
  message_retention_seconds = 1209600
}}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda" {{
  name              = "/aws/lambda/{project}-{env}-api"
  retention_in_days = {"30" if env == "production" else "7"}
}}

# IAM Role
resource "aws_iam_role" "lambda" {{
  name = "{project}-{env}-lambda-role"
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{ Action = "sts:AssumeRole", Effect = "Allow", Principal = {{ Service = "lambda.amazonaws.com" }} }}]
  }})
}}

resource "aws_iam_role_policy_attachment" "lambda_basic" {{
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}}

resource "aws_iam_role_policy_attachment" "lambda_xray" {{
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
}}
'''

    variables = f'''variable "region" {{ default = "us-east-1" }}
variable "lambda_memory" {{ default = 512 }}
variable "lambda_timeout" {{ default = 30 }}
'''

    outputs = f'''output "api_endpoint" {{
  value = aws_apigatewayv2_stage.default.invoke_url
}}

output "function_name" {{
  value = aws_lambda_function.api.function_name
}}
'''

    create_file(os.path.join(output, "main.tf"), main)
    create_file(os.path.join(output, "variables.tf"), variables)
    create_file(os.path.join(output, "outputs.tf"), outputs)

    # Create placeholder lambda
    create_file(os.path.join(output, "src", "index.mjs"), '''export const handler = async (event) => {
  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: "Hello from Lambda!", path: event.rawPath }),
  };
};
''')


def aws_container(env, project, output):
    is_prod = env == "production"
    main = f'''terraform {{
  required_version = ">= 1.7.0"
  required_providers {{
    aws = {{ source = "hashicorp/aws"; version = "~> 5.0" }}
  }}
}}

provider "aws" {{
  region = var.region
  default_tags {{
    tags = {{ Environment = "{env}", Project = "{project}", ManagedBy = "terraform" }}
  }}
}}

resource "aws_ecs_cluster" "main" {{
  name = "{project}-{env}"
  setting {{ name = "containerInsights"; value = "enabled" }}
}}

resource "aws_ecs_task_definition" "app" {{
  family                   = "{project}-{env}-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{{
    name      = "app"
    image     = var.container_image
    essential = true
    portMappings = [{{ containerPort = var.container_port, protocol = "tcp" }}]
    environment = [
      {{ name = "ENVIRONMENT", value = "{env}" }},
      {{ name = "PORT", value = tostring(var.container_port) }},
    ]
    logConfiguration = {{
      logDriver = "awslogs"
      options = {{
        "awslogs-group"         = aws_cloudwatch_log_group.app.name
        "awslogs-region"        = var.region
        "awslogs-stream-prefix" = "app"
      }}
    }}
    healthCheck = {{
      command     = ["CMD-SHELL", "curl -f http://localhost:${{var.container_port}}/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }}
  }}])

  runtime_platform {{
    cpu_architecture        = "ARM64"
    operating_system_family = "LINUX"
  }}
}}

resource "aws_ecs_service" "app" {{
  name            = "{project}-app"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {{
    subnets         = var.private_subnet_ids
    security_groups = var.security_group_ids
  }}

  deployment_circuit_breaker {{
    enable   = true
    rollback = true
  }}

  lifecycle {{ ignore_changes = [desired_count, task_definition] }}
}}

# Auto-scaling
resource "aws_appautoscaling_target" "ecs" {{
  max_capacity       = var.max_count
  min_capacity       = var.min_count
  resource_id        = "service/${{aws_ecs_cluster.main.name}}/${{aws_ecs_service.app.name}}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}}

resource "aws_appautoscaling_policy" "ecs_cpu" {{
  name               = "{project}-cpu"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {{
    predefined_metric_specification {{
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }}
    target_value       = 70
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }}
}}

resource "aws_cloudwatch_log_group" "app" {{
  name              = "/ecs/{project}-{env}"
  retention_in_days = {"30" if is_prod else "7"}
}}

# IAM Roles
resource "aws_iam_role" "ecs_execution" {{
  name = "{project}-{env}-ecs-exec"
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{ Action = "sts:AssumeRole", Effect = "Allow", Principal = {{ Service = "ecs-tasks.amazonaws.com" }} }}]
  }})
}}

resource "aws_iam_role_policy_attachment" "ecs_execution" {{
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}}

resource "aws_iam_role" "ecs_task" {{
  name = "{project}-{env}-ecs-task"
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{ Action = "sts:AssumeRole", Effect = "Allow", Principal = {{ Service = "ecs-tasks.amazonaws.com" }} }}]
  }})
}}
'''

    variables = f'''variable "region" {{ default = "us-east-1" }}
variable "container_image" {{ default = "nginx:alpine" }}
variable "container_port" {{ default = 8080 }}
variable "task_cpu" {{ default = {"1024" if is_prod else "256"} }}
variable "task_memory" {{ default = {"2048" if is_prod else "512"} }}
variable "desired_count" {{ default = {"3" if is_prod else "1"} }}
variable "min_count" {{ default = {"2" if is_prod else "1"} }}
variable "max_count" {{ default = {"10" if is_prod else "3"} }}
variable "private_subnet_ids" {{ type = list(string) }}
variable "security_group_ids" {{ type = list(string); default = [] }}
'''

    create_file(os.path.join(output, "main.tf"), main)
    create_file(os.path.join(output, "variables.tf"), variables)


def azure_vm(env, project, output):
    create_file(os.path.join(output, "main.tf"), f'''terraform {{
  required_version = ">= 1.7.0"
  required_providers {{ azurerm = {{ source = "hashicorp/azurerm"; version = "~> 3.0" }} }}
}}
provider "azurerm" {{ features {{}} }}

resource "azurerm_resource_group" "compute" {{
  name     = "{project}-{env}-compute-rg"
  location = var.location
}}

resource "azurerm_linux_virtual_machine_scale_set" "app" {{
  name                = "{project}-{env}-vmss"
  resource_group_name = azurerm_resource_group.compute.name
  location            = azurerm_resource_group.compute.location
  sku                 = var.vm_size
  instances           = var.desired_capacity
  admin_username      = "adminuser"
  disable_password_authentication = true

  admin_ssh_key {{
    username   = "adminuser"
    public_key = var.ssh_public_key
  }}

  source_image_reference {{
    publisher = "Canonical"
    offer     = "ubuntu-24_04-lts"
    sku       = "server"
    version   = "latest"
  }}

  os_disk {{
    storage_account_type = "Premium_LRS"
    caching              = "ReadWrite"
  }}

  network_interface {{
    name    = "primary"
    primary = true
    ip_configuration {{
      name      = "internal"
      primary   = true
      subnet_id = var.subnet_id
    }}
  }}

  identity {{ type = "SystemAssigned" }}
  zones = [1, 2, 3]
}}
''')
    create_file(os.path.join(output, "variables.tf"), f'''variable "location" {{ default = "eastus" }}
variable "vm_size" {{ default = "{"Standard_D4s_v3" if env == "production" else "Standard_B2s"}" }}
variable "desired_capacity" {{ default = {"3" if env == "production" else "1"} }}
variable "subnet_id" {{ type = string }}
variable "ssh_public_key" {{ type = string }}
''')


GENERATORS = {
    ("aws", "vm"): aws_vm,
    ("aws", "serverless"): aws_serverless,
    ("aws", "container"): aws_container,
    ("azure", "vm"): azure_vm,
}


def main():
    parser = argparse.ArgumentParser(description="Generate Compute Terraform")
    parser.add_argument("--provider", choices=["aws", "azure"], required=True)
    parser.add_argument("--compute-type", choices=["vm", "serverless", "container"], required=True)
    parser.add_argument("--environment", default="production")
    parser.add_argument("--project", default="myapp")
    parser.add_argument("--output", default="./compute")
    args = parser.parse_args()

    key = (args.provider, args.compute_type)
    gen = GENERATORS.get(key)

    if not gen:
        print(f"⚠️  {args.provider}/{args.compute_type} not yet implemented. Available: {list(GENERATORS.keys())}")
        return

    print(f"\n⚡ Generating {args.provider.upper()} {args.compute_type} compute ({args.environment})\n")
    gen(args.environment, args.project, args.output)
    print(f"\n✅ Compute config generated at: {args.output}/")


if __name__ == "__main__":
    main()

```
