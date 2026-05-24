# Authentication & Authorization Security Reference

## 1. JWT Security

### Secure JWT Implementation
```python
# ✅ Good JWT practices
import jwt
token = jwt.encode({
    "sub": user_id,
    "iat": datetime.utcnow(),
    "exp": datetime.utcnow() + timedelta(minutes=15),  # Short-lived
    "iss": "myapp",
    "aud": "myapp-api",
    "jti": str(uuid.uuid4()),  # Unique token ID (prevent replay)
}, SECRET_KEY, algorithm="HS256")

# Verification — always validate ALL claims
decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"],
    audience="myapp-api", issuer="myapp")
```

### JWT Attack Vectors & Prevention

| Attack | How | Prevention |
|--------|-----|-----------|
| Algorithm confusion (none) | Set alg=none to skip verification | Always specify `algorithms=["HS256"]` |
| Key confusion (RS→HS) | Use public key as HMAC secret | Explicitly set algorithm on verification |
| Token theft | XSS, network sniffing | HttpOnly cookies, TLS, short expiry |
| Brute force secret | Offline cracking of HS256 | Use RS256 (asymmetric) or strong secret (256+ bits) |
| Token replay | Reuse stolen token | Short expiry, `jti` claim, token blacklist |

### Access + Refresh Token Pattern
```
Login → Access Token (15 min) + Refresh Token (7 days, HttpOnly cookie)
API call → Send Access Token in Authorization header
Token expired → Use Refresh Token to get new Access Token
Logout → Revoke Refresh Token (server-side blacklist)
```

## 2. OAuth 2.0 / OIDC Security

### Secure OAuth Flow (Authorization Code + PKCE)
```
1. Client generates code_verifier (random 43-128 chars)
2. Client computes code_challenge = SHA256(code_verifier)
3. Client redirects to /authorize with code_challenge
4. User authenticates at IdP
5. IdP redirects back with authorization code
6. Client exchanges code + code_verifier for tokens
7. IdP verifies SHA256(code_verifier) == code_challenge
```

### OAuth Security Checklist
- [ ] Use Authorization Code flow with PKCE (never Implicit)
- [ ] Validate `state` parameter to prevent CSRF
- [ ] Validate `redirect_uri` against strict allowlist
- [ ] Store tokens securely (not localStorage — use HttpOnly cookies)
- [ ] Validate token issuer, audience, expiration
- [ ] Use short-lived access tokens (5-15 minutes)
- [ ] Implement token revocation endpoint

## 3. Session Management

### Secure Session Configuration
```python
# Flask
app.config['SESSION_COOKIE_SECURE'] = True       # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True      # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'    # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 3600   # 1 hour
app.config['SESSION_COOKIE_NAME'] = '__Host-session'  # Cookie prefix

# Express.js
app.use(session({
    secret: process.env.SESSION_SECRET,
    name: '__Host-session',
    cookie: {
        secure: true,
        httpOnly: true,
        sameSite: 'lax',
        maxAge: 3600000,
        path: '/',
    },
    resave: false,
    saveUninitialized: false,
}));
```

### Session Attacks & Prevention

| Attack | Prevention |
|--------|-----------|
| Session fixation | Regenerate session ID after login |
| Session hijacking | HttpOnly + Secure flags, bind to IP/user-agent |
| CSRF | SameSite cookie + CSRF token |
| Session replay | Short expiry, one-time tokens |

## 4. Password Security

### Password Policy
```python
# Minimum requirements (NIST 800-63B)
MIN_LENGTH = 8            # Absolute minimum
RECOMMENDED_LENGTH = 12   # Recommended
MAX_LENGTH = 128          # Prevent DoS via bcrypt
BREACHED_PASSWORD_CHECK = True  # Check against Have I Been Pwned

# DO NOT require: uppercase, special chars, frequent rotation
# DO require: minimum length, breached password check, MFA
```

### Secure Password Storage
```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

## 5. Multi-Factor Authentication

### MFA Implementation
```python
import pyotp

# Generate secret for user (store encrypted in DB)
secret = pyotp.random_base32()
totp = pyotp.TOTP(secret)

# Generate QR code URL
provisioning_uri = totp.provisioning_uri(
    name=user.email,
    issuer_name="MyApp"
)

# Verify TOTP code
is_valid = totp.verify(user_code, valid_window=1)  # ±30 seconds
```

### MFA Bypass Prevention
- Don't allow MFA skip via API directly
- Rate-limit MFA attempts (5 attempts, then lockout)
- Don't reveal which MFA factor failed
- Implement backup codes (one-time use, stored hashed)
- Don't trust "remember this device" for sensitive operations



---
