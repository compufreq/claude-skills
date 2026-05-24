# OWASP Top 10 Attack & Defense Reference

## A01:2021 — Broken Access Control

### Attack Patterns
| Attack | Example | Impact |
|--------|---------|--------|
| IDOR | `GET /api/users/123` → change to `/api/users/456` | Access other users' data |
| Forced browsing | `GET /admin/dashboard` without admin role | Admin access |
| Parameter manipulation | Change `role=user` to `role=admin` in request | Privilege escalation |
| Insecure direct object ref | Predictable file paths, sequential IDs | Data exposure |

### Defense
```python
# Always verify ownership
@app.route('/api/documents/<doc_id>')
@login_required
def get_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.owner_id != current_user.id and not current_user.is_admin:
        abort(403)
    return jsonify(doc.to_dict())

# Use UUIDs instead of sequential IDs
import uuid
id = str(uuid.uuid4())  # "550e8400-e29b-41d4-a716-446655440000"
```

## A02:2021 — Cryptographic Failures

### Defense
```python
# Password hashing — use bcrypt or argon2, NEVER md5/sha1
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))
verified = bcrypt.checkpw(password.encode(), hashed)

# Encryption at rest — use AES-256-GCM
from cryptography.fernet import Fernet
key = Fernet.generate_key()  # Store in Secrets Manager, not code
f = Fernet(key)
encrypted = f.encrypt(b"sensitive data")
```

## A03:2021 — Injection

### SQL Injection Defense
```python
# ❌ NEVER concatenate user input into queries
query = f"SELECT * FROM users WHERE id = {user_input}"  # VULNERABLE

# ✅ Parameterized queries
cursor.execute("SELECT * FROM users WHERE id = %s", (user_input,))

# ✅ ORM (SQLAlchemy)
user = User.query.filter_by(id=user_input).first()
```

### XSS Defense
```javascript
// ❌ NEVER insert untrusted data into DOM
element.innerHTML = userInput;  // VULNERABLE

// ✅ Use textContent (auto-escapes)
element.textContent = userInput;

// ✅ React/Vue auto-escape by default
return <div>{userInput}</div>;  // Safe in React

// ✅ CSP header (defense-in-depth)
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'
```

### Command Injection Defense
```python
# ❌ NEVER pass user input to shell
os.system(f"ping {host}")  # VULNERABLE

# ✅ Use subprocess with list arguments
subprocess.run(["ping", "-c", "1", host], capture_output=True, check=True)

# ✅ Validate input format
import re
if not re.match(r'^[a-zA-Z0-9.-]+$', host):
    raise ValueError("Invalid hostname")
```

## A04:2021 — Insecure Design

### Defense: Threat Modeling
```
For each feature, ask:
1. What could go wrong? (STRIDE: Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation)
2. What are we doing about it?
3. Did we do a good enough job?
```

## A05:2021 — Security Misconfiguration

### Hardening Checklist
- [ ] Remove default accounts and passwords
- [ ] Disable unnecessary features, ports, services
- [ ] Configure error handling (no stack traces in production)
- [ ] Set security headers (CSP, HSTS, X-Content-Type-Options)
- [ ] Disable directory listing
- [ ] Keep all software up to date

## A06:2021 — Vulnerable Components
→ Use SCA tools (Trivy, Snyk, Dependabot) — see `devsecops-scanning` skill

## A07:2021 — Auth Failures
→ See `references/auth-security.md`

## A08:2021 — Data Integrity Failures
```python
# Verify software integrity
# Use SBOM, sign container images, verify checksums
# Don't deserialize untrusted data
import json
data = json.loads(user_input)  # ✅ Safe
# NEVER: pickle.loads(user_input)  # ❌ RCE risk
```

## A09:2021 — Logging & Monitoring Failures
```python
# Log security events
logger.warning("Failed login attempt", extra={
    "event": "auth.login.failed",
    "username": username,
    "ip": request.remote_addr,
    "user_agent": request.user_agent.string,
})

# What to log: login success/failure, access denied, input validation failures,
# password changes, role changes, admin actions, API key usage
```

## A10:2021 — SSRF
```python
# ❌ NEVER fetch user-provided URLs without validation
response = requests.get(user_url)  # VULNERABLE

# ✅ Allowlist domains
ALLOWED = {"api.example.com", "cdn.example.com"}
parsed = urllib.parse.urlparse(user_url)
if parsed.hostname not in ALLOWED:
    raise ValueError("Domain not allowed")
if parsed.scheme not in ("https",):
    raise ValueError("Only HTTPS allowed")

# ✅ Block internal/metadata IPs
import ipaddress
ip = ipaddress.ip_address(socket.gethostbyname(parsed.hostname))
if ip.is_private or ip.is_loopback or ip.is_link_local:
    raise ValueError("Internal IPs not allowed")
```
