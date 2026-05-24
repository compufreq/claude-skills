# Hybrid Connectivity Reference

## Table of Contents
1. Connectivity Options
2. AWS ↔ Azure VPN
3. Hybrid: On-Premises ↔ Cloud
4. Network Architecture Patterns
5. DNS & Routing

---

## 1. Connectivity Options

| Method | Bandwidth | Latency | Cost | Setup Time | Best For |
|--------|----------|---------|------|-----------|---------|
| **Internet VPN** | < 1 Gbps | Variable | Low | Hours | Dev, backup link |
| **Site-to-Site VPN** | < 1.25 Gbps | 10-50ms | Low-Med | Hours-days | Small/medium hybrid |
| **AWS Direct Connect** | 1-100 Gbps | Low, consistent | High | Weeks-months | Production hybrid |
| **Azure ExpressRoute** | 50 Mbps-10 Gbps | Low, consistent | High | Weeks-months | Production hybrid |
| **SD-WAN** | Variable | Optimized | Medium | Days-weeks | Multi-site, branch |
| **Cloud Interconnect** | 10-100 Gbps | Very low | High | Weeks | Cloud ↔ Cloud |

---

## 2. AWS ↔ Azure VPN

### Architecture
```
AWS VPC (10.0.0.0/16) ←── IPsec Tunnel ──→ Azure VNet (10.1.0.0/16)
  AWS VPN Gateway                            Azure VPN Gateway
  (2 tunnels for HA)                         (Active-Active)
```

### AWS Side (Terraform)
```hcl
resource "aws_vpn_gateway" "main" {
  vpc_id          = module.vpc.vpc_id
  amazon_side_asn = 64512
  tags            = { Name = "${var.project}-vgw" }
}

resource "aws_customer_gateway" "azure_primary" {
  bgp_asn    = 65515
  ip_address = var.azure_vpn_public_ip_1
  type       = "ipsec.1"
  tags       = { Name = "azure-vpn-primary" }
}

resource "aws_customer_gateway" "azure_secondary" {
  bgp_asn    = 65515
  ip_address = var.azure_vpn_public_ip_2
  type       = "ipsec.1"
  tags       = { Name = "azure-vpn-secondary" }
}

resource "aws_vpn_connection" "azure_primary" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.azure_primary.id
  type                = "ipsec.1"
  static_routes_only  = false

  tunnel1_preshared_key = var.vpn_psk
  tunnel1_ike_versions  = ["ikev2"]

  tags = { Name = "aws-to-azure-primary" }
}

# Route to Azure VNet
resource "aws_route" "to_azure" {
  count                  = length(module.vpc.private_route_table_ids)
  route_table_id         = module.vpc.private_route_table_ids[count.index]
  destination_cidr_block = "10.1.0.0/16"
  gateway_id             = aws_vpn_gateway.main.id
}
```

### Azure Side (Terraform)
```hcl
resource "azurerm_virtual_network_gateway" "main" {
  name                = "${var.project}-vpn-gw"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  type                = "Vpn"
  vpn_type            = "RouteBased"
  sku                 = "VpnGw2"
  active_active       = true
  enable_bgp          = true

  bgp_settings {
    asn = 65515
  }

  ip_configuration {
    name                 = "primary"
    public_ip_address_id = azurerm_public_ip.vpn_1.id
    subnet_id            = azurerm_subnet.gateway.id
  }
  ip_configuration {
    name                 = "secondary"
    public_ip_address_id = azurerm_public_ip.vpn_2.id
    subnet_id            = azurerm_subnet.gateway.id
  }
}

resource "azurerm_local_network_gateway" "aws" {
  name                = "aws-vpn"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  gateway_address     = var.aws_vpn_public_ip
  address_space       = ["10.0.0.0/16"]

  bgp_settings {
    asn                 = 64512
    bgp_peering_address = var.aws_bgp_peer_ip
  }
}

resource "azurerm_virtual_network_gateway_connection" "aws" {
  name                       = "to-aws"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  type                       = "IPsec"
  virtual_network_gateway_id = azurerm_virtual_network_gateway.main.id
  local_network_gateway_id   = azurerm_local_network_gateway.aws.id
  shared_key                 = var.vpn_psk
  enable_bgp                 = true

  ipsec_policy {
    ike_encryption   = "AES256"
    ike_integrity    = "SHA256"
    dh_group         = "DHGroup14"
    ipsec_encryption = "AES256"
    ipsec_integrity  = "SHA256"
    pfs_group        = "PFS14"
    sa_lifetime      = 3600
  }
}
```

---

## 3. Hybrid: On-Premises ↔ Cloud

### Direct Connect / ExpressRoute Decision

| Factor | VPN | Direct Connect / ExpressRoute |
|--------|-----|-------------------------------|
| Budget | < $500/mo | $500-10,000+/mo |
| Bandwidth need | < 1 Gbps | 1-100 Gbps |
| Latency sensitivity | Tolerant | Strict (< 10ms) |
| Data volume | < 5 TB/month | > 5 TB/month |
| Compliance | Basic | PCI, HIPAA, financial |
| Reliability need | Best-effort | SLA-backed |

### Hybrid Architecture
```
On-Premises                      Cloud
┌────────────────┐              ┌────────────────┐
│ Active Directory│──Federation─►│ IAM / Azure AD  │
│ Legacy Apps     │              │ Modern Apps     │
│ Databases       │──DX/ER─────►│ Data Lakes      │
│ File Shares     │              │ K8s Workloads   │
│ Firewalls       │              │ Managed Services│
└────────────────┘              └────────────────┘
         │                              │
    Shared DNS (split-horizon)    VPC/VNet
    Shared Identity (SAML/OIDC)   Private subnets
    Shared Monitoring             PrivateLink
```

### Split-Horizon DNS
```
External queries (internet):
  app.example.com → 52.1.2.3 (cloud public IP)

Internal queries (VPN/DX):
  app.example.com → 10.0.1.100 (cloud private IP)
  legacy.example.com → 192.168.1.50 (on-prem private IP)
```

```hcl
# AWS Route 53 Private Hosted Zone
resource "aws_route53_zone" "internal" {
  name = "example.com"
  vpc { vpc_id = module.vpc.vpc_id }
}

# Route 53 Resolver (forward on-prem DNS queries)
resource "aws_route53_resolver_endpoint" "outbound" {
  name      = "to-onprem"
  direction = "OUTBOUND"
  security_group_ids = [aws_security_group.dns.id]

  ip_address { subnet_id = module.vpc.private_subnets[0] }
  ip_address { subnet_id = module.vpc.private_subnets[1] }
}

resource "aws_route53_resolver_rule" "onprem" {
  domain_name = "corp.example.com"
  rule_type   = "FORWARD"

  resolver_endpoint_id = aws_route53_resolver_endpoint.outbound.id

  target_ip { ip = "192.168.1.10" }
  target_ip { ip = "192.168.1.11" }
}
```

---

## 4. Network Architecture Patterns

### Hub-Spoke with Multi-Cloud Spokes
```
                  ┌───────────────┐
                  │   Hub VPC     │
                  │ (AWS Transit  │
                  │  Gateway)     │
                  └──┬────┬───┬──┘
         ┌───────────┘    │   └───────────┐
         ▼                ▼               ▼
    ┌─────────┐    ┌────────────┐   ┌──────────┐
    │AWS Spoke│    │On-Premises │   │Azure     │
    │(Prod)   │    │(VPN/DX)    │   │(VPN)     │
    └─────────┘    └────────────┘   └──────────┘
```

### CIDR Planning for Multi-Cloud

| Network | CIDR | Cloud |
|---------|------|-------|
| AWS Production | 10.0.0.0/16 | AWS |
| AWS Staging | 10.1.0.0/16 | AWS |
| Azure Production | 10.10.0.0/16 | Azure |
| Azure Staging | 10.11.0.0/16 | Azure |
| On-Premises | 192.168.0.0/16 | DC |
| Shared Services | 10.20.0.0/16 | AWS (hub) |

**Rule:** Never overlap CIDRs across any network that might be connected.

---

## 5. DNS & Routing

### Global DNS with Cloudflare (Cloud-Agnostic)
```
                    Cloudflare DNS
                   ╱       │       ╲
            ┌──────┐  ┌────────┐  ┌──────┐
            │ AWS  │  │ Azure  │  │ On-  │
            │ ALB  │  │ Front  │  │ Prem │
            │      │  │ Door   │  │ LB   │
            └──────┘  └────────┘  └──────┘

Routing policies:
  - Latency-based → nearest cloud region
  - Geo-based → EU users → Azure (EU), US users → AWS (US)
  - Failover → if AWS down, route to Azure
  - Weighted → 80% AWS, 20% Azure (canary)
```

### Monitoring Cross-Cloud Links
```
Monitor these for every cross-cloud connection:
  - Tunnel status (up/down)
  - Latency between clouds (ping, traceroute)
  - Bandwidth utilization (% of capacity)
  - Packet loss rate
  - BGP session status (if using BGP)
  - Data transfer volume (cost tracking)
```
