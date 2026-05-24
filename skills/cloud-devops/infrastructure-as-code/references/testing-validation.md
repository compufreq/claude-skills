# IaC Testing & Validation Reference

## Table of Contents
1. Testing Pyramid for IaC
2. Terraform Validation (tflint, Checkov)
3. Terratest
4. CloudFormation Validation
5. Ansible Testing
6. Policy-as-Code (OPA, Sentinel)

---

## 1. Testing Pyramid for IaC

```
        /  Integration Tests  \      Slow, expensive, high confidence
       /   (Terratest, taskcat) \    Deploy real resources, verify
      /─────────────────────────\
     /    Policy & Security      \   Medium speed, catches violations
    /   (Checkov, OPA, Sentinel)  \  Static analysis of IaC files
   /───────────────────────────────\
  /     Linting & Validation        \ Fast, cheap, catches basics
 / (tflint, cfn-lint, ansible-lint)  \ Syntax, best practices, formatting
/─────────────────────────────────────\
```

Run bottom-up: lint first (fastest), then policy, then integration (slowest).

---

## 2. Terraform Validation

### Built-in Validation
```bash
# Format check
terraform fmt -check -recursive

# Validate syntax
terraform validate

# Plan (shows what would change)
terraform plan -detailed-exitcode
# Exit code 0 = no changes, 1 = error, 2 = changes pending
```

### tflint (Linting)
```bash
# Install
brew install tflint

# Configure
cat > .tflint.hcl << 'EOF'
plugin "aws" {
  enabled = true
  version = "0.32.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

rule "terraform_naming_convention" {
  enabled = true
}

rule "terraform_documented_variables" {
  enabled = true
}

rule "terraform_documented_outputs" {
  enabled = true
}

rule "terraform_unused_declarations" {
  enabled = true
}
EOF

# Run
tflint --init
tflint --recursive
```

### Checkov (Security Scanning)
```bash
# Install
pip install checkov

# Scan Terraform
checkov -d ./infrastructure/ --framework terraform

# Scan specific file
checkov -f main.tf

# Skip specific checks
checkov -d . --skip-check CKV_AWS_79,CKV_AWS_144

# Output formats
checkov -d . -o json > checkov-results.json
checkov -d . -o sarif > checkov-results.sarif  # For GitHub Code Scanning

# Custom policy
checkov -d . --external-checks-dir ./custom-policies/
```

### Common Checkov Findings

| Check | Description | Fix |
|-------|------------|-----|
| CKV_AWS_79 | EC2 metadata service v2 not enforced | Add `http_tokens = "required"` |
| CKV_AWS_144 | S3 bucket not encrypted | Add `server_side_encryption_configuration` |
| CKV_AWS_145 | S3 public access not blocked | Add `aws_s3_bucket_public_access_block` |
| CKV_AWS_18 | S3 access logging disabled | Add `logging` block |
| CKV_AWS_23 | Security group allows 0.0.0.0/0 ingress | Restrict CIDR blocks |
| CKV_AWS_24 | Security group allows all egress | Restrict egress rules |
| CKV_AWS_88 | EC2 has public IP | Set `associate_public_ip_address = false` |
| CKV2_AWS_5 | Security group not attached | Attach to resource or remove |

### CI Integration
```yaml
# GitHub Actions
- name: Terraform Lint
  run: |
    terraform fmt -check -recursive
    tflint --init && tflint --recursive

- name: Security Scan
  uses: bridgecrewio/checkov-action@v12
  with:
    directory: ./infrastructure
    framework: terraform
    output_format: sarif
    output_file_path: checkov.sarif
    soft_fail: false

- name: Upload Scan Results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: checkov.sarif
```

---

## 3. Terratest (Integration Testing)

### Basic Test Structure
```go
// test/vpc_test.go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestVpcModule(t *testing.T) {
    t.Parallel()

    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../modules/networking",
        Vars: map[string]interface{}{
            "name":               "test-vpc",
            "cidr":               "10.99.0.0/16",
            "azs":                []string{"us-east-1a", "us-east-1b"},
            "private_subnets":    []string{"10.99.1.0/24", "10.99.2.0/24"},
            "public_subnets":     []string{"10.99.101.0/24", "10.99.102.0/24"},
            "enable_nat_gateway": false,  // Save cost in tests
        },
    })

    // Clean up after test
    defer terraform.Destroy(t, terraformOptions)

    // Deploy
    terraform.InitAndApply(t, terraformOptions)

    // Validate outputs
    vpcId := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcId)
    assert.Contains(t, vpcId, "vpc-")

    privateSubnets := terraform.OutputList(t, terraformOptions, "private_subnet_ids")
    assert.Len(t, privateSubnets, 2)
}
```

### Testing with AWS SDK
```go
func TestRdsModule(t *testing.T) {
    t.Parallel()

    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../modules/database",
        Vars: map[string]interface{}{
            "environment":    "test",
            "instance_class": "db.t4g.micro",  // Small for testing
            "storage":        20,
        },
    })

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    // Verify RDS endpoint is reachable
    endpoint := terraform.Output(t, terraformOptions, "db_endpoint")
    assert.NotEmpty(t, endpoint)

    // Verify encryption
    dbId := terraform.Output(t, terraformOptions, "db_identifier")
    aws.GetRdsInstanceDetails(t, dbId, "us-east-1")
}
```

### Running Terratest
```bash
cd test/
go test -v -timeout 30m -run TestVpcModule
go test -v -timeout 60m  # Run all tests
```

---

## 4. CloudFormation Validation

### cfn-lint
```bash
# Install
pip install cfn-lint

# Lint
cfn-lint template.yaml
cfn-lint templates/*.yaml

# With specific rules
cfn-lint -i W3002 template.yaml  # Ignore specific warning
```

### taskcat (Integration Testing)
```yaml
# .taskcat.yml
project:
  name: my-infrastructure
  regions:
    - us-east-1
    - eu-west-1

tests:
  vpc-test:
    template: templates/vpc.yaml
    parameters:
      Environment: test
      VpcCidr: 10.99.0.0/16
    regions:
      - us-east-1

  rds-test:
    template: templates/rds.yaml
    parameters:
      Environment: test
      DBInstanceClass: db.t4g.micro
```

```bash
# Run tests (creates real stacks, validates, then tears down)
taskcat test run
```

### AWS CloudFormation Guard (Policy)
```
# rules/s3-rules.guard
let s3_buckets = Resources.*[ Type == 'AWS::S3::Bucket' ]

rule s3_encryption_required when %s3_buckets !empty {
    %s3_buckets.Properties.BucketEncryption EXISTS
    %s3_buckets.Properties.BucketEncryption.ServerSideEncryptionConfiguration[*].ServerSideEncryptionByDefault.SSEAlgorithm == 'aws:kms'
}

rule s3_versioning_required when %s3_buckets !empty {
    %s3_buckets.Properties.VersioningConfiguration.Status == 'Enabled'
}
```

```bash
cfn-guard validate -d template.yaml -r rules/
```

---

## 5. Ansible Testing

### ansible-lint
```bash
# Install
pip install ansible-lint

# Run
ansible-lint playbooks/site.yml
ansible-lint roles/nginx/

# Configuration (.ansible-lint)
skip_list:
  - yaml[line-length]
  - name[casing]
warn_list:
  - experimental
```

### Molecule (Role Testing)
```bash
# Install
pip install molecule molecule-docker

# Initialize test scenario
cd roles/nginx
molecule init scenario -d docker

# Test lifecycle
molecule create      # Create test container
molecule converge    # Run the role
molecule verify      # Run assertions
molecule destroy     # Clean up
molecule test        # Full cycle (create → converge → verify → destroy)
```

```yaml
# roles/nginx/molecule/default/molecule.yml
driver:
  name: docker
platforms:
  - name: ubuntu
    image: ubuntu:24.04
    pre_build_image: true
    command: /sbin/init
    privileged: true
  - name: debian
    image: debian:bookworm
    pre_build_image: true
provisioner:
  name: ansible
  playbooks:
    converge: converge.yml
verifier:
  name: ansible
```

```yaml
# roles/nginx/molecule/default/verify.yml
- name: Verify nginx
  hosts: all
  tasks:
    - name: Check nginx is running
      service_facts:
    - name: Assert nginx is active
      assert:
        that: ansible_facts.services['nginx.service'].state == 'running'

    - name: Check nginx responds
      uri:
        url: http://localhost
        status_code: 200
```

---

## 6. Policy-as-Code

### Open Policy Agent (OPA) for Terraform
```rego
# policy/terraform/deny_public_s3.rego
package terraform.deny

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    resource.change.after.acl == "public-read"
    msg := sprintf("S3 bucket '%s' must not be public", [resource.address])
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_security_group_rule"
    resource.change.after.cidr_blocks[_] == "0.0.0.0/0"
    resource.change.after.type == "ingress"
    msg := sprintf("Security group '%s' must not allow ingress from 0.0.0.0/0", [resource.address])
}
```

```bash
# Generate plan JSON
terraform plan -out=plan.tfplan
terraform show -json plan.tfplan > plan.json

# Evaluate with OPA
opa eval --data policy/ --input plan.json "data.terraform.deny"
```

### Conftest (OPA wrapper)
```bash
# Install
brew install conftest

# Test Terraform plan
conftest test plan.json --policy policy/

# Test Dockerfile
conftest test Dockerfile --policy policy/docker/

# Test Kubernetes manifests
conftest test k8s/ --policy policy/kubernetes/
```

### CI Pipeline with Full Validation
```yaml
# Complete IaC validation pipeline
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3

      # 1. Format check
      - run: terraform fmt -check -recursive

      # 2. Lint
      - run: tflint --init && tflint --recursive

      # 3. Validate
      - run: terraform init -backend=false && terraform validate

      # 4. Security scan
      - uses: bridgecrewio/checkov-action@v12
        with:
          directory: ./infrastructure
          soft_fail: false

      # 5. Policy check
      - run: |
          terraform plan -out=plan.tfplan
          terraform show -json plan.tfplan > plan.json
          conftest test plan.json --policy policy/

      # 6. Cost estimation (optional)
      - uses: infracost/actions/setup@v3
      - run: infracost breakdown --path .
```



---

<!-- Script: scripts/generate_terraform.py -->

# Script: generate_terraform.py

```python
#!/usr/bin/env python3
"""
Generate Terraform configurations for AWS, GCP, or Azure.

Usage:
    python generate_terraform.py \
        --provider aws|gcp|azure \
        --resources vpc,compute,database,kubernetes,storage \
        --environment production \
        --project myapp \
        --region us-east-1 \
        --output ./infrastructure/
"""

import argparse
import os


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


# ── AWS Resources ──────────────────────────────────────────────

def aws_versions():
    return """terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
"""

def aws_backend(env, project, region):
    return f"""terraform {{
  backend "s3" {{
    bucket         = "{project}-terraform-state"
    key            = "{env}/terraform.tfstate"
    region         = "{region}"
    dynamodb_table = "{project}-terraform-locks"
    encrypt        = true
  }}
}}
"""

def aws_provider(region, env, project):
    return f"""provider "aws" {{
  region = "{region}"
  default_tags {{
    tags = {{
      Environment = "{env}"
      Project     = "{project}"
      ManagedBy   = "terraform"
    }}
  }}
}}
"""

def aws_vpc(env, project):
    return f"""# VPC Module
module "vpc" {{
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "{project}-{env}"
  cidr = var.vpc_cidr

  azs             = var.azs
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs

  enable_nat_gateway   = {"true" if env == "production" else "false"}
  single_nat_gateway   = {"false" if env == "production" else "true"}
  enable_dns_hostnames = true
  enable_dns_support   = true

  public_subnet_tags = {{
    "kubernetes.io/role/elb" = 1
  }}
  private_subnet_tags = {{
    "kubernetes.io/role/internal-elb" = 1
  }}

  tags = {{
    Name = "{project}-{env}-vpc"
  }}
}}
"""

def aws_rds(env, project):
    return f"""# RDS PostgreSQL
resource "aws_db_subnet_group" "main" {{
  name       = "{project}-{env}"
  subnet_ids = module.vpc.private_subnets
  tags       = {{ Name = "{project}-{env}-db-subnet" }}
}}

resource "aws_security_group" "db" {{
  name   = "{project}-{env}-db"
  vpc_id = module.vpc.vpc_id

  ingress {{
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    cidr_blocks     = module.vpc.private_subnets_cidr_blocks
    description     = "PostgreSQL from private subnets"
  }}

  tags = {{ Name = "{project}-{env}-db-sg" }}
}}

resource "aws_db_instance" "main" {{
  identifier     = "{project}-{env}"
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

  multi_az               = {"true" if env == "production" else "false"}
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]

  backup_retention_period = {"7" if env == "production" else "1"}
  deletion_protection     = {"true" if env == "production" else "false"}
  skip_final_snapshot     = {"false" if env == "production" else "true"}

  performance_insights_enabled = true

  tags = {{ Name = "{project}-{env}-postgres" }}
}}
"""

def aws_eks(env, project):
    return f"""# EKS Cluster
module "eks" {{
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "{project}-{env}"
  cluster_version = "1.31"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets

  cluster_endpoint_public_access = true
  enable_irsa                    = true

  eks_managed_node_groups = {{
    general = {{
      instance_types = var.eks_instance_types
      min_size       = var.eks_min_nodes
      max_size       = var.eks_max_nodes
      desired_size   = var.eks_desired_nodes

      labels = {{ role = "general" }}
    }}
  }}

  cluster_addons = {{
    coredns    = {{ most_recent = true }}
    kube-proxy = {{ most_recent = true }}
    vpc-cni    = {{ most_recent = true }}
  }}

  tags = {{ Name = "{project}-{env}-eks" }}
}}
"""

def aws_s3(env, project):
    return f"""# S3 Bucket
resource "aws_s3_bucket" "main" {{
  bucket = "{project}-{env}-assets"
  tags   = {{ Name = "{project}-{env}-assets" }}
}}

resource "aws_s3_bucket_versioning" "main" {{
  bucket = aws_s3_bucket.main.id
  versioning_configuration {{ status = "Enabled" }}
}}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {{
  bucket = aws_s3_bucket.main.id
  rule {{
    apply_server_side_encryption_by_default {{
      sse_algorithm = "aws:kms"
    }}
  }}
}}

resource "aws_s3_bucket_public_access_block" "main" {{
  bucket                  = aws_s3_bucket.main.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}
"""

def aws_variables(env, project, region):
    return f"""variable "vpc_cidr" {{
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}}

variable "azs" {{
  description = "Availability zones"
  type        = list(string)
  default     = ["{region}a", "{region}b", "{region}c"]
}}

variable "private_subnet_cidrs" {{
  type    = list(string)
  default = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}}

variable "public_subnet_cidrs" {{
  type    = list(string)
  default = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}}

variable "db_instance_class" {{
  type    = string
  default = "{"db.r6g.xlarge" if env == "production" else "db.t4g.medium"}"
}}

variable "db_storage" {{
  type    = number
  default = {"100" if env == "production" else "20"}
}}

variable "db_name" {{
  type    = string
  default = "{project.replace('-', '_')}"
}}

variable "db_username" {{
  type    = string
  default = "admin"
}}

variable "db_password" {{
  type      = string
  sensitive = true
}}

variable "eks_instance_types" {{
  type    = list(string)
  default = ["m6i.xlarge"]
}}

variable "eks_min_nodes" {{
  type    = number
  default = {"3" if env == "production" else "1"}
}}

variable "eks_max_nodes" {{
  type    = number
  default = {"10" if env == "production" else "3"}
}}

variable "eks_desired_nodes" {{
  type    = number
  default = {"3" if env == "production" else "2"}
}}
"""

def aws_outputs():
    return """output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnet_ids" {
  value = module.vpc.private_subnets
}

output "public_subnet_ids" {
  value = module.vpc.public_subnets
}
"""


# ── GCP Resources ──────────────────────────────────────────────

def gcp_provider(region, project_id, env):
    return f"""terraform {{
  required_version = ">= 1.7.0"
  required_providers {{
    google = {{
      source  = "hashicorp/google"
      version = "~> 5.0"
    }}
  }}
  backend "gcs" {{
    bucket = "{project_id}-terraform-state"
    prefix = "{env}"
  }}
}}

provider "google" {{
  project = "{project_id}"
  region  = "{region}"
}}
"""

def gcp_vpc(env, project):
    return f"""resource "google_compute_network" "vpc" {{
  name                    = "{project}-{env}"
  auto_create_subnetworks = false
}}

resource "google_compute_subnetwork" "subnet" {{
  name          = "{project}-{env}-subnet"
  ip_cidr_range = "10.0.0.0/20"
  region        = var.region
  network       = google_compute_network.vpc.id

  secondary_ip_range {{
    range_name    = "pods"
    ip_cidr_range = "10.1.0.0/16"
  }}
  secondary_ip_range {{
    range_name    = "services"
    ip_cidr_range = "10.2.0.0/20"
  }}
}}

resource "google_compute_router" "router" {{
  name    = "{project}-{env}-router"
  region  = var.region
  network = google_compute_network.vpc.id
}}

resource "google_compute_router_nat" "nat" {{
  name                               = "{project}-{env}-nat"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}}
"""


# ── Azure Resources ────────────────────────────────────────────

def azure_provider(region, env, project):
    return f"""terraform {{
  required_version = ">= 1.7.0"
  required_providers {{
    azurerm = {{
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }}
  }}
  backend "azurerm" {{
    resource_group_name  = "{project}-terraform-rg"
    storage_account_name = "{project.replace('-', '')}tfstate"
    container_name       = "tfstate"
    key                  = "{env}.terraform.tfstate"
  }}
}}

provider "azurerm" {{
  features {{}}
}}

resource "azurerm_resource_group" "main" {{
  name     = "{project}-{env}-rg"
  location = "{region}"
  tags = {{
    Environment = "{env}"
    Project     = "{project}"
    ManagedBy   = "terraform"
  }}
}}
"""

def azure_vnet(env, project):
    return f"""resource "azurerm_virtual_network" "main" {{
  name                = "{project}-{env}-vnet"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = ["10.0.0.0/16"]
}}

resource "azurerm_subnet" "private" {{
  name                 = "private"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}}

resource "azurerm_subnet" "public" {{
  name                 = "public"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.101.0/24"]
}}
"""


# ── Generator ──────────────────────────────────────────────

REGION_DEFAULTS = {"aws": "us-east-1", "gcp": "us-central1", "azure": "eastus"}

def generate_terraform(provider, resources, env, project, region, output_dir):
    res_set = set(resources.split(","))
    base = os.path.join(output_dir, "environments", env)
    region = region or REGION_DEFAULTS.get(provider, "us-east-1")

    print(f"\n🏗️  Generating Terraform for {provider.upper()} ({env})\n")

    if provider == "aws":
        create_file(os.path.join(base, "versions.tf"), aws_versions())
        create_file(os.path.join(base, "backend.tf"), aws_backend(env, project, region))
        create_file(os.path.join(base, "provider.tf"), aws_provider(region, env, project))
        create_file(os.path.join(base, "variables.tf"), aws_variables(env, project, region))
        create_file(os.path.join(base, "outputs.tf"), aws_outputs())

        main_content = ""
        if "vpc" in res_set:
            main_content += aws_vpc(env, project)
        if "database" in res_set:
            main_content += "\n" + aws_rds(env, project)
        if "kubernetes" in res_set:
            main_content += "\n" + aws_eks(env, project)
        if "storage" in res_set:
            main_content += "\n" + aws_s3(env, project)

        if main_content:
            create_file(os.path.join(base, "main.tf"), main_content)

        # tfvars
        create_file(os.path.join(base, "terraform.tfvars"), f"""# {env} environment variables
# db_password = "" # Set via TF_VAR_db_password or -var
""")

    elif provider == "gcp":
        gcp_project_id = f"{project}-{env}"
        create_file(os.path.join(base, "provider.tf"), gcp_provider(region, gcp_project_id, env))
        main_content = ""
        if "vpc" in res_set:
            main_content += gcp_vpc(env, project)
        if main_content:
            create_file(os.path.join(base, "main.tf"), main_content)
        create_file(os.path.join(base, "variables.tf"), f'variable "region" {{\n  default = "{region}"\n}}\n')

    elif provider == "azure":
        create_file(os.path.join(base, "provider.tf"), azure_provider(region, env, project))
        main_content = ""
        if "vpc" in res_set:
            main_content += azure_vnet(env, project)
        if main_content:
            create_file(os.path.join(base, "main.tf"), main_content)

    # Generate .terraform-version
    create_file(os.path.join(output_dir, ".terraform-version"), "1.7.0\n")

    # Generate .gitignore
    create_file(os.path.join(output_dir, ".gitignore"), """# Terraform
.terraform/
*.tfstate
*.tfstate.backup
*.tfplan
.terraform.lock.hcl
crash.log
override.tf
override.tf.json
*_override.tf
*.auto.tfvars
""")

    print(f"\n✅ Terraform config generated at: {base}/")
    print(f"   Provider: {provider.upper()}")
    print(f"   Resources: {resources}")
    print(f"   Environment: {env}")
    print(f"\n   Next steps:")
    print(f"   1. cd {base}")
    print(f"   2. terraform init")
    print(f"   3. terraform plan")


def main():
    parser = argparse.ArgumentParser(description="Generate Terraform Configuration")
    parser.add_argument("--provider", choices=["aws", "gcp", "azure"], required=True)
    parser.add_argument("--resources", default="vpc,database,kubernetes,storage",
                        help="Comma-separated: vpc,compute,database,kubernetes,storage")
    parser.add_argument("--environment", default="production")
    parser.add_argument("--project", default="myapp")
    parser.add_argument("--region", default=None)
    parser.add_argument("--output", default="./infrastructure")
    args = parser.parse_args()

    generate_terraform(args.provider, args.resources, args.environment,
                       args.project, args.region, args.output)


if __name__ == "__main__":
    main()

```
