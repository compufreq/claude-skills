# SOC 2 Type II Reference

## Trust Service Criteria

| Category | ID | Control Area | Technical Implementation |
|----------|----|-------------|------------------------|
| **Security** | CC6.1 | Logical access controls | IAM, RBAC, MFA, SSO |
| | CC6.2 | Access provisioning | Automated onboarding, JIT access |
| | CC6.3 | Access removal | Offboarding automation, access reviews |
| | CC6.6 | Encryption in transit | TLS 1.2+, certificate management |
| | CC6.7 | Encryption at rest | KMS, encrypted volumes/databases |
| | CC6.8 | Malware prevention | EDR, container scanning, WAF |
| | CC7.1 | Vulnerability management | SAST, SCA, DAST in CI/CD |
| | CC7.2 | Security monitoring | SIEM, GuardDuty, CloudTrail |
| | CC7.3 | Change management | Git-based, PR reviews, CI/CD |
| | CC7.4 | Incident response | Documented plan, tested quarterly |
| | CC8.1 | Secure development | SDLC policy, code review, testing |
| **Availability** | A1.1 | Capacity planning | Auto-scaling, monitoring |
| | A1.2 | Backup & recovery | Automated backups, tested restores |
| | A1.3 | DR plan | Documented, tested annually |
| **Confidentiality** | C1.1 | Data classification | Policy, labeling, handling procedures |
| | C1.2 | Data disposal | Secure deletion, crypto-shredding |

## Evidence Collection

| Control | Evidence Source | Automation |
|---------|---------------|-----------|
| Access reviews | IAM policy exports, user list | AWS Config, Azure Policy |
| MFA enforcement | IAM policy, Conditional Access | Automated compliance check |
| Encryption | KMS key policies, TLS configs | AWS Config rules |
| Vulnerability scanning | SARIF reports from CI/CD | Archive scan results |
| Change management | Git PR history, CI/CD logs | API export |
| Incident response | Incident tickets, post-mortems | Incident management tool |
| Monitoring | Dashboard screenshots, alert configs | Terraform/IaC export |
| Backup verification | Restore test results | Monthly automated test |

## SOC 2 Automation with AWS Config
```hcl
# Check MFA is enabled for all IAM users
resource "aws_config_config_rule" "mfa_enabled" {
  name = "iam-user-mfa-enabled"
  source {
    owner             = "AWS"
    source_identifier = "IAM_USER_MFA_ENABLED"
  }
}

# Check encryption at rest for EBS volumes
resource "aws_config_config_rule" "ebs_encrypted" {
  name = "encrypted-volumes"
  source {
    owner             = "AWS"
    source_identifier = "ENCRYPTED_VOLUMES"
  }
}

# Check S3 buckets are not public
resource "aws_config_config_rule" "s3_public" {
  name = "s3-bucket-public-read-prohibited"
  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_PUBLIC_READ_PROHIBITED"
  }
}

# Check CloudTrail is enabled
resource "aws_config_config_rule" "cloudtrail" {
  name = "cloudtrail-enabled"
  source {
    owner             = "AWS"
    source_identifier = "CLOUD_TRAIL_ENABLED"
  }
}
```

## Audit Preparation Checklist

### 3 Months Before Audit
- [ ] Review all control descriptions for accuracy
- [ ] Ensure evidence collection is automated where possible
- [ ] Identify any control gaps and remediate
- [ ] Review access logs and remove stale accounts
- [ ] Run internal audit / mock assessment

### 1 Month Before
- [ ] Collect all evidence for the audit period
- [ ] Organize evidence by control
- [ ] Prepare control narratives (how each control works)
- [ ] Brief relevant team members on audit process
- [ ] Confirm auditor access to systems (read-only)

### During Audit
- [ ] Designate single point of contact for auditor
- [ ] Respond to evidence requests within 24 hours
- [ ] Document any exceptions or deviations
- [ ] Track all auditor questions and responses



---

<!-- Script: scripts/generate_compliance.py -->

# Script: generate_compliance.py

```python
#!/usr/bin/env python3
"""Generate compliance assessment documents."""

import argparse, os
from datetime import datetime

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")

FRAMEWORKS = {
    "soc2": {
        "name": "SOC 2 Type II",
        "controls": [
            ("CC6.1", "Logical access security", "IAM, RBAC, MFA, SSO"),
            ("CC6.2", "Access provisioning", "Automated onboarding, approval workflow"),
            ("CC6.3", "Access removal", "Offboarding automation, access reviews"),
            ("CC6.6", "Encryption in transit", "TLS 1.2+, certificate management"),
            ("CC6.7", "Encryption at rest", "KMS, encrypted volumes/databases"),
            ("CC7.1", "Vulnerability management", "SAST, SCA, DAST scanning"),
            ("CC7.2", "Security monitoring", "SIEM, log aggregation, alerting"),
            ("CC7.3", "Change management", "Git PRs, CI/CD, approval gates"),
            ("CC7.4", "Incident response", "IR plan, tested quarterly"),
            ("CC8.1", "Secure development", "SDLC policy, code review"),
            ("A1.2", "Backup & recovery", "Automated backups, tested restores"),
            ("A1.3", "Disaster recovery", "DR plan, tested annually"),
        ],
    },
    "iso27001": {
        "name": "ISO 27001:2022",
        "controls": [
            ("A.5.1", "Information security policies", "Documented, reviewed annually"),
            ("A.8.1", "Asset management", "Asset inventory, classification"),
            ("A.8.2", "Information classification", "Labels, handling procedures"),
            ("A.9.1", "Access control policy", "RBAC, least privilege"),
            ("A.9.2", "User access management", "Provisioning, reviews, removal"),
            ("A.9.4", "System access control", "MFA, password policy, session mgmt"),
            ("A.10.1", "Cryptographic controls", "Encryption at rest/transit, key mgmt"),
            ("A.12.1", "Operational procedures", "Change management, capacity planning"),
            ("A.12.4", "Logging and monitoring", "Audit logs, SIEM, alerting"),
            ("A.12.6", "Vulnerability management", "Scanning, patching, remediation"),
            ("A.14.2", "Secure development", "SDLC, code review, testing"),
            ("A.16.1", "Incident management", "IR plan, reporting, lessons learned"),
            ("A.17.1", "Business continuity", "BCP, DR plan, testing"),
            ("A.18.1", "Compliance", "Legal requirements, audit program"),
        ],
    },
    "nist": {
        "name": "NIST CSF 2.0",
        "controls": [
            ("ID.AM-1", "Asset inventory", "Cloud resource inventory, CMDB"),
            ("ID.RA-1", "Risk assessment", "Annual risk assessment, threat modeling"),
            ("PR.AC-1", "Identity management", "IAM, SSO, MFA, lifecycle"),
            ("PR.AC-3", "Remote access", "VPN/ZTNA, conditional access"),
            ("PR.DS-1", "Data at rest protection", "Encryption, key management"),
            ("PR.DS-2", "Data in transit protection", "TLS, VPN, PrivateLink"),
            ("PR.IP-1", "Security baseline", "Hardened configs, CIS benchmarks"),
            ("PR.MA-1", "Maintenance", "Patch management, update policy"),
            ("DE.CM-1", "Network monitoring", "Flow logs, IDS, GuardDuty"),
            ("DE.CM-4", "Malware detection", "EDR, container scanning"),
            ("RS.RP-1", "Incident response", "IR plan, runbooks, testing"),
            ("RC.RP-1", "Recovery planning", "DR plan, backup restoration"),
        ],
    },
    "gdpr": {
        "name": "GDPR",
        "controls": [
            ("Art.5", "Data minimization", "Collect only necessary data"),
            ("Art.6", "Lawful processing basis", "Consent management, legal basis docs"),
            ("Art.7", "Consent management", "Granular consent, easy withdrawal"),
            ("Art.15", "Right of access", "Data export API, SAR workflow"),
            ("Art.17", "Right to erasure", "Deletion API, cascade delete"),
            ("Art.20", "Data portability", "JSON/CSV export"),
            ("Art.25", "Privacy by design", "PIA process, defaults to private"),
            ("Art.30", "Processing records", "Data flow mapping, registry"),
            ("Art.32", "Security of processing", "Encryption, access control, pseudonymization"),
            ("Art.33", "Breach notification", "72-hour process, IR plan"),
            ("Art.35", "DPIA", "Impact assessment for high-risk processing"),
        ],
    },
}

def gen_assessment(framework_key, project, output):
    d = datetime.now().strftime("%Y-%m-%d")
    fw = FRAMEWORKS[framework_key]

    rows = ""
    for ctrl_id, ctrl_name, ctrl_impl in fw["controls"]:
        rows += f"| {ctrl_id} | {ctrl_name} | {ctrl_impl} | ☐ Pass ☐ Fail ☐ N/A | |\n"

    content = f"""# {fw['name']} Compliance Assessment — {project}

**Date:** {d}
**Assessor:** [Name]
**Status:** In Progress

---

## Control Assessment

| Control ID | Control | Expected Implementation | Status | Evidence / Notes |
|------------|---------|------------------------|--------|-----------------|
{rows}

## Summary

| Status | Count |
|--------|-------|
| ✅ Pass | |
| ❌ Fail | |
| ⬜ N/A | |
| **Total** | {len(fw['controls'])} |

## Gap Remediation Plan

| Gap | Priority | Remediation | Owner | Due Date | Status |
|-----|----------|------------|-------|----------|--------|
| | ☐ P1 ☐ P2 ☐ P3 | | | | ☐ |
| | | | | | ☐ |
| | | | | | ☐ |

## Sign-Off

| Role | Name | Date |
|------|------|------|
| CISO / Security Lead | | |
| Engineering Lead | | |
| Compliance Officer | | |
"""
    create_file(os.path.join(output, f"{framework_key}-assessment-{project}.md"), content)

def gen_policy(project, output):
    d = datetime.now().strftime("%Y-%m-%d")
    content = f"""# Information Security Policy — {project}

**Version:** 1.0
**Date:** {d}
**Owner:** CISO
**Review:** Annual

---

## 1. Purpose
This policy establishes the information security requirements for {project}.

## 2. Scope
All employees, contractors, and systems that process company data.

## 3. Access Control
- All access requires authentication (SSO + MFA)
- Least privilege: users get minimum permissions needed
- Access reviews conducted quarterly
- Privileged access requires approval and is time-limited
- Access removed within 24 hours of role change or termination

## 4. Data Protection
- All data classified as Public, Internal, Confidential, or Restricted
- Confidential and Restricted data encrypted at rest and in transit
- PII processed only with lawful basis, minimized, and retained per policy
- Data retention schedules enforced; data deleted when no longer needed

## 5. Development Security
- All code changes require peer review (PR approval)
- Security scanning (SAST, SCA) runs on every PR
- Secrets never stored in code; use secrets management service
- Production deployments through CI/CD only (no manual changes)

## 6. Infrastructure Security
- All infrastructure defined as code (Terraform/IaC)
- Production environments isolated from dev/staging
- Network segmented; default-deny firewall rules
- Vulnerability scanning weekly; critical patches within 72 hours

## 7. Incident Response
- All security incidents reported to security team immediately
- Incident response plan tested quarterly
- Post-incident review within 5 business days
- Lessons learned incorporated into controls

## 8. Business Continuity
- Critical systems backed up daily with tested restoration
- DR plan documented and tested annually
- RPO and RTO defined per service tier

## 9. Compliance
- Annual risk assessment conducted
- Compliance monitoring automated where possible
- Audit findings tracked to closure
- Regulatory changes monitored and incorporated
"""
    create_file(os.path.join(output, f"security-policy-{project}.md"), content)

def main():
    p = argparse.ArgumentParser(description="Generate Compliance Documents")
    p.add_argument("--type", choices=["assessment", "policy"], required=True)
    p.add_argument("--framework", choices=list(FRAMEWORKS.keys()) + ["all"], default="soc2")
    p.add_argument("--project", default="myapp")
    p.add_argument("--output", default="./compliance")
    a = p.parse_args()

    print(f"\n📋 Generating {a.type} for {a.project}\n")

    if a.type == "assessment":
        if a.framework == "all":
            for fw in FRAMEWORKS:
                gen_assessment(fw, a.project, a.output)
        else:
            gen_assessment(a.framework, a.project, a.output)
    elif a.type == "policy":
        gen_policy(a.project, a.output)

    print(f"\n✅ Generated at: {a.output}/")

if __name__ == "__main__":
    main()

```
