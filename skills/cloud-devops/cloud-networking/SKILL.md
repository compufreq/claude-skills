---
name: cloud-networking
description: >-
  VPC/VNet design, load balancing, DNS, CDN, transit gateways, and hybrid connectivity for AWS and Azure. Use when the user mentions VPC, VNet, subnet, CIDR, NAT gateway, security group, network ACL, NSG, ALB, NLB, CloudFront, Route53, Azure DNS, Transit Gateway, VPC peering, PrivateLink, private endpoint, hub-spoke, Direct Connect, ExpressRoute, or designing/troubleshooting cloud network infrastructure.
---

# Cloud Networking

A production-grade skill for designing and implementing cloud network infrastructure across
AWS and Azure, including VPC/VNet design, load balancing, DNS, CDN, and multi-cloud connectivity.

## Quick Reference

| Area | AWS | Azure | Reference |
|------|-----|-------|-----------|
| Virtual Network | VPC | VNet | `references/vpc-vnet.md` |
| Load Balancing | ALB, NLB, CloudFront | App Gateway, Front Door | `references/load-balancing.md` |
| DNS | Route 53 | Azure DNS | `references/dns-cdn.md` |
| Transit/Hybrid | Transit Gateway, Direct Connect | Virtual WAN, ExpressRoute | `references/transit-hybrid.md` |

## Network Architecture Patterns

### Single-Region Production
```
Internet
  │
  ▼
┌─── Public Subnets (3 AZs) ────────────┐
│  ALB/App Gateway  │  NAT Gateway       │
│  Bastion Host     │  VPN Gateway       │
└────────────┬──────┴────────────────────┘
             │
┌─── Private Subnets (3 AZs) ───────────┐
│  App Servers (EKS/AKS, EC2/VMs)       │
│  Internal Load Balancers               │
└────────────┬───────────────────────────┘
             │
┌─── Data Subnets (3 AZs) ──────────────┐
│  RDS/SQL  │  ElastiCache/Redis         │
│  No internet access                     │
└────────────────────────────────────────┘
```

### Hub-Spoke (Enterprise)
```
                ┌──────────────┐
                │   Hub VPC    │
                │  Transit GW  │
                │  Firewall    │
                │  Shared Svcs │
                └──────┬───────┘
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │ Spoke 1 │  │ Spoke 2 │  │ Spoke 3 │
    │ Prod    │  │ Staging │  │ Dev     │
    └─────────┘  └─────────┘  └─────────┘
```

## CIDR Planning Guide

### Standard 3-Tier VPC

| Tier | Subnet Purpose | CIDR Example | Hosts |
|------|---------------|-------------|-------|
| Public | ALB, NAT, Bastion | 10.0.0.0/24 – 10.0.2.0/24 | 254 each |
| Private | App servers, K8s nodes | 10.0.10.0/23 – 10.0.14.0/23 | 510 each |
| Data | RDS, ElastiCache | 10.0.20.0/24 – 10.0.22.0/24 | 254 each |

### CIDR Planning Rules
1. **Don't overlap** — plan CIDR ranges across all VPCs/VNets for peering compatibility
2. **Size for growth** — allocate 2-4x expected hosts
3. **Reserve space** — leave unused CIDR blocks for future subnets
4. **Document everything** — maintain a CIDR registry (spreadsheet or IPAM tool)
5. **Use /16 for VPCs** — gives plenty of room for subnets
6. **Minimum /28 for subnets** — AWS/Azure reserve 5 IPs per subnet

### Multi-VPC CIDR Allocation

| VPC/VNet | CIDR | Environment |
|----------|------|-------------|
| Production | 10.0.0.0/16 | Production workloads |
| Staging | 10.1.0.0/16 | Staging/QA |
| Development | 10.2.0.0/16 | Development |
| Shared Services | 10.10.0.0/16 | DNS, AD, monitoring |
| Management | 10.20.0.0/16 | Bastion, VPN, logging |

---

## Scripts

### generate_network_terraform.py
Generate Terraform configurations for VPC/VNet, subnets, load balancers, and DNS.

```bash
python scripts/generate_network_terraform.py \
  --provider aws|azure \
  --pattern single-region|hub-spoke \
  --environment production \
  --cidr 10.0.0.0/16 \
  --azs 3 \
  --features lb,dns,nat,bastion,vpn \
  --output ./networking/
```

---

## Best Practices

1. **3 AZs minimum** for production (HA across failure domains)
2. **Private subnets for workloads** — only load balancers and bastions in public subnets
3. **Network ACLs as backup** — use security groups/NSGs as primary, NACLs as defense-in-depth
4. **VPC Flow Logs / NSG Flow Logs** — enable for security and troubleshooting
5. **PrivateLink/Private Endpoints** — access cloud services without internet traversal
6. **Tag everything** — CIDR allocation, purpose, team, environment
7. **Centralize egress** — route internet-bound traffic through a central firewall/NAT
8. **DNS delegation** — use hosted zones, not manual DNS records
9. **WAF on all public endpoints** — protect against OWASP Top 10 at the edge
10. **Test failover** — regularly test multi-AZ and multi-region failover



---
