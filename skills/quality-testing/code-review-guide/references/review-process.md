# Code Review Process Reference

## 1. PR Checklist (Reviewer)

### Correctness
- [ ] Does the code do what the ticket/description says?
- [ ] Are edge cases handled (null, empty, boundary values)?
- [ ] Are error paths handled gracefully?
- [ ] Is the logic correct (no off-by-one, race conditions)?
- [ ] Are external inputs validated and sanitized?

### Design
- [ ] Does this fit the existing architecture?
- [ ] Is the code in the right layer (controller vs service vs repository)?
- [ ] Are abstractions appropriate (not over/under-engineered)?
- [ ] Is there unnecessary duplication?
- [ ] Are dependencies appropriate and minimal?

### Security
- [ ] No hardcoded secrets, tokens, or passwords?
- [ ] Input validation on all user-supplied data?
- [ ] Parameterized queries (no SQL concatenation)?
- [ ] No sensitive data in logs?
- [ ] Authorization checks on protected endpoints?
- [ ] Output encoding to prevent XSS?

### Performance
- [ ] No N+1 query problems?
- [ ] Appropriate use of caching?
- [ ] No unnecessary database calls in loops?
- [ ] Large collections paginated?
- [ ] Async for I/O-bound operations?

### Testing
- [ ] Unit tests for new/changed logic?
- [ ] Edge cases tested?
- [ ] Integration test if touching external services?
- [ ] Tests are readable and well-named?
- [ ] No test data leaking to production?

### Readability
- [ ] Clear, descriptive naming (variables, functions, classes)?
- [ ] Comments explain "why", not "what"?
- [ ] Functions are small and single-purpose?
- [ ] No dead code or commented-out blocks?
- [ ] Consistent formatting (linter passing)?

### Operations
- [ ] Database migrations are backward-compatible?
- [ ] Feature flagged if risky?
- [ ] Monitoring/logging added for new functionality?
- [ ] Documentation updated (README, API docs)?
- [ ] No breaking changes to public APIs without versioning?

## 2. PR Author Checklist

Before requesting review:
- [ ] Self-reviewed the diff line by line
- [ ] PR description explains what and why
- [ ] Linked to ticket/issue
- [ ] Tests pass locally and in CI
- [ ] Linter/formatter passes
- [ ] PR is reasonably sized (< 400 lines of real changes)
- [ ] Removed debug code, TODOs, commented-out code
- [ ] Screenshots for UI changes

## 3. PR Size Guidelines

| Size | Lines Changed | Review Time | Risk |
|------|-------------|-------------|------|
| XS | < 50 | 5-10 min | Low |
| S | 50-200 | 15-30 min | Low |
| M | 200-400 | 30-60 min | Medium |
| L | 400-800 | 1-2 hours | High |
| XL | > 800 | Split the PR | Very High |

**Rule:** If a PR is > 400 lines, it should probably be split. Large PRs get superficial reviews.

### Splitting Strategies
- Separate refactoring from feature changes
- Split by layer (database migration → model → service → API → UI)
- Extract shared utilities first, then feature PRs
- Use feature flags to merge incomplete features safely

## 4. Review Workflow

```
Author creates PR → Automated checks (CI, linting, security scan)
                   → Assign reviewer(s)
                   → Review (comments, suggestions, approvals)
                   → Author addresses feedback
                   → Re-review if substantial changes
                   → Approve → Merge
```

### Branch Protection Rules
```yaml
# GitHub branch protection for main
required_reviews: 1           # Minimum approvals
dismiss_stale_reviews: true   # Re-review after new pushes
require_code_owner_review: true
require_status_checks:
  - ci/test
  - ci/lint
  - security/scan
require_linear_history: true  # No merge commits (squash or rebase)
restrict_pushes: true         # No direct pushes to main
```



---

<!-- Script: scripts/generate_review_checklist.py -->

# Script: generate_review_checklist.py

```python
#!/usr/bin/env python3
"""Generate code review checklists by type and language."""

import argparse, os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")

LANG_SPECIFICS = {
    "python": {
        "type_safety": "- [ ] Type hints on all function signatures\n- [ ] mypy / pyright passing",
        "imports": "- [ ] No wildcard imports (`from x import *`)\n- [ ] Standard import ordering (stdlib → third-party → local)",
        "patterns": "- [ ] Using dataclasses/Pydantic for data structures\n- [ ] Context managers for resource handling (`with` statements)",
        "testing": "- [ ] pytest used with clear arrange/act/assert\n- [ ] Fixtures used for setup/teardown",
    },
    "typescript": {
        "type_safety": "- [ ] No `any` types (use `unknown` if needed)\n- [ ] Strict mode enabled in tsconfig",
        "imports": "- [ ] No circular imports\n- [ ] Barrel exports used appropriately",
        "patterns": "- [ ] Interfaces over type aliases for object shapes\n- [ ] Discriminated unions for state management",
        "testing": "- [ ] Jest/Vitest with proper mocking\n- [ ] Testing Library for component tests (no implementation details)",
    },
    "go": {
        "type_safety": "- [ ] Errors returned, not panicked\n- [ ] Interfaces accepted, structs returned",
        "imports": "- [ ] `goimports` formatted\n- [ ] No unused imports",
        "patterns": "- [ ] Table-driven tests\n- [ ] Context propagation for cancellation\n- [ ] `defer` for cleanup",
        "testing": "- [ ] `_test.go` files in same package\n- [ ] `testify` or stdlib assertions",
    },
}

def gen_pr_checklist(lang, output):
    ls = LANG_SPECIFICS.get(lang, LANG_SPECIFICS["python"])
    create_file(os.path.join(output, f"pr-checklist-{lang}.md"), f"""# Pull Request Review Checklist ({lang.title()})

## Before Reviewing
- [ ] PR description explains **what** and **why**
- [ ] PR is < 400 lines (excluding tests and generated code)
- [ ] CI/CD pipeline is green
- [ ] No merge conflicts

## Security
- [ ] No hardcoded secrets, API keys, or credentials
- [ ] User input validated and sanitized
- [ ] Authentication/authorization checked on new endpoints
- [ ] SQL queries parameterized (no string concatenation)
- [ ] No sensitive data in logs
- [ ] Dependencies free of known vulnerabilities

## Correctness
- [ ] Code does what the PR description says
- [ ] Edge cases handled (null, empty, boundary values)
- [ ] Error handling is appropriate (not swallowed silently)
- [ ] Database migrations are backward-compatible
- [ ] No race conditions in concurrent code
- [ ] API contracts maintained (no breaking changes)

## Design
- [ ] Single Responsibility — each function/class does one thing
- [ ] DRY — no significant duplication
- [ ] Appropriate abstraction level (not over/under-engineered)
- [ ] Dependencies injected (testable, loosely coupled)
- [ ] New code follows existing patterns in the codebase

## Language-Specific ({lang.title()})
### Type Safety
{ls['type_safety']}

### Imports & Dependencies
{ls['imports']}

### Patterns
{ls['patterns']}

### Testing
{ls['testing']}

## Readability
- [ ] Clear, descriptive naming (variables, functions, classes)
- [ ] Comments explain **why**, not **what**
- [ ] No dead code or commented-out code
- [ ] Functions are < 30 lines (ideally < 20)
- [ ] Consistent with project coding standards

## Testing
- [ ] New code has tests (unit, integration as appropriate)
- [ ] Tests cover happy path AND error paths
- [ ] Tests are deterministic (no flaky tests)
- [ ] Test names describe behavior, not implementation
- [ ] Coverage maintained or improved

## Documentation
- [ ] README updated if behavior changes
- [ ] API documentation updated (OpenAPI, JSDoc, docstrings)
- [ ] ADR written if this is a significant design decision
""")

def gen_security_checklist(output):
    create_file(os.path.join(output, "security-review-checklist.md"), """# Security-Focused Review Checklist

## Authentication & Authorization
- [ ] All endpoints require authentication (unless intentionally public)
- [ ] Authorization checked at controller AND service layer
- [ ] No horizontal privilege escalation (IDOR)
- [ ] No vertical privilege escalation (role bypass)
- [ ] Admin endpoints have additional authorization

## Input Validation
- [ ] All user input validated (type, length, format, range)
- [ ] File uploads validated (type, size, content)
- [ ] SQL injection prevented (parameterized queries)
- [ ] XSS prevented (output encoding, CSP)
- [ ] Command injection prevented (no shell execution with user input)
- [ ] SSRF prevented (URL allowlisting)
- [ ] Path traversal prevented (no user input in file paths)

## Data Protection
- [ ] PII encrypted at rest
- [ ] Sensitive data not logged
- [ ] Passwords hashed with bcrypt/argon2 (never MD5/SHA1)
- [ ] Secrets from Secrets Manager (not env vars or config files)
- [ ] API responses don't leak internal details

## Session & Token Security
- [ ] JWT expiration set (< 15 minutes for access tokens)
- [ ] Refresh token rotation implemented
- [ ] Session cookies: Secure, HttpOnly, SameSite
- [ ] CSRF protection on state-changing operations
- [ ] No sensitive data stored in localStorage

## Error Handling
- [ ] No stack traces in production responses
- [ ] Error messages don't reveal internal details
- [ ] Failed operations don't leave partial state
- [ ] Security events logged (failed auth, access denied)
""")

def gen_architecture_checklist(output):
    create_file(os.path.join(output, "architecture-review-checklist.md"), """# Architecture Review Checklist

## API Design
- [ ] RESTful conventions followed (nouns, HTTP methods, status codes)
- [ ] API versioning strategy defined
- [ ] Pagination implemented for list endpoints
- [ ] Rate limiting configured
- [ ] Request/response schemas documented (OpenAPI)

## Data Model
- [ ] Database schema normalized appropriately
- [ ] Indexes created for query patterns
- [ ] Migrations are additive (backward-compatible)
- [ ] Foreign keys and constraints defined
- [ ] Soft delete vs hard delete decision documented

## Scalability
- [ ] Stateless services (no in-memory session state)
- [ ] Database connection pooling configured
- [ ] Caching strategy defined (what, where, TTL)
- [ ] Async processing for non-critical operations
- [ ] Idempotent operations (safe to retry)

## Reliability
- [ ] Circuit breakers on external service calls
- [ ] Retries with exponential backoff
- [ ] Timeouts configured on all network calls
- [ ] Graceful degradation when dependencies fail
- [ ] Health check endpoint implemented

## Observability
- [ ] Structured logging with correlation IDs
- [ ] Metrics emitted (request rate, latency, error rate)
- [ ] Distributed tracing configured
- [ ] Alerts defined for SLO violations
- [ ] Dashboard exists for this service
""")

def main():
    p = argparse.ArgumentParser(description="Generate Review Checklists")
    p.add_argument("--type", choices=["pr", "security", "architecture", "all"], required=True)
    p.add_argument("--language", choices=["python", "typescript", "go"], default="python")
    p.add_argument("--output", default="./review")
    a = p.parse_args()

    print(f"\n📝 Generating {a.type} checklist\n")
    if a.type in ("pr", "all"):
        gen_pr_checklist(a.language, a.output)
    if a.type in ("security", "all"):
        gen_security_checklist(a.output)
    if a.type in ("architecture", "all"):
        gen_architecture_checklist(a.output)
    print(f"\n✅ Generated at: {a.output}/")

if __name__ == "__main__":
    main()

```
