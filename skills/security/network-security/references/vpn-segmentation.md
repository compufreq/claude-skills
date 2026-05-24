# VPN & Network Segmentation Reference

## 1. VPN Technologies

| Technology | Type | Speed | Use Case |
|-----------|------|-------|---------|
| **IPsec** | Site-to-site | Good | Cloud VPN gateways, corporate |
| **WireGuard** | Point-to-point | Excellent | Modern, fast, simple config |
| **OpenVPN** | Client/site-to-site | Good | Legacy, broad compatibility |
| **AWS Client VPN** | Client VPN | Good | AWS-managed remote access |
| **Azure P2S VPN** | Client VPN | Good | Azure-managed remote access |

### WireGuard Configuration
```ini
# Server (/etc/wireguard/wg0.conf)
[Interface]
PrivateKey = <server_private_key>
Address = 10.100.0.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
PublicKey = <client_public_key>
AllowedIPs = 10.100.0.2/32

# Client
[Interface]
PrivateKey = <client_private_key>
Address = 10.100.0.2/24
DNS = 10.0.0.2

[Peer]
PublicKey = <server_public_key>
Endpoint = vpn.example.com:51820
AllowedIPs = 10.0.0.0/8  # Route internal traffic through VPN
PersistentKeepalive = 25
```

## 2. Network Segmentation

### Segmentation Strategies

| Level | How | Granularity |
|-------|-----|------------|
| **VLAN** | Layer 2 network isolation | Per subnet/department |
| **Subnet ACLs** | Layer 3 firewall rules | Per subnet |
| **Security Groups** | Layer 4 per-instance firewall | Per service/role |
| **NetworkPolicy (K8s)** | Pod-level firewall | Per microservice |
| **Service Mesh** | Layer 7 per-request policy | Per API call |

### Kubernetes Network Segmentation
```yaml
# Default deny all in namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]

# Allow specific traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-db
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: postgres
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: api-server
      ports:
        - protocol: TCP
          port: 5432
```

### Segmentation Best Practices
1. **Segment by sensitivity** — PCI data separate from general data
2. **Segment by function** — web tier, app tier, data tier
3. **Segment by environment** — prod, staging, dev never share networks
4. **Default deny** — explicitly allow only required traffic
5. **Document all rules** — each rule needs a business justification
6. **Audit quarterly** — remove rules that are no longer needed



---
