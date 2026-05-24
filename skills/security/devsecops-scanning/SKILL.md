---
name: devsecops-scanning
description: >
  Comprehensive DevSecOps security scanning skill covering SAST, DAST, SCA, secret scanning,
  compliance frameworks, and remediation guidance. Use this skill whenever the user mentions
  SAST, DAST, SCA, security scanning, static analysis, dynamic analysis, dependency scanning,
  vulnerability scanning, secret scanning, Semgrep, SonarQube, CodeQL, OWASP ZAP, Burp Suite,
  Snyk, Dependabot, Trivy, TruffleHog, GitLeaks, Gitleaks, software composition analysis,
  CVE, vulnerability, security pipeline, shift-left security, OWASP Top 10, CIS benchmark,
  SOC2, compliance scanning, code security, supply chain security, SBOM, container scanning,
  image scanning, license compliance, security gate, security policy, remediation, or any request
  involving integrating security scanning into CI/CD pipelines or finding and fixing security
  vulnerabilities in code, dependencies, containers, or infrastructure. This skill complements
  ci-cd-pipelines for the security integration layer.
---

# DevSecOps Scanning

A production-grade skill for integrating security scanning into the development lifecycle.
Covers SAST, DAST, SCA, secret scanning, compliance frameworks, and actionable remediation.

## Quick Reference

| Scan Type | What It Finds | When to Run | Reference |
|-----------|--------------|-------------|-----------|
| SAST | Code vulnerabilities (SQLi, XSS, etc.) | Every PR | `references/sast.md` |
| DAST | Runtime vulnerabilities (in running app) | Staging deploy | `references/dast.md` |
| SCA | Vulnerable dependencies, license issues | Every PR | `references/sca.md` |
| Secret Scanning | Leaked credentials in code/history | Every push | `references/secrets.md` |
| Compliance | Framework alignment (OWASP, CIS, SOC2) | Periodic | `references/compliance.md` |

## Security Scanning Pipeline

```
Push/PR → Secret Scan → SAST → SCA → Build → Container Scan → DAST (staging)
            ↓              ↓       ↓                ↓              ↓
         Block if       Warn/    Warn/           Warn/         Report
         secrets found  Block    Block           Block         findings
```

### Pipeline Integration Strategy

| Stage | Tool | Blocking? | Speed |
|-------|------|-----------|-------|
| Pre-commit | GitLeaks, Semgrep (subset) | Yes | < 5 sec |
| PR / Push | SAST (Semgrep/CodeQL), SCA (Trivy/Snyk), Secrets (TruffleHog) | Configurable | 2-5 min |
| Build | Container scan (Trivy), SBOM generation | Warn | 1-2 min |
| Staging | DAST (ZAP baseline), API scan | Warn | 5-15 min |
| Scheduled | Full DAST, compliance audit, license audit | Report only | 30+ min |

### Severity → Action Mapping

| Severity | PR Policy | Production Policy |
|----------|-----------|------------------|
| Critical | Block merge | Block deploy, immediate fix |
| High | Block merge | Fix within 7 days |
| Medium | Warn, don't block | Fix within 30 days |
| Low | Informational | Fix when convenient |

---

## Tool Comparison

### SAST Tools

| Tool | Languages | CI Integration | License | Best For |
|------|----------|---------------|---------|---------|
| **Semgrep** | 30+ | GitHub/GitLab/Jenkins | Free (OSS rules) | Custom rules, fast |
| **CodeQL** | 10+ | GitHub native | Free (GitHub) | Deep analysis, GitHub-native |
| **SonarQube** | 30+ | All CI platforms | Free (Community) | Quality + security combined |
| **Bandit** | Python | Any | Free | Python-specific |
| **Brakeman** | Ruby | Any | Free | Rails-specific |

### SCA Tools

| Tool | Ecosystems | CI Integration | License | Best For |
|------|-----------|---------------|---------|---------|
| **Trivy** | All + containers | All | Free | Containers + deps + IaC |
| **Snyk** | All | All | Freemium | Developer-friendly, fix PRs |
| **Dependabot** | All | GitHub native | Free | GitHub-native, auto-PRs |
| **npm audit** | Node.js | Any | Free | Quick Node.js check |
| **pip audit** | Python | Any | Free | Quick Python check |

### Secret Scanning Tools

| Tool | Detection | CI Integration | Best For |
|------|----------|---------------|---------|
| **GitHub Secret Scanning** | Push protection | GitHub native | GitHub repos |
| **TruffleHog** | Regex + entropy + verified | All | Deep history scanning |
| **GitLeaks** | Regex patterns | All | Fast, pre-commit |
| **detect-secrets** | Regex + heuristics | All | Custom rules |

---

## Scripts

### generate_security_pipeline.py
Generate security scanning CI configurations for GitHub Actions or GitLab CI.

```bash
python scripts/generate_security_pipeline.py \
  --provider github|gitlab \
  --scans sast,sca,secrets,container,dast \
  --sast-tool semgrep|codeql|sonarqube \
  --sca-tool trivy|snyk \
  --output .
```

---

## Best Practices

1. **Shift left** — scan as early as possible (pre-commit > PR > build > deploy)
2. **Don't block everything** — start with critical/high only, expand over time
3. **Fix the pipeline, not just the findings** — make secure defaults easy
4. **Triage before acting** — not all findings are exploitable
5. **Track metrics** — mean time to remediate, finding trends, false positive rate
6. **Automate remediation** — Dependabot/Snyk auto-PRs for dependency updates
7. **Baseline existing debt** — don't block PRs for pre-existing issues
8. **Developer-friendly output** — inline PR comments > report files
9. **Regular audits** — scheduled full scans catch what incremental misses
10. **SBOM for everything** — know what's in your software at all times



---
