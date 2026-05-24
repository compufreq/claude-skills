# Transit & Hybrid Networking Reference

## Table of Contents
1. Hub-Spoke Architecture
2. AWS Transit Gateway
3. Azure Virtual WAN
4. Site-to-Site VPN
5. Direct Connect / ExpressRoute
6. Multi-Cloud Connectivity

---

## 1. Hub-Spoke Architecture

### Why Hub-Spoke
- **Centralized control** — firewall, DNS, monitoring in the hub
- **Scalability** — add spokes without reconfiguring existing ones
- **Isolation** — spokes can't communicate directly (unless explicitly allowed)
- **Cost efficiency** — shared services in hub, not duplicated per spoke

### Design Pattern
```
                    ┌─── Internet ───┐
                    │                │
              ┌─────▼────────────────▼──────┐
              │         Hub VPC/VNet         │
              │  • Transit Gateway / vWAN    │
              │  • Centralized Firewall      │
              │  • VPN/DX/ER Gateway         │
              │  • Shared DNS                │
              │  • Bastion / Jump Host       │
              │  • Logging / Monitoring      │
              └──┬───────┬───────┬──────────┘
                 │       │       │
           ┌─────▼──┐ ┌──▼────┐ ┌▼───────┐
           │Spoke 1 │ │Spoke 2│ │Spoke 3  │
           │Prod    │ │Stage  │ │Dev      │
           │10.1/16 │ │10.2/16│ │10.3/16  │
           └────────┘ └───────┘ └─────────┘

On-Premises ─── VPN/DX/ER ──→ Hub
```

---

## 2. AWS Transit Gateway

```hcl
# Transit Gateway
resource "aws_ec2_transit_gateway" "main" {
  description                     = "Main Transit Gateway"
  default_route_table_association = "disable"
  default_route_table_propagation = "disable"
  dns_support                     = "enable"
  vpn_ecmp_support                = "enable"

  tags = { Name = "${var.project}-tgw" }
}

# Attach Hub VPC
resource "aws_ec2_transit_gateway_vpc_attachment" "hub" {
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  vpc_id             = module.vpc_hub.vpc_id
  subnet_ids         = module.vpc_hub.private_subnets

  transit_gateway_default_route_table_association = false
  transit_gateway_default_route_table_propagation = false

  tags = { Name = "hub-attachment" }
}

# Attach Spoke VPCs
resource "aws_ec2_transit_gateway_vpc_attachment" "prod" {
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  vpc_id             = module.vpc_prod.vpc_id
  subnet_ids         = module.vpc_prod.private_subnets

  tags = { Name = "prod-attachment" }
}

resource "aws_ec2_transit_gateway_vpc_attachment" "staging" {
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  vpc_id             = module.vpc_staging.vpc_id
  subnet_ids         = module.vpc_staging.private_subnets

  tags = { Name = "staging-attachment" }
}

# Route Tables (control which spokes can talk to each other)
resource "aws_ec2_transit_gateway_route_table" "spokes" {
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  tags               = { Name = "spoke-routes" }
}

resource "aws_ec2_transit_gateway_route_table" "hub" {
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  tags               = { Name = "hub-routes" }
}

# Associate spokes with spoke route table
resource "aws_ec2_transit_gateway_route_table_association" "prod" {
  transit_gateway_attachment_id  = aws_ec2_transit_gateway_vpc_attachment.prod.id
  transit_gateway_route_table_id = aws_ec2_transit_gateway_route_table.spokes.id
}

# Propagate hub routes to spoke route table (spokes can reach hub)
resource "aws_ec2_transit_gateway_route_table_propagation" "hub_to_spokes" {
  transit_gateway_attachment_id  = aws_ec2_transit_gateway_vpc_attachment.hub.id
  transit_gateway_route_table_id = aws_ec2_transit_gateway_route_table.spokes.id
}

# Default route from spokes to hub (for internet via centralized NAT/firewall)
resource "aws_ec2_transit_gateway_route" "spokes_default" {
  destination_cidr_block         = "0.0.0.0/0"
  transit_gateway_attachment_id  = aws_ec2_transit_gateway_vpc_attachment.hub.id
  transit_gateway_route_table_id = aws_ec2_transit_gateway_route_table.spokes.id
}

# VPC route tables — point to TGW
resource "aws_route" "prod_to_tgw" {
  count                  = length(module.vpc_prod.private_route_table_ids)
  route_table_id         = module.vpc_prod.private_route_table_ids[count.index]
  destination_cidr_block = "10.0.0.0/8"    # All internal traffic
  transit_gateway_id     = aws_ec2_transit_gateway.main.id
}
```

### Transit Gateway vs VPC Peering

| Feature | Transit Gateway | VPC Peering |
|---------|----------------|-------------|
| Transitive routing | Yes | No |
| Scale | 5,000 VPCs | 125 per VPC |
| Centralized firewall | Yes (route through hub) | No |
| Cost | Per attachment + data | Data transfer only |
| Complexity | Medium-High | Low |
| Best for | 5+ VPCs, hub-spoke | 2-4 VPCs, direct connectivity |

---

## 3. Azure Virtual WAN

```hcl
resource "azurerm_virtual_wan" "main" {
  name                = "${var.project}-vwan"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}

resource "azurerm_virtual_hub" "main" {
  name                = "${var.project}-hub"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  virtual_wan_id      = azurerm_virtual_wan.main.id
  address_prefix      = "10.0.0.0/23"
}

# Connect spoke VNets
resource "azurerm_virtual_hub_connection" "prod" {
  name                      = "prod-connection"
  virtual_hub_id            = azurerm_virtual_hub.main.id
  remote_virtual_network_id = azurerm_virtual_network.prod.id
  internet_security_enabled = true
}

resource "azurerm_virtual_hub_connection" "staging" {
  name                      = "staging-connection"
  virtual_hub_id            = azurerm_virtual_hub.main.id
  remote_virtual_network_id = azurerm_virtual_network.staging.id
  internet_security_enabled = true
}
```

### Azure Virtual WAN vs VNet Peering

| Feature | Virtual WAN | VNet Peering |
|---------|-------------|-------------|
| Transitive routing | Yes (automatic) | No |
| VPN integration | Built-in | Separate gateway |
| ExpressRoute | Built-in | Separate gateway |
| Firewall | Azure Firewall Manager | Manual |
| Cost | Higher | Lower |
| Best for | Large enterprise, hybrid | Simple multi-VNet |

---

## 4. Site-to-Site VPN

### AWS
```hcl
resource "aws_customer_gateway" "onprem" {
  bgp_asn    = 65000
  ip_address = var.onprem_vpn_ip
  type       = "ipsec.1"
  tags       = { Name = "on-premises" }
}

resource "aws_vpn_gateway" "main" {
  vpc_id = module.vpc_hub.vpc_id
  tags   = { Name = "${var.project}-vgw" }
}

resource "aws_vpn_connection" "main" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.onprem.id
  type                = "ipsec.1"
  static_routes_only  = false    # Use BGP

  tags = { Name = "onprem-vpn" }
}
```

### Azure
```hcl
resource "azurerm_virtual_network_gateway" "vpn" {
  name                = "${var.project}-vpn-gw"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  type                = "Vpn"
  vpn_type            = "RouteBased"
  sku                 = "VpnGw2"
  active_active       = true

  ip_configuration {
    name                 = "primary"
    public_ip_address_id = azurerm_public_ip.vpn_primary.id
    subnet_id            = azurerm_subnet.gateway.id
  }

  ip_configuration {
    name                 = "secondary"
    public_ip_address_id = azurerm_public_ip.vpn_secondary.id
    subnet_id            = azurerm_subnet.gateway.id
  }
}

resource "azurerm_local_network_gateway" "onprem" {
  name                = "on-premises"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  gateway_address     = var.onprem_vpn_ip
  address_space       = ["192.168.0.0/16"]
}

resource "azurerm_virtual_network_gateway_connection" "onprem" {
  name                       = "onprem-connection"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  type                       = "IPsec"
  virtual_network_gateway_id = azurerm_virtual_network_gateway.vpn.id
  local_network_gateway_id   = azurerm_local_network_gateway.onprem.id
  shared_key                 = var.vpn_shared_key

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

## 5. Direct Connect / ExpressRoute

### When to Use Dedicated Connectivity

| Criteria | VPN | Direct Connect / ExpressRoute |
|----------|-----|------------------------------|
| Bandwidth | < 1 Gbps | 1-100 Gbps |
| Latency | Variable (internet) | Predictable (dedicated) |
| Cost | Low | High (monthly + port fees) |
| Encryption | IPsec built-in | Optional (MACsec / VPN overlay) |
| Setup time | Minutes | Weeks to months |
| Redundancy | Dual tunnels | Dual circuits recommended |
| Best for | Dev, low-traffic, backup | Production, high-bandwidth, compliance |

### AWS Direct Connect (Terraform)
```hcl
resource "aws_dx_gateway" "main" {
  name            = "${var.project}-dx-gw"
  amazon_side_asn = "64512"
}

resource "aws_dx_gateway_association" "tgw" {
  dx_gateway_id         = aws_dx_gateway.main.id
  associated_gateway_id = aws_ec2_transit_gateway.main.id
  allowed_prefixes      = ["10.0.0.0/8"]
}
```

---

## 6. Multi-Cloud Connectivity

### AWS ↔ Azure via VPN
```
AWS VPC ──→ AWS VPN Gateway ──── IPsec Tunnel ──── Azure VPN Gateway ──→ Azure VNet
   │                                                                          │
10.0.0.0/16                                                            10.1.0.0/16
```

### Implementation Pattern
1. Create VPN gateways in both clouds
2. Exchange public IPs and pre-shared keys
3. Configure BGP or static routes
4. Set up route tables in both VPCs/VNets
5. Test connectivity with ping/traceroute
6. Monitor tunnel status in both cloud consoles

### Multi-Cloud DNS
- Use a primary DNS provider (Route 53 or Azure DNS) for external zones
- Use private zones in each cloud for internal resolution
- Set up DNS forwarding between clouds via VPN/peering
- Consider using a third-party DNS (e.g., Cloudflare) for cloud-agnostic management

### Multi-Cloud Best Practices
1. **Don't overlap CIDRs** across clouds
2. **Encrypt all cross-cloud traffic** (VPN tunnels, not public internet)
3. **Monitor tunnel health** with alerts on both sides
4. **Document all connections** in a network diagram
5. **Plan for failure** — what happens if the tunnel goes down?
6. **Minimize cross-cloud data transfer** — it's expensive



---
