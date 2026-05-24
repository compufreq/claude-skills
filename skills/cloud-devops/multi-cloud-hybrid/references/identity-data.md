# Cross-Cloud Identity & Data Reference

## Table of Contents
1. Identity Federation
2. Cross-Cloud IAM
3. Data Replication Patterns
4. Global DNS Strategy

---

## 1. Identity Federation

### Architecture: Single IdP, Multiple Clouds
```
                   ┌─────────────────┐
                   │  Identity Provider│
                   │  (Okta / Azure AD │
                   │   / Google Workspace)│
                   └────┬───────┬────┘
                        │       │
                  SAML/OIDC   SAML/OIDC
                        │       │
                   ┌────▼──┐ ┌──▼─────┐
                   │  AWS  │ │ Azure  │
                   │  IAM  │ │  AD    │
                   └───────┘ └────────┘
```

### AWS: SAML Federation with External IdP
```hcl
resource "aws_iam_saml_provider" "okta" {
  name                   = "okta"
  saml_metadata_document = file("${path.module}/okta-metadata.xml")
}

resource "aws_iam_role" "federated_admin" {
  name = "FederatedAdmin"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Federated = aws_iam_saml_provider.okta.arn }
      Action = "sts:AssumeRoleWithSAML"
      Condition = {
        StringEquals = {
          "SAML:aud" = "https://signin.aws.amazon.com/saml"
        }
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "admin" {
  role       = aws_iam_role.federated_admin.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}
```

### AWS: OIDC Federation (for CI/CD)
```hcl
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

resource "aws_iam_role" "github_actions" {
  name = "GitHubActionsRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Federated = aws_iam_openid_connect_provider.github.arn }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringLike = {
          "token.actions.githubusercontent.com:sub" = "repo:myorg/*:ref:refs/heads/main"
        }
      }
    }]
  })
}
```

### Azure AD as Central IdP
```hcl
# Azure AD App Registration for AWS SSO
resource "azuread_application" "aws_sso" {
  display_name = "AWS SSO"
  identifier_uris = ["https://signin.aws.amazon.com/saml"]

  web {
    redirect_uris = ["https://signin.aws.amazon.com/saml"]
  }
}

resource "azuread_service_principal" "aws_sso" {
  client_id = azuread_application.aws_sso.client_id
}

# Azure AD Groups → AWS Roles mapping
resource "azuread_group" "aws_admins" {
  display_name     = "AWS-Admins"
  security_enabled = true
}

resource "azuread_group" "aws_developers" {
  display_name     = "AWS-Developers"
  security_enabled = true
}
```

### Cross-Cloud Service Identity

| Pattern | How | Use Case |
|---------|-----|---------|
| **Workload Identity** | K8s SA → cloud IAM role | Pods accessing cloud services |
| **AWS IRSA** | EKS ServiceAccount → IAM Role | AWS workloads |
| **Azure Workload Identity** | AKS pod → Azure AD MI | Azure workloads |
| **SPIFFE/SPIRE** | Cross-cloud workload identity | Multi-cloud service mesh |

### SPIFFE (Cross-Cloud Workload Identity)
```
                    SPIRE Server
                   ╱            ╲
            SPIRE Agent      SPIRE Agent
            (AWS node)       (Azure node)
                │                │
            Workload A       Workload B
            spiffe://        spiffe://
            example.com/     example.com/
            aws/prod/api     azure/prod/db
                │                │
                └── mTLS ────────┘
                (cross-cloud, no passwords)
```

---

## 2. Cross-Cloud IAM

### Least Privilege Across Clouds

| Principle | AWS Implementation | Azure Implementation |
|-----------|-------------------|---------------------|
| No permanent admin keys | IAM Identity Center (SSO) | Azure AD PIM (just-in-time) |
| Service accounts scoped | IAM Roles with resource ARNs | Managed Identity + RBAC |
| MFA everywhere | IAM MFA policy | Conditional Access |
| Audit all access | CloudTrail | Activity Log |
| Automated review | Access Analyzer | Access Reviews |

### Cross-Cloud Access Pattern
```
Scenario: Lambda needs to read from Azure Blob Storage

AWS Lambda
  → Assumes IAM role (IRSA or execution role)
  → Calls STS to get temporary credentials
  → Exchanges AWS token for Azure AD token (via OIDC federation)
  → Accesses Azure Blob with Azure AD token

Implementation:
  1. Register AWS as external IdP in Azure AD
  2. Create Azure AD App with Blob Reader permissions
  3. Configure federated credential (trust AWS OIDC)
  4. Lambda code exchanges AWS token for Azure token
```

---

## 3. Data Replication Patterns

### Pattern Selection

| Pattern | Consistency | Latency | Complexity | Use Case |
|---------|-----------|---------|-----------|---------|
| **Active-Passive** | Strong (one writer) | High (async) | Low | DR |
| **Active-Active** | Eventual | Medium | High | Multi-region |
| **CQRS** | Eventual (reads) | Low | Medium | Read-heavy |
| **Event Sourcing** | Eventual | Medium | High | Audit, replay |
| **ETL/Batch** | Eventual (hours) | Very High | Low | Analytics |

### Active-Passive (Cross-Cloud DR)
```
AWS (Primary)                   Azure (DR)
┌──────────────┐               ┌──────────────┐
│  RDS Primary │──async rep──→│  Azure SQL    │
│  (writes)    │              │  (read-only)  │
│              │              │               │
│  S3 bucket   │──S3→Blob───→│  Blob Storage │
│              │  replication │               │
└──────────────┘               └──────────────┘
```

### Event-Based Replication
```
AWS                                    Azure
┌──────────┐    ┌──────────┐          ┌──────────┐
│ DynamoDB │──→│ Stream   │──Lambda─→│ Event Hub│──Function──→ Cosmos DB
│          │    │          │  (sync)   │          │  (process)
└──────────┘    └──────────┘          └──────────┘
```

### Data Sovereignty Considerations
```
EU Data:
  Primary: Azure (West Europe) — EU regulations met
  Replicated metadata only to: AWS (us-east-1) — no PII

US Data:
  Primary: AWS (us-east-1)
  No replication to EU required

Implementation:
  - Tag data with region/jurisdiction
  - Enforce replication rules based on tags
  - Audit cross-region data flow
  - Use encryption with region-specific keys
```

### Cross-Cloud Data Transfer Cost

| From | To | Cost (per GB) | Optimization |
|------|-----|--------------|-------------|
| AWS → Internet | Any | $0.09 | Use VPN/DX (cheaper) |
| Azure → Internet | Any | $0.087 | Use ER (cheaper) |
| AWS → Azure (VPN) | | $0.02-0.09 | Compress, batch |
| Within AWS region | | Free | Keep data in-region |
| Within Azure region | | Free | Keep data in-region |

**Rule:** Minimize cross-cloud data transfer. Process data where it lives.

---

## 4. Global DNS Strategy

### Option 1: Cloudflare (Recommended for Multi-Cloud)
```
Cloudflare DNS (cloud-agnostic)
  app.example.com → Load Balance
    ├── AWS ALB (us-east-1) — weight 50, health check
    ├── Azure Front Door (westeurope) — weight 50, health check
    └── Failover: if AWS down → 100% Azure
```

Benefits: cloud-agnostic, global anycast, DDoS protection, analytics.

### Option 2: Route53 with Failover to Azure
```hcl
# Primary → AWS
resource "aws_route53_record" "primary" {
  zone_id        = aws_route53_zone.main.zone_id
  name           = "app.example.com"
  type           = "A"
  set_identifier = "aws-primary"
  failover_routing_policy { type = "PRIMARY" }
  health_check_id = aws_route53_health_check.aws.id
  alias {
    name    = aws_lb.app.dns_name
    zone_id = aws_lb.app.zone_id
    evaluate_target_health = true
  }
}

# Secondary → Azure
resource "aws_route53_record" "secondary" {
  zone_id        = aws_route53_zone.main.zone_id
  name           = "app.example.com"
  type           = "CNAME"
  set_identifier = "azure-dr"
  failover_routing_policy { type = "SECONDARY" }
  ttl     = 60
  records = ["app-dr.azurefd.net"]
}
```

### Internal DNS (Cross-Cloud)
```
Scenario: Services in AWS need to resolve services in Azure

AWS:
  Route53 Resolver → Forward "azure.internal" queries → Azure DNS (via VPN)

Azure:
  Azure DNS Private Resolver → Forward "aws.internal" queries → Route53 (via VPN)

Both:
  Service discovery within K8s (CoreDNS) handles cluster-local
  Cross-cluster: use external DNS names or service mesh
```

### DNS Monitoring
```
Monitor for all cross-cloud DNS:
  - Resolution time (should be < 50ms)
  - Resolution failures (should be 0)
  - Health check status per endpoint
  - Failover events (alert on every failover)
  - TTL compliance (actual vs configured)
```
