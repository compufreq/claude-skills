# QA Frameworks Reference

## 1. Framework Comparison

| Feature | Playwright | Cypress | Selenium | Appium |
|---------|-----------|---------|----------|--------|
| Languages | JS/TS, Python, Java, C# | JS/TS | All major | All major |
| Browsers | Chromium, Firefox, WebKit | Chrome, Firefox, Edge, WebKit | All via WebDriver | Mobile browsers |
| Mobile | Emulation only | No native | Via Appium | Native + hybrid |
| Speed | Very fast (parallel) | Fast (single tab) | Medium | Slow |
| Auto-wait | Built-in | Built-in | Manual waits | Manual waits |
| Network intercept | Full control | Full control | Limited | Limited |
| Multi-tab/window | Yes | Limited | Yes | N/A |
| iFrames | Easy | Difficult | Yes | N/A |
| CI-friendly | Excellent (Docker, traces) | Good | Good | Complex |
| Best for | Modern web, API, cross-browser | SPA testing, dev-friendly | Legacy, enterprise | Mobile apps |

### Recommendation
- **New projects:** Playwright (most capable, fastest, best DX)
- **React/Vue SPAs:** Playwright or Cypress
- **Enterprise/legacy:** Selenium (broadest ecosystem)
- **Mobile native:** Appium

## 2. Playwright

### Setup
```bash
npm init playwright@latest
# Creates: playwright.config.ts, tests/, .github/workflows/
```

### Configuration
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 4 : undefined,
  reporter: [['html'], ['junit', { outputFile: 'results.xml' }]],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'mobile-chrome', use: { ...devices['Pixel 5'] } },
    { name: 'mobile-safari', use: { ...devices['iPhone 13'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### Test Example
```typescript
import { test, expect } from '@playwright/test';

test.describe('Checkout Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: 'Login' }).click();
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Sign In' }).click();
    await expect(page.getByText('Welcome')).toBeVisible();
  });

  test('should complete checkout with valid payment', async ({ page }) => {
    // Add item to cart
    await page.goto('/products/widget-123');
    await page.getByRole('button', { name: 'Add to Cart' }).click();
    await expect(page.getByTestId('cart-count')).toHaveText('1');

    // Checkout
    await page.getByRole('link', { name: 'Cart' }).click();
    await page.getByRole('button', { name: 'Checkout' }).click();

    // Payment
    await page.getByLabel('Card Number').fill('4242424242424242');
    await page.getByLabel('Expiry').fill('12/28');
    await page.getByLabel('CVC').fill('123');
    await page.getByRole('button', { name: 'Pay' }).click();

    // Confirmation
    await expect(page.getByText('Order Confirmed')).toBeVisible({ timeout: 10000 });
    await expect(page.getByTestId('order-id')).toBeVisible();
  });

  test('should show error for declined card', async ({ page }) => {
    await page.goto('/cart');
    await page.getByRole('button', { name: 'Checkout' }).click();
    await page.getByLabel('Card Number').fill('4000000000000002'); // Decline card
    await page.getByLabel('Expiry').fill('12/28');
    await page.getByLabel('CVC').fill('123');
    await page.getByRole('button', { name: 'Pay' }).click();
    await expect(page.getByText('Payment declined')).toBeVisible();
  });
});
```

### API Testing with Playwright
```typescript
test('API: create and retrieve order', async ({ request }) => {
  // Create
  const createResponse = await request.post('/api/orders', {
    data: { items: [{ sku: 'WIDGET-1', quantity: 2 }] },
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(createResponse.ok()).toBeTruthy();
  const order = await createResponse.json();
  expect(order.id).toBeTruthy();

  // Retrieve
  const getResponse = await request.get(`/api/orders/${order.id}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const retrieved = await getResponse.json();
  expect(retrieved.items).toHaveLength(1);
});
```

## 3. Cypress

### Test Example
```javascript
describe('Login Flow', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('should login with valid credentials', () => {
    cy.get('[data-testid="email"]').type('test@example.com');
    cy.get('[data-testid="password"]').type('password123');
    cy.get('[data-testid="login-button"]').click();
    cy.url().should('include', '/dashboard');
    cy.contains('Welcome').should('be.visible');
  });

  it('should show error for invalid credentials', () => {
    cy.get('[data-testid="email"]').type('test@example.com');
    cy.get('[data-testid="password"]').type('wrong');
    cy.get('[data-testid="login-button"]').click();
    cy.contains('Invalid credentials').should('be.visible');
  });
});

// Custom command for reusable login
Cypress.Commands.add('login', (email, password) => {
  cy.session([email], () => {
    cy.visit('/login');
    cy.get('[data-testid="email"]').type(email);
    cy.get('[data-testid="password"]').type(password);
    cy.get('[data-testid="login-button"]').click();
    cy.url().should('include', '/dashboard');
  });
});
```

## 4. Appium (Mobile)

```javascript
const { remote } = require('webdriverio');

const capabilities = {
  platformName: 'Android',
  'appium:deviceName': 'Pixel_5',
  'appium:app': './app-release.apk',
  'appium:automationName': 'UiAutomator2',
};

describe('Mobile Login', () => {
  let driver;

  before(async () => {
    driver = await remote({ hostname: 'localhost', port: 4723, capabilities });
  });

  it('should login successfully', async () => {
    const emailField = await driver.$('~email-input');
    await emailField.setValue('test@example.com');
    const passwordField = await driver.$('~password-input');
    await passwordField.setValue('password123');
    const loginButton = await driver.$('~login-button');
    await loginButton.click();
    const welcome = await driver.$('~welcome-message');
    expect(await welcome.getText()).toContain('Welcome');
  });

  after(async () => { await driver.deleteSession(); });
});
```

## 5. Selector Strategy

| Priority | Strategy | Example | Why |
|----------|---------|---------|-----|
| 1st | `data-testid` | `[data-testid="submit"]` | Stable, decoupled from UI |
| 2nd | Role/label | `getByRole('button', { name: 'Submit' })` | Accessible, semantic |
| 3rd | Text content | `getByText('Submit')` | User-facing, readable |
| Avoid | CSS class | `.btn-primary` | Fragile, changes with styling |
| Avoid | XPath | `//div[3]/button` | Fragile, hard to read |



---
