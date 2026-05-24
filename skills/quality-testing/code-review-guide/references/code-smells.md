# Code Smells & Refactoring Reference

## 1. Code Smell Catalog

### Function/Method Level

| Smell | Symptom | Refactoring |
|-------|---------|------------|
| **Long method** | > 20 lines, does multiple things | Extract Method — split by responsibility |
| **Long parameter list** | > 3-4 parameters | Introduce Parameter Object or Builder |
| **Deeply nested** | 3+ levels of if/for nesting | Extract method, early returns, guard clauses |
| **Boolean parameters** | `doThing(true, false)` | Split into separate methods |
| **Side effects** | Function does hidden mutations | Make pure, return new values |
| **Magic numbers** | `if (status === 3)` | Extract to named constants |

### Class Level

| Smell | Symptom | Refactoring |
|-------|---------|------------|
| **God class** | Class does everything, 500+ lines | Extract classes by responsibility |
| **Feature envy** | Method uses another class's data more than its own | Move method to the data's class |
| **Data clumps** | Same 3-4 fields always appear together | Extract into value object/DTO |
| **Primitive obsession** | Using strings for emails, money, IDs | Introduce domain types |
| **Divergent change** | One class changes for many different reasons | Split by axis of change (SRP) |
| **Shotgun surgery** | One change requires editing many classes | Consolidate related logic |

### Architecture Level

| Smell | Symptom | Refactoring |
|-------|---------|------------|
| **Circular dependencies** | A depends on B depends on A | Extract shared interface, dependency inversion |
| **Leaky abstraction** | Implementation details exposed to callers | Encapsulate, define clean interfaces |
| **Dead code** | Unreachable code, unused exports | Delete it (Git remembers) |
| **Copy-paste** | Same logic in 3+ places | Extract shared function/module |
| **Inappropriate intimacy** | Classes know too much about each other's internals | Define interfaces, encapsulate |

## 2. Refactoring Patterns

### Extract Method
```python
# Before: long method doing multiple things
def process_order(order):
    # Validate
    if not order.items:
        raise ValueError("Empty order")
    if order.total <= 0:
        raise ValueError("Invalid total")
    # Calculate tax
    tax = order.total * 0.08
    if order.state == "OR":
        tax = 0
    total_with_tax = order.total + tax
    # Process payment
    payment = PaymentGateway.charge(order.user_id, total_with_tax)
    if not payment.success:
        raise PaymentError(payment.error)
    # Create record
    db.insert("orders", {**order.to_dict(), "tax": tax, "payment_id": payment.id})
    email_service.send_confirmation(order.user_id, order.id)

# After: each step is a clear, testable function
def process_order(order):
    validate_order(order)
    tax = calculate_tax(order)
    payment = charge_payment(order.user_id, order.total + tax)
    save_order(order, tax, payment.id)
    send_confirmation(order.user_id, order.id)
```

### Guard Clauses (Flatten Nesting)
```python
# Before: deep nesting
def get_discount(user, order):
    if user is not None:
        if user.is_premium:
            if order.total > 100:
                if not order.has_discount:
                    return 0.15
    return 0

# After: guard clauses
def get_discount(user, order):
    if user is None:
        return 0
    if not user.is_premium:
        return 0
    if order.total <= 100:
        return 0
    if order.has_discount:
        return 0
    return 0.15
```

### Replace Conditional with Polymorphism
```python
# Before: switch/if chain
def calculate_shipping(order):
    if order.type == "standard":
        return 5.99
    elif order.type == "express":
        return 15.99
    elif order.type == "overnight":
        return 29.99
    elif order.type == "international":
        return order.weight * 2.50

# After: strategy pattern
class ShippingStrategy(Protocol):
    def calculate(self, order: Order) -> float: ...

class StandardShipping:
    def calculate(self, order): return 5.99

class ExpressShipping:
    def calculate(self, order): return 15.99

STRATEGIES = {"standard": StandardShipping(), "express": ExpressShipping(), ...}
def calculate_shipping(order):
    return STRATEGIES[order.type].calculate(order)
```

### Introduce Parameter Object
```python
# Before: too many params
def search_users(name, email, role, department, active, created_after, created_before, limit):
    ...

# After: parameter object
@dataclass
class UserSearchCriteria:
    name: str | None = None
    email: str | None = None
    role: str | None = None
    department: str | None = None
    active: bool = True
    created_after: datetime | None = None
    created_before: datetime | None = None
    limit: int = 50

def search_users(criteria: UserSearchCriteria):
    ...
```

## 3. Technical Debt Tracking

### Severity Levels

| Level | Impact | Timeline | Example |
|-------|--------|---------|---------|
| **Critical** | Bugs, security, data loss risk | Sprint | SQL injection, no input validation |
| **High** | Slows development significantly | Quarter | No tests, God class, no CI/CD |
| **Medium** | Moderate friction | Semester | Inconsistent patterns, poor naming |
| **Low** | Minor annoyance | Backlog | Outdated comments, minor duplication |

### Tech Debt Decision
```
Is it blocking a feature? → Fix now
Is it causing bugs? → Fix this sprint
Is it slowing the team? → Fix this quarter
Is it just ugly? → Document, fix when nearby
```



---
