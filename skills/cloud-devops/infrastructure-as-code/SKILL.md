---
name: infrastructure-as-code
description: >-
  Terraform, CloudFormation, and Ansible for multi-cloud infrastructure. Use when the user mentions Terraform, HCL, terraform plan/apply, tfstate, modules, CloudFormation, CFN, AWS SAM, nested stacks, Ansible, playbooks, roles, infrastructure as code, IaC, state management, drift detection, Checkov, tflint, Terratest, OPA, or provisioning cloud resources in code. Complements container-orchestration and ci-cd-pipelines.
---

# Infrastructure as Code

A production-grade skill for defining, provisioning, and managing cloud infrastructure using
Terraform, CloudFormation, and Ansible across AWS, GCP, and Azure.

## Quick Reference

| Tool | Config Language | State | Best For | Reference |
|------|----------------|-------|----------|-----------|
| Terraform | HCL | Remote (S3, GCS, Blob) | Multi-cloud, modules | `references/terraform.md` |
| CloudFormation | YAML/JSON | AWS-managed | AWS-native, deep integration | `references/cloudformation.md` |
| Ansible | YAML | Stateless (idempotent) | Configuration mgmt, provisioning | `references/ansible.md` |
| Testing | Various | N/A | Validation, security, compliance | `references/testing-validation.md` |

## Core Workflow

1. **Identify the tool:**
   - Multi-cloud or modular infrastructure → Terraform
   - AWS-only with deep service integration → CloudFormation
   - Server configuration and orchestration → Ansible
   - Often used together: Terraform (infra) + Ansible (config)

2. **Read relevant reference** before generating code

3. **Generate configurations** using `scripts/generate_terraform.py`

---

## Tool Selection Guide

| Criteria | Terraform | CloudFormation | Ansible |
|----------|-----------|---------------|---------|
| Multi-cloud | ✅ Native | ❌ AWS only | ✅ Any SSH/API target |
| State management | Remote backend | AWS-managed | Stateless |
| Drift detection | `terraform plan` | Drift detection | Re-run playbook |
| Modularity | Modules + Registry | Nested stacks | Roles + Galaxy |
| Learning curve | Medium | Medium | Low-Medium |
| Ecosystem | Huge (providers, modules) | AWS-only | Huge (Galaxy roles) |
| Declarative | Yes | Yes | Procedural (task-based) |
| Rollback | Manual (`terraform apply` old state) | Automatic | Re-run previous playbook |
| Testing | Terratest, Checkov, tflint | cfn-lint, taskcat | Molecule, ansible-lint |
| Best for | Infrastructure provisioning | AWS infrastructure | Configuration management |

## Combination Patterns

```
Pattern 1: Terraform + Ansible
  Terraform creates infrastructure (VPCs, VMs, databases)
  → Ansible configures the created infrastructure (packages, services, users)

Pattern 2: Terraform only
  Terraform creates + configures using user_data, cloud-init, or provisioners
  Best for immutable infrastructure (containers, serverless)

Pattern 3: CloudFormation + Ansible
  CFN creates AWS infrastructure
  → Ansible configures EC2 instances via SSM or SSH

Pattern 4: Terraform + CloudFormation
  Terraform for multi-cloud/shared patterns
  CFN for AWS-specific features (SAM, Step Functions, custom resources)
```

---

## Project Structure

### Terraform
```
infrastructure/
├── modules/                    # Reusable modules
│   ├── networking/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── compute/
│   ├── database/
│   └── kubernetes/
├── environments/               # Environment-specific configs
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   └── production/
├── global/                     # Shared resources (IAM, DNS)
│   ├── iam/
│   └── dns/
└── scripts/
    └── init.sh                 # Backend initialization
```

### CloudFormation
```
infrastructure/
├── templates/
│   ├── vpc.yaml
│   ├── ecs-cluster.yaml
│   ├── rds.yaml
│   └── nested/
│       ├── security-groups.yaml
│       └── iam-roles.yaml
├── parameters/
│   ├── dev.json
│   ├── staging.json
│   └── production.json
├── scripts/
│   ├── deploy.sh
│   └── validate.sh
└── taskcat/
    └── .taskcat.yml
```

### Ansible
```
ansible/
├── inventory/
│   ├── dev/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   ├── staging/
│   └── production/
├── playbooks/
│   ├── site.yml
│   ├── webservers.yml
│   └── databases.yml
├── roles/
│   ├── common/
│   │   ├── tasks/main.yml
│   │   ├── handlers/main.yml
│   │   ├── templates/
│   │   ├── files/
│   │   ├── vars/main.yml
│   │   └── defaults/main.yml
│   ├── nginx/
│   └── app/
├── group_vars/
│   └── all.yml
├── ansible.cfg
└── requirements.yml
```

---

## Scripts

### generate_terraform.py
Generate Terraform modules and environment configurations for common patterns.

```bash
python scripts/generate_terraform.py \
  --provider aws|gcp|azure \
  --resources vpc,compute,database,kubernetes,storage \
  --environment production \
  --output ./infrastructure/
```

---

## Best Practices

1. **Version pin everything** — providers, modules, Terraform itself
2. **Remote state with locking** — S3+DynamoDB, GCS, Azure Blob
3. **One module per concern** — networking, compute, database, etc.
4. **Environment parity** — same modules, different variables per env
5. **Least privilege IAM** — IaC service accounts get only what's needed
6. **Plan before apply** — always review `terraform plan` output
7. **Code review IaC** — infrastructure changes go through PR review
8. **Test infrastructure** — Checkov for security, tflint for lint, Terratest for integration
9. **Tag everything** — environment, team, cost center, managed-by
10. **Encrypt state** — state files contain sensitive data, encrypt at rest



---
