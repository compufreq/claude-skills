# Multi-Cloud Strategy Reference

## Table of Contents
1. When Multi-Cloud Makes Sense
2. Vendor Lock-In Analysis
3. Abstraction Layers
4. Cloud-Agnostic Tooling

---

## 1. When Multi-Cloud Makes Sense

| Reason | Valid? | Notes |
|--------|--------|-------|
| **Regulatory** — data must stay in region/cloud | ✅ Yes | GDPR, data sovereignty |
| **Best-of-breed** — specific service only on one cloud | ✅ Yes | But minimize cross-cloud coupling |
| **M&A** — acquired company uses different cloud | ✅ Yes | Common enterprise scenario |
| **DR** — survive entire cloud provider outage | ⚠️ Maybe | Very rare; multi-region usually sufficient |
| **Avoid lock-in** — negotiate better deals | ⚠️ Maybe | Cost of multi-cloud often exceeds savings |
| **"Because we should"** — no specific reason | ❌ No | Single cloud is simpler and cheaper |

### Anti-Patterns
- Running identical workloads on 2 clouds "just in case"
- Using lowest-common-denominator services to stay portable
- Building custom abstraction layers instead of using proven tools
- Multi-cloud without a dedicated platform team

---

## 2. Vendor Lock-In Analysis

### Lock-In Spectrum

| Service Type | Lock-In Risk | Portability Strategy |
|-------------|-------------|---------------------|
| **Compute (VMs)** | Low | Standard Linux, cloud-init |
| **Containers (K8s)** | Low | K8s is cloud-agnostic |
| **Object storage** | Low-Medium | S3 API is de facto standard |
| **Relational DB** | Medium | Use PostgreSQL/MySQL (portable engines) |
| **NoSQL DB** | High | DynamoDB/Cosmos are proprietary |
| **Serverless** | High | Lambda/Functions are cloud-specific |
| **AI/ML services** | High | Cloud-specific APIs |
| **IAM** | High | Cloud-specific identity systems |
| **Messaging** | Medium-High | SQS/EventBridge vs Service Bus |

### Mitigation Strategies

| Strategy | Effort | Effectiveness |
|----------|--------|--------------|
| **Use open standards** (K8s, PostgreSQL, Redis) | Low | High for compute/data |
| **Terraform for IaC** | Low | High for infrastructure |
| **Container workloads** | Medium | High for applications |
| **Hexagonal architecture** | Medium | High for application logic |
| **Crossplane** | High | Very high (full abstraction) |
| **Custom abstraction** | Very High | Varies (often over-engineered) |

### Hexagonal Architecture for Cloud Portability
```
                 ┌─────────────────────────┐
                 │    Business Logic        │
                 │    (cloud-agnostic)      │
                 └────┬──────────┬─────────┘
                      │          │
              ┌───────▼──┐  ┌───▼────────┐
              │ Port:    │  │ Port:      │
              │ Storage  │  │ Messaging  │
              └───┬──────┘  └────┬───────┘
                  │              │
          ┌───────┼──────┐  ┌───┼────────┐
          ▼       ▼      ▼  ▼   ▼        ▼
        S3     Blob    GCS  SQS  SvcBus  PubSub
       Adapter Adapter     Adapter Adapter
```

Application logic depends on interfaces (ports). Adapters implement them
per cloud. Switching clouds = swap adapters, not business logic.

---

## 3. Abstraction Layers

### Crossplane (Kubernetes-Native Multi-Cloud)

```yaml
# Define a cloud-agnostic "Database" resource
apiVersion: database.example.org/v1alpha1
kind: PostgreSQLInstance
metadata:
  name: my-database
spec:
  parameters:
    storageGB: 100
    version: "16"
    highAvailability: true
  compositionSelector:
    matchLabels:
      provider: aws    # Change to "azure" to switch clouds
---
# Crossplane Composition (AWS)
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: postgresql-aws
  labels:
    provider: aws
spec:
  compositeTypeRef:
    apiVersion: database.example.org/v1alpha1
    kind: PostgreSQLInstance
  resources:
    - name: rds-instance
      base:
        apiVersion: rds.aws.crossplane.io/v1alpha1
        kind: DBInstance
        spec:
          forProvider:
            engine: postgres
            dbInstanceClass: db.r6g.xlarge
            masterUsername: admin
            allocatedStorage: 100
            multiAZ: true
```

### Terraform Multi-Provider
```hcl
# Single codebase, multiple providers
terraform {
  required_providers {
    aws = { source = "hashicorp/aws"; version = "~> 5.0" }
    azurerm = { source = "hashicorp/azurerm"; version = "~> 3.0" }
  }
}

# Modules abstract cloud-specific details
module "primary_infra" {
  source   = "./modules/aws"
  providers = { aws = aws }
  environment = var.environment
}

module "dr_infra" {
  source   = "./modules/azure"
  providers = { azurerm = azurerm }
  environment = var.environment
}
```

### Pulumi Multi-Cloud (TypeScript)
```typescript
import * as aws from "@pulumi/aws";
import * as azure from "@pulumi/azure-native";

// AWS resources
const awsBucket = new aws.s3.Bucket("primary-data", {
  versioning: { enabled: true },
});

// Azure resources
const azureStorage = new azure.storage.StorageAccount("dr-data", {
  resourceGroupName: resourceGroup.name,
  kind: "StorageV2",
  sku: { name: "Standard_GRS" },
});

// Cross-cloud output
export const primaryBucket = awsBucket.bucket;
export const drStorage = azureStorage.name;
```

---

## 4. Cloud-Agnostic Tooling

| Category | Cloud-Agnostic Tool | Replaces |
|----------|-------------------|----------|
| **IaC** | Terraform, Pulumi, Crossplane | CloudFormation, ARM, Deployment Manager |
| **Containers** | Kubernetes (EKS/AKS/GKE) | ECS, Azure Container Instances |
| **CI/CD** | GitHub Actions, GitLab CI, Jenkins | CodePipeline, Azure DevOps Pipelines |
| **GitOps** | ArgoCD, Flux | — |
| **Monitoring** | Prometheus, Grafana, Datadog | CloudWatch, Azure Monitor |
| **Logging** | Loki, Elasticsearch, Datadog | CloudWatch Logs, Log Analytics |
| **Tracing** | Jaeger, OpenTelemetry | X-Ray, Application Insights |
| **Service Mesh** | Istio, Linkerd | App Mesh |
| **Secrets** | HashiCorp Vault | Secrets Manager, Key Vault |
| **DNS** | Cloudflare, NS1 | Route 53, Azure DNS |
| **Database** | PostgreSQL, MySQL, Redis | RDS, Azure SQL, ElastiCache |
