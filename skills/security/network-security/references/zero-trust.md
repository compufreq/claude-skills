# Zero Trust Architecture Reference

## Core Principles

```
1. Never trust, always verify — authenticate and authorize every request
2. Least privilege access — minimum permissions, just-in-time
3. Assume breach — design as if the network is already compromised
4. Verify explicitly — identity, device, location, behavior
5. Microsegmentation — isolate workloads, limit blast radius
```

## Zero Trust Components

| Component | Traditional | Zero Trust |
|-----------|------------|-----------|
| Network | Trust internal network | No trusted network zones |
| Identity | VPN = authenticated | Verify every request |
| Device | Corporate device = trusted | Verify device health |
| Access | Role-based, static | Context-aware, dynamic |
| Segmentation | Network VLANs | Microsegmentation per workload |
| Monitoring | Perimeter-focused | All traffic monitored |

## Implementation Layers

### 1. Identity (Foundation)
```
- Strong authentication (MFA everywhere)
- Single sign-on (SAML/OIDC)
- Just-in-time access (Azure AD PIM, AWS IAM Identity Center)
- Conditional access policies (device compliance, location, risk)
- Service identity (workload identity, mTLS)
```

### 2. Device Trust
```
- Device health attestation
- MDM enrollment required
- Endpoint detection and response (EDR)
- Certificate-based authentication
- Posture checks before access
```

### 3. Network Microsegmentation
```
Traditional:
  [Trusted Zone] ←→ all services can talk to each other

Zero Trust:
  Service A ──policy──→ Service B (allowed: HTTPS port 443)
  Service A ──policy──✗ Service C (blocked: no policy)
  
Implementation:
  - Kubernetes NetworkPolicy
  - Service mesh (Istio/Linkerd) policies
  - Cloud security groups (per-service)
  - Software-defined networking (NSX, Calico)
```

### 4. Application Access
```
Traditional: VPN → internal network → any application
Zero Trust:  Identity Provider → verify context → specific application only

Tools:
  - Cloudflare Access / Zero Trust
  - Google BeyondCorp Enterprise
  - Zscaler Private Access
  - Azure AD Application Proxy
  - AWS Verified Access
```

## Cloud Zero Trust Architecture
```
User → Identity Provider (MFA) → Context Engine (device, location, risk)
         ↓ (if approved)
    Application Proxy / Verified Access
         ↓ (per-application policy)
    Specific Application (not network-level access)
         ↓
    Service Mesh (mTLS between services)
         ↓
    Microsegmented data access (per-service DB permissions)
```

## Zero Trust Maturity Model

| Level | Identity | Network | Data | Workloads |
|-------|---------|---------|------|-----------|
| **Traditional** | Passwords, VPN | Perimeter firewall | Flat access | No segmentation |
| **Initial** | MFA, SSO | Basic segmentation | Role-based access | Security groups |
| **Advanced** | Conditional access, JIT | Microsegmentation | Attribute-based access | NetworkPolicy, mesh |
| **Optimal** | Continuous verification, passwordless | Per-request auth, no VPN | DLP, classification | mTLS everywhere, SPIFFE |

## Implementation Roadmap

```
Phase 1 (3 months): Identity foundation
  - Deploy SSO/OIDC for all applications
  - Enable MFA for all users
  - Implement conditional access policies
  - Audit and remove standing admin access

Phase 2 (3 months): Network segmentation
  - Implement Kubernetes NetworkPolicies
  - Security groups per service (not per subnet)
  - Enable VPC flow logs / NSG flow logs
  - Deploy service mesh for internal mTLS

Phase 3 (6 months): Application access
  - Replace VPN with identity-aware proxy
  - Implement device trust / posture checks
  - Per-application access policies
  - Continuous session monitoring

Phase 4 (ongoing): Continuous improvement
  - Automated policy enforcement
  - Behavioral analytics
  - Passwordless authentication
  - Full microsegmentation
```
