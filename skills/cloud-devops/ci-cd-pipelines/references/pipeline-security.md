# Pipeline Security Reference

## Table of Contents
1. Secrets Management
2. OIDC (Keyless Authentication)
3. Least Privilege
4. Supply Chain Security
5. Pipeline Hardening Checklist

---

## 1. Secrets Management

### Rules
1. **Never hardcode secrets** in pipeline files, Dockerfiles, or code
2. **Never echo/print secrets** in logs (use masking)
3. **Rotate secrets regularly** (90 days for most, 30 for high-value)
4. **Scope secrets narrowly** — environment-level > repo-level > org-level
5. **Audit secret access** — know who/what can read each secret

### Platform-Specific Secret Storage

**GitHub Actions:**
```yaml
# Repository secrets: Settings → Secrets → Actions
# Organization secrets: Org → Settings → Secrets
# Environment secrets: Settings → Environments → [name] → Secrets

env:
  API_KEY: ${{ secrets.API_KEY }}       # Automatically masked in logs
```

**GitLab CI:**
```yaml
# Project → Settings → CI/CD → Variables
# Group → Settings → CI/CD → Variables
# Protected: Only available on protected branches
# Masked: Hidden in logs

variables:
  API_KEY: $API_KEY                     # Set as CI/CD variable
```

**Jenkins:**
```groovy
// Manage Jenkins → Manage Credentials → [domain] → Add
withCredentials([string(credentialsId: 'api-key', variable: 'API_KEY')]) {
    sh 'curl -H "Authorization: Bearer $API_KEY" ...'
}
```

### Secret Scanning in CI
```yaml
# GitHub Actions — scan for leaked secrets
- uses: trufflesecurity/trufflehog@v3
  with:
    path: ./
    base: ${{ github.event.pull_request.base.sha }}
    head: ${{ github.event.pull_request.head.sha }}

# GitLab built-in
include:
  - template: Security/Secret-Detection.gitlab-ci.yml
```

---

## 2. OIDC (Keyless Authentication)

OIDC eliminates the need for long-lived cloud credentials in CI. The CI provider
generates a short-lived token that the cloud provider trusts.

### GitHub Actions → AWS (OIDC)
```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/GitHubActionsRole
          aws-region: us-east-1
          # No access key or secret needed!

      - run: aws s3 sync ./dist s3://my-bucket/
```

### GitHub Actions → GCP (OIDC)
```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: 'projects/123/locations/global/workloadIdentityPools/github/providers/github'
    service_account: 'ci-deploy@my-project.iam.gserviceaccount.com'

- uses: google-github-actions/setup-gcloud@v2
- run: gcloud run deploy myapp --image gcr.io/my-project/myapp:${{ github.sha }}
```

### GitHub Actions → Azure (OIDC)
```yaml
- uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    # No client secret needed with OIDC!
```

### Why OIDC > Static Credentials
- **No secrets to leak** — no access keys stored anywhere
- **Short-lived tokens** — tokens expire in minutes, not months
- **Auditable** — cloud provider logs show which pipeline requested access
- **No rotation needed** — tokens are generated fresh each time

---

## 3. Least Privilege

### GitHub Actions Permissions
```yaml
# Restrict at workflow level
permissions:
  contents: read          # Only read code
  packages: write         # Push to GitHub Packages
  id-token: write         # OIDC
  # Everything else is denied

# Or restrict per-job
jobs:
  build:
    permissions:
      contents: read
  deploy:
    permissions:
      contents: read
      id-token: write     # Only deploy job gets OIDC
```

### Action Pinning
```yaml
# BAD — mutable tag, can be compromised
- uses: actions/checkout@v4

# GOOD — pinned to specific commit SHA
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1

# Tools like Dependabot or Renovate can auto-update SHA pins
```

### Runner Security
- **GitHub-hosted runners**: Ephemeral, clean VM per job (most secure)
- **Self-hosted runners**: Persistent, must be hardened
  - Run in isolated VMs or containers
  - Use ephemeral runners (scale to zero, fresh per job)
  - Never run on development machines
  - Restrict to private repositories only
  - Keep runner software updated

---

## 4. Supply Chain Security

### Dependency Verification
```yaml
# GitHub — Dependency review on PRs
- uses: actions/dependency-review-action@v4
  with:
    fail-on-severity: moderate
    deny-licenses: GPL-3.0, AGPL-3.0

# GitLab — built-in
include:
  - template: Security/Dependency-Scanning.gitlab-ci.yml

# Generic — npm audit / pip audit
- run: npm audit --audit-level=high
- run: pip audit
```

### Container Image Scanning
```yaml
# Trivy (popular, open-source)
- uses: aquasecurity/trivy-action@master
  with:
    image-ref: myapp:${{ github.sha }}
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
    exit-code: 1                  # Fail on critical/high vulnerabilities

# Grype
- run: |
    curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s
    grype myapp:${{ github.sha }} --fail-on high
```

### SBOM (Software Bill of Materials)
```yaml
# Generate SBOM with Syft
- uses: anchore/sbom-action@v0
  with:
    image: myapp:${{ github.sha }}
    format: spdx-json
    output-file: sbom.spdx.json
    upload-artifact: true

# Attach SBOM to container image
- run: cosign attach sbom --sbom sbom.spdx.json myapp:${{ github.sha }}
```

### Image Signing (Cosign)
```yaml
# Sign container image (keyless with OIDC)
- uses: sigstore/cosign-installer@v3
- run: cosign sign --yes ghcr.io/myorg/myapp:${{ github.sha }}

# Verify signature before deploying
- run: cosign verify ghcr.io/myorg/myapp:${{ github.sha }}
```

---

## 5. Pipeline Hardening Checklist

### Secrets
- [ ] No secrets hardcoded in pipeline files
- [ ] All secrets stored in platform secret management
- [ ] Secrets scoped to minimum required level (env > repo > org)
- [ ] Secret rotation policy in place (90 days max)
- [ ] Secret scanning enabled on repository
- [ ] Secrets masked in CI logs

### Authentication
- [ ] OIDC used for cloud provider auth (no static keys)
- [ ] Service accounts have minimum required permissions
- [ ] No shared credentials between environments
- [ ] MFA enabled on CI platform accounts

### Pipeline Integrity
- [ ] Actions/images pinned to SHA (not mutable tags)
- [ ] Dependabot/Renovate configured for action updates
- [ ] Branch protection enabled on main/release branches
- [ ] Required reviewers for pipeline config changes
- [ ] Pipeline runs only on trusted branches for deployments

### Supply Chain
- [ ] Dependency scanning on every PR
- [ ] Container image scanning before deploy
- [ ] SBOM generated for production artifacts
- [ ] Container images signed with Cosign/Notary
- [ ] License compliance checking enabled

### Runtime
- [ ] Build artifacts are immutable (content-addressed)
- [ ] Same artifact deployed to all environments
- [ ] Deployment audit trail (who deployed what, when)
- [ ] Automatic rollback on health check failure
- [ ] Pipeline metrics tracked (DORA metrics)



---

<!-- Script: scripts/generate_pipeline.py -->

# Script: generate_pipeline.py

```python
#!/usr/bin/env python3
"""
Generate CI/CD pipeline configurations for GitHub Actions, GitLab CI, or Jenkins.
Supports Node.js, Python, Go, Java, and Docker application types.

Usage:
    python generate_pipeline.py \
        --provider github|gitlab|jenkins \
        --app-type nodejs|python|go|java|docker \
        --features test,lint,build,scan,deploy,docker \
        --environments dev,staging,production \
        --output .

    python generate_pipeline.py \
        --provider github \
        --app-type python \
        --features test,lint,build,docker,deploy \
        --environments staging,production \
        --docker-registry ghcr.io \
        --output .
"""

import argparse
import os
import sys


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


# ── App Type Configurations ──────────────────────────────────────────

APP_CONFIGS = {
    "nodejs": {
        "image": "node:20-alpine",
        "setup": "- uses: actions/setup-node@v4\n        with:\n          node-version: '20'\n          cache: 'npm'",
        "install": "npm ci",
        "lint": "npm run lint",
        "test": "npm test",
        "build": "npm run build",
        "test_cmd_gitlab": "npm test",
        "cache_paths": "node_modules/\n      .npm/",
        "cache_key_files": "package-lock.json",
        "dockerfile": """FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --production=false
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./
EXPOSE 3000
CMD ["node", "dist/index.js"]
""",
        "jenkins_image": "node:20-alpine",
        "jenkins_install": "sh 'npm ci'",
        "jenkins_test": "sh 'npm test'",
        "jenkins_build": "sh 'npm run build'",
        "jenkins_lint": "sh 'npm run lint'",
    },
    "python": {
        "image": "python:3.12-slim",
        "setup": "- uses: actions/setup-python@v5\n        with:\n          python-version: '3.12'\n          cache: 'pip'",
        "install": "pip install -r requirements.txt",
        "lint": "ruff check . && ruff format --check .",
        "test": "pytest --cov --junitxml=junit.xml",
        "build": "python -m build",
        "test_cmd_gitlab": "pytest --cov --junitxml=junit.xml",
        "cache_paths": ".venv/\n      .cache/pip/",
        "cache_key_files": "requirements*.txt",
        "dockerfile": """FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
        "jenkins_image": "python:3.12-slim",
        "jenkins_install": "sh 'pip install -r requirements.txt'",
        "jenkins_test": "sh 'pytest --cov --junitxml=junit.xml'",
        "jenkins_build": "sh 'python -m build'",
        "jenkins_lint": "sh 'ruff check . && ruff format --check .'",
    },
    "go": {
        "image": "golang:1.22-alpine",
        "setup": "- uses: actions/setup-go@v5\n        with:\n          go-version: '1.22'\n          cache: true",
        "install": "go mod download",
        "lint": "golangci-lint run",
        "test": "go test -v -race -coverprofile=coverage.out ./...",
        "build": "CGO_ENABLED=0 go build -o bin/app ./cmd/app",
        "test_cmd_gitlab": "go test -v -race ./...",
        "cache_paths": "/go/pkg/mod/",
        "cache_key_files": "go.sum",
        "dockerfile": """FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /bin/app ./cmd/app

FROM alpine:3.19
RUN apk --no-cache add ca-certificates
COPY --from=builder /bin/app /app
EXPOSE 8080
ENTRYPOINT ["/app"]
""",
        "jenkins_image": "golang:1.22-alpine",
        "jenkins_install": "sh 'go mod download'",
        "jenkins_test": "sh 'go test -v -race ./...'",
        "jenkins_build": "sh 'CGO_ENABLED=0 go build -o bin/app ./cmd/app'",
        "jenkins_lint": "sh 'golangci-lint run'",
    },
    "java": {
        "image": "eclipse-temurin:21-jdk",
        "setup": "- uses: actions/setup-java@v4\n        with:\n          distribution: 'temurin'\n          java-version: '21'\n          cache: 'gradle'",
        "install": "./gradlew dependencies",
        "lint": "./gradlew checkstyleMain",
        "test": "./gradlew test",
        "build": "./gradlew bootJar",
        "test_cmd_gitlab": "./gradlew test",
        "cache_paths": ".gradle/\n      ~/.gradle/caches/",
        "cache_key_files": "**/*.gradle*,**/gradle-wrapper.properties",
        "dockerfile": """FROM eclipse-temurin:21-jdk AS builder
WORKDIR /app
COPY gradle/ gradle/
COPY gradlew build.gradle* settings.gradle* ./
RUN ./gradlew dependencies --no-daemon
COPY src/ src/
RUN ./gradlew bootJar --no-daemon

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=builder /app/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
""",
        "jenkins_image": "eclipse-temurin:21-jdk",
        "jenkins_install": "sh './gradlew dependencies'",
        "jenkins_test": "sh './gradlew test'",
        "jenkins_build": "sh './gradlew bootJar'",
        "jenkins_lint": "sh './gradlew checkstyleMain'",
    },
    "docker": {
        "image": "docker:27",
        "setup": "- uses: docker/setup-buildx-action@v3",
        "install": "",
        "lint": "hadolint Dockerfile",
        "test": "docker compose -f docker-compose.test.yml up --abort-on-container-exit",
        "build": "docker build -t myapp .",
        "test_cmd_gitlab": "docker compose -f docker-compose.test.yml up --abort-on-container-exit",
        "cache_paths": "",
        "cache_key_files": "Dockerfile",
        "dockerfile": "",
        "jenkins_image": "docker:27-dind",
        "jenkins_install": "",
        "jenkins_test": "sh 'docker compose -f docker-compose.test.yml up --abort-on-container-exit'",
        "jenkins_build": "sh 'docker build -t myapp .'",
        "jenkins_lint": "sh 'hadolint Dockerfile'",
    },
}


def generate_github_actions(app_type, features, environments, docker_registry, output_dir):
    """Generate GitHub Actions workflow."""
    cfg = APP_CONFIGS[app_type]
    feat = set(features.split(","))
    envs = environments.split(",") if environments else []

    jobs = []

    # Lint job
    if "lint" in feat:
        jobs.append(f"""  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      {cfg['setup']}
      - run: {cfg['install']}
      - name: Lint
        run: {cfg['lint']}""")

    # Test job
    if "test" in feat:
        needs = "    needs: lint" if "lint" in feat else ""
        jobs.append(f"""  test:
    runs-on: ubuntu-latest
{needs}
    steps:
      - uses: actions/checkout@v4
      {cfg['setup']}
      - run: {cfg['install']}
      - name: Test
        run: {cfg['test']}
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: |
            junit.xml
            coverage/""")

    # Build job
    if "build" in feat:
        prev = []
        if "lint" in feat:
            prev.append("lint")
        if "test" in feat:
            prev.append("test")
        needs_str = f"    needs: [{', '.join(prev)}]" if prev else ""
        jobs.append(f"""  build:
    runs-on: ubuntu-latest
{needs_str}
    steps:
      - uses: actions/checkout@v4
      {cfg['setup']}
      - run: {cfg['install']}
      - name: Build
        run: {cfg['build']}
      - uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: dist/""")

    # Docker build
    if "docker" in feat:
        registry = docker_registry or "ghcr.io"
        prev_jobs = [j for j in ["lint", "test", "build"] if j in feat]
        needs_str = f"    needs: [{', '.join(prev_jobs)}]" if prev_jobs else ""
        jobs.append(f"""  docker:
    runs-on: ubuntu-latest
{needs_str}
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v')
    permissions:
      contents: read
      packages: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: {registry}
          username: ${{{{ github.actor }}}}
          password: ${{{{ secrets.GITHUB_TOKEN }}}}
      - uses: docker/metadata-action@v5
        id: meta
        with:
          images: {registry}/${{{{ github.repository }}}}
          tags: |
            type=sha,prefix=
            type=ref,event=branch
            type=semver,pattern={{{{version}}}}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{{{ steps.meta.outputs.tags }}}}
          cache-from: type=gha
          cache-to: type=gha,mode=max""")

    # Scan job
    if "scan" in feat:
        jobs.append(f"""  scan:
    runs-on: ubuntu-latest
    needs: [{"docker" if "docker" in feat else "build" if "build" in feat else "test"}]
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'""")

    # Deploy jobs
    if "deploy" in feat:
        for i, env_name in enumerate(envs):
            prev_job = envs[i - 1] if i > 0 else ("docker" if "docker" in feat else "build" if "build" in feat else "test")
            prev_ref = f"deploy-{envs[i - 1]}" if i > 0 else prev_job
            when_clause = ""
            if env_name in ("dev", "development"):
                when_clause = "\n    if: github.ref == 'refs/heads/develop'"
            elif env_name in ("staging",):
                when_clause = "\n    if: github.ref == 'refs/heads/main'"
            elif env_name in ("production", "prod"):
                when_clause = "\n    if: github.ref == 'refs/heads/main'"

            jobs.append(f"""  deploy-{env_name}:
    runs-on: ubuntu-latest
    needs: {prev_ref}{when_clause}
    environment:
      name: {env_name}
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to {env_name}
        run: echo "Deploying to {env_name}..."
        # TODO: Add actual deployment commands""")

    jobs_str = "\n\n".join(jobs)

    workflow = f"""name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

concurrency:
  group: ${{{{ github.workflow }}}}-${{{{ github.ref }}}}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
{jobs_str}
"""
    create_file(os.path.join(output_dir, ".github", "workflows", "ci.yml"), workflow)

    # Generate Dockerfile if docker feature is enabled
    if "docker" in feat and cfg.get("dockerfile"):
        create_file(os.path.join(output_dir, "Dockerfile"), cfg["dockerfile"])


def generate_gitlab_ci(app_type, features, environments, docker_registry, output_dir):
    """Generate GitLab CI pipeline."""
    cfg = APP_CONFIGS[app_type]
    feat = set(features.split(","))
    envs = environments.split(",") if environments else []

    stages = []
    jobs = []

    if "lint" in feat:
        stages.append("lint")
    if "test" in feat:
        stages.append("test")
    if "build" in feat or "docker" in feat:
        stages.append("build")
    if "scan" in feat:
        stages.append("scan")
    if "deploy" in feat:
        stages.append("deploy")

    stages_str = "\n  - ".join(stages)

    # Default settings
    defaults = f"""default:
  image: {cfg['image']}
  cache:
    key: ${{CI_COMMIT_REF_SLUG}}
    paths:
      - {cfg['cache_paths']}
"""
    if cfg.get("install"):
        defaults += f"""  before_script:
    - {cfg['install']}
"""

    # Lint
    if "lint" in feat:
        jobs.append(f"""lint:
  stage: lint
  script:
    - {cfg['lint']}
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_COMMIT_BRANCH == "develop"'""")

    # Test
    if "test" in feat:
        jobs.append(f"""test:
  stage: test
  script:
    - {cfg['test_cmd_gitlab']}
  artifacts:
    when: always
    reports:
      junit: junit.xml
    expire_in: 7 days""")

    # Build / Docker
    if "docker" in feat:
        registry = docker_registry or "$CI_REGISTRY"
        jobs.append(f"""build:docker:
  stage: build
  image: docker:27
  services:
    - docker:27-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t {registry}/$CI_PROJECT_PATH:$CI_COMMIT_SHA .
    - docker push {registry}/$CI_PROJECT_PATH:$CI_COMMIT_SHA
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'""")
    elif "build" in feat:
        jobs.append(f"""build:
  stage: build
  script:
    - {cfg['build']}
  artifacts:
    paths: [dist/]
    expire_in: 7 days""")

    # Deploy
    if "deploy" in feat:
        for i, env_name in enumerate(envs):
            when_clause = 'when: on_success' if env_name != "production" else 'when: manual\n      allow_failure: false'
            branch_rule = "develop" if env_name in ("dev", "development") else "main"
            jobs.append(f"""deploy:{env_name}:
  stage: deploy
  environment:
    name: {env_name}
  script:
    - echo "Deploying to {env_name}..."
  rules:
    - if: '$CI_COMMIT_BRANCH == "{branch_rule}"'
      {when_clause}""")

    jobs_str = "\n\n".join(jobs)

    pipeline = f"""stages:
  - {stages_str}

{defaults}
{jobs_str}
"""
    create_file(os.path.join(output_dir, ".gitlab-ci.yml"), pipeline)

    if "docker" in feat and cfg.get("dockerfile"):
        create_file(os.path.join(output_dir, "Dockerfile"), cfg["dockerfile"])


def generate_jenkinsfile(app_type, features, environments, docker_registry, output_dir):
    """Generate Jenkinsfile."""
    cfg = APP_CONFIGS[app_type]
    feat = set(features.split(","))
    envs = environments.split(",") if environments else []

    stages = []

    if "lint" in feat:
        stages.append(f"""        stage('Lint') {{
            steps {{
                {cfg['jenkins_lint']}
            }}
        }}""")

    if "test" in feat:
        stages.append(f"""        stage('Test') {{
            steps {{
                {cfg['jenkins_test']}
            }}
            post {{
                always {{
                    junit allowEmptyResults: true, testResults: '**/junit.xml'
                }}
            }}
        }}""")

    if "build" in feat:
        stages.append(f"""        stage('Build') {{
            steps {{
                {cfg['jenkins_build']}
            }}
        }}""")

    if "docker" in feat:
        registry = docker_registry or "ghcr.io"
        stages.append(f"""        stage('Docker Build') {{
            when {{
                branch 'main'
            }}
            steps {{
                script {{
                    def image = docker.build("{registry}/${{env.JOB_NAME.toLowerCase()}}:${{env.GIT_COMMIT}}")
                    docker.withRegistry('https://{registry}', 'registry-credentials') {{
                        image.push()
                        image.push('latest')
                    }}
                }}
            }}
        }}""")

    for env_name in envs:
        when_clause = "branch 'main'" if env_name != "production" else "tag pattern: 'v\\\\d+\\\\.\\\\d+\\\\.\\\\d+', comparator: 'REGEXP'"
        input_block = ""
        if env_name == "production":
            input_block = """
            input {
                message 'Deploy to production?'
                ok 'Deploy'
            }"""

        stages.append(f"""        stage('Deploy {env_name.title()}') {{
            when {{
                {when_clause}
            }}{input_block}
            steps {{
                sh "./deploy.sh {env_name} ${{env.GIT_COMMIT}}"
            }}
        }}""")

    stages_str = "\n\n".join(stages)
    install = cfg.get("jenkins_install", "")
    install_step = f"""
        stage('Install') {{
            steps {{
                {install}
            }}
        }}

""" if install else ""

    jenkinsfile = f"""pipeline {{
    agent {{
        docker {{
            image '{cfg['jenkins_image']}'
        }}
    }}

    options {{
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds(abortPrevious: true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }}

    environment {{
        CI = 'true'
    }}

    stages {{
{install_step}{stages_str}
    }}

    post {{
        success {{
            echo '✅ Pipeline succeeded'
        }}
        failure {{
            echo '🔴 Pipeline failed'
        }}
        always {{
            cleanWs()
        }}
    }}
}}
"""
    create_file(os.path.join(output_dir, "Jenkinsfile"), jenkinsfile)

    if "docker" in feat and cfg.get("dockerfile"):
        create_file(os.path.join(output_dir, "Dockerfile"), cfg["dockerfile"])


GENERATORS = {
    "github": generate_github_actions,
    "gitlab": generate_gitlab_ci,
    "jenkins": generate_jenkinsfile,
}


def main():
    parser = argparse.ArgumentParser(description="Generate CI/CD Pipeline Configuration")
    parser.add_argument("--provider", choices=GENERATORS.keys(), required=True)
    parser.add_argument("--app-type", choices=APP_CONFIGS.keys(), required=True)
    parser.add_argument("--features", default="lint,test,build,docker,deploy",
                        help="Comma-separated: lint,test,build,scan,deploy,docker")
    parser.add_argument("--environments", default="staging,production",
                        help="Comma-separated: dev,staging,production")
    parser.add_argument("--docker-registry", default=None, help="Container registry URL")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()

    print(f"\n🔧 Generating {args.provider.title()} pipeline for {args.app_type}\n")
    print(f"   Features: {args.features}")
    print(f"   Environments: {args.environments}")
    print(f"   Registry: {args.docker_registry or 'default'}\n")

    GENERATORS[args.provider](
        args.app_type, args.features, args.environments,
        args.docker_registry, args.output
    )

    print(f"\n✅ Pipeline generated successfully")


if __name__ == "__main__":
    main()

```
