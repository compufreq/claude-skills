# Compliance Frameworks Reference

## Table of Contents
1. OWASP Top 10 (2021) — Scan Mapping
2. CIS Benchmarks
3. SOC2 Controls
4. Compliance Dashboard

---

## 1. OWASP Top 10 (2021) — Scan Mapping

| # | Category | Detection Tool | Key Rules |
|---|----------|---------------|-----------|
| A01 | Broken Access Control | SAST (Semgrep), DAST (ZAP) | Missing auth checks, IDOR, CORS misconfig |
| A02 | Cryptographic Failures | SAST (Semgrep, CodeQL) | Weak algorithms, hardcoded keys, missing TLS |
| A03 | Injection | SAST + DAST | SQLi, XSS, command injection, LDAP injection |
| A04 | Insecure Design | Manual review, threat modeling | Business logic flaws, missing rate limits |
| A05 | Security Misconfiguration | DAST (ZAP), IaC scan (Checkov) | Default creds, verbose errors, missing headers |
| A06 | Vulnerable Components | SCA (Trivy, Snyk, Dependabot) | Known CVEs in dependencies |
| A07 | Auth & Session Failures | SAST + DAST | Weak passwords, missing MFA, session fixation |
| A08 | Data Integrity Failures | SCA, SBOM | Unsigned updates, untrusted CI/CD, deserialization |
| A09 | Logging & Monitoring Failures | SAST (custom rules) | Missing audit logs, no alerting |
| A10 | SSRF | SAST (Semgrep) + DAST | Unvalidated URLs, internal network access |

### Mapping Scans to OWASP

```yaml
# Minimum scan coverage for OWASP Top 10
owasp_coverage:
  A01_access_control:
    tools: [semgrep, zap]
    rules: ["p/owasp-top-ten", "40012-40018"]
  A02_crypto:
    tools: [semgrep]
    rules: ["rules/crypto-weak-algorithms"]
  A03_injection:
    tools: [semgrep, codeql, zap]
    rules: ["p/owasp-top-ten", "40012", "40018", "40014"]
  A05_misconfiguration:
    tools: [checkov, zap, trivy]
    rules: ["CKV_*", "10015-10038"]
  A06_vulnerable_components:
    tools: [trivy, snyk, dependabot]
    rules: ["severity >= HIGH"]
  A08_integrity:
    tools: [trivy-sbom, cosign]
    rules: ["SBOM generation", "image signing"]
```

---

## 2. CIS Benchmarks

### CIS for Docker
```bash
# Run CIS Docker Benchmark
docker run --rm --net host --pid host --userns host --cap-add audit_control \
  -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
  -v /var/lib:/var/lib:ro \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /etc:/etc:ro \
  docker/docker-bench-security
```

Key CIS Docker checks:
| # | Check | Tool |
|---|-------|------|
| 4.1 | Image built from trusted base | Trivy, policy |
| 4.2 | No unnecessary packages | Dockerfile review |
| 4.5 | Content trust enabled | `DOCKER_CONTENT_TRUST=1` |
| 4.6 | HEALTHCHECK added | Dockerfile lint |
| 4.9 | No secrets in image | Secret scanning |
| 5.4 | Read-only root filesystem | K8s securityContext |
| 5.12 | No privileged containers | PSA enforcement |
| 5.25 | Container restricted from acquiring new privileges | `allowPrivilegeEscalation: false` |

### CIS for Kubernetes
```bash
# Run kube-bench
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
kubectl logs job/kube-bench

# Or with Trivy
trivy k8s --compliance k8s-cis --report summary cluster
```

### CIS for AWS
```bash
# Prowler — AWS CIS benchmark scanner
pip install prowler
prowler aws --compliance cis_2.0_aws

# Checkov for IaC CIS compliance
checkov -d ./terraform --framework terraform --check CIS*
```

---

## 3. SOC2 Controls

### SOC2 Trust Service Criteria → DevSecOps Mapping

| SOC2 Criteria | Control | DevSecOps Implementation |
|--------------|---------|-------------------------|
| CC6.1 | Logical access security | RBAC, MFA, least privilege IAM |
| CC6.2 | Access provisioning | Automated user management, JIT access |
| CC6.3 | Access removal | Automated deprovisioning on offboarding |
| CC6.6 | Encryption in transit | TLS everywhere, certificate management |
| CC6.7 | Encryption at rest | Encrypted storage, KMS for secrets |
| CC7.1 | Vulnerability management | SAST + SCA + DAST scanning in CI |
| CC7.2 | Security monitoring | Log aggregation, SIEM, alerting |
| CC7.3 | Change management | Git-based changes, PR reviews, CI/CD |
| CC7.4 | Incident response | Runbooks, on-call, post-mortems |
| CC8.1 | Secure development | SDLC policy, security training, code review |

### Evidence Collection for SOC2

| Evidence | Source | Automation |
|----------|--------|-----------|
| Code review logs | GitHub/GitLab PR history | API export |
| Security scan results | SARIF files from CI | Archive artifacts |
| Deployment logs | CI/CD pipeline logs | Artifact retention |
| Access reviews | IAM policies, RBAC configs | IaC audit trail |
| Incident records | Incident management tool | API integration |
| Vulnerability remediation | Scan results + fix PRs | Snyk/Dependabot history |
| Change approvals | PR approvals, deploy gates | GitHub environment protection |
| Encryption evidence | TLS configs, KMS policies | IaC + runtime verification |

---

## 4. Compliance Dashboard Metrics

Track these metrics for compliance reporting:

| Metric | Target | Measurement |
|--------|--------|-------------|
| MTTR (Mean Time to Remediate) Critical | < 24 hours | Time from finding to fix merged |
| MTTR High | < 7 days | Time from finding to fix merged |
| Open Critical Vulnerabilities | 0 | Current scan results |
| Open High Vulnerabilities | < 5 | Current scan results |
| Dependency patch currency | > 90% up to date | SCA scan results |
| Security scan coverage | 100% of repos | CI pipeline audit |
| Secret leak incidents | 0 per quarter | Secret scanning logs |
| Failed security gates | Track trend | CI pipeline metrics |
| SBOM coverage | 100% of production images | Build pipeline audit |
| Penetration test frequency | Annual minimum | Test reports |

### Generating Compliance Report
```bash
# Aggregate scan results into a report
python scripts/generate_security_pipeline.py \
  --provider github \
  --scans sast,sca,secrets,container \
  --output . \
  --compliance-report compliance_report.md
```



---
