# Pipeline Patterns Reference

## Table of Contents
1. Monorepo Pipelines
2. Multi-Environment Promotion
3. Parallel Testing & Matrix
4. Artifact Management
5. Container Registry Integration
6. DORA Metrics

---

## 1. Monorepo Pipelines

### Challenge
In a monorepo, building and testing everything on every commit is wasteful. Pipelines should
only run for the services/packages that changed.

### Path-Based Triggering

**GitHub Actions:**
```yaml
# Detect changes and trigger selectively
jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      api: ${{ steps.filter.outputs.api }}
      web: ${{ steps.filter.outputs.web }}
      shared: ${{ steps.filter.outputs.shared }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            api:
              - 'services/api/**'
              - 'packages/shared/**'
            web:
              - 'apps/web/**'
              - 'packages/shared/**'
            shared:
              - 'packages/shared/**'

  build-api:
    needs: detect-changes
    if: needs.detect-changes.outputs.api == 'true'
    uses: ./.github/workflows/build-service.yml
    with:
      service: api

  build-web:
    needs: detect-changes
    if: needs.detect-changes.outputs.web == 'true'
    uses: ./.github/workflows/build-service.yml
    with:
      service: web
```

**GitLab CI (Parent-Child):**
```yaml
# Root .gitlab-ci.yml
stages: [trigger]

trigger:api:
  stage: trigger
  trigger:
    include: services/api/.gitlab-ci.yml
    strategy: depend
  rules:
    - changes: [services/api/**]

trigger:web:
  stage: trigger
  trigger:
    include: apps/web/.gitlab-ci.yml
    strategy: depend
  rules:
    - changes: [apps/web/**]
```

### Shared Dependencies
When a shared package changes, rebuild all dependent services:
```yaml
# If packages/shared changes, both api and web should rebuild
api:
  - 'services/api/**'
  - 'packages/shared/**'    # Shared dependency
web:
  - 'apps/web/**'
  - 'packages/shared/**'    # Same shared dependency
```

### Monorepo Best Practices
1. Each service has its own CI config (or uses reusable workflows)
2. Shared packages trigger all dependent services
3. Infrastructure changes (`terraform/`, `k8s/`) trigger infra pipelines
4. CI config changes (`.github/`, `.gitlab-ci.yml`) trigger full pipeline
5. Use `paths-ignore` for docs, README changes

---

## 2. Multi-Environment Promotion

### Promotion Flow
```
Build → Dev → Staging → Production
         ↓        ↓          ↓
      Auto     Auto/Manual  Manual + Approval
```

### Key Principle: Same Artifact, Different Config

```yaml
# Build ONCE, deploy the same artifact everywhere
build:
  outputs:
    image-tag: ghcr.io/org/app:${{ github.sha }}

deploy-dev:
  needs: build
  environment: development
  env:
    CONFIG_FILE: config/dev.yaml

deploy-staging:
  needs: deploy-dev
  environment: staging
  env:
    CONFIG_FILE: config/staging.yaml

deploy-production:
  needs: deploy-staging
  environment: production    # Requires approval
  env:
    CONFIG_FILE: config/production.yaml
```

### Environment Configuration

```
config/
├── dev.yaml          # Development settings
├── staging.yaml      # Staging settings
├── production.yaml   # Production settings
└── base.yaml         # Shared settings
```

Each environment overrides base config. The application binary is identical — only the
configuration changes between environments.

### Promotion Patterns

| Pattern | How | Best For |
|---------|-----|---------|
| **Auto-promote** | Pass all tests → auto deploy to next env | Dev → Staging |
| **Manual gate** | Human clicks "approve" | Staging → Production |
| **Scheduled** | Deploy at specific time (e.g., Tuesday 2pm) | Production releases |
| **Canary** | Deploy to 5% → monitor → expand | High-traffic production |
| **Blue-green** | Deploy to inactive, swap traffic | Zero-downtime production |

### Rollback Strategy
```yaml
# Automated rollback on health check failure
deploy:
  steps:
    - name: Deploy
      run: kubectl set image deployment/app app=myapp:${{ github.sha }}

    - name: Health Check
      run: |
        for i in $(seq 1 30); do
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://app.example.com/health)
          if [ "$STATUS" = "200" ]; then exit 0; fi
          sleep 10
        done
        echo "Health check failed — rolling back"
        kubectl rollout undo deployment/app
        exit 1
```

---

## 3. Parallel Testing & Matrix

### Test Splitting (Parallel Workers)

```yaml
# GitHub Actions — split tests across N workers
test:
  strategy:
    matrix:
      shard: [1, 2, 3, 4]
  steps:
    - run: |
        TOTAL_SHARDS=4
        npx jest --shard=${{ matrix.shard }}/${TOTAL_SHARDS}
```

### Test Type Parallelism
```yaml
# Run different test types in parallel
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:unit

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres: { image: 'postgres:16', env: { POSTGRES_PASSWORD: test } }
    steps:
      - run: npm run test:integration

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - run: npx playwright test

  # All must pass
  all-tests-pass:
    needs: [unit-tests, integration-tests, e2e-tests]
    runs-on: ubuntu-latest
    steps:
      - run: echo "All tests passed"
```

### Matrix Best Practices
- Use `fail-fast: false` so one failure doesn't cancel other jobs
- Use `exclude` to skip invalid combinations
- Use `include` to add extra properties to specific combos
- Keep matrix size reasonable (< 20 combinations)

---

## 4. Artifact Management

### Build Artifacts

| Artifact Type | Storage | Retention |
|--------------|---------|-----------|
| Container images | Container registry (GHCR, ECR, GCR) | Forever (production), 30d (dev) |
| Test reports | CI artifact storage | 7-30 days |
| Coverage reports | CI artifact storage | 30 days |
| Binaries / packages | Package registry (npm, PyPI, Maven) | Forever (releases) |
| Build logs | CI platform | 90 days |
| SBOM | Artifact storage or attached to image | Same as image |

### Artifact Naming Convention
```
Format: {app}-{version}-{commit-sha}-{platform}
Example: myapp-2.3.1-abc1234-linux-amd64

Container: ghcr.io/org/myapp:abc1234           (commit SHA)
           ghcr.io/org/myapp:2.3.1             (semantic version)
           ghcr.io/org/myapp:main              (branch — mutable, dev only)
```

### GitHub Actions Artifacts
```yaml
# Upload
- uses: actions/upload-artifact@v4
  with:
    name: build-output
    path: dist/
    retention-days: 7
    if-no-files-found: error

# Download in another job
- uses: actions/download-artifact@v4
  with:
    name: build-output
    path: dist/
```

### GitLab CI Artifacts
```yaml
build:
  artifacts:
    paths: [dist/]
    expire_in: 7 days
    reports:
      junit: report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

---

## 5. Container Registry Integration

### GitHub Container Registry (GHCR)
```yaml
- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}

- uses: docker/build-push-action@v6
  with:
    push: true
    tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
```

### AWS ECR
```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: us-east-1

- uses: aws-actions/amazon-ecr-login@v2
  id: ecr

- uses: docker/build-push-action@v6
  with:
    push: true
    tags: ${{ steps.ecr.outputs.registry }}/myapp:${{ github.sha }}
```

### Google Artifact Registry
```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
    service_account: ${{ secrets.WIF_SA }}

- run: gcloud auth configure-docker us-docker.pkg.dev

- uses: docker/build-push-action@v6
  with:
    push: true
    tags: us-docker.pkg.dev/${{ vars.GCP_PROJECT }}/docker/myapp:${{ github.sha }}
```

### Image Tagging Strategy
```yaml
- uses: docker/metadata-action@v5
  id: meta
  with:
    images: ghcr.io/${{ github.repository }}
    tags: |
      type=sha,prefix=                         # abc1234
      type=ref,event=branch                    # main
      type=semver,pattern={{version}}           # 2.3.1
      type=semver,pattern={{major}}.{{minor}}   # 2.3
      type=raw,value=latest,enable=${{ github.ref == format('refs/heads/{0}', 'main') }}
```

---

## 6. DORA Metrics

Track these four metrics to measure CI/CD effectiveness:

| Metric | Definition | Elite Target |
|--------|-----------|-------------|
| **Deployment Frequency** | How often you deploy to production | Multiple times per day |
| **Lead Time for Changes** | Time from commit to production deploy | Less than 1 hour |
| **Change Failure Rate** | % of deployments causing a failure | 0-15% |
| **Mean Time to Recover** | Time to restore service after failure | Less than 1 hour |

### Measuring in CI

```yaml
# Track deployment frequency
- name: Record deployment
  run: |
    curl -X POST https://metrics.example.com/deployments \
      -d '{"service":"myapp","environment":"production","sha":"${{ github.sha }}","timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)"}'

# Track lead time
- name: Record lead time
  run: |
    COMMIT_TIME=$(git log -1 --format=%ct ${{ github.sha }})
    DEPLOY_TIME=$(date +%s)
    LEAD_TIME_SECONDS=$((DEPLOY_TIME - COMMIT_TIME))
    echo "Lead time: ${LEAD_TIME_SECONDS} seconds"
```



---
