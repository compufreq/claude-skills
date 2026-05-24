# API Security Reference

## 1. REST API Security

### OWASP API Top 10 (2023)

| # | Risk | Defense |
|---|------|---------|
| API1 | Broken Object Level Authorization | Verify ownership on every object access |
| API2 | Broken Authentication | Strong auth, rate limiting, MFA |
| API3 | Broken Object Property Level Authorization | Return only authorized fields |
| API4 | Unrestricted Resource Consumption | Rate limiting, pagination, max payload size |
| API5 | Broken Function Level Authorization | RBAC on every endpoint |
| API6 | Unrestricted Access to Sensitive Business Flows | Bot detection, CAPTCHA, business logic controls |
| API7 | Server Side Request Forgery | URL allowlisting, block internal IPs |
| API8 | Security Misconfiguration | Harden defaults, disable debug, security headers |
| API9 | Improper Inventory Management | API catalog, deprecation policy, versioning |
| API10 | Unsafe Consumption of APIs | Validate all third-party API responses |

### Rate Limiting
```python
# Token bucket (recommended)
from flask_limiter import Limiter
limiter = Limiter(app, default_limits=["100 per minute"])

@app.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute")  # Strict for login
def login():
    pass

@app.route("/api/data")
@limiter.limit("100 per minute")  # Standard for API
def get_data():
    pass

# Express.js
const rateLimit = require('express-rate-limit');
app.use('/api/', rateLimit({ windowMs: 60000, max: 100 }));
app.use('/api/login', rateLimit({ windowMs: 60000, max: 5 }));
```

### Input Validation
```python
from pydantic import BaseModel, validator, constr, conint
from typing import Optional

class CreateUserRequest(BaseModel):
    name: constr(min_length=1, max_length=100, pattern=r'^[a-zA-Z\s]+$')
    email: constr(pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    age: conint(ge=13, le=150)
    role: Optional[str] = "user"  # Default, never trust client-set role

    @validator('role')
    def validate_role(cls, v):
        if v not in ('user', 'editor'):  # Never allow 'admin' from input
            raise ValueError('Invalid role')
        return v
```

## 2. GraphQL Security

### Common GraphQL Attacks

| Attack | Example | Defense |
|--------|---------|---------|
| Introspection abuse | `{ __schema { types { name } } }` | Disable in production |
| Deep nesting DoS | `{ user { friends { friends { friends... } } } }` | Query depth limiting |
| Batching abuse | Send 100 queries in one request | Query cost analysis |
| Alias flooding | `{ a1: user(id:1) a2: user(id:2) ... a1000: ... }` | Alias limiting |

### GraphQL Hardening
```javascript
// Apollo Server security configuration
const server = new ApolloServer({
  schema,
  introspection: process.env.NODE_ENV !== 'production',  // Disable in prod
  plugins: [
    // Query depth limiting
    depthLimitPlugin(10),
    // Query cost analysis
    queryCostPlugin({ maxCost: 1000 }),
  ],
  validationRules: [
    // Disable introspection queries in production
    process.env.NODE_ENV === 'production' ? NoSchemaIntrospectionCustomRule : undefined,
  ].filter(Boolean),
});
```
