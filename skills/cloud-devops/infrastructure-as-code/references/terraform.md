# Terraform Reference

## Table of Contents
1. Configuration Basics
2. Module Design
3. State Management
4. Provider Configuration (AWS, GCP, Azure)
5. Common Resource Patterns
6. Variables & Outputs
7. Workspaces vs Directory Structure
8. CI/CD Integration

---

## 1. Configuration Basics

### Terraform Block
```hcl
terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  backend "s3" {
    bucket         = "myorg-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

### Provider Configuration
```hcl
# AWS
provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "terraform"
      Project     = var.project_name
    }
  }
}

# GCP
provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# Azure
provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
}
```

---

## 2. Module Design

### Module Structure
```
modules/networking/
├── main.tf           # Resource definitions
├── variables.tf      # Input variables
├── outputs.tf        # Output values
├── versions.tf       # Required providers
├── locals.tf         # Local values
└── README.md         # Documentation
```

### Module Example: VPC
```hcl
# modules/networking/variables.tf
variable "name" {
  description = "VPC name"
  type        = string
}

variable "cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "azs" {
  description = "Availability zones"
  type        = list(string)
}

variable "private_subnets" {
  description = "Private subnet CIDRs"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnets" {
  description = "Public subnet CIDRs"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
```

```hcl
# modules/networking/main.tf
resource "aws_vpc" "this" {
  cidr_block           = var.cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(var.tags, {
    Name = var.name
  })
}

resource "aws_subnet" "private" {
  count             = length(var.private_subnets)
  vpc_id            = aws_vpc.this.id
  cidr_block        = var.private_subnets[count.index]
  availability_zone = var.azs[count.index]

  tags = merge(var.tags, {
    Name = "${var.name}-private-${var.azs[count.index]}"
    Tier = "private"
  })
}

resource "aws_subnet" "public" {
  count                   = length(var.public_subnets)
  vpc_id                  = aws_vpc.this.id
  cidr_block              = var.public_subnets[count.index]
  availability_zone       = var.azs[count.index]
  map_public_ip_on_launch = true

  tags = merge(var.tags, {
    Name = "${var.name}-public-${var.azs[count.index]}"
    Tier = "public"
  })
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
  tags   = merge(var.tags, { Name = "${var.name}-igw" })
}

resource "aws_nat_gateway" "this" {
  count         = var.enable_nat_gateway ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id
  tags          = merge(var.tags, { Name = "${var.name}-nat" })
}

resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? 1 : 0
  domain = "vpc"
  tags   = merge(var.tags, { Name = "${var.name}-nat-eip" })
}
```

```hcl
# modules/networking/outputs.tf
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.this.id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}
```

### Calling Modules
```hcl
# environments/production/main.tf
module "vpc" {
  source = "../../modules/networking"

  name               = "production"
  cidr               = "10.0.0.0/16"
  azs                = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets    = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  enable_nat_gateway = true

  tags = {
    Environment = "production"
  }
}

module "database" {
  source = "../../modules/database"

  name              = "production-db"
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.private_subnet_ids
  instance_class    = "db.r6g.xlarge"
  allocated_storage = 100
}
```

---

## 3. State Management

### Remote Backend Setup

**AWS S3:**
```hcl
terraform {
  backend "s3" {
    bucket         = "myorg-terraform-state"
    key            = "env/production/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

**GCP GCS:**
```hcl
terraform {
  backend "gcs" {
    bucket = "myorg-terraform-state"
    prefix = "env/production"
  }
}
```

**Azure Blob:**
```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "myorgtfstate"
    container_name       = "tfstate"
    key                  = "production.terraform.tfstate"
  }
}
```

### State Best Practices
1. **Always use remote state** — never local for shared infrastructure
2. **Enable state locking** — prevents concurrent modifications
3. **Encrypt state** — contains sensitive data (passwords, keys)
4. **Separate state per environment** — production state ≠ staging state
5. **Never edit state manually** — use `terraform state mv/rm/import`
6. **Back up state** — enable versioning on the state bucket

### State Commands
```bash
# List resources in state
terraform state list

# Show specific resource
terraform state show aws_instance.web

# Move resource (rename without recreate)
terraform state mv aws_instance.old aws_instance.new

# Import existing resource
terraform import aws_instance.web i-1234567890abcdef0

# Remove from state (doesn't delete resource)
terraform state rm aws_instance.web

# Pull remote state locally (for debugging)
terraform state pull > state.json
```

---

## 4. Provider Patterns

### Multi-Region (AWS)
```hcl
provider "aws" {
  alias  = "us_east"
  region = "us-east-1"
}

provider "aws" {
  alias  = "eu_west"
  region = "eu-west-1"
}

module "vpc_us" {
  source    = "./modules/networking"
  providers = { aws = aws.us_east }
  name      = "us-east-vpc"
}

module "vpc_eu" {
  source    = "./modules/networking"
  providers = { aws = aws.eu_west }
  name      = "eu-west-vpc"
}
```

### Multi-Cloud Pattern
```hcl
# Single Terraform config managing multiple clouds
module "aws_infrastructure" {
  source = "./modules/aws"
  providers = { aws = aws }
}

module "gcp_infrastructure" {
  source = "./modules/gcp"
  providers = { google = google }
}

# Cross-cloud: GCP app connects to AWS database
output "aws_db_endpoint" {
  value = module.aws_infrastructure.db_endpoint
}
```

---

## 5. Common Resource Patterns

### AWS EKS Cluster
```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "${var.environment}-cluster"
  cluster_version = "1.31"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids

  eks_managed_node_groups = {
    general = {
      instance_types = ["m6i.xlarge"]
      min_size       = 3
      max_size       = 10
      desired_size   = 3
    }
  }

  cluster_addons = {
    coredns    = { most_recent = true }
    kube-proxy = { most_recent = true }
    vpc-cni    = { most_recent = true }
  }

  enable_irsa = true
}
```

### AWS RDS
```hcl
resource "aws_db_instance" "main" {
  identifier     = "${var.environment}-postgres"
  engine         = "postgres"
  engine_version = "16.3"
  instance_class = var.db_instance_class

  allocated_storage     = var.db_storage
  max_allocated_storage = var.db_storage * 2
  storage_encrypted     = true
  storage_type          = "gp3"

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  multi_az               = var.environment == "production"
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]

  backup_retention_period = 7
  deletion_protection     = var.environment == "production"
  skip_final_snapshot     = var.environment != "production"

  performance_insights_enabled = true

  tags = { Name = "${var.environment}-postgres" }
}
```

### GCP GKE
```hcl
resource "google_container_cluster" "primary" {
  name     = "${var.environment}-cluster"
  location = var.region

  enable_autopilot = true

  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  release_channel {
    channel = "REGULAR"
  }
}
```

### Azure AKS
```hcl
resource "azurerm_kubernetes_cluster" "main" {
  name                = "${var.environment}-aks"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = var.environment
  kubernetes_version  = "1.31"

  default_node_pool {
    name                = "general"
    vm_size             = "Standard_D4s_v3"
    enable_auto_scaling = true
    min_count           = 3
    max_count           = 10
    zones               = [1, 2, 3]
  }

  identity { type = "SystemAssigned" }

  network_profile {
    network_plugin = "azure"
    network_policy = "azure"
  }
}
```

---

## 6. Variables & Outputs

### Variable Validation
```hcl
variable "environment" {
  description = "Deployment environment"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
  validation {
    condition     = can(regex("^(t3|m6i|r6i|c6i)\\.", var.instance_type))
    error_message = "Only t3, m6i, r6i, and c6i instance families are allowed."
  }
}
```

### Locals for Computed Values
```hcl
locals {
  name_prefix = "${var.project}-${var.environment}"

  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
    Team        = var.team
  }

  is_production = var.environment == "production"
  az_count      = local.is_production ? 3 : 2
}
```

---

## 7. Workspaces vs Directory Structure

### Directory Structure (Recommended)
```
environments/
├── dev/
│   ├── main.tf
│   ├── terraform.tfvars    # env-specific values
│   └── backend.tf          # separate state per env
├── staging/
└── production/
```

Advantages: clear separation, independent state, different provider configs.

### Workspaces (simpler, less isolation)
```bash
terraform workspace new staging
terraform workspace new production
terraform workspace select production
terraform apply -var-file="production.tfvars"
```

**Recommendation:** Use directory structure for production. Workspaces are fine for
simple setups but provide less isolation.

---

## 8. CI/CD Integration

### GitHub Actions
```yaml
jobs:
  terraform:
    runs-on: ubuntu-latest
    permissions:
      id-token: write    # OIDC
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with: { terraform_version: "1.7.0" }
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-east-1
      - run: terraform init
      - run: terraform plan -out=plan.tfplan
        # On PR: plan only. On merge to main: apply.
      - if: github.ref == 'refs/heads/main'
        run: terraform apply -auto-approve plan.tfplan
```



---
