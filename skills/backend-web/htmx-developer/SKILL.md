---
name: htmx-developer
description: >
  Expert HTMX frontend developer skill for building hypermedia-driven web interfaces using HTMX 2.x.
  Use this skill whenever the user mentions HTMX, htmx, hx- attributes, hypermedia-driven UIs,
  server-rendered HTML with AJAX, or wants to build interactive web pages without heavy JavaScript
  frameworks. Also trigger when the user asks about replacing React/Vue/Angular with a simpler
  approach, building forms with inline validation, infinite scroll, active search, lazy loading,
  server-sent events, WebSocket-driven UIs, View Transitions, SPA-like routing without JS frameworks,
  optimistic UI, HTMX security/CSP, HTMX with Alpine.js/Hyperscript/Tailwind, or SEO for
  server-rendered dynamic apps. Trigger even if the user doesn't say "HTMX" explicitly but describes
  a pattern HTMX solves (e.g., "update part of page without a reload"). Covers core HTMX, all
  extensions, Python (Flask/Django/FastAPI) and Go backends, advanced patterns, CSS animations,
  security, testing, deployment, library integrations, and SEO/accessibility.
---

# HTMX Frontend Developer Skill

You are an expert HTMX frontend developer. Your job is to help users build modern, interactive web
interfaces using HTMX's hypermedia-driven approach — returning HTML from the server and swapping it
into the DOM declaratively, with minimal or zero custom JavaScript.

## Core Philosophy

HTMX extends HTML as a hypertext by generalizing four things:
1. **Any element** can issue HTTP requests (not just anchors and forms)
2. **Any event** can trigger requests (not just clicks and submits)
3. **Any HTTP verb** can be used (not just GET and POST)
4. **Any element** can be the swap target (not just the whole window)

The server returns **HTML fragments**, not JSON. This is the HATEOAS (Hypermedia As The Engine Of
Application State) architecture. When writing HTMX code, always think in terms of HTML responses
and DOM swaps, not client-side state management.

## Current Version

HTMX **2.0.x** is the current major version. Always use 2.x patterns and CDN URLs:

```html
<!-- Recommended CDN include -->
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js"
        integrity="sha384-/TgkGk7p307TH7EXJDuUlgG3Ce1UVolAOFopFekQkkXihi5u/6OCvVKyz1W+idaz"
        crossorigin="anonymous"></script>
```

Key 2.x changes from 1.x to be aware of:
- `hx-sse` and `hx-ws` attributes are removed; use the SSE and WebSocket extensions instead
- Extensions live at https://extensions.htmx.org and are versioned independently
- `DELETE` requests use query parameters, not form-encoded bodies
- Head tag processing from `head-support` extension is integrated into core for boosted links
- `htmx.config.selfRequestsOnly` defaults to `true` (only same-origin requests by default)
- `hx-on` attribute uses the `hx-on:` prefix (e.g., `hx-on:click` not `hx-on="click: ..."`)

## Core Attributes Quick Reference

### Request Attributes
| Attribute | Purpose |
|-----------|---------|
| `hx-get` | Issue GET to URL |
| `hx-post` | Issue POST to URL |
| `hx-put` | Issue PUT to URL |
| `hx-patch` | Issue PATCH to URL |
| `hx-delete` | Issue DELETE to URL |

### Behavior Attributes
| Attribute | Purpose |
|-----------|---------|
| `hx-trigger` | Event that triggers the request (default: natural event of element) |
| `hx-target` | CSS selector for the element to swap content into |
| `hx-swap` | How to swap: `innerHTML` (default), `outerHTML`, `beforebegin`, `afterbegin`, `beforeend`, `afterend`, `delete`, `none` |
| `hx-select` | CSS selector to pick content from the response |
| `hx-select-oob` | Pick out-of-band content from response by ID |
| `hx-swap-oob` | Mark response elements for out-of-band swap |
| `hx-indicator` | Element to show as loading indicator |
| `hx-push-url` | Push URL to browser history |
| `hx-replace-url` | Replace current URL in browser history |
| `hx-include` | Include additional element values in request |
| `hx-params` | Filter parameters sent with request |
| `hx-vals` | Add JSON-formatted values to request |
| `hx-headers` | Add custom headers to request |
| `hx-confirm` | Show confirm dialog before request |
| `hx-prompt` | Show prompt dialog, value sent as `HX-Prompt` header |
| `hx-boost` | Progressive enhancement for links and forms |
| `hx-sync` | Synchronize requests between elements |
| `hx-validate` | Force validation before request |
| `hx-encoding` | Set request encoding (e.g., `multipart/form-data` for file uploads) |
| `hx-ext` | Enable extensions |
| `hx-disable` | Disable htmx processing |
| `hx-disabled-elt` | Disable elements during request |
| `hx-disinherit` | Prevent attribute inheritance |
| `hx-preserve` | Preserve element across swaps |
| `hx-history` | Control history cache behavior |
| `hx-on:*` | Inline event handlers (e.g., `hx-on:htmx:beforeRequest`) |

### Trigger Modifiers
Triggers support modifiers separated by spaces after the event name:
- `once` — fire only once
- `changed` — only if value changed
- `delay:<time>` — debounce (e.g., `delay:500ms`)
- `throttle:<time>` — throttle (e.g., `throttle:1s`)
- `from:<selector>` — listen on a different element
- `target:<selector>` — filter by event target
- `consume` — consume the event (preventDefault)
- `queue:<strategy>` — `first`, `last`, `all`, `none`
- Trigger filters via `[expression]` (e.g., `click[ctrlKey]`)
- Special events: `load`, `revealed`, `intersect`
- Polling: `every <interval>` (e.g., `every 2s`)

### Swap Modifiers
The `hx-swap` attribute supports additional modifiers:
- `transition:true` — use View Transitions API
- `swap:<time>` — delay between clearing old and inserting new content
- `settle:<time>` — delay between insert and settle
- `ignoreTitle:true` — don't update document title
- `scroll:top|bottom` — scroll target element
- `show:top|bottom` — scroll target into view
- `focus-scroll:true|false` — control focus scrolling behavior

### Response Headers (Server → Client)
| Header | Purpose |
|--------|---------|
| `HX-Location` | Client-side redirect without full reload |
| `HX-Push-Url` | Push URL to history |
| `HX-Redirect` | Full client-side redirect |
| `HX-Refresh` | Full page refresh if `"true"` |
| `HX-Replace-Url` | Replace URL in history |
| `HX-Reswap` | Override the swap method |
| `HX-Retarget` | Override the target element (CSS selector) |
| `HX-Reselect` | Override `hx-select` |
| `HX-Trigger` | Trigger client-side events (JSON for multiple) |
| `HX-Trigger-After-Settle` | Trigger events after settle step |
| `HX-Trigger-After-Swap` | Trigger events after swap step |

### Request Headers (Client → Server)
| Header | Purpose |
|--------|---------|
| `HX-Boosted` | Request is from a boosted element |
| `HX-Current-URL` | Current browser URL |
| `HX-History-Restore-Request` | History restoration request |
| `HX-Prompt` | User's response to `hx-prompt` |
| `HX-Request` | Always `"true"` for HTMX requests |
| `HX-Target` | ID of the target element |
| `HX-Trigger-Name` | Name of the triggered element |
| `HX-Trigger` | ID of the triggered element |

### CSS Classes
| Class | When Applied |
|-------|-------------|
| `htmx-indicator` | Elements hidden by default (opacity: 0), shown during requests |
| `htmx-request` | Applied to element (or indicator target) during request |
| `htmx-added` | Applied to new content before swap, removed after settle |
| `htmx-settling` | Applied to target after swap, removed after settle |
| `htmx-swapping` | Applied to target before swap, removed after swap |

## Extensions

Extensions are loaded separately from HTMX core. Always include the extension script after the
main htmx script, and activate with `hx-ext` on the relevant element or `<body>`.

### Core Extensions (maintained by htmx team)

**Idiomorph** — DOM morphing swap strategy. Preserves focus, form state, video playback.
```html
<script src="https://cdn.jsdelivr.net/npm/idiomorph@0.3.0/dist/idiomorph-ext.min.js"></script>
<body hx-ext="morph">
  <div hx-get="/content" hx-swap="morph:innerHTML">...</div>
</body>
```

**SSE (Server-Sent Events)** — Receive real-time updates from the server.
```html
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-sse@2.2.4"></script>
<div hx-ext="sse" sse-connect="/events" sse-swap="message">
  <!-- Content updates on each SSE message -->
</div>
```

**WebSockets** — Bidirectional real-time communication.
```html
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-ws@2.0.0/dist/ws.min.js"></script>
<div hx-ext="ws" ws-connect="/chat">
  <form ws-send>
    <input name="message">
    <button>Send</button>
  </form>
  <div id="messages"></div>
</div>
```

**Response Targets** — Different swap targets based on HTTP status codes.
```html
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-response-targets@2.0.0/dist/response-targets.min.js"></script>
<body hx-ext="response-targets">
  <form hx-post="/submit"
        hx-target="#result"
        hx-target-422="#errors"
        hx-target-5*="#server-error">
    ...
  </form>
</body>
```

**Preload** — Prefetch pages on hover/focus for near-instant navigation.
```html
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-preload@2.0.1/dist/preload.min.js"></script>
<body hx-ext="preload">
  <a href="/page" preload="mousedown">Fast Link</a>
</body>
```

**Head Support** — Merge `<head>` content (styles, scripts) from HTMX responses.
```html
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-head-support@2.0.1/dist/head-support.min.js"></script>
<body hx-ext="head-support">
  <!-- head tags in responses will be merged -->
</body>
```
Note: Head processing is built into core for boosted links in 2.x, but this extension provides
it for all HTMX requests.

### Community Extensions (frequently used)

- **json-enc** — Send request body as JSON instead of form-encoded
- **client-side-templates** — Transform JSON responses via Mustache/Handlebars/Nunjucks before swap
- **loading-states** — Manage loading UI states (disable elements, toggle classes)
- **class-tools** — Toggle CSS classes on timers (`classes="add foo:1s, remove foo:2s"`)
- **multi-swap** — Swap multiple elements from a single response
- **path-params** — Use request params to fill URL path variables
- **debug** — Log all HTMX events via `console.debug`
- **remove-me** — Auto-remove an element after a time interval

## Common Patterns

When generating HTMX code, use these proven patterns:

### Active Search
```html
<input type="search" name="q"
       hx-get="/search"
       hx-trigger="input changed delay:300ms"
       hx-target="#results"
       hx-indicator="#spinner"
       placeholder="Search...">
<span id="spinner" class="htmx-indicator">Searching...</span>
<div id="results"></div>
```

### Inline Editing (Click-to-Edit)
```html
<!-- Display mode -->
<div hx-get="/contact/1/edit" hx-trigger="click" hx-swap="outerHTML">
  <span>Click to edit: John Doe</span>
</div>

<!-- Edit mode (returned by server) -->
<form hx-put="/contact/1" hx-target="this" hx-swap="outerHTML">
  <input name="name" value="John Doe">
  <button type="submit">Save</button>
  <button hx-get="/contact/1" hx-swap="outerHTML">Cancel</button>
</form>
```

### Infinite Scroll
```html
<table>
  <tbody id="results">
    <tr>...</tr>
    <!-- Last row triggers load -->
    <tr hx-get="/items?page=2"
        hx-trigger="revealed"
        hx-swap="afterend"
        hx-select="tbody > tr">
      <td>Loading more...</td>
    </tr>
  </tbody>
</table>
```

### Delete with Confirmation + Fade Out
```html
<button hx-delete="/item/42"
        hx-confirm="Are you sure?"
        hx-target="closest tr"
        hx-swap="outerHTML swap:500ms">
  Delete
</button>
```
With CSS:
```css
tr.htmx-swapping { opacity: 0; transition: opacity 500ms ease-out; }
```

### Polling with Stop
```html
<div hx-get="/job/123/status"
     hx-trigger="every 2s"
     hx-target="this"
     hx-swap="innerHTML">
  Checking status...
</div>
<!-- Server returns 286 to stop polling -->
```

### Out-of-Band Updates (Updating Multiple Page Areas)
```html
<!-- Main request -->
<button hx-post="/cart/add/42" hx-target="#cart-items">Add to Cart</button>

<!-- Server response updates cart AND badge -->
<div id="cart-items">
  <!-- updated cart contents -->
</div>
<span id="cart-count" hx-swap-oob="true">3</span>
```

### Form Validation with Error Targeting
```html
<body hx-ext="response-targets">
  <form hx-post="/register"
        hx-target="#success"
        hx-target-422="#form-errors">
    <input name="email" type="email" required>
    <input name="password" type="password" required>
    <button type="submit">Register</button>
    <div id="form-errors"></div>
  </form>
  <div id="success"></div>
</body>
```

### Lazy Loading Content
```html
<div hx-get="/dashboard/chart"
     hx-trigger="load"
     hx-swap="outerHTML">
  <img class="htmx-indicator" src="/spinner.svg" alt="Loading chart...">
</div>
```

### Tabs
```html
<div class="tabs" hx-target="#tab-content" hx-swap="innerHTML">
  <button hx-get="/tabs/overview" class="active"
          hx-on:htmx:afterOnLoad="
            document.querySelectorAll('.tabs button').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
          ">Overview</button>
  <button hx-get="/tabs/details">Details</button>
  <button hx-get="/tabs/history">History</button>
</div>
<div id="tab-content">
  <!-- Tab content loaded here -->
</div>
```

### File Upload with Progress
```html
<form hx-post="/upload"
      hx-encoding="multipart/form-data"
      hx-target="#upload-result">
  <input type="file" name="document">
  <button type="submit">Upload</button>
  <progress id="progress" value="0" max="100" class="htmx-indicator"></progress>
</form>
<div id="upload-result"></div>

<script>
  htmx.on('#upload-form', 'htmx:xhr:progress', function(evt) {
    htmx.find('#progress').setAttribute('value', evt.detail.loaded / evt.detail.total * 100);
  });
</script>
```

## Backend Integration

HTMX is backend-agnostic — any server that returns HTML works. The key server-side patterns are:

1. **Detect HTMX requests** via the `HX-Request: true` header
2. **Return HTML fragments** (not full pages) for HTMX requests
3. **Use response headers** (`HX-Trigger`, `HX-Push-Url`, etc.) to control client behavior
4. **Return appropriate status codes** (e.g., 422 for validation errors with `response-targets`)

For backend-specific implementation patterns, read the appropriate reference file:
- **Python (Flask/Django/FastAPI)**: Read `references/python-backends.md`
- **Go**: Read `references/go-backend.md`

## Extended Reference Files

The following reference files provide deep coverage of specific topics.
Read them when the user's request involves these areas:

- **Advanced patterns** (SPA-like routing, multi-step wizards, optimistic UI,
  dependent selects, keyboard shortcuts, drag-and-drop, disjoint page updates,
  transitional app architecture): Read `references/advanced-patterns.md`
- **Security hardening** (XSS prevention, CSRF, Content Security Policy, hx-disable,
  secure cookies, authentication patterns, defense checklist):
  Read `references/security.md`
- **CSS animations & View Transitions** (swap/settle lifecycle, fade/slide/bounce recipes,
  View Transitions API, loading skeletons, progress indicators, page transitions):
  Read `references/css-animations.md`
- **Testing & debugging** (htmx.logAll, debug extension, common pitfalls like target-not-found
  and 422 handling, server-side testing, Playwright/Cypress, SSE/WS testing):
  Read `references/testing-debugging.md`
- **Deployment & production** (self-hosting, bundling, performance optimization, caching
  strategies, CDN configuration, monitoring):
  Read `references/deployment.md`
- **Library integrations** (Alpine.js, Hyperscript, Tailwind CSS, Web Components,
  Sortable.js, Chart.js, plugin re-initialization patterns):
  Read `references/integrations.md`
- **SEO, modern design & accessibility** (SEO advantages of HTMX, structured data/JSON-LD,
  Core Web Vitals, Open Graph, modern UI patterns, ARIA live regions, focus management,
  progressive enhancement, noscript fallbacks):
  Read `references/seo-design.md`

## Security Considerations

HTMX follows the browser's security model, but keep these points in mind:

- `htmx.config.selfRequestsOnly` defaults to `true` in 2.x — only same-origin requests are allowed
  unless explicitly configured otherwise
- Always sanitize and escape HTML on the server side — HTMX swaps raw HTML into the DOM
- Use `hx-disable` to prevent HTMX processing on user-generated content
- For CSP (Content Security Policy), HTMX itself doesn't use `eval()`, but `hx-on:*` attributes
  and trigger filters use `new Function()`, so you may need `unsafe-eval` or the `safe-nonce` extension
- CSRF protection: include CSRF tokens in forms or use `hx-headers` to add them to all requests
- Be cautious with `hx-vals` containing user input — always validate server-side

## Debugging

When users have issues, suggest these approaches:

1. **`htmx.logAll()`** — Call in browser console to log all HTMX events
2. **Debug extension** — Add `hx-ext="debug"` to an element for verbose logging
3. **Browser DevTools Network tab** — Inspect request/response pairs; look for HTML fragments
4. **`htmx:responseError` event** — Listen for non-2xx responses
5. **Check `HX-Request` header** — Verify server detects HTMX requests correctly

## Output Guidelines

Adapt your output format to what the user needs:

- **Quick question or code snippet**: Provide the HTML/attribute pattern inline with explanation
- **Component or pattern**: Provide complete HTML with necessary CSS and any minimal JS
- **Full page or feature**: Provide a complete HTML file with HTMX included via CDN, plus server-side endpoint examples
- **Project scaffold**: Provide a directory structure with HTML templates and server code for the chosen backend
- **Debugging help**: Walk through the issue, suggest diagnostic steps, and provide corrected code

Always include the HTMX script tag when providing full HTML files. Prefer CDN includes for simplicity
unless the user's context suggests npm/bundler usage.

When showing server-side code, check if the user has specified a backend. If not, show the HTML
pattern with comments describing what the server endpoint should return. If they've mentioned
Python or Go, read the appropriate reference file and use those patterns.
