# Security Hardening for HTMX Applications

## Table of Contents
1. [The Four Golden Rules](#golden-rules)
2. [XSS Prevention](#xss-prevention)
3. [CSRF Protection](#csrf-protection)
4. [Content Security Policy (CSP)](#csp)
5. [HTMX Security Configuration](#htmx-config)
6. [Input Validation](#input-validation)
7. [Authentication Patterns](#authentication)
8. [Defense in Depth Checklist](#checklist)

---

## The Four Golden Rules

The htmx team's security essay establishes four foundational rules. Follow all four
and your HTMX app will be as secure as any SPA or traditional web app:

1. **Use an auto-escaping template engine** — Jinja2, Django templates, Go's html/template,
   and similar engines escape HTML by default. Never use `|safe`, `{% autoescape off %}`,
   `template.HTML()`, or `dangerouslySetInnerHTML` unless you have sanitized the content.

2. **Only serve routes you control** — `htmx.config.selfRequestsOnly` defaults to `true`
   in HTMX 2.x. Only same-origin requests are allowed. Don't disable this unless you
   have a specific need and understand the implications.

3. **Use secure cookie attributes** — Set `HttpOnly`, `Secure`, and `SameSite=Lax` (or
   `Strict`) on session/auth cookies. This prevents JavaScript from accessing cookies
   and provides CSRF protection.

4. **Sanitize user-generated HTML** — If you must render raw HTML from users (rich text
   editors, markdown), use a server-side sanitizer like Bleach (Python), DOMPurify on
   server, or bluemonday (Go). Whitelist allowed tags and attributes. Always strip `hx-*`
   and `data-hx-*` attributes from user content.

---

## XSS Prevention

HTMX swaps raw HTML into the DOM, so XSS prevention is critical. The risk is the same
as any server-rendered app — the difference is that HTMX makes HTML more expressive,
so injected `hx-*` attributes are dangerous too.

### Auto-Escaping (Primary Defense)
Every template engine should escape by default:

**Jinja2 (Flask)**: Escaping is on by default. `{{ user_input }}` is safe.
`{{ user_input | safe }}` is dangerous — only use on sanitized content.

**Django**: Escaping is on by default. `{{ user_input }}` is safe.
`{{ user_input | safe }}` and `{% autoescape off %}` are dangerous.

**Go html/template**: Escaping is on by default. Using `text/template` instead
of `html/template` is dangerous.

### Stripping HTMX Attributes from User Content
If you render user HTML (e.g., from a rich text editor), strip HTMX attributes:
```python
# Python example using bleach
import bleach

ALLOWED_TAGS = ['p', 'b', 'i', 'em', 'strong', 'a', 'ul', 'ol', 'li', 'br', 'h1', 'h2', 'h3']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}
# Note: hx-*, data-hx-*, hx-on:* are NOT in the whitelist — they're stripped

def sanitize_html(raw_html):
    return bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
```

### Using hx-disable
Wrap user-generated content in an element with `hx-disable` to prevent HTMX processing:
```html
<div hx-disable>
    {{ user_generated_content | safe }}
</div>
```
This cannot be overridden by injected content — if `hx-disable` appears anywhere in an
element's ancestor chain, HTMX will not process that element.

---

## CSRF Protection

### SameSite Cookies (Primary Defense)
Modern browsers support `SameSite` cookie attributes:
- `SameSite=Lax` — cookies not sent on cross-site POST requests (default in modern browsers)
- `SameSite=Strict` — cookies never sent cross-site

For most HTMX apps with `selfRequestsOnly: true` and `SameSite=Lax` cookies, CSRF
tokens may not be strictly necessary. However, defense in depth is recommended.

### CSRF Token Patterns
See `python-backends.md` for Django-specific CSRF patterns (3 approaches).

General pattern for any framework:
```html
<!-- Global CSRF header on body -->
<body hx-headers='{"X-CSRF-Token": "SERVER_GENERATED_TOKEN"}'>
```

Or per-form with a hidden input:
```html
<form hx-post="/action">
    <input type="hidden" name="_csrf" value="SERVER_GENERATED_TOKEN">
    ...
</form>
```

### CSRF for Non-Form Requests
Buttons with `hx-delete`, `hx-put`, etc. don't have a form to include the token.
Use the `hx-headers` approach on `<body>` or use `htmx:configRequest`:
```javascript
document.body.addEventListener('htmx:configRequest', function(evt) {
    if (!/^(GET|HEAD|OPTIONS)$/i.test(evt.detail.verb)) {
        evt.detail.headers['X-CSRF-Token'] = getMeta('csrf-token');
    }
});
```

---

## Content Security Policy (CSP)

### Baseline CSP for HTMX
```http
Content-Security-Policy:
    default-src 'self';
    script-src 'self' https://cdn.jsdelivr.net;
    style-src 'self' 'unsafe-inline';
    connect-src 'self';
    img-src 'self' data:;
```

### HTMX Features That Require `unsafe-eval`
These features use `new Function()` internally:
- `hx-on:*` attributes (inline event handlers)
- Trigger filters (e.g., `hx-trigger="click[ctrlKey]"`)
- `hx-vals` with `js:` prefix
- `hx-headers` with `js:` prefix

If you need a strict CSP without `unsafe-eval`:
```javascript
// Disable eval-based features
htmx.config.allowEval = false;
```
This disables `hx-on:*`, trigger filters, and `js:` expressions. You'll need to use
`addEventListener` and `htmx:configRequest` instead.

### Using Nonces with HTMX
```javascript
htmx.config.inlineScriptNonce = "SERVER_GENERATED_NONCE";
htmx.config.inlineStyleNonce = "SERVER_GENERATED_NONCE";
```
This applies the nonce to any `<script>` or `<style>` elements htmx creates.

### CSP for HTMX + Extensions from CDN
```http
Content-Security-Policy:
    default-src 'self';
    script-src 'self' https://cdn.jsdelivr.net 'nonce-ABC123';
    connect-src 'self' wss://yourdomain.com;
    style-src 'self' 'unsafe-inline';
```

### safe-nonce Extension
For trusted inline scripts in HTMX responses:
```html
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-safe-nonce/dist/safe-nonce.min.js"></script>
<body hx-ext="safe-nonce">
```
This extension allows you to return inline scripts safely in server responses by applying nonces.

---

## HTMX Security Configuration

All configuration options relevant to security:

```javascript
htmx.config.selfRequestsOnly = true;    // Default: true. Only allow same-origin requests
htmx.config.allowScriptTags = true;      // Default: true. Process <script> in responses
htmx.config.allowEval = true;            // Default: true. Allow eval-based features
htmx.config.historyCacheSize = 10;       // Default: 10. Set to 0 to disable history cache
htmx.config.inlineScriptNonce = '';      // Nonce for inline scripts
htmx.config.inlineStyleNonce = '';       // Nonce for inline styles
```

Recommended hardened configuration:
```html
<script>
    // After htmx loads
    htmx.config.selfRequestsOnly = true;
    htmx.config.allowScriptTags = false;   // Disable unless needed
    htmx.config.allowEval = false;          // Disable if CSP requires it
    htmx.config.historyCacheSize = 0;       // Disable if pages have sensitive data
</script>
```

### htmx:validateUrl Event
Intercept and block requests to specific URLs:
```javascript
document.body.addEventListener('htmx:validateUrl', function(evt) {
    if (!evt.detail.sameHost) {
        evt.preventDefault();  // Block cross-origin request
    }
});
```

---

## Input Validation

### Server-Side Validation (Mandatory)
All input validation must happen on the server. HTMX sends form data the same
way regular HTML forms do — never trust it.

### Client-Side Validation (UX Enhancement)
Use `hx-validate` to enforce HTML5 validation before the request:
```html
<form hx-post="/submit" hx-validate="true">
    <input name="email" type="email" required>
    <input name="age" type="number" min="18" max="120">
    <button type="submit">Submit</button>
</form>
```

### Inline Validation Pattern
Validate individual fields as the user fills them:
```html
<input name="username"
       hx-post="/validate/username"
       hx-trigger="change"
       hx-target="next .error"
       hx-swap="innerHTML">
<span class="error"></span>
```

---

## Authentication

### Cookie-Based (Recommended for HTMX)
Cookies with `HttpOnly` and `SameSite` are the simplest and most secure approach.
HTMX sends cookies automatically — no extra configuration needed.

### Token-Based (JWT)
If you must use tokens:
```javascript
document.body.addEventListener('htmx:configRequest', function(evt) {
    let token = localStorage.getItem('access_token');
    if (token) {
        evt.detail.headers['Authorization'] = 'Bearer ' + token;
    }
});
```
**Warning**: Tokens in `localStorage` are accessible to any JavaScript on the page.
If an XSS vulnerability exists, tokens are compromised. Prefer `HttpOnly` cookies.

### Handling 401/403
```javascript
document.body.addEventListener('htmx:responseError', function(evt) {
    if (evt.detail.xhr.status === 401) {
        window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
    }
});
```

---

## Defense in Depth Checklist

- [ ] Template engine auto-escaping is enabled (never disabled globally)
- [ ] `selfRequestsOnly` is `true` (default in 2.x)
- [ ] Session cookies have `HttpOnly`, `Secure`, `SameSite=Lax`
- [ ] User-generated HTML is sanitized server-side (hx-* attributes stripped)
- [ ] User-generated content is wrapped in `hx-disable`
- [ ] CSRF tokens are used for state-changing requests (or SameSite cookies are set)
- [ ] CSP headers are configured
- [ ] `allowScriptTags` is `false` unless explicitly needed
- [ ] All input is validated server-side
- [ ] Sensitive pages use `hx-history="false"` to avoid localStorage caching
- [ ] Rate limiting is applied on server endpoints
- [ ] Error responses don't leak stack traces or internal details
