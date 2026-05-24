# CI Integration & Visual Regression Reference

## 1. CI Pipeline Integration

### GitHub Actions — Playwright
```yaml
name: E2E Tests
on: [push, pull_request]

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
          BASE_URL: http://localhost:3000
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 7
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: test-traces
          path: test-results/
          retention-days: 7
```

### GitHub Actions — Cypress
```yaml
name: Cypress Tests
on: [push, pull_request]

jobs:
  cypress:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cypress-io/github-action@v6
        with:
          build: npm run build
          start: npm start
          wait-on: http://localhost:3000
          browser: chrome
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: cypress-screenshots
          path: cypress/screenshots
```

### Docker-Based E2E (Any CI)
```dockerfile
# Dockerfile.e2e
FROM mcr.microsoft.com/playwright:v1.42.0-noble
WORKDIR /tests
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["npx", "playwright", "test"]
```
```yaml
# docker-compose.e2e.yml
services:
  app:
    build: .
    ports: ["3000:3000"]
  e2e:
    build: { dockerfile: Dockerfile.e2e }
    depends_on: [app]
    environment:
      BASE_URL: http://app:3000
```

## 2. Parallel Execution

### Playwright Sharding
```yaml
# Run across multiple CI jobs
jobs:
  e2e:
    strategy:
      matrix:
        shard: [1/4, 2/4, 3/4, 4/4]
    steps:
      - run: npx playwright test --shard=${{ matrix.shard }}
```

### Test Categorization
```typescript
// Tag tests for selective runs
test('critical: checkout flow', { tag: ['@critical', '@checkout'] }, async ({ page }) => {
  // ...
});

// Run only critical tests on every PR
// npx playwright test --grep @critical

// Run full suite on main branch only
// npx playwright test
```

## 3. Visual Regression Testing

### Playwright Visual Comparison
```typescript
test('homepage visual regression', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveScreenshot('homepage.png', {
    maxDiffPixelRatio: 0.01,  // Allow 1% difference
    threshold: 0.2,           // Per-pixel color tolerance
    animations: 'disabled',   // Freeze animations
  });
});

test('product card component', async ({ page }) => {
  await page.goto('/products/widget');
  const card = page.getByTestId('product-card');
  await expect(card).toHaveScreenshot('product-card.png');
});

// Update baseline screenshots:
// npx playwright test --update-snapshots
```

### Percy (Cloud Visual Testing)
```typescript
import percySnapshot from '@percy/playwright';

test('visual: checkout page', async ({ page }) => {
  await page.goto('/checkout');
  await percySnapshot(page, 'Checkout Page', {
    widths: [375, 768, 1280],  // Mobile, tablet, desktop
  });
});
```

### Visual Regression Strategy

| Approach | Tool | Cost | Best For |
|----------|------|------|---------|
| Built-in screenshots | Playwright toHaveScreenshot | Free | Simple projects |
| Cloud visual testing | Percy, Chromatic, Applitools | Paid | Teams, cross-browser |
| Storybook + Chromatic | Chromatic | Free tier | Component libraries |

## 4. Cross-Browser Testing

### Playwright Multi-Browser
```typescript
// playwright.config.ts — run same tests on all browsers
projects: [
  { name: 'chromium', use: devices['Desktop Chrome'] },
  { name: 'firefox', use: devices['Desktop Firefox'] },
  { name: 'webkit', use: devices['Desktop Safari'] },
  { name: 'mobile-chrome', use: devices['Pixel 5'] },
  { name: 'mobile-safari', use: devices['iPhone 13'] },
]
```

### Browser-Specific Issues
```typescript
test('should handle file upload', async ({ page, browserName }) => {
  test.skip(browserName === 'webkit', 'File upload not supported in WebKit CI');
  // ...
});
```

## 5. Accessibility Testing

### Playwright + axe-core
```typescript
import AxeBuilder from '@axe-core/playwright';

test('homepage should have no a11y violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])  // WCAG 2.1 AA
    .exclude('.third-party-widget')    // Exclude things you don't control
    .analyze();
  expect(results.violations).toEqual([]);
});

test('login form accessibility', async ({ page }) => {
  await page.goto('/login');
  const results = await new AxeBuilder({ page })
    .include('[data-testid="login-form"]')
    .analyze();
  expect(results.violations).toEqual([]);
});
```

## 6. Flaky Test Management

| Strategy | Implementation |
|----------|---------------|
| Auto-retry | `retries: 2` in config (CI only) |
| Wait for stability | `await expect(el).toBeVisible()` (not `sleep`) |
| Isolate state | Fresh context/storage per test |
| Quarantine flaky | Tag with `@flaky`, investigate weekly |
| Track flake rate | CI dashboard, alert if > 5% |
| Fix root causes | Network mocks, test data isolation, deterministic IDs |



---
