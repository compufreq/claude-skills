# GitHub Actions Reference

## Table of Contents
1. Workflow Structure
2. Reusable Workflows
3. Composite Actions
4. Matrix Builds
5. Environment Protection
6. Caching
7. Container Builds
8. Advanced Patterns

---

## 1. Workflow Structure

```yaml
name: CI/CD Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:           # Manual trigger
    inputs:
      environment:
        description: 'Deploy environment'
        required: true
        type: choice
        options: [staging, production]

permissions:
  contents: read                # Least privilege
  packages: write               # For container registry
  id-token: write               # For OIDC

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true      # Cancel stale runs

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint
        run: echo "linting..."

  test:
    runs-on: ubuntu-latest
    needs: lint                 # Depends on lint
    steps:
      - uses: actions/checkout@v4
      - name: Test
        run: echo "testing..."

  build:
    runs-on: ubuntu-latest
    needs: test
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: echo "building..."

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: staging        # Protection rules apply
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: echo "deploying to staging..."

  deploy-production:
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    environment: production     # Requires approval
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: echo "deploying to production..."
```

---

## 2. Reusable Workflows

### Defining a Reusable Workflow
```yaml
# .github/workflows/reusable-build.yml
name: Reusable Build
on:
  workflow_call:
    inputs:
      node-version:
        required: false
        type: string
        default: '20'
      environment:
        required: true
        type: string
    secrets:
      DEPLOY_TOKEN:
        required: true
    outputs:
      artifact-url:
        description: "URL of the built artifact"
        value: ${{ jobs.build.outputs.artifact-url }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      artifact-url: ${{ steps.upload.outputs.artifact-url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: npm
      - run: npm ci
      - run: npm run build
      - name: Upload artifact
        id: upload
        uses: actions/upload-artifact@v4
        with:
          name: build-${{ inputs.environment }}
          path: dist/
```

### Calling a Reusable Workflow
```yaml
# .github/workflows/main.yml
jobs:
  build-staging:
    uses: ./.github/workflows/reusable-build.yml
    with:
      environment: staging
      node-version: '20'
    secrets:
      DEPLOY_TOKEN: ${{ secrets.STAGING_DEPLOY_TOKEN }}

  build-production:
    uses: ./.github/workflows/reusable-build.yml
    with:
      environment: production
    secrets:
      DEPLOY_TOKEN: ${{ secrets.PROD_DEPLOY_TOKEN }}
```

---

## 3. Composite Actions

### Creating a Composite Action
```yaml
# .github/actions/setup-and-test/action.yml
name: 'Setup and Test'
description: 'Install deps and run tests'
inputs:
  node-version:
    description: 'Node.js version'
    required: false
    default: '20'
  coverage-threshold:
    description: 'Minimum coverage %'
    required: false
    default: '80'
runs:
  using: 'composite'
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: npm
    - run: npm ci
      shell: bash
    - run: npm test -- --coverage --coverageThreshold='{"global":{"lines":${{ inputs.coverage-threshold }}}}'
      shell: bash
```

### Using the Composite Action
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-and-test
        with:
          node-version: '20'
          coverage-threshold: '85'
```

---

## 4. Matrix Builds

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false          # Don't cancel other matrix jobs on failure
      matrix:
        os: [ubuntu-latest, macos-latest]
        node-version: [18, 20, 22]
        exclude:
          - os: macos-latest
            node-version: 18    # Skip old Node on macOS
        include:
          - os: ubuntu-latest
            node-version: 20
            coverage: true      # Extra flag for specific combo
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm test
      - if: matrix.coverage
        run: npm run coverage
```

---

## 5. Environment Protection

```yaml
# Configure in: Settings → Environments → [env name]
# - Required reviewers (up to 6 people)
# - Wait timer (delay before deployment)
# - Deployment branches (restrict which branches can deploy)
# - Environment secrets (scoped to this environment)

jobs:
  deploy-production:
    environment:
      name: production
      url: https://app.example.com    # Shown in PR/deployment UI
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        env:
          API_KEY: ${{ secrets.PROD_API_KEY }}  # Environment-scoped secret
        run: ./deploy.sh
```

---

## 6. Caching

### NPM / Node.js
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'                # Built-in caching
```

### pip / Python
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'
```

### Go modules
```yaml
- uses: actions/setup-go@v5
  with:
    go-version: '1.22'
    cache: true
```

### Gradle / Java
```yaml
- uses: actions/setup-java@v4
  with:
    distribution: 'temurin'
    java-version: '21'
    cache: 'gradle'
```

### Docker Layer Caching
```yaml
- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ${{ env.IMAGE }}:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Manual Cache
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/custom-tool
      build/intermediates
    key: custom-${{ runner.os }}-${{ hashFiles('**/lockfile') }}
    restore-keys: |
      custom-${{ runner.os }}-
```

---

## 7. Container Builds

```yaml
jobs:
  docker:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/metadata-action@v5
        id: meta
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha,prefix=
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64
```

---

## 8. Advanced Patterns

### Path-Based Triggers (Monorepo)
```yaml
on:
  push:
    paths:
      - 'services/api/**'
      - 'packages/shared/**'
      - '.github/workflows/api.yml'
    paths-ignore:
      - '**.md'
      - 'docs/**'
```

### Conditional Steps
```yaml
- name: Deploy to production
  if: |
    github.ref == 'refs/heads/main' &&
    github.event_name == 'push' &&
    !contains(github.event.head_commit.message, '[skip deploy]')
  run: ./deploy.sh
```

### Job Outputs
```yaml
jobs:
  detect:
    outputs:
      api-changed: ${{ steps.changes.outputs.api }}
      web-changed: ${{ steps.changes.outputs.web }}
    steps:
      - uses: dorny/paths-filter@v3
        id: changes
        with:
          filters: |
            api: 'services/api/**'
            web: 'apps/web/**'

  build-api:
    needs: detect
    if: needs.detect.outputs.api-changed == 'true'
    runs-on: ubuntu-latest
    steps: [...]
```

### Approval Gate (Manual)
```yaml
deploy-prod:
    needs: deploy-staging
    environment:
      name: production          # Configured with required reviewers
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: ./deploy-prod.sh
```



---
