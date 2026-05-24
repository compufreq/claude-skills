# TDD & BDD Reference

## 1. Test-Driven Development (TDD)

### Red-Green-Refactor Cycle
```
1. RED    — Write a failing test for the next small behavior
2. GREEN  — Write the minimum code to make it pass
3. REFACTOR — Clean up code while keeping tests green
4. REPEAT
```

### TDD Example (Python)
```python
# Step 1: RED — write failing test
def test_empty_cart_total_is_zero():
    cart = ShoppingCart()
    assert cart.total() == 0

# Step 2: GREEN — minimal implementation
class ShoppingCart:
    def total(self):
        return 0

# Step 3: RED — next behavior
def test_single_item_total():
    cart = ShoppingCart()
    cart.add(Item("Widget", price=9.99))
    assert cart.total() == 9.99

# Step 4: GREEN — make it pass
class ShoppingCart:
    def __init__(self):
        self._items = []

    def add(self, item):
        self._items.append(item)

    def total(self):
        return sum(item.price for item in self._items)

# Step 5: RED — discount behavior
def test_total_with_percentage_discount():
    cart = ShoppingCart()
    cart.add(Item("Widget", price=100))
    cart.apply_discount(percent=10)
    assert cart.total() == 90

# Continue cycle...
```

### When TDD Helps Most
- Complex business logic with many edge cases
- Algorithms and data transformations
- APIs with well-defined contracts
- Bug fixes (write test that reproduces bug first)

### When TDD is Less Practical
- Exploratory/prototype code (design unknown)
- UI/visual layouts
- Integration with unknown external APIs
- One-off scripts

## 2. Behavior-Driven Development (BDD)

### Gherkin Syntax
```gherkin
Feature: Shopping Cart Checkout
  As a customer
  I want to checkout my shopping cart
  So that I can purchase my items

  Scenario: Successful checkout with valid payment
    Given I have items in my cart totaling $99.99
    And I am logged in as "alice@example.com"
    When I proceed to checkout
    And I enter valid payment details
    Then my order should be confirmed
    And I should receive a confirmation email
    And my cart should be empty

  Scenario: Checkout with insufficient inventory
    Given I have 5 units of "Widget" in my cart
    But only 3 units of "Widget" are in stock
    When I proceed to checkout
    Then I should see an error "Insufficient stock for Widget"
    And my cart should still contain 5 units

  Scenario Outline: Shipping cost by order total
    Given I have items totaling <total> in my cart
    When I view the shipping cost
    Then shipping should be <shipping>

    Examples:
      | total  | shipping |
      | $25.00 | $5.99    |
      | $50.00 | $3.99    |
      | $75.00 | $0.00    |
```

### BDD with pytest-bdd (Python)
```python
from pytest_bdd import scenario, given, when, then, parsers

@scenario('features/checkout.feature', 'Successful checkout with valid payment')
def test_successful_checkout():
    pass

@given(parsers.parse('I have items in my cart totaling ${total:f}'))
def cart_with_items(total):
    cart = ShoppingCart()
    cart.add(Item("Test Item", price=total))
    return cart

@given(parsers.parse('I am logged in as "{email}"'))
def logged_in_user(email):
    return User(email=email, authenticated=True)

@when('I proceed to checkout')
def proceed_to_checkout(cart, logged_in_user):
    return CheckoutService.initiate(cart, logged_in_user)

@then('my order should be confirmed')
def order_confirmed(checkout_result):
    assert checkout_result.status == "confirmed"
```

### BDD with Cucumber.js (JavaScript)
```javascript
const { Given, When, Then } = require('@cucumber/cucumber');
const { expect } = require('chai');

Given('I have items in my cart totaling ${float}', function(total) {
  this.cart = new ShoppingCart();
  this.cart.add(new Item('Test', total));
});

When('I proceed to checkout', async function() {
  this.result = await checkout(this.cart, this.user);
});

Then('my order should be confirmed', function() {
  expect(this.result.status).to.equal('confirmed');
});
```

## 3. Contract Testing

### Consumer-Driven Contracts (Pact)
```
Consumer (Frontend) defines: "I expect GET /api/users/123 to return { id, name, email }"
Provider (Backend) verifies: "My API satisfies all consumer contracts"

If provider changes response shape → contract test fails → breaking change caught
```

```javascript
// Consumer side (Pact)
const interaction = {
  state: 'user 123 exists',
  uponReceiving: 'a request for user 123',
  withRequest: { method: 'GET', path: '/api/users/123' },
  willRespondWith: {
    status: 200,
    body: {
      id: like('123'),
      name: like('Alice'),
      email: like('alice@example.com'),
    },
  },
};
```

### When to Use Contract Testing
- Microservices with many consumers
- API versioning decisions
- Frontend-backend teams working independently
- Replacing expensive E2E tests for API shape verification



---
