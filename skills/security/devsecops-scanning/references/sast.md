# SAST Reference

## Table of Contents
1. Semgrep
2. CodeQL
3. SonarQube
4. Top 20 SAST Findings & Remediation

---

## 1. Semgrep

### GitHub Actions Integration
```yaml
- uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/owasp-top-ten
      p/javascript
      p/python
      p/typescript
    generateSarif: "1"
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: semgrep.sarif
```

### Custom Rules
```yaml
# .semgrep/custom-rules.yml
rules:
  - id: no-eval
    patterns:
      - pattern: eval(...)
    message: "Avoid eval() — use safer alternatives"
    languages: [javascript, typescript]
    severity: ERROR
    metadata:
      owasp: [A03:2021 - Injection]
      cwe: [CWE-95]

  - id: no-hardcoded-secrets
    patterns:
      - pattern: |
          $VAR = "..."
      - metavariable-regex:
          metavariable: $VAR
          regex: (password|secret|api_key|token)
      - metavariable-regex:
          metavariable: $VALUE
          regex: .{8,}
    message: "Possible hardcoded secret in $VAR"
    languages: [python, javascript, typescript, java, go]
    severity: ERROR

  - id: sql-injection-risk
    patterns:
      - pattern: |
          $QUERY = f"... {$INPUT} ..."
      - pattern-not: |
          $QUERY = f"... {$CONST} ..."
    message: "Possible SQL injection — use parameterized queries"
    languages: [python]
    severity: ERROR
    metadata:
      owasp: [A03:2021 - Injection]
```

### Semgrep Configuration
```yaml
# .semgrep.yml
rules:
  - p/owasp-top-ten
  - p/javascript
  - p/python
  - p/typescript
  - p/secrets
  - .semgrep/custom-rules.yml

exclude:
  - "test/**"
  - "**/*_test.go"
  - "node_modules/**"
  - "vendor/**"

severity:
  - ERROR
  - WARNING
```

---

## 2. CodeQL

### GitHub Actions
```yaml
# .github/workflows/codeql.yml
name: CodeQL Analysis
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6 AM

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      actions: read
      contents: read
    strategy:
      matrix:
        language: [javascript, python]  # Add your languages
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: security-extended  # security-and-quality for more
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3
        with:
          category: "/language:${{ matrix.language }}"
```

### Custom CodeQL Queries
```ql
// queries/hardcoded-credentials.ql
/**
 * @name Hardcoded credentials
 * @description Finds hardcoded passwords and API keys
 * @kind problem
 * @problem.severity error
 * @security-severity 9.0
 * @tags security
 */
import javascript

from StringLiteral s, VariableDeclarator v
where
  v.getInit() = s and
  v.getBindingPattern().(VarDecl).getName().regexpMatch("(?i)(password|secret|api.?key|token)") and
  s.getValue().length() > 5
select s, "Possible hardcoded credential: " + v.getBindingPattern().(VarDecl).getName()
```

---

## 3. SonarQube

### Docker Setup
```bash
docker run -d --name sonarqube \
  -p 9000:9000 \
  -v sonar_data:/opt/sonarqube/data \
  sonarqube:lts-community
```

### CI Integration
```yaml
# GitHub Actions
- uses: SonarSource/sonarqube-scan-action@v3
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
  with:
    args: >
      -Dsonar.projectKey=myapp
      -Dsonar.sources=src/
      -Dsonar.tests=tests/
      -Dsonar.javascript.lcov.reportPaths=coverage/lcov.info
```

### Quality Gate
```
# sonar-project.properties
sonar.projectKey=myapp
sonar.sources=src/
sonar.tests=tests/
sonar.qualitygate.wait=true        # Fail CI if gate fails
sonar.qualitygate.timeout=300
```

---

## 4. Top 20 SAST Findings & Remediation

### 1. SQL Injection (CWE-89)
```python
# ❌ Vulnerable
query = f"SELECT * FROM users WHERE id = {user_input}"
cursor.execute(query)

# ✅ Fixed — parameterized query
cursor.execute("SELECT * FROM users WHERE id = %s", (user_input,))
```

### 2. Cross-Site Scripting / XSS (CWE-79)
```javascript
// ❌ Vulnerable
element.innerHTML = userInput;

// ✅ Fixed — use textContent or sanitize
element.textContent = userInput;
// Or: DOMPurify.sanitize(userInput)
```

### 3. Command Injection (CWE-78)
```python
# ❌ Vulnerable
os.system(f"ping {user_input}")

# ✅ Fixed — use subprocess with list args
subprocess.run(["ping", "-c", "1", user_input], check=True)
```

### 4. Path Traversal (CWE-22)
```python
# ❌ Vulnerable
file_path = os.path.join("/uploads", user_filename)
open(file_path)

# ✅ Fixed — resolve and validate
safe_path = os.path.realpath(os.path.join("/uploads", user_filename))
if not safe_path.startswith(os.path.realpath("/uploads")):
    raise ValueError("Invalid path")
```

### 5. Hardcoded Credentials (CWE-798)
```python
# ❌ Vulnerable
DB_PASSWORD = "supersecret123"

# ✅ Fixed — environment variable
DB_PASSWORD = os.environ["DB_PASSWORD"]
```

### 6. Insecure Deserialization (CWE-502)
```python
# ❌ Vulnerable
data = pickle.loads(user_input)

# ✅ Fixed — use safe formats
data = json.loads(user_input)
```

### 7. Missing Authentication (CWE-306)
```python
# ❌ Vulnerable — no auth check
@app.route("/admin/users")
def admin_users():
    return get_all_users()

# ✅ Fixed — require authentication
@app.route("/admin/users")
@login_required
@require_role("admin")
def admin_users():
    return get_all_users()
```

### 8. Broken Access Control (CWE-284)
```python
# ❌ Vulnerable — no ownership check
@app.route("/api/documents/<doc_id>")
def get_document(doc_id):
    return Document.query.get(doc_id)

# ✅ Fixed — verify ownership
@app.route("/api/documents/<doc_id>")
@login_required
def get_document(doc_id):
    doc = Document.query.get(doc_id)
    if doc.owner_id != current_user.id:
        abort(403)
    return doc
```

### 9. Weak Cryptography (CWE-327)
```python
# ❌ Vulnerable
hashlib.md5(password.encode())
hashlib.sha1(password.encode())

# ✅ Fixed — use bcrypt/argon2 for passwords
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))
```

### 10. SSRF (CWE-918)
```python
# ❌ Vulnerable
response = requests.get(user_provided_url)

# ✅ Fixed — allowlist domains
ALLOWED_DOMAINS = {"api.example.com", "cdn.example.com"}
parsed = urlparse(user_provided_url)
if parsed.hostname not in ALLOWED_DOMAINS:
    raise ValueError("Domain not allowed")
```

### 11-20 Quick Reference

| # | Finding | CWE | Fix |
|---|---------|-----|-----|
| 11 | Open redirect | CWE-601 | Validate redirect URLs against allowlist |
| 12 | XML External Entity (XXE) | CWE-611 | Disable external entities in XML parser |
| 13 | Insufficient logging | CWE-778 | Log auth events, access denials, input validation failures |
| 14 | Unvalidated input | CWE-20 | Validate type, length, range, format on all inputs |
| 15 | Sensitive data exposure | CWE-200 | Don't log PII, mask in error messages |
| 16 | Missing CSRF protection | CWE-352 | Use CSRF tokens on state-changing requests |
| 17 | Insecure cookie | CWE-614 | Set Secure, HttpOnly, SameSite flags |
| 18 | Race condition | CWE-362 | Use database transactions, optimistic locking |
| 19 | Integer overflow | CWE-190 | Validate bounds, use safe math libraries |
| 20 | Use after free / memory | CWE-416 | Use memory-safe languages, or ASAN in C/C++ |



---
