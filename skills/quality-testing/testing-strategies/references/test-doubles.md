# Test Doubles & Patterns Reference

## 1. Test Double Types

| Double | Purpose | When to Use |
|--------|---------|-------------|
| **Stub** | Returns fixed values | Replace dependency with predictable output |
| **Mock** | Verifies interactions | Assert a method was called with specific args |
| **Fake** | Working implementation (simplified) | In-memory DB, local file system |
| **Spy** | Records calls, delegates to real | Observe behavior without replacing |
| **Dummy** | Placeholder, never used | Fill required parameters |

## 2. Python Examples (pytest + unittest.mock)

### Stubs
```python
from unittest.mock import patch, MagicMock

# Stub an external service
@patch('services.payment.PaymentGateway.charge')
def test_process_order_successful_payment(mock_charge):
    mock_charge.return_value = PaymentResult(success=True, id="pay_123")
    result = OrderService.process(order)
    assert result.status == "confirmed"

# Stub with side_effect for different calls
@patch('services.inventory.check_stock')
def test_partial_availability(mock_stock):
    mock_stock.side_effect = [True, False, True]  # item1: yes, item2: no, item3: yes
    result = OrderService.check_availability(items)
    assert result.unavailable == ["item2"]
```

### Mocks (Verify Interactions)
```python
@patch('services.email.send')
def test_sends_confirmation_email(mock_send):
    OrderService.process(order)
    mock_send.assert_called_once_with(
        to=order.user_email,
        template="order_confirmation",
        data={"order_id": order.id, "total": order.total}
    )

# Verify NOT called
@patch('services.email.send')
def test_no_email_on_failed_payment(mock_send):
    with patch('services.payment.PaymentGateway.charge', return_value=PaymentResult(success=False)):
        with pytest.raises(PaymentError):
            OrderService.process(order)
    mock_send.assert_not_called()
```

### Fakes
```python
# In-memory repository (fake)
class InMemoryUserRepository:
    def __init__(self):
        self._users = {}

    def save(self, user):
        self._users[user.id] = user

    def find_by_id(self, user_id):
        return self._users.get(user_id)

    def find_by_email(self, email):
        return next((u for u in self._users.values() if u.email == email), None)

# Use in tests
def test_create_user():
    repo = InMemoryUserRepository()
    service = UserService(repository=repo)
    user = service.create(name="Alice", email="alice@example.com")
    assert repo.find_by_id(user.id).name == "Alice"
```

## 3. JavaScript/TypeScript Examples (Jest)

### Stubs & Mocks
```typescript
// Mock module
jest.mock('./paymentGateway');

import { PaymentGateway } from './paymentGateway';
const mockCharge = PaymentGateway.charge as jest.MockedFunction<typeof PaymentGateway.charge>;

describe('OrderService', () => {
  it('should confirm order on successful payment', async () => {
    mockCharge.mockResolvedValue({ success: true, id: 'pay_123' });
    const result = await OrderService.process(order);
    expect(result.status).toBe('confirmed');
    expect(mockCharge).toHaveBeenCalledWith(order.userId, order.total);
  });

  it('should throw on failed payment', async () => {
    mockCharge.mockResolvedValue({ success: false, error: 'declined' });
    await expect(OrderService.process(order)).rejects.toThrow('Payment failed');
  });
});
```

### Spy
```typescript
it('should log failed attempts', async () => {
  const logSpy = jest.spyOn(logger, 'warn');
  await authService.login('user', 'wrong-password');
  expect(logSpy).toHaveBeenCalledWith(
    expect.stringContaining('Failed login'),
    expect.objectContaining({ username: 'user' })
  );
  logSpy.mockRestore();
});
```

## 4. Testing Patterns

### Arrange-Act-Assert (AAA)
```python
def test_apply_discount():
    # Arrange
    order = Order(items=[Item(price=100)], coupon="SAVE10")
    discount_service = DiscountService()

    # Act
    result = discount_service.apply(order)

    # Assert
    assert result.total == 90
    assert result.discount_applied == 10
```

### Builder Pattern for Test Data
```python
class OrderBuilder:
    def __init__(self):
        self._order = Order(id="ord-1", user_id="usr-1", items=[], status="pending")

    def with_items(self, *items):
        self._order.items = list(items)
        return self

    def with_status(self, status):
        self._order.status = status
        return self

    def with_total(self, total):
        self._order.total = total
        return self

    def build(self):
        return self._order

# Usage
order = OrderBuilder().with_items(item1, item2).with_total(99.99).build()
```

### Parameterized Tests
```python
@pytest.mark.parametrize("input_val,expected", [
    ("hello@example.com", True),
    ("invalid-email", False),
    ("", False),
    ("a@b.c", True),
    ("user@.com", False),
])
def test_validate_email(input_val, expected):
    assert validate_email(input_val) == expected
```

## 5. What NOT to Mock

| Don't Mock | Why | Instead |
|-----------|-----|---------|
| Value objects | No side effects, fast | Use real objects |
| Pure functions | Deterministic, no I/O | Call directly |
| Data structures | No behavior | Use real data |
| The thing you're testing | Defeats the purpose | Test the real implementation |
| Everything | Tautological tests | Mock boundaries only |

**Rule of thumb:** Mock at architectural boundaries (DB, APIs, file system, external services). Don't mock internal collaborators unless they're slow or non-deterministic.



---
