# DAST Reference

## Table of Contents
1. OWASP ZAP
2. ZAP CI Integration
3. API Scanning
4. DAST Finding Remediation

---

## 1. OWASP ZAP

### Scan Types

| Scan | Time | Depth | Use Case |
|------|------|-------|---------|
| **Baseline** | 1-5 min | Passive only | PR/CI gates |
| **Full** | 30-120 min | Active + passive | Scheduled/release |
| **API** | 5-30 min | OpenAPI-guided | API-only apps |
| **AJAX Spider** | 15-60 min | JS-heavy apps | SPAs, modern web |

### Docker Quick Start
```bash
# Baseline scan (passive — safe for CI)
docker run --rm -t zaproxy/zap-stable zap-baseline.py \
  -t https://staging.example.com \
  -r report.html

# Full scan (active — only against staging/test)
docker run --rm -t zaproxy/zap-stable zap-full-scan.py \
  -t https://staging.example.com \
  -r report.html

# API scan
docker run --rm -t zaproxy/zap-stable zap-api-scan.py \
  -t https://staging.example.com/openapi.json \
  -f openapi \
  -r report.html
```

---

## 2. ZAP CI Integration

### GitHub Actions — Baseline Scan
```yaml
zap-scan:
  runs-on: ubuntu-latest
  needs: deploy-staging
  steps:
    - name: ZAP Baseline Scan
      uses: zaproxy/action-baseline@v0.12.0
      with:
        target: 'https://staging.example.com'
        rules_file_name: '.zap/rules.tsv'
        fail_action: 'true'           # Fail on alerts
        allow_issue_writing: 'false'

    - name: Upload Report
      uses: actions/upload-artifact@v4
      with:
        name: zap-report
        path: report_html.html
```

### GitHub Actions — Full Scan
```yaml
zap-full-scan:
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  steps:
    - name: ZAP Full Scan
      uses: zaproxy/action-full-scan@v0.10.0
      with:
        target: 'https://staging.example.com'
        rules_file_name: '.zap/rules.tsv'
```

### ZAP Rules File
```tsv
# .zap/rules.tsv
# Rule ID	Action	Parameter
10010	IGNORE		# Cookie No HttpOnly Flag (handled by framework)
10011	WARN		# Cookie Without Secure Flag
10015	FAIL		# Incomplete or No Cache-control Headers
10021	FAIL		# X-Content-Type-Options Missing
10038	FAIL		# Content Security Policy Missing
40012	FAIL		# Cross Site Scripting (Reflected)
40014	FAIL		# Cross Site Scripting (Persistent)
40018	FAIL		# SQL Injection
90033	WARN		# Loosely Scoped Cookie
```

### GitLab CI
```yaml
dast:
  image: zaproxy/zap-stable
  stage: test
  script:
    - zap-baseline.py -t https://staging.example.com -r report.html -I
  artifacts:
    paths: [report.html]
    expire_in: 7 days
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
```

---

## 3. API Scanning

### With OpenAPI Spec
```bash
docker run --rm -t zaproxy/zap-stable zap-api-scan.py \
  -t https://staging.example.com/openapi.json \
  -f openapi \
  -r api-report.html \
  -c zap-api-config.conf
```

### ZAP API Config
```
# zap-api-config.conf
# Authentication
replacer.full_list(0).description=Add auth header
replacer.full_list(0).enabled=true
replacer.full_list(0).matchtype=REQ_HEADER
replacer.full_list(0).matchstr=Authorization
replacer.full_list(0).replacement=Bearer ${API_TOKEN}
```

### Authenticated Scanning
```bash
# Form-based auth
docker run --rm -t zaproxy/zap-stable zap-full-scan.py \
  -t https://staging.example.com \
  -r report.html \
  --hook=/zap/auth_hook.py

# Auth hook script
# auth_hook.py
def zap_started(zap, target):
    zap.authentication.set_authentication_method(
        context_id, 'formBasedAuthentication',
        'loginUrl=https://staging.example.com/login&loginRequestData=username%3D{%username%}%26password%3D{%password%}'
    )
    zap.users.set_user_enabled(context_id, user_id, True)
    zap.forcedUser.set_forced_user(context_id, user_id)
```

---

## 4. DAST Finding Remediation

### Security Headers
```
# ❌ Missing headers
# ✅ Add to server/reverse proxy configuration

# Nginx
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "0" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

# Express.js — use helmet
const helmet = require('helmet');
app.use(helmet());

# Django
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
```

### Cookie Security
```python
# ❌ Insecure cookie
response.set_cookie("session", value, httponly=False, secure=False)

# ✅ Secure cookie
response.set_cookie("session", value,
    httponly=True,
    secure=True,
    samesite="Lax",
    max_age=3600,
    path="/",
    domain=".example.com"
)
```

### CORS Configuration
```python
# ❌ Overly permissive
Access-Control-Allow-Origin: *

# ✅ Restrictive
CORS_ALLOWED_ORIGINS = [
    "https://app.example.com",
    "https://admin.example.com",
]
CORS_ALLOW_CREDENTIALS = True
```



---
