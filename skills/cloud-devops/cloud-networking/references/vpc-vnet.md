# VPC / VNet Design Reference

## Table of Contents
1. AWS VPC
2. Azure VNet
3. Security Groups vs NACLs vs NSGs
4. NAT & Internet Access
5. VPC/VNet Peering
6. PrivateLink / Private Endpoints

---

## 1. AWS VPC

### Production VPC (Terraform)
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project}-${var.environment}"
  cidr = var.vpc_cidr                        # e.g., 10.0.0.0/16

  azs             = var.azs                  # ["us-east-1a", "us-east-1b", "us-east-1c"]
  public_subnets  = var.public_subnets       # ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = var.private_subnets      # ["10.0.10.0/23", "10.0.12.0/23", "10.0.14.0/23"]
  database_subnets = var.database_subnets    # ["10.0.20.0/24", "10.0.21.0/24", "10.0.22.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = var.environment != "production"  # One NAT per AZ in prod
  one_nat_gateway_per_az = var.environment == "production"

  enable_dns_hostnames = true
  enable_dns_support   = true

  # VPC Flow Logs
  enable_flow_log                      = true
  create_flow_log_cloudwatch_log_group = true
  create_flow_log_iam_role             = true
  flow_log_max_aggregation_interval    = 60

  # Kubernetes tags
  public_subnet_tags = {
    "kubernetes.io/role/elb" = 1
  }
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = 1
  }

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
```

### VPC Endpoints (PrivateLink to AWS Services)
```hcl
# Gateway endpoints (S3, DynamoDB — free)
module "vpc_endpoints" {
  source  = "terraform-aws-modules/vpc/aws//modules/vpc-endpoints"
  vpc_id  = module.vpc.vpc_id

  endpoints = {
    s3 = {
      service      = "s3"
      service_type = "Gateway"
      route_table_ids = module.vpc.private_route_table_ids
    }
    dynamodb = {
      service      = "dynamodb"
      service_type = "Gateway"
      route_table_ids = module.vpc.private_route_table_ids
    }
    # Interface endpoints (ECR, STS, etc. — cost per hour + data)
    ecr_api = {
      service             = "ecr.api"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
    }
    ecr_dkr = {
      service             = "ecr.dkr"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
    }
    sts = {
      service             = "sts"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
    }
  }
}
```

---

## 2. Azure VNet

### Production VNet (Terraform)
```hcl
resource "azurerm_virtual_network" "main" {
  name                = "${var.project}-${var.environment}-vnet"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = [var.vnet_cidr]    # ["10.0.0.0/16"]

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Public subnet (for LB, bastion)
resource "azurerm_subnet" "public" {
  name                 = "public"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.0.0/24"]
}

# App subnet (AKS, VMs)
resource "azurerm_subnet" "app" {
  name                 = "app"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.10.0/23"]

  # Allow Private Endpoints
  private_endpoint_network_policies = "Enabled"
}

# Data subnet (SQL, Redis)
resource "azurerm_subnet" "data" {
  name                 = "data"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.20.0/24"]

  service_endpoints = ["Microsoft.Sql", "Microsoft.Storage"]
}

# NAT Gateway
resource "azurerm_nat_gateway" "main" {
  name                = "${var.project}-${var.environment}-nat"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku_name            = "Standard"
}

resource "azurerm_public_ip" "nat" {
  name                = "${var.project}-${var.environment}-nat-ip"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_nat_gateway_public_ip_association" "main" {
  nat_gateway_id       = azurerm_nat_gateway.main.id
  public_ip_address_id = azurerm_public_ip.nat.id
}

resource "azurerm_subnet_nat_gateway_association" "app" {
  subnet_id      = azurerm_subnet.app.id
  nat_gateway_id = azurerm_nat_gateway.main.id
}

# Network Watcher Flow Logs
resource "azurerm_network_watcher_flow_log" "main" {
  network_watcher_name = azurerm_network_watcher.main.name
  resource_group_name  = azurerm_resource_group.main.name
  name                 = "${var.project}-flow-log"

  network_security_group_id = azurerm_network_security_group.app.id
  storage_account_id        = azurerm_storage_account.logs.id
  enabled                   = true
  version                   = 2

  retention_policy {
    enabled = true
    days    = 30
  }

  traffic_analytics {
    enabled               = true
    workspace_id          = azurerm_log_analytics_workspace.main.workspace_id
    workspace_region      = azurerm_resource_group.main.location
    workspace_resource_id = azurerm_log_analytics_workspace.main.id
    interval_in_minutes   = 10
  }
}
```

---

## 3. Security Groups vs NACLs vs NSGs

### AWS: Security Groups (Stateful, per-ENI)
```hcl
resource "aws_security_group" "app" {
  name   = "${var.project}-${var.environment}-app"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]  # Only from ALB
    description     = "App traffic from ALB"
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS outbound"
  }

  egress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.db.id]
    description     = "PostgreSQL to database"
  }
}
```

### AWS: NACLs (Stateless, per-subnet — defense-in-depth)
```hcl
resource "aws_network_acl" "private" {
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Allow inbound from VPC
  ingress {
    rule_no    = 100
    protocol   = "tcp"
    action     = "allow"
    cidr_block = var.vpc_cidr
    from_port  = 0
    to_port    = 65535
  }

  # Allow outbound to internet (via NAT)
  egress {
    rule_no    = 100
    protocol   = "tcp"
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 443
    to_port    = 443
  }

  # Deny everything else (implicit)
}
```

### Azure: Network Security Groups (Stateful, per-subnet or NIC)
```hcl
resource "azurerm_network_security_group" "app" {
  name                = "${var.project}-app-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "allow-lb"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8080"
    source_address_prefix      = "AzureLoadBalancer"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "deny-all-inbound"
    priority                   = 4096
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "app" {
  subnet_id                 = azurerm_subnet.app.id
  network_security_group_id = azurerm_network_security_group.app.id
}
```

### Comparison

| Feature | AWS SG | AWS NACL | Azure NSG |
|---------|--------|----------|-----------|
| Stateful | Yes | No | Yes |
| Level | ENI (instance) | Subnet | Subnet or NIC |
| Rules | Allow only | Allow + Deny | Allow + Deny |
| Evaluation | All rules | Ordered by number | Priority-based |
| Default | Deny all in, allow all out | Allow all | Varies |
| Use case | Primary control | Defense-in-depth | Primary control |

---

## 4. NAT & Internet Access

### AWS NAT Gateway
- One per AZ for production (HA)
- Single NAT for dev/staging (cost saving)
- Alternative: NAT instances (cheaper, less reliable)
- Egress-only IGW for IPv6

### Azure NAT Gateway
- Regional (not AZ-specific)
- Supports multiple public IPs for scale
- Better SNAT port allocation than LB-based SNAT

### When to Avoid NAT
- Use VPC endpoints / private endpoints instead (cheaper, more secure)
- ECR, S3, Secrets Manager, etc. all support private access
- NAT is for general internet access only

---

## 5. VPC/VNet Peering

### AWS VPC Peering
```hcl
resource "aws_vpc_peering_connection" "prod_to_shared" {
  vpc_id      = module.vpc_prod.vpc_id
  peer_vpc_id = module.vpc_shared.vpc_id
  auto_accept = true

  accepter { allow_remote_vpc_dns_resolution = true }
  requester { allow_remote_vpc_dns_resolution = true }

  tags = { Name = "prod-to-shared-services" }
}

# Route in prod VPC to shared services
resource "aws_route" "prod_to_shared" {
  count                     = length(module.vpc_prod.private_route_table_ids)
  route_table_id            = module.vpc_prod.private_route_table_ids[count.index]
  destination_cidr_block    = module.vpc_shared.vpc_cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.prod_to_shared.id
}
```

### Azure VNet Peering
```hcl
resource "azurerm_virtual_network_peering" "prod_to_hub" {
  name                      = "prod-to-hub"
  resource_group_name       = azurerm_resource_group.prod.name
  virtual_network_name      = azurerm_virtual_network.prod.name
  remote_virtual_network_id = azurerm_virtual_network.hub.id

  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
  allow_gateway_transit        = false
  use_remote_gateways          = true   # Use hub's VPN gateway
}

resource "azurerm_virtual_network_peering" "hub_to_prod" {
  name                      = "hub-to-prod"
  resource_group_name       = azurerm_resource_group.hub.name
  virtual_network_name      = azurerm_virtual_network.hub.name
  remote_virtual_network_id = azurerm_virtual_network.prod.id

  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
  allow_gateway_transit        = true   # Allow hub to be transit
}
```

### Peering Limitations
- Not transitive (A↔B and B↔C doesn't mean A↔C) — use Transit Gateway/Virtual WAN
- CIDR ranges must not overlap
- Cross-region peering has data transfer costs
- Maximum peering connections: 125 (AWS), 500 (Azure)

---

## 6. PrivateLink / Private Endpoints

### AWS PrivateLink
```hcl
# Access your service privately from another VPC
resource "aws_vpc_endpoint_service" "myservice" {
  acceptance_required        = false
  network_load_balancer_arns = [aws_lb.nlb.arn]
}

# Consumer side
resource "aws_vpc_endpoint" "myservice" {
  vpc_id             = module.consumer_vpc.vpc_id
  service_name       = aws_vpc_endpoint_service.myservice.service_name
  vpc_endpoint_type  = "Interface"
  subnet_ids         = module.consumer_vpc.private_subnets
  security_group_ids = [aws_security_group.endpoint.id]
  private_dns_enabled = true
}
```

### Azure Private Endpoint
```hcl
resource "azurerm_private_endpoint" "sql" {
  name                = "${var.project}-sql-pe"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.data.id

  private_service_connection {
    name                           = "sql-connection"
    private_connection_resource_id = azurerm_mssql_server.main.id
    subresource_names              = ["sqlServer"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "sql-dns"
    private_dns_zone_ids = [azurerm_private_dns_zone.sql.id]
  }
}

resource "azurerm_private_dns_zone" "sql" {
  name                = "privatelink.database.windows.net"
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "sql" {
  name                  = "sql-dns-link"
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.sql.name
  virtual_network_id    = azurerm_virtual_network.main.id
}
```



---

<!-- Script: scripts/generate_network_terraform.py -->

# Script: generate_network_terraform.py

```python
#!/usr/bin/env python3
"""
Generate Terraform network configurations for AWS or Azure.

Usage:
    python generate_network_terraform.py \
        --provider aws|azure \
        --pattern single-region|hub-spoke \
        --environment production \
        --cidr 10.0.0.0/16 \
        --azs 3 \
        --features lb,dns,nat,waf,vpn \
        --project myapp \
        --output ./networking/
"""

import argparse
import os


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


def aws_single_region(env, project, cidr, azs, features, output):
    feat = set(features.split(","))
    region = "us-east-1"
    az_list = [f'"{region}{c}"' for c in "abcdefghij"[:azs]]
    az_str = ", ".join(az_list)

    priv = [f'"10.0.{i*2+10}.0/23"' for i in range(azs)]
    pub = [f'"10.0.{i}.0/24"' for i in range(azs)]
    data = [f'"10.0.{i+20}.0/24"' for i in range(azs)]

    main = f'''terraform {{
  required_version = ">= 1.7.0"
  required_providers {{
    aws = {{ source = "hashicorp/aws"; version = "~> 5.0" }}
  }}
}}

provider "aws" {{
  region = "{region}"
  default_tags {{
    tags = {{
      Environment = "{env}"
      Project     = "{project}"
      ManagedBy   = "terraform"
    }}
  }}
}}

module "vpc" {{
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "{project}-{env}"
  cidr = "{cidr}"

  azs              = [{az_str}]
  public_subnets   = [{", ".join(pub)}]
  private_subnets  = [{", ".join(priv)}]
  database_subnets = [{", ".join(data)}]

  enable_nat_gateway     = {"true" if "nat" in feat else "false"}
  single_nat_gateway     = {"false" if env == "production" else "true"}
  one_nat_gateway_per_az = {"true" if env == "production" else "false"}

  enable_dns_hostnames = true
  enable_dns_support   = true

  enable_flow_log                      = true
  create_flow_log_cloudwatch_log_group = true
  create_flow_log_iam_role             = true

  public_subnet_tags = {{
    "kubernetes.io/role/elb" = 1
    Tier                     = "public"
  }}
  private_subnet_tags = {{
    "kubernetes.io/role/internal-elb" = 1
    Tier                              = "private"
  }}
  database_subnet_tags = {{ Tier = "data" }}
}}
'''

    if "lb" in feat:
        main += f'''
# ── Application Load Balancer ──────────────────────────

resource "aws_security_group" "alb" {{
  name   = "{project}-{env}-alb"
  vpc_id = module.vpc.vpc_id

  ingress {{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }}

  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP redirect"
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [module.vpc.vpc_cidr_block]
    description = "To VPC"
  }}

  tags = {{ Name = "{project}-{env}-alb-sg" }}
}}

resource "aws_lb" "app" {{
  name               = "{project}-{env}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets

  enable_deletion_protection = {"true" if env == "production" else "false"}
  drop_invalid_header_fields = true

  tags = {{ Name = "{project}-{env}-alb" }}
}}

resource "aws_lb_listener" "https" {{
  load_balancer_arn = aws_lb.app.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn

  default_action {{
    type = "fixed-response"
    fixed_response {{
      content_type = "text/plain"
      message_body = "OK"
      status_code  = "200"
    }}
  }}
}}

resource "aws_lb_listener" "http_redirect" {{
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {{
    type = "redirect"
    redirect {{
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }}
  }}
}}
'''

    if "waf" in feat:
        main += f'''
# ── WAF ────────────────────────────────────────────────

resource "aws_wafv2_web_acl" "main" {{
  name  = "{project}-{env}-waf"
  scope = "REGIONAL"

  default_action {{ allow {{}} }}

  rule {{
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 1
    override_action {{ none {{}} }}
    statement {{
      managed_rule_group_statement {{
        vendor_name = "AWS"
        name        = "AWSManagedRulesCommonRuleSet"
      }}
    }}
    visibility_config {{
      cloudwatch_metrics_enabled = true
      metric_name                = "CommonRules"
      sampled_requests_enabled   = true
    }}
  }}

  rule {{
    name     = "RateLimit"
    priority = 2
    action {{ block {{}} }}
    statement {{
      rate_based_statement {{
        limit              = 2000
        aggregate_key_type = "IP"
      }}
    }}
    visibility_config {{
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimit"
      sampled_requests_enabled   = true
    }}
  }}

  visibility_config {{
    cloudwatch_metrics_enabled = true
    metric_name                = "WAF"
    sampled_requests_enabled   = true
  }}
}}

resource "aws_wafv2_web_acl_association" "alb" {{
  resource_arn = aws_lb.app.arn
  web_acl_arn  = aws_wafv2_web_acl.main.arn
}}
'''

    if "dns" in feat:
        main += f'''
# ── DNS ────────────────────────────────────────────────

resource "aws_route53_zone" "main" {{
  name = var.domain_name
}}

resource "aws_route53_record" "app" {{
  zone_id = aws_route53_zone.main.zone_id
  name    = "app.${{var.domain_name}}"
  type    = "A"
  alias {{
    name                   = aws_lb.app.dns_name
    zone_id                = aws_lb.app.zone_id
    evaluate_target_health = true
  }}
}}

resource "aws_route53_health_check" "app" {{
  fqdn              = "app.${{var.domain_name}}"
  port               = 443
  type               = "HTTPS"
  resource_path      = "/health"
  failure_threshold  = 3
  request_interval   = 30
  tags               = {{ Name = "{project}-app-health" }}
}}
'''

    # Variables
    variables = f'''variable "certificate_arn" {{
  description = "ACM certificate ARN for HTTPS"
  type        = string
  default     = ""
}}

variable "domain_name" {{
  description = "Domain name for DNS zone"
  type        = string
  default     = "example.com"
}}
'''

    # Outputs
    outputs = f'''output "vpc_id" {{
  value = module.vpc.vpc_id
}}

output "vpc_cidr" {{
  value = module.vpc.vpc_cidr_block
}}

output "public_subnet_ids" {{
  value = module.vpc.public_subnets
}}

output "private_subnet_ids" {{
  value = module.vpc.private_subnets
}}

output "database_subnet_ids" {{
  value = module.vpc.database_subnets
}}
'''
    if "lb" in feat:
        outputs += f'''
output "alb_dns_name" {{
  value = aws_lb.app.dns_name
}}

output "alb_arn" {{
  value = aws_lb.app.arn
}}
'''

    create_file(os.path.join(output, "main.tf"), main)
    create_file(os.path.join(output, "variables.tf"), variables)
    create_file(os.path.join(output, "outputs.tf"), outputs)


def azure_single_region(env, project, cidr, azs, features, output):
    feat = set(features.split(","))
    region = "eastus"

    main = f'''terraform {{
  required_version = ">= 1.7.0"
  required_providers {{
    azurerm = {{ source = "hashicorp/azurerm"; version = "~> 3.0" }}
  }}
}}

provider "azurerm" {{ features {{}} }}

resource "azurerm_resource_group" "net" {{
  name     = "{project}-{env}-network-rg"
  location = "{region}"
  tags = {{
    Environment = "{env}"
    Project     = "{project}"
    ManagedBy   = "terraform"
  }}
}}

# ── VNet ───────────────────────────────────────────────

resource "azurerm_virtual_network" "main" {{
  name                = "{project}-{env}-vnet"
  location            = azurerm_resource_group.net.location
  resource_group_name = azurerm_resource_group.net.name
  address_space       = ["{cidr}"]
}}

resource "azurerm_subnet" "public" {{
  name                 = "public"
  resource_group_name  = azurerm_resource_group.net.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.0.0/24"]
}}

resource "azurerm_subnet" "app" {{
  name                 = "app"
  resource_group_name  = azurerm_resource_group.net.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.10.0/23"]
}}

resource "azurerm_subnet" "data" {{
  name                 = "data"
  resource_group_name  = azurerm_resource_group.net.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.20.0/24"]
  service_endpoints    = ["Microsoft.Sql", "Microsoft.Storage"]
}}

# ── NSG ────────────────────────────────────────────────

resource "azurerm_network_security_group" "app" {{
  name                = "{project}-{env}-app-nsg"
  location            = azurerm_resource_group.net.location
  resource_group_name = azurerm_resource_group.net.name

  security_rule {{
    name                       = "allow-lb"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8080"
    source_address_prefix      = "AzureLoadBalancer"
    destination_address_prefix = "*"
  }}

  security_rule {{
    name                       = "deny-all"
    priority                   = 4096
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }}
}}

resource "azurerm_subnet_network_security_group_association" "app" {{
  subnet_id                 = azurerm_subnet.app.id
  network_security_group_id = azurerm_network_security_group.app.id
}}
'''

    if "nat" in feat:
        main += f'''
# ── NAT Gateway ────────────────────────────────────────

resource "azurerm_public_ip" "nat" {{
  name                = "{project}-{env}-nat-ip"
  location            = azurerm_resource_group.net.location
  resource_group_name = azurerm_resource_group.net.name
  allocation_method   = "Static"
  sku                 = "Standard"
}}

resource "azurerm_nat_gateway" "main" {{
  name                = "{project}-{env}-nat"
  location            = azurerm_resource_group.net.location
  resource_group_name = azurerm_resource_group.net.name
  sku_name            = "Standard"
}}

resource "azurerm_nat_gateway_public_ip_association" "main" {{
  nat_gateway_id       = azurerm_nat_gateway.main.id
  public_ip_address_id = azurerm_public_ip.nat.id
}}

resource "azurerm_subnet_nat_gateway_association" "app" {{
  subnet_id      = azurerm_subnet.app.id
  nat_gateway_id = azurerm_nat_gateway.main.id
}}
'''

    if "dns" in feat:
        main += f'''
# ── DNS ────────────────────────────────────────────────

resource "azurerm_dns_zone" "main" {{
  name                = var.domain_name
  resource_group_name = azurerm_resource_group.net.name
}}

resource "azurerm_private_dns_zone" "internal" {{
  name                = "internal.${{var.domain_name}}"
  resource_group_name = azurerm_resource_group.net.name
}}

resource "azurerm_private_dns_zone_virtual_network_link" "main" {{
  name                  = "vnet-link"
  resource_group_name   = azurerm_resource_group.net.name
  private_dns_zone_name = azurerm_private_dns_zone.internal.name
  virtual_network_id    = azurerm_virtual_network.main.id
  registration_enabled  = true
}}
'''

    variables = f'''variable "domain_name" {{
  description = "Domain name"
  type        = string
  default     = "example.com"
}}
'''

    outputs = f'''output "vnet_id" {{
  value = azurerm_virtual_network.main.id
}}

output "vnet_name" {{
  value = azurerm_virtual_network.main.name
}}

output "app_subnet_id" {{
  value = azurerm_subnet.app.id
}}

output "data_subnet_id" {{
  value = azurerm_subnet.data.id
}}

output "public_subnet_id" {{
  value = azurerm_subnet.public.id
}}
'''

    create_file(os.path.join(output, "main.tf"), main)
    create_file(os.path.join(output, "variables.tf"), variables)
    create_file(os.path.join(output, "outputs.tf"), outputs)


def main():
    parser = argparse.ArgumentParser(description="Generate Network Terraform")
    parser.add_argument("--provider", choices=["aws", "azure"], required=True)
    parser.add_argument("--pattern", choices=["single-region", "hub-spoke"], default="single-region")
    parser.add_argument("--environment", default="production")
    parser.add_argument("--cidr", default="10.0.0.0/16")
    parser.add_argument("--azs", type=int, default=3)
    parser.add_argument("--features", default="lb,dns,nat,waf",
                        help="Comma-separated: lb,dns,nat,waf,vpn")
    parser.add_argument("--project", default="myapp")
    parser.add_argument("--output", default="./networking")
    args = parser.parse_args()

    print(f"\n🌐 Generating {args.provider.upper()} networking ({args.pattern})\n")
    print(f"   Environment: {args.environment}")
    print(f"   CIDR: {args.cidr}")
    print(f"   AZs: {args.azs}")
    print(f"   Features: {args.features}\n")

    if args.provider == "aws":
        aws_single_region(args.environment, args.project, args.cidr, args.azs, args.features, args.output)
    elif args.provider == "azure":
        azure_single_region(args.environment, args.project, args.cidr, args.azs, args.features, args.output)

    print(f"\n✅ Network config generated at: {args.output}/")


if __name__ == "__main__":
    main()

```
