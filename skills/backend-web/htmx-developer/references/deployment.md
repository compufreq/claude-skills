# Deployment & Production for HTMX Applications

## Table of Contents
1. [Self-Hosting HTMX](#self-hosting)
2. [Bundling](#bundling)
3. [Performance Optimization](#performance)
4. [Caching Strategies](#caching)
5. [CDN Configuration](#cdn)
6. [Monitoring & Observability](#monitoring)

---

## Self-Hosting HTMX

For production, self-host htmx rather than relying on a CDN:

### Download and Serve Statically
```bash
# Download the latest version
curl -o static/js/htmx.min.js https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js
```
```html
<script src="/static/js/htmx.min.js"></script>
```

### npm Install
```bash
npm install htmx.org@2.0.8
# File at node_modules/htmx.org/dist/htmx.min.js
```

### Why Self-Host
- No dependency on third-party CDN uptime
- Faster first load if your server is geographically close to users
- No privacy concerns from CDN tracking
- Guaranteed version pinning
- Works on air-gapped / intranet deployments
- Subresource Integrity (SRI) is optional when self-hosting

---

## Bundling

HTMX is dependency-free and works without a build step. But if you're already bundling:

### Webpack
```javascript
// index.js
import 'htmx.org';
window.htmx = require('htmx.org');
```

### Vite / ESBuild
```javascript
import htmx from 'htmx.org';
window.htmx = htmx;
```

### Bundling Extensions
```javascript
import 'htmx.org';
import 'htmx-ext-sse';
import 'htmx-ext-response-targets';
```

### No-Bundle Approach (Recommended)
HTMX is designed to work without bundling. A single `<script>` tag is sufficient:
```html
<script src="/static/js/htmx.min.js" defer></script>
```
At ~14KB gzipped, there's minimal benefit to bundling htmx with other code.

---

## Performance Optimization

### Response Size
HTMX's biggest performance advantage is returning small HTML fragments instead of
full JSON payloads + client-side rendering. Keep fragments lean:

- Return only the changed content, not the entire page
- Use `hx-select` to pick specific content from larger responses
- Use OOB swaps to batch multiple small updates in one response
- Avoid including `<script>` tags in every response — load JS once

### Preloading
The `preload` extension fetches pages before the user clicks:
```html
<body hx-ext="preload">
    <a href="/page" preload>Link</a>                    <!-- preload on mousedown (default) -->
    <a href="/page" preload="mouseover">Link</a>        <!-- preload on hover -->
    <a href="/page" preload="mouseover" preload-images>  <!-- also preload images -->
</body>
```

### Lazy Loading
Defer loading of below-the-fold content:
```html
<div hx-get="/heavy-chart"
     hx-trigger="revealed"
     hx-swap="outerHTML">
    <div class="skeleton">Loading chart...</div>
</div>
```
`revealed` triggers when the element enters the viewport.

### Debouncing & Throttling
Prevent excessive requests from fast-firing events:
```html
<!-- Debounce: wait 300ms after last keystroke -->
<input hx-get="/search" hx-trigger="input changed delay:300ms">

<!-- Throttle: max once per second -->
<div hx-get="/updates" hx-trigger="scroll throttle:1s">
```

### Request Batching with hx-sync
Prevent redundant concurrent requests:
```html
<form hx-post="/save">
    <input hx-post="/validate" hx-trigger="change" hx-sync="closest form:abort">
</form>
```
If the form submits while validation is in-flight, validation is aborted.

### Server-Side Performance
- **Template caching**: Pre-compile templates at startup
- **Fragment caching**: Cache rendered HTML fragments (Redis, memcached)
- **Conditional rendering**: Only re-render what changed
- **HTTP caching headers**: Use `Cache-Control`, `ETag`, `Last-Modified` for GET requests

---

## Caching Strategies

### HTTP Cache Headers for HTMX
HTMX respects standard HTTP caching. Use it for relatively static fragments:
```python
@app.route("/sidebar")
def sidebar():
    resp = make_response(render_template("partials/sidebar.html"))
    resp.headers["Cache-Control"] = "public, max-age=300"  # 5 min cache
    resp.headers["Vary"] = "HX-Request"  # Different cache for HTMX vs normal
    return resp
```

### Vary Header
Always include `Vary: HX-Request` if the same URL returns different content for
HTMX vs. non-HTMX requests:
```python
response.headers["Vary"] = "HX-Request"
```

### ETag for Conditional Requests
```python
import hashlib

@app.route("/data")
def data():
    content = render_template("partials/data.html", items=get_items())
    etag = hashlib.md5(content.encode()).hexdigest()

    if request.headers.get("If-None-Match") == etag:
        return "", 304  # Not modified

    resp = make_response(content)
    resp.headers["ETag"] = etag
    return resp
```

### History Cache
HTMX stores page snapshots in `localStorage` for back-button support.
Control this with:
```javascript
htmx.config.historyCacheSize = 10;     // Pages to cache (default: 10)
```
```html
<body hx-history="false">             <!-- Exclude page from cache -->
```

---

## CDN Configuration

If using a CDN (Cloudflare, Fastly, etc.) in front of your server:

### Cache Key Configuration
Include `HX-Request` in the cache key so HTMX fragment responses
and full page responses are cached separately:
```
# Cloudflare Page Rules / Cache Rules
Vary: HX-Request
```

### Edge-Side Includes (ESI)
Some CDNs support ESI for assembling pages from cached fragments:
```html
<div id="user-nav">
    <esi:include src="/fragments/user-nav"/>
</div>
<div id="content">
    <esi:include src="/fragments/dashboard"/>
</div>
```

---

## Monitoring & Observability

### Client-Side Error Tracking
```javascript
document.body.addEventListener('htmx:responseError', function(evt) {
    // Send to your error tracking service
    reportError({
        url: evt.detail.xhr.responseURL,
        status: evt.detail.xhr.status,
        target: evt.detail.target?.id,
    });
});

document.body.addEventListener('htmx:sendError', function(evt) {
    reportError({ type: 'network_error', url: evt.detail.requestConfig?.path });
});

document.body.addEventListener('htmx:timeout', function(evt) {
    reportError({ type: 'timeout', url: evt.detail.requestConfig?.path });
});
```

### Server-Side Metrics
Track HTMX-specific metrics:
```python
from functools import wraps
import time

def track_htmx(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        start = time.time()
        response = f(*args, **kwargs)
        duration = time.time() - start

        is_htmx = request.headers.get("HX-Request") == "true"
        metrics.histogram('response_time',
            value=duration,
            tags={'htmx': str(is_htmx), 'endpoint': request.endpoint})
        return response
    return decorated
```

### Request Timeout Configuration
```javascript
htmx.config.timeout = 10000;  // 10 second timeout (default: 0 = no timeout)
```

### Compressed Responses
HTMX fragment responses are already small, but enable gzip/brotli compression:
```python
# Flask
from flask_compress import Compress
Compress(app)

# Go
import "github.com/NYTimes/gziphandler"
handler = gziphandler.GzipHandler(mux)
```
