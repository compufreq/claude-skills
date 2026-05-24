# Claude Skills Collection

A curated collection of **35 custom skills** for [Claude](https://claude.ai) and [Claude Code](https://docs.claude.com/en/docs/claude-code), spanning cloud, DevOps, mobile, security, backend, QA, and career development.

Each skill is a self-contained folder with a `SKILL.md` (YAML frontmatter + instructions) plus supporting references and scripts. Claude loads the relevant skill automatically when a user's request matches its trigger keywords.

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/compufreq/claude-skills.git
cd claude-skills

# Install all skills into ~/.claude/skills/
./scripts/install.sh

# Or install only one category
./scripts/install.sh --category cloud-devops

# Or install a single skill
./scripts/install.sh --skill fastapi-backend
```

Skills install to `~/.claude/skills/` by default. Override with `--dest /custom/path`.

---

## What is a Claude Skill?

A skill is a folder Claude reads on demand to gain domain-specific expertise. Structure:

```
my-skill/
├── SKILL.md          # YAML frontmatter (name, description) + instructions
├── references/       # Optional: deep-dive docs Claude reads when needed
└── scripts/          # Optional: helper scripts the skill can run
```

The `description` field is the most important part — it tells Claude *when* to load the skill. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for authoring guidance.

---

## Skill Catalog
### 📋 Agile & Project Management

| Skill | Description |
|-------|-------------|
| [`agile-ceremonies`](skills/agile/agile-ceremonies/) | Complete Agile ceremony facilitation toolkit covering daily standups, sprint planning, sprint reviews, and retrospectives for Scrum and Kanban teams. |
| [`agile-metrics-tracker`](skills/agile/agile-metrics-tracker/) | Agile metrics, velocity tracking, flow metrics, and forecasting for Scrum and Kanban teams. |
| [`agile-roadmap-builder`](skills/agile/agile-roadmap-builder/) | Agile roadmap creation, release planning, and dependency mapping. |
| [`agile-sprint-planner`](skills/agile/agile-sprint-planner/) | Comprehensive Agile sprint planning, backlog grooming, user story writing, and estimation skill for Scrum and Kanban teams. |

### ☁️  Cloud & DevOps

| Skill | Description |
|-------|-------------|
| [`ci-cd-pipelines`](skills/cloud-devops/ci-cd-pipelines/) | CI/CD pipeline design with GitHub Actions, GitLab CI, and Jenkins. |
| [`cloud-compute`](skills/cloud-devops/cloud-compute/) | Comprehensive cloud compute skill covering virtual machines, serverless functions, container compute, and auto-scaling across AWS and Azure. |
| [`cloud-migration`](skills/cloud-devops/cloud-migration/) | Comprehensive cloud migration skill covering the 6 Rs strategy, migration assessment, database migration, and cutover planning for AWS and Azure. |
| [`cloud-monitoring`](skills/cloud-devops/cloud-monitoring/) | Comprehensive cloud monitoring skill covering AWS CloudWatch, Azure Monitor, Prometheus/Grafana, SLO/SLI frameworks, and observability best practices. |
| [`cloud-networking`](skills/cloud-devops/cloud-networking/) | VPC/VNet design, load balancing, DNS, CDN, transit gateways, and hybrid connectivity for AWS and Azure. |
| [`cloud-solution-architect`](skills/cloud-devops/cloud-solution-architect/) | Well-Architected Framework, multi-tier patterns, FinOps, and disaster recovery for AWS and Azure. |
| [`cloud-storage-data`](skills/cloud-devops/cloud-storage-data/) | Comprehensive cloud storage and data services skill covering object storage, relational databases, NoSQL databases, and caching across AWS and Azure. |
| [`container-orchestration`](skills/cloud-devops/container-orchestration/) | Docker, Kubernetes, Helm, service mesh, GitOps, and managed clusters (EKS, GKE, AKS). |
| [`infrastructure-as-code`](skills/cloud-devops/infrastructure-as-code/) | Terraform, CloudFormation, and Ansible for multi-cloud infrastructure. |
| [`multi-cloud-hybrid`](skills/cloud-devops/multi-cloud-hybrid/) | Comprehensive multi-cloud and hybrid cloud skill covering strategy, connectivity, multi-cloud Kubernetes, cloud-agnostic tooling, identity federation, and data replication. |
| [`serverless-architecture`](skills/cloud-devops/serverless-architecture/) | Comprehensive serverless architecture skill covering API patterns, event-driven design, workflow orchestration, and data patterns for AWS and Azure. |

### 📱 Mobile Development

| Skill | Description |
|-------|-------------|
| [`android-kotlin-dev`](skills/mobile/android-kotlin-dev/) | Android development with Kotlin, Jetpack Compose, XML Views, Retrofit, Room, Hilt, Coroutines, and Play Store submission. |
| [`app-opportunity-scout`](skills/mobile/app-opportunity-scout/) | End-to-end mobile app business opportunity finder and planner. |
| [`ios-swift-dev`](skills/mobile/ios-swift-dev/) | iOS development with Swift, SwiftUI, UIKit, Combine, async/await, and App Store submission. |
| [`mobile-architecture`](skills/mobile/mobile-architecture/) | Mobile architecture patterns, modularization, state management, and Kotlin Multiplatform. |
| [`mobile-ci-cd`](skills/mobile/mobile-ci-cd/) | Mobile CI/CD with Fastlane, code signing, and app store deployment. |

### 🔒 Security

| Skill | Description |
|-------|-------------|
| [`devsecops-scanning`](skills/security/devsecops-scanning/) | Comprehensive DevSecOps security scanning skill covering SAST, DAST, SCA, secret scanning, compliance frameworks, and remediation guidance. |
| [`network-security`](skills/security/network-security/) | Comprehensive network security skill covering firewall rules, IDS/IPS, zero trust architecture, VPN, network segmentation, and threat detection. |
| [`osint-specialist`](skills/security/osint-specialist/) | OSINT investigation specialist across four domains: people/identity, infrastructure/network, company/organization, and geolocation/imagery. |
| [`pentest-methodology`](skills/security/pentest-methodology/) | Comprehensive penetration testing methodology skill covering OWASP, PTES, NIST frameworks, reconnaissance, enumeration, exploitation techniques, and professional reporting. |
| [`security-compliance`](skills/security/security-compliance/) | Comprehensive security compliance skill covering SOC 2, ISO 27001, NIST CSF, and GDPR with control mappings, evidence collection, and implementation guidance. |
| [`web-app-security`](skills/security/web-app-security/) | Comprehensive web application security skill covering OWASP Top 10, authentication/authorization testing, API security, WAF configuration, and security header hardening. |

### ⚙️  Backend & Web

| Skill | Description |
|-------|-------------|
| [`fastapi-backend`](skills/backend-web/fastapi-backend/) | Senior Python backend development with FastAPI, Pydantic, and Python 3.14+. |
| [`htmx-developer`](skills/backend-web/htmx-developer/) | Expert HTMX frontend developer skill for building hypermedia-driven web interfaces using HTMX 2.x. |
| [`k8s-web-dashboard`](skills/backend-web/k8s-web-dashboard/) | Build professional Kubernetes cluster monitoring and management web apps using FastAPI + HTMX + the official Kubernetes Python client. |

### 🧪 Quality & Testing

| Skill | Description |
|-------|-------------|
| [`code-review-guide`](skills/quality-testing/code-review-guide/) | Comprehensive code review skill covering PR checklists, code smells, refactoring patterns, review etiquette, and automated review tooling. |
| [`performance-testing`](skills/quality-testing/performance-testing/) | Comprehensive performance testing skill covering load testing, stress testing, k6, JMeter, Locust, performance budgets, profiling, APM, and capacity planning. |
| [`qa-automation`](skills/quality-testing/qa-automation/) | Comprehensive QA automation skill covering Playwright, Cypress, Selenium, Appium, page object model, CI integration, visual regression, and cross-browser testing. |
| [`testing-strategies`](skills/quality-testing/testing-strategies/) | Comprehensive testing strategies skill covering unit, integration, E2E testing, TDD/BDD, test pyramids, test doubles, and coverage strategies. |

### 🎓 Career & Learning

| Skill | Description |
|-------|-------------|
| [`cka-exam-prep`](skills/career/cka-exam-prep/) | Comprehensive CKA (Certified Kubernetes Administrator) exam preparation assistant. |
| [`job-hunter`](skills/career/job-hunter/) | End-to-end job hunting assistant that finds matching jobs, refines or builds CVs from scratch, and writes tailored cover letters — all in ATS-compatible .docx and .pdf formats. |

---

## Repo Layout

```
claude-skills/
├── skills/
│   ├── agile/            # 4 skills
│   ├── cloud-devops/     # 11 skills
│   ├── mobile/           # 5 skills
│   ├── security/         # 6 skills
│   ├── backend-web/      # 3 skills
│   ├── quality-testing/  # 4 skills
│   └── career/           # 2 skills
├── scripts/
│   └── install.sh        # Installer (copy / symlink to ~/.claude/skills)
├── .github/workflows/
│   └── lint-skills.yml   # Validates every SKILL.md frontmatter on PR
├── CONTRIBUTING.md
├── LICENSE               # CC BY-NC-SA 4.0
└── README.md
```

---

## Contributing

PRs welcome! Each new skill must:

1. Live under the correct category folder.
2. Include a `SKILL.md` with valid YAML frontmatter (`name` + `description`).
3. Pass the [SKILL.md linter](.github/workflows/lint-skills.yml).

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for detailed authoring guidelines, description-writing tips, and the description style guide.

---

## License

This collection is released under **[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](LICENSE)**.

You are free to:

- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

Under the following terms:

- **Attribution** — You must give appropriate credit to Alaa Alhorani - Compufreq and link back to this repo.
- **NonCommercial** — You may not use the material for commercial purposes.
- **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license.

### Commercial Use

For commercial licensing inquiries (using these skills inside a paid product, SaaS offering, or any revenue-generating context), please contact:

Alaa Alhorani — `alaa.alhorani@proton.me`

A separate commercial license can be granted upon request.

---

## Author

Built and maintained by **[Compufreq](https://github.com/compufreq)**.

If you find these skills useful, ⭐ the repo and share your own contributions.
