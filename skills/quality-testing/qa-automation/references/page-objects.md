# Page Object Model Reference

## 1. Page Object Pattern

```
Tests → Page Objects → Browser/App
  ↓         ↓             ↓
describe  LoginPage    playwright/cypress
  it()    .login()     .click(), .fill()
```

### Why Page Objects
- **DRY** — selector changes in one place, not every test
- **Readable** — tests read like user stories
- **Maintainable** — UI changes only affect page objects, not tests

## 2. Playwright Page Objects

```typescript
// pages/LoginPage.ts
import { Page, Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign In' });
    this.errorMessage = page.getByTestId('error-message');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string) {
    await expect(this.errorMessage).toHaveText(message);
  }
}

// pages/DashboardPage.ts
export class DashboardPage {
  readonly page: Page;
  readonly welcomeMessage: Locator;
  readonly userMenu: Locator;

  constructor(page: Page) {
    this.page = page;
    this.welcomeMessage = page.getByTestId('welcome');
    this.userMenu = page.getByTestId('user-menu');
  }

  async expectLoggedIn(name: string) {
    await expect(this.welcomeMessage).toContainText(name);
  }

  async logout() {
    await this.userMenu.click();
    await this.page.getByRole('menuitem', { name: 'Logout' }).click();
  }
}

// tests/login.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';

test.describe('Login', () => {
  test('successful login', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboard = new DashboardPage(page);

    await loginPage.goto();
    await loginPage.login('alice@example.com', 'password123');
    await dashboard.expectLoggedIn('Alice');
  });

  test('invalid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('alice@example.com', 'wrong');
    await loginPage.expectError('Invalid credentials');
  });
});
```

## 3. Component Pattern (Complex Pages)

```typescript
// components/NavigationBar.ts
export class NavigationBar {
  constructor(private page: Page) {}

  async navigateTo(item: string) {
    await this.page.getByRole('navigation').getByRole('link', { name: item }).click();
  }

  async search(query: string) {
    await this.page.getByRole('searchbox').fill(query);
    await this.page.getByRole('searchbox').press('Enter');
  }

  async getCartCount(): Promise<number> {
    const text = await this.page.getByTestId('cart-count').textContent();
    return parseInt(text || '0');
  }
}

// pages/ProductPage.ts — composes components
export class ProductPage {
  readonly nav: NavigationBar;

  constructor(private page: Page) {
    this.nav = new NavigationBar(page);
  }

  async addToCart() {
    await this.page.getByRole('button', { name: 'Add to Cart' }).click();
  }

  async selectSize(size: string) {
    await this.page.getByLabel('Size').selectOption(size);
  }
}
```

## 4. Page Object Rules

| Do | Don't |
|----|-------|
| Expose user actions as methods | Expose locators directly to tests |
| Return other page objects for navigation | Put assertions inside page objects (mostly) |
| Use descriptive method names | Name methods after implementation details |
| Keep page objects focused (one page/component) | Create God page objects |
| Use composition for shared components | Deeply inherit page object hierarchies |

## 5. Fixtures and Helpers

```typescript
// fixtures/auth.fixture.ts
import { test as base } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';

type Fixtures = {
  loginPage: LoginPage;
  dashboard: DashboardPage;
  authenticatedPage: DashboardPage;
};

export const test = base.extend<Fixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  dashboard: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },
  authenticatedPage: async ({ page }, use) => {
    // Auto-login before each test
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('test@example.com', 'password123');
    await use(new DashboardPage(page));
  },
});

// tests/dashboard.spec.ts
import { test } from '../fixtures/auth.fixture';

test('view dashboard after login', async ({ authenticatedPage }) => {
  await authenticatedPage.expectLoggedIn('Test User');
});
```



---

<!-- Script: scripts/generate_qa_boilerplate.py -->

# Script: generate_qa_boilerplate.py

```python
#!/usr/bin/env python3
"""Generate QA automation boilerplate and configuration."""

import argparse, os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")

def gen_playwright(project, output):
    create_file(os.path.join(output, "playwright.config.ts"), f"""import {{ defineConfig, devices }} from '@playwright/test';

export default defineConfig({{
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 4 : undefined,
  reporter: [
    ['html', {{ open: 'never' }}],
    ['junit', {{ outputFile: 'test-results/junit.xml' }}],
  ],
  use: {{
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  }},
  projects: [
    {{ name: 'chromium', use: {{ ...devices['Desktop Chrome'] }} }},
    {{ name: 'firefox', use: {{ ...devices['Desktop Firefox'] }} }},
    {{ name: 'mobile', use: {{ ...devices['iPhone 14'] }} }},
  ],
}});
""")

    create_file(os.path.join(output, "e2e", "pages", "login.page.ts"), """import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async getError(): Promise<string | null> {
    return this.errorMessage.textContent();
  }
}
""")

    create_file(os.path.join(output, "e2e", "auth.spec.ts"), """import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login.page';

test.describe('Authentication', () => {
  test('should login with valid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('user@example.com', 'password123');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('user@example.com', 'wrong');
    await expect(loginPage.errorMessage).toBeVisible();
  });

  test('should redirect unauthenticated users to login', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/login');
  });
});
""")

def gen_cypress(project, output):
    create_file(os.path.join(output, "cypress.config.ts"), f"""import {{ defineConfig }} from 'cypress';

export default defineConfig({{
  e2e: {{
    baseUrl: process.env.BASE_URL || 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    retries: {{ runMode: 2, openMode: 0 }},
    specPattern: 'cypress/e2e/**/*.cy.ts',
  }},
}});
""")

    create_file(os.path.join(output, "cypress", "e2e", "auth.cy.ts"), """describe('Authentication', () => {
  it('should login successfully', () => {
    cy.visit('/login');
    cy.getByLabel('Email').type('user@example.com');
    cy.getByLabel('Password').type('password123');
    cy.getByRole('button', { name: 'Sign in' }).click();
    cy.url().should('include', '/dashboard');
  });

  it('should show error for invalid credentials', () => {
    cy.visit('/login');
    cy.getByLabel('Email').type('user@example.com');
    cy.getByLabel('Password').type('wrong');
    cy.getByRole('button', { name: 'Sign in' }).click();
    cy.getByRole('alert').should('be.visible');
  });
});
""")

def gen_ci_config(framework, output):
    configs = {
        "playwright": """# .github/workflows/e2e.yml
name: E2E Tests
on:
  pull_request:
  schedule:
    - cron: '0 6 * * *'  # Nightly

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
""",
        "cypress": """# .github/workflows/e2e.yml
name: E2E Tests
on:
  pull_request:
  schedule:
    - cron: '0 6 * * *'

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cypress-io/github-action@v6
        with:
          start: npm start
          wait-on: 'http://localhost:3000'
          browser: chrome
        env:
          CYPRESS_BASE_URL: ${{ secrets.STAGING_URL }}
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: cypress-screenshots
          path: cypress/screenshots/
""",
    }
    create_file(os.path.join(output, f"ci-{framework}.yml"), configs.get(framework, configs["playwright"]))

def main():
    p = argparse.ArgumentParser(description="Generate QA Automation Boilerplate")
    p.add_argument("--framework", choices=["playwright", "cypress"], required=True)
    p.add_argument("--project", default="myapp")
    p.add_argument("--output", default="./qa")
    a = p.parse_args()

    print(f"\n🤖 Generating {a.framework} boilerplate for {a.project}\n")
    if a.framework == "playwright":
        gen_playwright(a.project, a.output)
    else:
        gen_cypress(a.project, a.output)
    gen_ci_config(a.framework, a.output)
    print(f"\n✅ Generated at: {a.output}/")

if __name__ == "__main__":
    main()

```
