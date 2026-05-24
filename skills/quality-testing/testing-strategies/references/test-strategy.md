# Test Strategy Reference

## 1. Test Pyramid

```
         ╱  E2E   ╲        Few, slow, expensive
        ╱ (UI/API)  ╲       Critical user journeys only
       ╱─────────────╲
      ╱  Integration   ╲    Moderate count
     ╱  (services, DB)  ╲   Test boundaries between components
    ╱────────────────────╲
   ╱     Unit Tests       ╲  Many, fast, cheap
  ╱  (functions, classes)  ╲ Test logic in isolation
 ╱──────────────────────────╲
```

### Layer Comparison

| Layer | Count | Speed | Scope | Reliability | Cost |
|-------|-------|-------|-------|-------------|------|
| **Unit** | 1000s | ms each | Single function/class | Very high | Low |
| **Integration** | 100s | seconds | Multiple components | High | Medium |
| **E2E** | 10s-50s | minutes | Full system | Medium (flaky risk) | High |

### What to Test at Each Layer

| Layer | Test These | Don't Test These |
|-------|-----------|-----------------|
| **Unit** | Business logic, calculations, transformations, validation, parsing | Database queries, API calls, file I/O |
| **Integration** | API endpoints, DB queries, service interactions, auth flows | UI rendering, visual layout |
| **E2E** | Critical user journeys, checkout, registration, login | Every edge case, every page |

## 2. Testing Strategy by App Type

| App Type | Unit Focus | Integration Focus | E2E Focus |
|----------|-----------|-------------------|-----------|
| **API/Backend** | Business logic, validators | API endpoints, DB queries | Critical flows via API |
| **Frontend SPA** | Components, state, utils | API integration, routing | User journeys (login, CRUD) |
| **Microservices** | Service logic | Service-to-service, contracts | End-to-end flows |
| **CLI tool** | Command parsing, logic | File I/O, system calls | Full command scenarios |
| **Data pipeline** | Transformations, parsing | Source/sink connections | Full pipeline runs |

## 3. Coverage Strategy

### Coverage Types

| Type | Measures | Target |
|------|---------|--------|
| **Line coverage** | Lines executed | 80%+ |
| **Branch coverage** | Decision paths taken | 70%+ |
| **Function coverage** | Functions called | 90%+ |
| **Mutation coverage** | Tests catch changes | 60%+ (gold standard) |

### Coverage Guidelines
```
Don't aim for 100% — aim for meaningful coverage

High-value targets (test thoroughly):
  - Business logic and calculations
  - Validation and authorization
  - Error handling paths
  - Edge cases (null, empty, boundary)

Low-value targets (test lightly or skip):
  - Getters/setters
  - Framework boilerplate
  - Third-party library wrappers
  - Config/constants
```

### Coverage Configuration
```json
// Jest (jest.config.js)
{
  "coverageThreshold": {
    "global": {
      "branches": 70,
      "functions": 80,
      "lines": 80,
      "statements": 80
    },
    "src/services/": {
      "branches": 90,
      "lines": 90
    }
  }
}
```

```ini
# pytest (pyproject.toml)
[tool.coverage.run]
branch = true
source = ["src"]

[tool.coverage.report]
fail_under = 80
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

## 4. Test Naming Convention

```
# Pattern: test_[what]_[condition]_[expected result]

# Python
def test_calculate_total_with_discount_returns_discounted_price():
def test_login_with_invalid_password_raises_auth_error():
def test_create_order_with_empty_cart_raises_validation_error():

# JavaScript
describe('calculateTotal', () => {
  it('should return discounted price when discount is applied', () => {});
  it('should throw when items array is empty', () => {});
});

# Given-When-Then (BDD style)
def test_given_premium_user_when_ordering_over_100_then_free_shipping():
```

## 5. Test Organization

```
src/
  services/
    order_service.py
    payment_service.py
tests/
  unit/
    services/
      test_order_service.py
      test_payment_service.py
  integration/
    test_order_api.py
    test_payment_integration.py
  e2e/
    test_checkout_flow.py
    test_user_registration.py
  fixtures/
    orders.py
    users.py
  conftest.py
```



---

<!-- Script: scripts/generate_test_strategy.py -->

# Script: generate_test_strategy.py

```python
#!/usr/bin/env python3
"""Generate testing strategy documents and test templates."""

import argparse, os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")

def gen_strategy(project, framework, output):
    create_file(os.path.join(output, f"test-strategy-{project}.md"), f"""# Test Strategy — {project}

## Test Pyramid

| Level | Coverage Target | Framework | Execution |
|-------|----------------|-----------|-----------|
| Unit | 80%+ line coverage | {framework} | Every commit (CI) |
| Integration | Key workflows | {framework} + testcontainers | Every PR |
| E2E | Critical user journeys (5-10) | Playwright / Cypress | Nightly + pre-deploy |
| Performance | SLO validation | k6 / Locust | Weekly + pre-release |

## Test Organization
```
tests/
├── unit/           # Fast, isolated, mocked dependencies
│   ├── services/
│   ├── models/
│   └── utils/
├── integration/    # Real dependencies (DB, cache, queues)
│   ├── api/
│   └── repositories/
├── e2e/            # Full user journeys through UI/API
│   ├── auth.spec.ts
│   ├── checkout.spec.ts
│   └── admin.spec.ts
├── performance/    # Load and stress tests
│   └── load-test.js
├── fixtures/       # Shared test data
└── factories/      # Test data builders
```

## Coverage Targets

| Metric | Minimum | Target | Measured By |
|--------|---------|--------|-------------|
| Line coverage | 70% | 85% | Coverage tool |
| Branch coverage | 60% | 75% | Coverage tool |
| Critical path coverage | 100% | 100% | Manual review |
| Mutation score | 50% | 70% | Mutation testing |

## Test Quality Rules
1. Tests must be deterministic (no flaky tests)
2. Tests must be independent (run in any order)
3. Test names describe behavior: `should_return_404_when_user_not_found`
4. No logic in tests (no if/else, loops)
5. One assertion concept per test
6. Tests run in < 5 minutes (unit), < 15 minutes (integration)
7. Flaky tests are bugs — fix or delete within 48 hours
""")

def gen_template(language, output):
    templates = {
        "python": """# Python Test Templates

## Unit Test (pytest)
```python
import pytest
from unittest.mock import Mock, patch
from myapp.services.user_service import UserService

class TestUserService:
    def setup_method(self):
        self.repo = Mock()
        self.service = UserService(repo=self.repo)

    def test_get_user_returns_user_when_found(self):
        # Arrange
        self.repo.find_by_id.return_value = {"id": "123", "name": "Alice"}

        # Act
        result = self.service.get_user("123")

        # Assert
        assert result["name"] == "Alice"
        self.repo.find_by_id.assert_called_once_with("123")

    def test_get_user_raises_not_found_when_missing(self):
        self.repo.find_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            self.service.get_user("999")

    @pytest.mark.parametrize("email,valid", [
        ("user@example.com", True),
        ("invalid", False),
        ("", False),
        ("user@.com", False),
    ])
    def test_validate_email(self, email, valid):
        assert self.service.validate_email(email) == valid
```

## Integration Test (pytest + testcontainers)
```python
import pytest
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="module")
def postgres():
    with PostgresContainer("postgres:16") as pg:
        yield pg.get_connection_url()

@pytest.fixture
def db_session(postgres):
    engine = create_engine(postgres)
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.rollback()
    session.close()

def test_create_and_retrieve_user(db_session):
    repo = UserRepository(db_session)
    repo.create(User(name="Alice", email="alice@test.com"))
    user = repo.find_by_email("alice@test.com")
    assert user.name == "Alice"
```
""",
        "typescript": """# TypeScript Test Templates

## Unit Test (Jest/Vitest)
```typescript
import { describe, it, expect, vi } from 'vitest';
import { UserService } from './user-service';

describe('UserService', () => {
  const mockRepo = { findById: vi.fn(), save: vi.fn() };
  const service = new UserService(mockRepo);

  it('should return user when found', async () => {
    mockRepo.findById.mockResolvedValue({ id: '123', name: 'Alice' });

    const user = await service.getUser('123');

    expect(user.name).toBe('Alice');
    expect(mockRepo.findById).toHaveBeenCalledWith('123');
  });

  it('should throw NotFoundError when user missing', async () => {
    mockRepo.findById.mockResolvedValue(null);

    await expect(service.getUser('999')).rejects.toThrow(NotFoundError);
  });
});
```

## React Component Test (Testing Library)
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  it('should show error when submitting empty form', async () => {
    const onSubmit = vi.fn();
    render(<LoginForm onSubmit={onSubmit} />);

    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });
});
```
""",
        "go": """# Go Test Templates

## Unit Test
```go
func TestGetUser_ReturnsUser_WhenFound(t *testing.T) {
    repo := &MockUserRepo{
        FindByIDFunc: func(id string) (*User, error) {
            return &User{ID: "123", Name: "Alice"}, nil
        },
    }
    svc := NewUserService(repo)

    user, err := svc.GetUser("123")

    assert.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
}

// Table-driven test
func TestValidateEmail(t *testing.T) {
    tests := []struct {
        name  string
        email string
        valid bool
    }{
        {"valid email", "user@example.com", true},
        {"missing @", "invalid", false},
        {"empty", "", false},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            assert.Equal(t, tt.valid, ValidateEmail(tt.email))
        })
    }
}
```
""",
    }
    tmpl = templates.get(language, templates["python"])
    create_file(os.path.join(output, f"test-templates-{language}.md"), tmpl)

def main():
    p = argparse.ArgumentParser(description="Generate Test Strategy Documents")
    p.add_argument("--type", choices=["strategy", "templates", "all"], required=True)
    p.add_argument("--language", choices=["python", "typescript", "go"], default="python")
    p.add_argument("--project", default="myapp")
    p.add_argument("--output", default="./testing")
    a = p.parse_args()

    print(f"\n🧪 Generating {a.type} for {a.project}\n")
    if a.type in ("strategy", "all"):
        fw = {"python": "pytest", "typescript": "vitest", "go": "go test"}[a.language]
        gen_strategy(a.project, fw, a.output)
    if a.type in ("templates", "all"):
        gen_template(a.language, a.output)
    print(f"\n✅ Generated at: {a.output}/")

if __name__ == "__main__":
    main()

```
