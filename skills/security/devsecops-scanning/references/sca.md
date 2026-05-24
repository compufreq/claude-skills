# SCA (Software Composition Analysis) Reference

## Table of Contents
1. Trivy (Dependencies + Containers + IaC)
2. Snyk
3. Dependabot
4. Language-Specific Auditing
5. Secret Scanning Tools
6. Top SCA Remediation Patterns

---

## 1. Trivy

### GitHub Actions — Full Scan
```yaml
# Filesystem scan (dependencies + IaC)
- uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: '.'
    format: 'sarif'
    output: 'trivy-fs.sarif'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'

# Container scan
- uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'ghcr.io/org/myapp:${{ github.sha }}'
    format: 'sarif'
    output: 'trivy-image.sarif'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'
    ignore-unfixed: true      # Skip vulns without a fix

# Upload results
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: 'trivy-fs.sarif'
```

### Trivy Configuration
```yaml
# trivy.yaml
severity:
  - CRITICAL
  - HIGH
vulnerability:
  type:
    - os
    - library
ignore-unfixed: true
db:
  skip-update: false
```

### Trivy Ignore File
```
# .trivyignore
# Ignore specific CVEs (with justification)
CVE-2023-12345  # False positive for our usage — tracked in JIRA-456
CVE-2023-67890  # No fix available, mitigated by WAF rule
```

---

## 2. Snyk

### GitHub Actions
```yaml
- uses: snyk/actions/node@master    # Or: python, golang, docker
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
  with:
    args: --severity-threshold=high --sarif-file-output=snyk.sarif

- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: snyk.sarif
```

### Snyk CLI
```bash
# Test dependencies
snyk test --severity-threshold=high

# Monitor (continuous)
snyk monitor

# Container scan
snyk container test myapp:latest --severity-threshold=high

# IaC scan
snyk iac test ./terraform/ --severity-threshold=high

# Fix dependencies (auto-PR)
snyk fix
```

### Snyk Policy
```yaml
# .snyk
version: v1.25.0
ignore:
  SNYK-JS-LODASH-1234567:
    - '*':
        reason: 'Not exploitable in our context'
        expires: 2025-06-01T00:00:00.000Z
patch: {}
```

---

## 3. Dependabot

### Configuration
```yaml
# .github/dependabot.yml
version: 2
updates:
  # npm
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    reviewers: ["security-team"]
    labels: ["dependencies", "security"]
    ignore:
      - dependency-name: "aws-sdk"
        update-types: ["version-update:semver-major"]
    groups:
      minor-and-patch:
        update-types: ["minor", "patch"]

  # Python
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"

  # Docker
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"

  # Terraform
  - package-ecosystem: "terraform"
    directory: "/infrastructure"
    schedule:
      interval: "monthly"
```

---

## 4. Language-Specific Auditing

```bash
# Node.js
npm audit --audit-level=high
npm audit fix            # Auto-fix compatible updates

# Python
pip audit                # pip-audit package
safety check             # safety package

# Go
govulncheck ./...        # Official Go vulnerability checker

# Ruby
bundle audit check
bundle audit update

# Java (Gradle)
./gradlew dependencyCheckAnalyze    # OWASP dependency-check plugin

# Rust
cargo audit
```

---

## 5. Top SCA Remediation Patterns

### 1. Direct Dependency Vulnerable
```bash
# Update to patched version
npm install lodash@4.17.21          # Specific safe version
pip install requests>=2.32.0        # Minimum safe version
```

### 2. Transitive Dependency Vulnerable
```json
// package.json — force resolution
"overrides": {
  "vulnerable-package": ">=2.0.1"
}

// Or in npm:
"resolutions": {
  "**/vulnerable-package": "^2.0.1"
}
```

### 3. No Fix Available
- Check if vulnerability is exploitable in your context
- Add to ignore list with expiration and justification
- Monitor for fix release
- Consider alternative package

### 4. Major Version Update Required
- Check changelog for breaking changes
- Create separate PR for major updates
- Run full test suite
- Test in staging before production

### 5. License Compliance Issue
```bash
# Check licenses
npx license-checker --failOn "GPL-3.0;AGPL-3.0"
pip-licenses --allow-only="MIT;BSD;Apache"

# Trivy license scan
trivy fs --scanners license --severity CRITICAL .
```



---

<!-- Script: scripts/generate_security_pipeline.py -->

# Script: generate_security_pipeline.py

```python
#!/usr/bin/env python3
"""
Generate security scanning CI configurations for GitHub Actions or GitLab CI.

Usage:
    python generate_security_pipeline.py \
        --provider github|gitlab \
        --scans sast,sca,secrets,container,dast \
        --sast-tool semgrep|codeql \
        --sca-tool trivy|snyk \
        --output .
"""

import argparse
import os


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


def github_security_workflow(scans, sast_tool, sca_tool):
    scan_set = set(scans.split(","))
    jobs = []

    # Secret scanning
    if "secrets" in scan_set:
        jobs.append("""  secret-scan:
    name: Secret Scanning
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: trufflesecurity/trufflehog@v3
        with:
          path: ./
          base: ${{ github.event.pull_request.base.sha || 'HEAD~1' }}
          head: ${{ github.event.pull_request.head.sha || 'HEAD' }}
          extra_args: --only-verified""")

    # SAST
    if "sast" in scan_set:
        if sast_tool == "semgrep":
            jobs.append("""  sast:
    name: SAST (Semgrep)
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/owasp-top-ten
            p/secrets
            p/default
          generateSarif: "1"
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: semgrep.sarif""")
        elif sast_tool == "codeql":
            jobs.append("""  sast:
    name: SAST (CodeQL)
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      actions: read
      contents: read
    strategy:
      matrix:
        language: [javascript]  # Add your languages
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: security-extended
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3""")

    # SCA
    if "sca" in scan_set:
        if sca_tool == "trivy":
            jobs.append("""  sca:
    name: SCA (Trivy)
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-sca.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: trivy-sca.sarif""")
        elif sca_tool == "snyk":
            jobs.append("""  sca:
    name: SCA (Snyk)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high --sarif-file-output=snyk.sarif
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: snyk.sarif""")

    # Container scanning
    if "container" in scan_set:
        jobs.append("""  container-scan:
    name: Container Scan
    runs-on: ubuntu-latest
    needs: [sast, sca]
    if: github.ref == 'refs/heads/main'
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: false
          tags: myapp:scan
          load: true
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:scan'
          format: 'sarif'
          output: 'trivy-image.sarif'
          severity: 'CRITICAL,HIGH'
          ignore-unfixed: true
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: trivy-image.sarif

      # Generate SBOM
      - uses: anchore/sbom-action@v0
        with:
          image: myapp:scan
          format: spdx-json
          output-file: sbom.spdx.json
      - uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.spdx.json""")

    # DAST
    if "dast" in scan_set:
        jobs.append("""  dast:
    name: DAST (ZAP Baseline)
    runs-on: ubuntu-latest
    needs: [container-scan]
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: zaproxy/action-baseline@v0.12.0
        with:
          target: 'https://staging.example.com'
          rules_file_name: '.zap/rules.tsv'
          fail_action: 'true'
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: zap-report
          path: report_html.html""")

    jobs_str = "\n\n".join(jobs)

    return f"""name: Security Scans

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6 AM

concurrency:
  group: security-${{{{ github.ref }}}}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
{jobs_str}
"""


def gitlab_security_pipeline(scans, sast_tool, sca_tool):
    scan_set = set(scans.split(","))
    stages = ["scan"]
    jobs = []

    if "secrets" in scan_set:
        jobs.append("""secret-scan:
  stage: scan
  image: trufflesecurity/trufflehog:latest
  script:
    - trufflehog git file://. --only-verified --fail
  allow_failure: false
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'""")

    if "sast" in scan_set:
        if sast_tool == "semgrep":
            jobs.append("""sast:semgrep:
  stage: scan
  image: returntocorp/semgrep
  script:
    - semgrep scan --config p/owasp-top-ten --config p/default --sarif -o semgrep.sarif .
  artifacts:
    reports:
      sast: semgrep.sarif
    expire_in: 7 days
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'""")
        else:
            jobs.append("""include:
  - template: Security/SAST.gitlab-ci.yml""")

    if "sca" in scan_set:
        if sca_tool == "trivy":
            jobs.append("""sca:trivy:
  stage: scan
  image:
    name: aquasec/trivy:latest
    entrypoint: [""]
  script:
    - trivy fs --severity CRITICAL,HIGH --exit-code 1 --format json -o trivy-sca.json .
  artifacts:
    paths: [trivy-sca.json]
    expire_in: 7 days
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'""")
        else:
            jobs.append("""include:
  - template: Security/Dependency-Scanning.gitlab-ci.yml""")

    if "container" in scan_set:
        jobs.append("""container-scan:
  stage: scan
  image:
    name: aquasec/trivy:latest
    entrypoint: [""]
  script:
    - trivy image --severity CRITICAL,HIGH --exit-code 1 --ignore-unfixed $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'""")

    if "dast" in scan_set:
        jobs.append("""dast:zap:
  stage: scan
  image: zaproxy/zap-stable
  script:
    - zap-baseline.py -t https://staging.example.com -r zap-report.html -I
  artifacts:
    paths: [zap-report.html]
    expire_in: 7 days
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'""")

    stages_str = "\n  - ".join(stages)
    jobs_str = "\n\n".join(jobs)

    return f"""stages:
  - {stages_str}

{jobs_str}
"""


def generate_zap_rules():
    return """10010\tIGNORE\t\t# Cookie No HttpOnly Flag
10011\tWARN\t\t# Cookie Without Secure Flag
10015\tFAIL\t\t# Incomplete or No Cache-control Headers
10017\tIGNORE\t\t# Cross-Domain JavaScript Source File Inclusion
10020\tFAIL\t\t# X-Frame-Options Header
10021\tFAIL\t\t# X-Content-Type-Options Missing
10035\tFAIL\t\t# Strict-Transport-Security Header
10036\tWARN\t\t# HTTP Server Response Header
10038\tFAIL\t\t# Content Security Policy Missing
10098\tIGNORE\t\t# Cross-Domain Misconfiguration
40012\tFAIL\t\t# Cross Site Scripting (Reflected)
40014\tFAIL\t\t# Cross Site Scripting (Persistent)
40018\tFAIL\t\t# SQL Injection
40019\tFAIL\t\t# SQL Injection (MySQL)
40020\tFAIL\t\t# SQL Injection (Hypersonic)
40021\tFAIL\t\t# SQL Injection (Oracle)
40022\tFAIL\t\t# SQL Injection (PostgreSQL)
90001\tWARN\t\t# Insecure JSF ViewState
90033\tIGNORE\t\t# Loosely Scoped Cookie
"""


def generate_semgrep_config():
    return """rules:
  - p/owasp-top-ten
  - p/secrets
  - p/default

exclude:
  - "test/**"
  - "**/*_test.*"
  - "node_modules/**"
  - "vendor/**"
  - ".git/**"
"""


def generate_trivyignore():
    return """# .trivyignore
# Add CVEs to ignore with justification
# CVE-2024-XXXXX  # False positive — see JIRA-123
"""


def generate_pre_commit():
    return """repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.4
    hooks:
      - id: gitleaks

  - repo: https://github.com/returntocorp/semgrep
    rev: v1.56.0
    hooks:
      - id: semgrep
        args: ['--config', 'p/secrets', '--config', 'p/owasp-top-ten']
"""


def main():
    parser = argparse.ArgumentParser(description="Generate Security Scanning Pipeline")
    parser.add_argument("--provider", choices=["github", "gitlab"], default="github")
    parser.add_argument("--scans", default="sast,sca,secrets,container",
                        help="Comma-separated: sast,sca,secrets,container,dast")
    parser.add_argument("--sast-tool", choices=["semgrep", "codeql"], default="semgrep")
    parser.add_argument("--sca-tool", choices=["trivy", "snyk"], default="trivy")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()

    print(f"\n🔒 Generating security pipeline ({args.provider})\n")
    print(f"   Scans: {args.scans}")
    print(f"   SAST: {args.sast_tool}")
    print(f"   SCA: {args.sca_tool}\n")

    if args.provider == "github":
        workflow = github_security_workflow(args.scans, args.sast_tool, args.sca_tool)
        create_file(os.path.join(args.output, ".github", "workflows", "security.yml"), workflow)
    elif args.provider == "gitlab":
        pipeline = gitlab_security_pipeline(args.scans, args.sast_tool, args.sca_tool)
        create_file(os.path.join(args.output, ".gitlab-ci-security.yml"), pipeline)

    # Supporting config files
    scan_set = set(args.scans.split(","))

    if "dast" in scan_set:
        create_file(os.path.join(args.output, ".zap", "rules.tsv"), generate_zap_rules())

    if "sast" in scan_set and args.sast_tool == "semgrep":
        create_file(os.path.join(args.output, ".semgrep.yml"), generate_semgrep_config())

    if "sca" in scan_set:
        create_file(os.path.join(args.output, ".trivyignore"), generate_trivyignore())

    if "secrets" in scan_set:
        create_file(os.path.join(args.output, ".pre-commit-config.yaml"), generate_pre_commit())

    print(f"\n✅ Security pipeline generated")
    print(f"   CI config: {'security.yml' if args.provider == 'github' else '.gitlab-ci-security.yml'}")
    print(f"   Supporting configs: .semgrep.yml, .trivyignore, .zap/rules.tsv, .pre-commit-config.yaml")


if __name__ == "__main__":
    main()

```
