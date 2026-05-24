# GitLab CI Reference

## Table of Contents
1. Pipeline Structure
2. Templates & Includes
3. Environments & Deployments
4. Rules & Conditional Logic
5. Services & Docker-in-Docker
6. Advanced Patterns

---

## 1. Pipeline Structure

```yaml
# .gitlab-ci.yml
stages:
  - lint
  - test
  - build
  - scan
  - deploy

variables:
  DOCKER_IMAGE: $CI_REGISTRY_IMAGE
  NODE_VERSION: "20"

default:
  image: node:${NODE_VERSION}-alpine
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/
      - .npm/
  before_script:
    - npm ci --cache .npm --prefer-offline

lint:
  stage: lint
  script:
    - npm run lint
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_COMMIT_BRANCH == "develop"'

test:unit:
  stage: test
  script:
    - npm run test:unit -- --coverage
  coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'
  artifacts:
    when: always
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
    expire_in: 7 days

test:integration:
  stage: test
  services:
    - postgres:16-alpine
    - redis:7-alpine
  variables:
    POSTGRES_DB: test
    POSTGRES_USER: test
    POSTGRES_PASSWORD: test
    DATABASE_URL: "postgres://test:test@postgres:5432/test"
    REDIS_URL: "redis://redis:6379"
  script:
    - npm run test:integration

build:
  stage: build
  image: docker:27
  services:
    - docker:27-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $DOCKER_IMAGE:$CI_COMMIT_SHA .
    - docker push $DOCKER_IMAGE:$CI_COMMIT_SHA
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'

deploy:staging:
  stage: deploy
  environment:
    name: staging
    url: https://staging.example.com
  script:
    - ./deploy.sh staging $CI_COMMIT_SHA
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'

deploy:production:
  stage: deploy
  environment:
    name: production
    url: https://app.example.com
  script:
    - ./deploy.sh production $CI_COMMIT_SHA
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: manual
      allow_failure: false
```

---

## 2. Templates & Includes

### Local Templates
```yaml
# templates/node-job.yml
.node-job:
  image: node:20-alpine
  cache:
    key: node-${CI_COMMIT_REF_SLUG}
    paths: [node_modules/]
  before_script:
    - npm ci

# .gitlab-ci.yml
include:
  - local: templates/node-job.yml

lint:
  extends: .node-job
  stage: lint
  script: npm run lint

test:
  extends: .node-job
  stage: test
  script: npm test
```

### Remote Templates
```yaml
include:
  - project: 'devops/ci-templates'
    ref: main
    file: '/templates/docker-build.yml'

  - remote: 'https://example.com/ci/security-scan.yml'

  - template: Security/SAST.gitlab-ci.yml    # GitLab built-in
  - template: Security/Dependency-Scanning.gitlab-ci.yml
```

### Component Templates (GitLab CI/CD Components)
```yaml
include:
  - component: gitlab.com/my-org/ci-components/docker-build@1.0.0
    inputs:
      registry: $CI_REGISTRY
      image_name: $CI_REGISTRY_IMAGE
```

---

## 3. Environments & Deployments

```yaml
deploy:staging:
  stage: deploy
  environment:
    name: staging
    url: https://staging.example.com
    on_stop: stop:staging                # Cleanup job
    auto_stop_in: 1 week                 # Auto-stop after 1 week
  script: ./deploy.sh staging

stop:staging:
  stage: deploy
  environment:
    name: staging
    action: stop
  script: ./teardown.sh staging
  when: manual

# Dynamic environments (per branch)
deploy:review:
  stage: deploy
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    url: https://$CI_COMMIT_REF_SLUG.review.example.com
    on_stop: stop:review
    auto_stop_in: 3 days
  script: ./deploy-review.sh $CI_COMMIT_REF_SLUG
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
```

---

## 4. Rules & Conditional Logic

```yaml
# Rules replace only/except (preferred)
job:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_COMMIT_TAG =~ /^v\d+/'
      when: manual

# Changes-based (monorepo)
build:api:
  rules:
    - changes:
        - services/api/**/*
        - packages/shared/**/*
      when: on_success
    - when: never

# Variable-based
deploy:
  rules:
    - if: '$DEPLOY_ENABLED == "true" && $CI_COMMIT_BRANCH == "main"'
```

### Parallel Matrix
```yaml
test:
  stage: test
  parallel:
    matrix:
      - PYTHON_VERSION: ["3.10", "3.11", "3.12"]
        DATABASE: ["postgres", "mysql"]
  image: python:${PYTHON_VERSION}
  script:
    - pip install -r requirements.txt
    - pytest --db=$DATABASE
```

---

## 5. Services & Docker-in-Docker

```yaml
# Services (sidecar containers)
test:
  services:
    - name: postgres:16
      alias: db
      variables:
        POSTGRES_DB: test_db
    - name: redis:7
      alias: cache
    - name: elasticsearch:8.12.0
      alias: search
      variables:
        discovery.type: single-node
  variables:
    DATABASE_URL: "postgres://postgres@db/test_db"
    REDIS_URL: "redis://cache:6379"
    ELASTICSEARCH_URL: "http://search:9200"

# Docker-in-Docker
build:docker:
  image: docker:27
  services:
    - docker:27-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
    DOCKER_HOST: tcp://docker:2376
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

# Kaniko (Docker build without Docker daemon — more secure)
build:kaniko:
  image:
    name: gcr.io/kaniko-project/executor:debug
    entrypoint: [""]
  script:
    - /kaniko/executor
      --context $CI_PROJECT_DIR
      --dockerfile Dockerfile
      --destination $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
      --cache=true
```

---

## 6. Advanced Patterns

### DAG (Directed Acyclic Graph) — Non-Linear Pipeline
```yaml
stages: [build, test, deploy]

build:frontend:
  stage: build
  script: npm run build:frontend

build:backend:
  stage: build
  script: npm run build:backend

test:frontend:
  stage: test
  needs: [build:frontend]      # Only waits for frontend build
  script: npm run test:frontend

test:backend:
  stage: test
  needs: [build:backend]       # Only waits for backend build
  script: npm run test:backend

deploy:
  stage: deploy
  needs: [test:frontend, test:backend]
  script: ./deploy.sh
```

### Parent-Child Pipelines (Monorepo)
```yaml
# Root .gitlab-ci.yml
trigger:api:
  trigger:
    include: services/api/.gitlab-ci.yml
    strategy: depend
  rules:
    - changes: [services/api/**/*]

trigger:web:
  trigger:
    include: apps/web/.gitlab-ci.yml
    strategy: depend
  rules:
    - changes: [apps/web/**/*]
```

### Caching Strategies
```yaml
# Per-branch cache
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths: [node_modules/]

# Lock-file based cache (most accurate)
cache:
  key:
    files: [package-lock.json]
  paths: [node_modules/]

# Fallback cache
cache:
  key:
    files: [package-lock.json]
    prefix: ${CI_JOB_NAME}
  paths: [node_modules/]
  policy: pull-push              # Default: both read and write
```



---
