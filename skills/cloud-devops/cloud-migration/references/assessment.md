# Migration Assessment Reference

## Table of Contents
1. Discovery & Inventory
2. Dependency Mapping
3. TCO Analysis
4. AWS & Azure Assessment Tools

---

## 1. Discovery & Inventory

### Application Inventory Template

| Field | Description | Example |
|-------|------------|---------|
| App Name | Application name | order-management |
| Owner | Team/individual responsible | Backend team |
| Business Function | What it does | Processes customer orders |
| Users | Number of users | 500 internal, 50K external |
| Criticality | Tier 1-4 | Tier 2 (Business Critical) |
| Current Hosting | Where it runs today | VMware, DC-East |
| OS | Operating system | Ubuntu 22.04 |
| Runtime | Language/framework | Java 17 / Spring Boot 3 |
| Database | Database engine + version | PostgreSQL 15 (self-managed) |
| Storage | Storage requirements | 200 GB data, 50 GB logs |
| CPU | CPU allocation | 8 vCPU |
| Memory | RAM allocation | 16 GB |
| Peak CPU % | Peak utilization | 45% |
| Peak Memory % | Peak utilization | 60% |
| Network | Bandwidth needs | 100 Mbps avg, 500 Mbps peak |
| Dependencies | What it depends on | Auth service, payment gateway, PostgreSQL |
| Dependents | What depends on it | Reporting service, mobile app |
| Compliance | Regulatory requirements | PCI DSS, SOC 2 |
| Data Classification | Sensitivity level | Confidential |
| Migration Strategy | Recommended R | Replatform (ECS + RDS) |
| Estimated Effort | Migration effort | 3 weeks |
| Migration Wave | Assigned wave | Wave 3 |

### Server Inventory (Infrastructure)

| Field | Description |
|-------|------------|
| Hostname | Server name |
| IP Address | Primary IP |
| OS | Operating system + version |
| vCPU / Cores | CPU allocation |
| RAM (GB) | Memory allocation |
| Disk (GB) | Total disk allocation |
| Avg CPU % | Average utilization (30 days) |
| Peak CPU % | Peak utilization |
| Avg Memory % | Average utilization |
| Network In/Out | Average throughput |
| Running Services | Applications on this server |
| Last Patched | Date of last OS update |

---

## 2. Dependency Mapping

### Dependency Discovery Methods

| Method | Tools | Effort | Accuracy |
|--------|-------|--------|----------|
| **Agent-based** | AWS Application Discovery, Azure Migrate appliance | Medium | High |
| **Agentless** | Network flow analysis, port scanning | Low | Medium |
| **Manual interview** | Architecture docs, team interviews | High | Medium |
| **Code analysis** | Static analysis of configs, connection strings | Medium | High |
| **Network monitoring** | VPC Flow Logs, packet capture | Low | High |

### Dependency Matrix

```
                App A   App B   App C   DB-1   Cache  Queue  External-API
App A             —      →       →       →      →             →
App B                    —               →      →      →
App C                           —        →             →
```

Legend: → = depends on (App A depends on App B)

### Migration Group Rules
1. Apps that depend on each other should migrate together
2. Shared databases are migration blockers — plan data migration carefully
3. External dependencies (SaaS, partner APIs) usually don't need migration
4. Identify circular dependencies — these need special handling

### Dependency Patterns

| Pattern | Challenge | Solution |
|---------|----------|---------|
| Shared database | Can't migrate apps independently | Replatform DB first, or use DB proxy |
| Tight coupling | Apps fail if dependency is unavailable | Add circuit breakers, migrate together |
| On-premises dependency | Cloud app needs on-premises service | VPN/Direct Connect, or migrate dependency first |
| Hardcoded IPs | Config points to specific servers | Use DNS names, service discovery |
| File shares | Multiple apps read/write same files | EFS/Azure Files, or object storage |

---

## 3. TCO Analysis

### TCO Comparison Template

| Cost Category | On-Premises (Annual) | Cloud (Annual) | Savings |
|-------------|---------------------|---------------|---------|
| **Compute** | | | |
| Servers (depreciation) | $ | EC2/VM cost | $ |
| Server maintenance | $ | Included | $ |
| Virtualization licenses | $ | Included | $ |
| **Storage** | | | |
| SAN/NAS (depreciation) | $ | S3/EBS/Blob cost | $ |
| Storage maintenance | $ | Included | $ |
| Backup infrastructure | $ | Backup service cost | $ |
| **Networking** | | | |
| Network equipment | $ | VPC/VNet cost | $ |
| Bandwidth | $ | Data transfer cost | $ |
| Load balancers | $ | ALB/App GW cost | $ |
| **Data Center** | | | |
| Facility (rent/own) | $ | N/A | $ |
| Power & cooling | $ | N/A | $ |
| Physical security | $ | N/A | $ |
| **People** | | | |
| System administrators | $ | Reduced (managed services) | $ |
| Network administrators | $ | Reduced | $ |
| Security team | $ | Shared responsibility | $ |
| **Software** | | | |
| OS licenses | $ | Included or BYOL | $ |
| Database licenses | $ | Included or BYOL | $ |
| Monitoring tools | $ | CloudWatch/Monitor | $ |
| **Total** | **$** | **$** | **$** |

### Hidden Costs to Include

| Often Missed | On-Premises | Cloud |
|-------------|------------|-------|
| DR infrastructure | 2x for active-passive | Pay for what you use |
| Dev/test environments | Always running | Schedule on/off (70% savings) |
| Capacity planning buffer | 30-40% over-provisioned | Auto-scaling |
| Procurement cycle | 3-6 months for hardware | Minutes to provision |
| End-of-life refresh | Every 3-5 years | Continuous |
| Compliance audits | Manual, expensive | Automated (Config, Policy) |

### Cloud Cost Estimation Tools
- **AWS**: AWS Pricing Calculator, Migration Evaluator (formerly TSO Logic)
- **Azure**: Azure Pricing Calculator, Azure Migrate (TCO calculator)
- **Third-party**: Flexera, CloudHealth, Apptio

---

## 4. AWS & Azure Assessment Tools

### AWS Discovery & Migration Tools

| Tool | Purpose | Method |
|------|---------|--------|
| **Migration Hub** | Central tracking dashboard | Aggregates all migration tools |
| **Application Discovery Service** | Inventory + dependencies | Agent or agentless |
| **Migration Evaluator** | TCO analysis | Collector agent |
| **Application Migration Service** | Rehost (lift & shift) | Agent-based replication |
| **DMS** | Database migration | Replication instance |
| **SCT** | Schema conversion | Analyzes + converts DDL |

### AWS Migration Hub Setup
```bash
# Enable Migration Hub in your primary region
aws migrationhub-config create-home-region-control --home-region us-east-1

# Import server inventory (from Discovery Service or manual CSV)
aws discovery start-data-collection-by-agent-ids --agent-ids agent-1 agent-2

# Track migration status
aws migrationhub list-migration-tasks
```

### Azure Migrate

| Tool | Purpose |
|------|---------|
| **Azure Migrate: Discovery** | Discover on-premises VMs, apps, DBs |
| **Azure Migrate: Assessment** | Readiness assessment + cost estimation |
| **Azure Migrate: Server Migration** | Rehost VMs to Azure |
| **Azure DMS** | Database migration |
| **App Service Migration Assistant** | Migrate .NET/Java web apps |
| **Data Box** | Offline data transfer (large volumes) |

### Azure Migrate Setup
```bash
# Create Azure Migrate project
az migrate project create \
  --name myapp-migration \
  --resource-group migration-rg \
  --location eastus

# Deploy Azure Migrate appliance
# Download OVA from Azure portal → deploy in VMware/Hyper-V
# Register appliance with your Azure Migrate project
```

### Assessment Output Example
```
Server: web-server-01
  Current: 8 vCPU, 16 GB RAM, 200 GB disk
  Avg CPU: 25%, Avg Memory: 40%
  
  AWS Recommendation:
    Right-sized: m6i.large (2 vCPU, 8 GB) — $70/mo
    On-Demand: $70/mo | 1yr RI: $45/mo | 3yr RI: $30/mo
    
  Azure Recommendation:
    Right-sized: Standard_D2s_v5 (2 vCPU, 8 GB) — $70/mo
    Pay-as-you-go: $70/mo | 1yr Reserved: $45/mo
    
  Migration Strategy: Rehost → optimize post-migration
```



---
