# NIST Cybersecurity Framework Reference

## NIST Cybersecurity Framework (CSF 2.0)

### Five Core Functions

| Function | Purpose | Key Activities |
|----------|---------|---------------|
| **Identify** | Know your assets and risks | Asset inventory, risk assessment, governance |
| **Protect** | Safeguard critical services | Access control, training, data security, maintenance |
| **Detect** | Timely discovery of events | Monitoring, anomaly detection, continuous monitoring |
| **Respond** | Take action on incidents | Response planning, communications, mitigation |
| **Recover** | Restore services | Recovery planning, improvements, communications |

### NIST CSF → Technical Implementation

| Category | Subcategory | Cloud Implementation |
|----------|------------|---------------------|
| **ID.AM** Asset Management | ID.AM-1: Physical devices inventoried | Cloud asset inventory (AWS Config, Azure Resource Graph) |
| | ID.AM-2: Software platforms inventoried | SBOM, container registry, dependency tracking |
| **PR.AC** Access Control | PR.AC-1: Identities managed | IAM, SSO, MFA, lifecycle management |
| | PR.AC-3: Remote access managed | VPN / zero trust proxy, conditional access |
| | PR.AC-4: Access permissions managed | RBAC, least privilege, quarterly reviews |
| **PR.DS** Data Security | PR.DS-1: Data at rest protected | KMS encryption, encrypted volumes |
| | PR.DS-2: Data in transit protected | TLS 1.2+, VPN, PrivateLink |
| | PR.DS-5: Protections against data leaks | DLP, S3 policies, network controls |
| **DE.CM** Continuous Monitoring | DE.CM-1: Network monitored | VPC Flow Logs, GuardDuty, IDS |
| | DE.CM-4: Malicious code detected | EDR, container scanning, WAF |
| | DE.CM-7: Unauthorized activity monitored | CloudTrail, audit logging, SIEM |
| **RS.RP** Response Planning | RS.RP-1: Response plan executed | Incident response plan, runbooks |
| **RC.RP** Recovery Planning | RC.RP-1: Recovery plan executed | DR plan, backup restoration |

### NIST CSF Maturity Assessment

| Level | Description | Score |
|-------|------------|-------|
| **Tier 1: Partial** | Ad hoc, reactive | 1 |
| **Tier 2: Risk Informed** | Aware but not formalized | 2 |
| **Tier 3: Repeatable** | Formally approved, regularly reviewed | 3 |
| **Tier 4: Adaptive** | Continuously improved, integrated | 4 |

### Cross-Framework Mapping

| NIST CSF | SOC 2 | ISO 27001 |
|----------|-------|-----------|
| ID.AM (Asset Management) | CC6.1 | A.8 |
| PR.AC (Access Control) | CC6.1-CC6.3 | A.9 |
| PR.DS (Data Security) | CC6.6-CC6.7 | A.10, A.13 |
| DE.CM (Monitoring) | CC7.2 | A.12.4 |
| RS.RP (Response) | CC7.4 | A.16 |
| RC.RP (Recovery) | A1.2-A1.3 | A.17 |



---
