# Disaster Recovery Reference

## Table of Contents
1. RPO & RTO
2. DR Patterns
3. AWS DR Implementation
4. Azure DR Implementation
5. DR Testing
6. Business Continuity Planning

---

## 1. RPO & RTO

| Term | Definition | Question |
|------|-----------|---------|
| **RPO** (Recovery Point Objective) | Max acceptable data loss | "How much data can we afford to lose?" |
| **RTO** (Recovery Time Objective) | Max acceptable downtime | "How long can we be down?" |

### RPO/RTO Targets by Tier

| Tier | RPO | RTO | Example | DR Pattern |
|------|-----|-----|---------|-----------|
| **Tier 1** (Critical) | 0 | < 15 min | Payment, auth | Active-active |
| **Tier 2** (Important) | < 1 hour | < 1 hour | Core API, CRM | Warm standby |
| **Tier 3** (Standard) | < 4 hours | < 4 hours | Internal tools | Pilot light |
| **Tier 4** (Low) | < 24 hours | < 24 hours | Dev, batch jobs | Backup & restore |

---

## 2. DR Patterns

### Pattern Comparison

```
Cost & Complexity ──────────────────────────────►
Recovery Speed  ◄──────────────────────────────

┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Backup & │  │  Pilot   │  │  Warm    │  │ Active-  │
│ Restore  │  │  Light   │  │ Standby  │  │ Active   │
│          │  │          │  │          │  │          │
│ RTO: hrs │  │ RTO: min │  │ RTO: min │  │ RTO: sec │
│ RPO: hrs │  │ RPO: min │  │ RPO: sec │  │ RPO: 0   │
│ Cost: $  │  │ Cost: $$ │  │Cost: $$$ │  │Cost: $$$$│
└──────────┘  └──────────┘  └──────────┘  └──────────┘
```

### Backup & Restore
```
Primary Region:  Running (full stack)
DR Region:       Backups stored (S3 CRR / Azure GRS)

Failover:
1. Restore infrastructure from IaC (Terraform)  ~30 min
2. Restore data from latest backup              ~1-4 hours
3. Update DNS to point to DR region             ~5 min
4. Verify and accept traffic                    ~15 min
Total RTO: 2-6 hours
```

### Pilot Light
```
Primary Region:  Running (full stack)
DR Region:       Core infrastructure running (DB replica, minimal compute)
                 App servers OFF or at minimum

Failover:
1. Scale up DR compute (ASG/VMSS desired count)  ~5 min
2. Verify DB replica is caught up                ~1-5 min
3. Promote DB replica to primary                 ~2-5 min
4. Update DNS / failover routing                 ~5 min
Total RTO: 15-30 minutes
```

### Warm Standby
```
Primary Region:  Running (full stack, full capacity)
DR Region:       Running (reduced capacity — e.g., 30% of production)
                 DB with continuous replication

Failover:
1. Scale up DR to full capacity                  ~2-5 min
2. Promote DB replica                            ~1-2 min
3. DNS failover (Route53/Traffic Manager)         ~60 sec
Total RTO: 5-10 minutes
```

### Active-Active (Multi-Region)
```
Region A:  Running (full stack, serving users)
Region B:  Running (full stack, serving users)
           Global load balancer distributes traffic

Failover:
1. Global LB detects Region A failure             ~30 sec
2. Traffic automatically routes to Region B        ~0 sec
3. Region B absorbs all traffic                    ~0 sec
Total RTO: < 1 minute (often automatic)
```

---

## 3. AWS DR Implementation

### Cross-Region Database Replication
```hcl
# Aurora Global Database (RPO < 1 second)
resource "aws_rds_global_cluster" "main" {
  global_cluster_identifier = "${var.project}-global"
  engine                    = "aurora-postgresql"
  engine_version            = "16.1"
  storage_encrypted         = true
}

# Primary cluster (us-east-1)
resource "aws_rds_cluster" "primary" {
  provider                  = aws.primary
  cluster_identifier        = "${var.project}-primary"
  global_cluster_identifier = aws_rds_global_cluster.main.id
  engine                    = "aurora-postgresql"
  engine_version            = "16.1"
  master_username           = var.db_username
  master_password           = var.db_password
  db_subnet_group_name      = aws_db_subnet_group.primary.name
}

# Secondary cluster (eu-west-1)
resource "aws_rds_cluster" "secondary" {
  provider                  = aws.secondary
  cluster_identifier        = "${var.project}-secondary"
  global_cluster_identifier = aws_rds_global_cluster.main.id
  engine                    = "aurora-postgresql"
  engine_version            = "16.1"
  db_subnet_group_name      = aws_db_subnet_group.secondary.name
  depends_on                = [aws_rds_cluster.primary]
}
```

### Route 53 Failover
```hcl
resource "aws_route53_health_check" "primary" {
  fqdn              = "primary-alb.us-east-1.elb.amazonaws.com"
  port               = 443
  type               = "HTTPS"
  resource_path      = "/health"
  failure_threshold  = 3
  request_interval   = 10
}

resource "aws_route53_record" "failover_primary" {
  zone_id        = aws_route53_zone.main.zone_id
  name           = "app.example.com"
  type           = "A"
  set_identifier = "primary"

  failover_routing_policy { type = "PRIMARY" }
  health_check_id = aws_route53_health_check.primary.id

  alias {
    name                   = aws_lb.primary.dns_name
    zone_id                = aws_lb.primary.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "failover_secondary" {
  zone_id        = aws_route53_zone.main.zone_id
  name           = "app.example.com"
  type           = "A"
  set_identifier = "secondary"

  failover_routing_policy { type = "SECONDARY" }

  alias {
    name                   = aws_lb.secondary.dns_name
    zone_id                = aws_lb.secondary.zone_id
    evaluate_target_health = true
  }
}
```

### S3 Cross-Region Replication
```hcl
resource "aws_s3_bucket_replication_configuration" "main" {
  bucket = aws_s3_bucket.primary.id
  role   = aws_iam_role.replication.arn

  rule {
    id     = "replicate-all"
    status = "Enabled"

    destination {
      bucket        = aws_s3_bucket.dr.arn
      storage_class = "STANDARD_IA"
    }
  }
}
```

---

## 4. Azure DR Implementation

### Azure Site Recovery
```hcl
resource "azurerm_site_recovery_replicated_vm" "vm_replication" {
  name                                      = "${var.project}-vm-replication"
  resource_group_name                       = azurerm_resource_group.dr.name
  recovery_vault_name                       = azurerm_recovery_services_vault.dr.name
  source_recovery_fabric_name               = azurerm_site_recovery_fabric.primary.name
  source_vm_id                              = azurerm_linux_virtual_machine.primary.id
  recovery_replication_policy_id            = azurerm_site_recovery_replication_policy.main.id
  source_recovery_protection_container_name = azurerm_site_recovery_protection_container.primary.name
  target_resource_group_id                  = azurerm_resource_group.dr.id
  target_recovery_fabric_id                 = azurerm_site_recovery_fabric.dr.id
  target_recovery_protection_container_id   = azurerm_site_recovery_protection_container.dr.id
}
```

### Azure SQL Failover Group
```hcl
resource "azurerm_mssql_failover_group" "main" {
  name      = "${var.project}-fog"
  server_id = azurerm_mssql_server.primary.id

  partner_server {
    id = azurerm_mssql_server.secondary.id
  }

  databases = [azurerm_mssql_database.main.id]

  read_write_endpoint_failover_policy {
    mode          = "Automatic"
    grace_minutes = 60
  }

  readonly_endpoint_failover_policy_enabled = true
}
```

### Traffic Manager Failover
```hcl
resource "azurerm_traffic_manager_profile" "dr" {
  name                   = "${var.project}-dr-tm"
  resource_group_name    = azurerm_resource_group.global.name
  traffic_routing_method = "Priority"

  dns_config {
    relative_name = var.project
    ttl           = 60
  }

  monitor_config {
    protocol = "HTTPS"
    port     = 443
    path     = "/health"
  }
}

resource "azurerm_traffic_manager_azure_endpoint" "primary" {
  name               = "primary"
  profile_id         = azurerm_traffic_manager_profile.dr.id
  target_resource_id = azurerm_public_ip.primary.id
  priority           = 1
}

resource "azurerm_traffic_manager_azure_endpoint" "secondary" {
  name               = "secondary"
  profile_id         = azurerm_traffic_manager_profile.dr.id
  target_resource_id = azurerm_public_ip.secondary.id
  priority           = 2
}
```

---

## 5. DR Testing

### Test Types

| Test | Frequency | Impact | Duration |
|------|-----------|--------|----------|
| **Tabletop** | Quarterly | None | 1-2 hours |
| **Walkthrough** | Semi-annual | None | 2-4 hours |
| **Simulation** | Annual | Minimal | 4-8 hours |
| **Full failover** | Annual | Some (planned) | 2-4 hours |

### DR Test Runbook Template
```markdown
# DR Test: [Service Name] Failover

## Pre-Test Checklist
- [ ] Notify stakeholders of planned test window
- [ ] Verify DR infrastructure is running
- [ ] Confirm monitoring is active in both regions
- [ ] Document current primary region metrics (baseline)
- [ ] Prepare rollback plan

## Test Steps
1. Initiate failover (Route 53 / Traffic Manager / DB promotion)
2. Verify traffic is flowing to DR region
3. Run smoke tests against DR endpoints
4. Monitor error rates and latency
5. Verify data consistency
6. [If full test] Operate in DR mode for 1 hour
7. Initiate failback to primary

## Success Criteria
- [ ] RTO met: Failover completed within [X] minutes
- [ ] RPO met: Data loss within [X] minutes
- [ ] Error rate < 1% during and after failover
- [ ] All critical user journeys functional

## Post-Test
- [ ] Document actual RTO and RPO achieved
- [ ] Note any issues encountered
- [ ] Create action items for improvements
- [ ] Update runbooks with lessons learned
```

---

## 6. Business Continuity Planning

### BCP Components

| Component | Owner | Frequency |
|-----------|-------|-----------|
| Risk assessment | Security/Architecture | Annual |
| DR plan per service | Service team | Annual + changes |
| DR testing | SRE/Platform | Quarterly (tabletop), Annual (full) |
| Communication plan | Management | Annual |
| Vendor assessment | Procurement | Annual |
| Backup verification | SRE | Monthly |

### Service Classification

Classify every service into a tier (determines DR investment):

```
Tier 1 (Mission Critical)
  → Active-active or warm standby
  → RTO < 15 min, RPO ≈ 0
  → Examples: Authentication, payment processing, core API

Tier 2 (Business Critical)
  → Warm standby or pilot light
  → RTO < 1 hour, RPO < 1 hour
  → Examples: User-facing app, order processing, CRM

Tier 3 (Business Support)
  → Pilot light or backup/restore
  → RTO < 4 hours, RPO < 4 hours
  → Examples: Reporting, analytics, internal tools

Tier 4 (Non-Critical)
  → Backup/restore only
  → RTO < 24 hours, RPO < 24 hours
  → Examples: Development environments, archive systems
```



---
