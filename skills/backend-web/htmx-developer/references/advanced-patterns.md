# Advanced HTMX Patterns

## Table of Contents
1. [SPA-Like Navigation](#spa-like-navigation)
2. [Multi-Step Wizards](#multi-step-wizards)
3. [Optimistic UI](#optimistic-ui)
4. [Dependent / Cascading Selects](#dependent-selects)
5. [Keyboard Shortcuts](#keyboard-shortcuts)
6. [Drag and Drop with Sortable](#drag-and-drop)
7. [Updating Disjoint Page Areas](#disjoint-updates)
8. [Async Authentication Tokens](#async-auth)
9. [Transitional Applications](#transitional-apps)

---

## SPA-Like Navigation

HTMX can replicate the smooth, no-reload feel of SPAs while keeping the server-rendered architecture.

### Full Page Navigation via hx-boost
The simplest approach — convert all links and forms to AJAX-driven navigation:
```html
<body hx-boost="true">
    <nav>
        <a href="/dashboard">Dashboard</a>   <!-- AJAX-loaded -->
        <a href="/settings">Settings</a>      <!-- AJAX-loaded -->
    </nav>
    <main id="content">
        <!-- Page content swapped here -->
    </main>
</body>
```
With `hx-boost`, every `<a>` and `<form>` within the boosted element will:
- Issue an AJAX request instead of a full page load
- Swap the response into the page (the `<body>` by default)
- Push the URL to browser history
- Merge `<head>` tags (styles, title) automatically in 2.x

### Partial Page Swaps (SPA Shell Pattern)
For a persistent layout (sidebar, header) with only the content area changing:
```html
<body>
    <nav id="sidebar"><!-- persists across navigations --></nav>
    <main id="page-content"
          hx-get="/initial-page"
          hx-trigger="load"
          hx-swap="innerHTML"
          hx-push-url="true">
    </main>
</body>
```
Navigation links target just the content area:
```html
<a hx-get="/dashboard"
   hx-target="#page-content"
   hx-swap="innerHTML transition:true"
   hx-push-url="true">Dashboard</a>
```

### Back/Forward Button Support
HTMX automatically handles the browser's back and forward buttons when using
`hx-push-url` or `hx-boost`. It snapshots the current DOM into `localStorage`
before each navigation and restores it on popstate. Configure via:
- `htmx.config.historyCacheSize` — number of pages to cache (default: 10, set to 0 to disable)
- `hx-history="false"` — exclude a page from the history cache (e.g., pages with sensitive data)
- `HX-Push-Url` response header — server-side URL control
- `HX-Replace-Url` response header — replace instead of push

### History Restore Fallback
If a cached page is missing, HTMX makes a fresh request with `HX-History-Restore-Request: true`.
Your server should return the full page HTML (not a fragment) when it sees this header:
```python
# Flask example
@app.route("/dashboard")
def dashboard():
    data = get_dashboard_data()
    if request.headers.get("HX-History-Restore-Request"):
        return render_template("dashboard.html", data=data)  # full page
    if is_htmx():
        return render_template("partials/dashboard_content.html", data=data)
    return render_template("dashboard.html", data=data)
```

---

## Multi-Step Wizards

### Server-Driven Wizard
Each step is a server endpoint that returns the next step's form:
```html
<!-- Step 1 -->
<div id="wizard">
    <form hx-post="/wizard/step-1"
          hx-target="#wizard"
          hx-swap="outerHTML">
        <h2>Step 1: Personal Info</h2>
        <input name="name" required>
        <input name="email" type="email" required>
        <button type="submit">Next →</button>
    </form>
</div>
```
Server response for step 1 replaces the wizard div with step 2:
```html
<!-- Server returns this on POST /wizard/step-1 -->
<div id="wizard">
    <form hx-post="/wizard/step-2"
          hx-target="#wizard"
          hx-swap="outerHTML">
        <h2>Step 2: Address</h2>
        <!-- Hidden fields preserve previous steps' data -->
        <input type="hidden" name="name" value="Jane Doe">
        <input type="hidden" name="email" value="jane@example.com">
        <input name="address" required>
        <input name="city" required>
        <button hx-get="/wizard/step-1?name=Jane+Doe&email=jane@example.com"
                hx-target="#wizard" hx-swap="outerHTML"
                type="button">← Back</button>
        <button type="submit">Next →</button>
    </form>
</div>
```

### Progress Indicator with OOB
Update a progress bar alongside the wizard:
```html
<div class="wizard-progress">
    <div id="progress-bar" style="width: 33%">Step 1 of 3</div>
</div>
<div id="wizard"><!-- form --></div>
```
Server response includes OOB progress update:
```html
<div id="wizard"><!-- step 2 form --></div>
<div id="progress-bar" hx-swap-oob="true" style="width: 66%">Step 2 of 3</div>
```

### Validation Between Steps
Return the current step with errors on validation failure (422):
```python
@app.route("/wizard/step-1", methods=["POST"])
def wizard_step_1():
    errors = validate_step_1(request.form)
    if errors:
        return render_template("wizard/step1.html", errors=errors, data=request.form), 422
    return render_template("wizard/step2.html", data=request.form)
```

---

## Optimistic UI

Show the expected result immediately, then reconcile with the server response.

### Like Button Pattern
```html
<button id="like-42"
        hx-post="/posts/42/like"
        hx-target="this"
        hx-swap="outerHTML"
        hx-on:click="
            this.textContent = '❤️ Liked (' + (parseInt(this.dataset.count) + 1) + ')';
            this.disabled = true;
        "
        data-count="7">
    🤍 Like (7)
</button>
```
The `hx-on:click` immediately updates the UI. When the server responds, it replaces
the button with the authoritative state. If the request fails, `htmx:responseError`
can revert the change.

### Optimistic Delete with Rollback
```html
<tr id="item-42"
    hx-on:htmx:beforeRequest="this.style.opacity = '0.3'"
    hx-on:htmx:responseError="this.style.opacity = '1'">
    <td>Item Name</td>
    <td>
        <button hx-delete="/items/42"
                hx-target="#item-42"
                hx-swap="outerHTML swap:300ms">Delete</button>
    </td>
</tr>
```
The row fades immediately on click. If the server returns an error, opacity is restored.

---

## Dependent Selects

Chain select dropdowns where the second depends on the first:
```html
<label>Country</label>
<select name="country"
        hx-get="/api/states"
        hx-target="#state-select"
        hx-swap="innerHTML"
        hx-trigger="change"
        hx-indicator="#states-loading">
    <option value="">Select country...</option>
    <option value="us">United States</option>
    <option value="ca">Canada</option>
</select>
<span id="states-loading" class="htmx-indicator">Loading...</span>

<label>State/Province</label>
<select name="state" id="state-select">
    <option value="">Select country first...</option>
</select>
```
Server returns `<option>` elements for the selected country.

---

## Keyboard Shortcuts

Use trigger filters and the `from:body` modifier for global shortcuts:
```html
<!-- Ctrl+K opens search -->
<div hx-get="/search-modal"
     hx-trigger="keydown[ctrlKey&&key=='k'] from:body"
     hx-target="#modal-container"
     hx-swap="innerHTML">
</div>

<!-- Escape closes modal -->
<div id="modal-container"
     hx-on:keydown="if(event.key === 'Escape') this.innerHTML = ''">
</div>
```

---

## Drag and Drop

Using Sortable.js with HTMX:
```html
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>

<form id="task-list" hx-post="/tasks/reorder" hx-trigger="end" hx-swap="none">
    <div class="sortable-item" data-id="1"><input type="hidden" name="order[]" value="1">Task 1</div>
    <div class="sortable-item" data-id="2"><input type="hidden" name="order[]" value="2">Task 2</div>
    <div class="sortable-item" data-id="3"><input type="hidden" name="order[]" value="3">Task 3</div>
</form>

<script>
    new Sortable(document.getElementById('task-list'), {
        animation: 150,
        ghostClass: 'sortable-ghost',
        onEnd: function(evt) {
            // Update hidden input values to reflect new order
            this.el.querySelectorAll('.sortable-item').forEach((item, i) => {
                item.querySelector('input').value = i + 1;
            });
            // Trigger HTMX to save the new order
            htmx.trigger(this.el, 'end');
        }
    });
</script>
```

---

## Disjoint Updates

When one action needs to update multiple unrelated areas of the page:

### Approach 1: Out-of-Band Swaps (recommended)
Include OOB elements in the response (see main SKILL.md).

### Approach 2: HX-Trigger Events
Server sends event, multiple elements listen:
```python
response.headers["HX-Trigger"] = json.dumps({"cartUpdated": {"count": 5}})
```
```html
<!-- Badge listens for the event -->
<span id="cart-badge"
      hx-get="/cart/count"
      hx-trigger="cartUpdated from:body"
      hx-swap="innerHTML">0</span>

<!-- Mini-cart also listens -->
<div id="mini-cart"
     hx-get="/cart/preview"
     hx-trigger="cartUpdated from:body"
     hx-swap="innerHTML">Empty</div>
```

### Approach 3: path-deps Extension
Declare URL-based dependencies between elements:
```html
<body hx-ext="path-deps">
    <form hx-post="/contacts" hx-target="#form-area">...</form>
    <table hx-get="/contacts" hx-trigger="path-deps" path-deps="/contacts">
        <!-- Auto-refreshes when any POST/PUT/DELETE hits /contacts -->
    </table>
</body>
```

---

## Async Auth

When using token-based authentication (JWT, OAuth) where tokens expire:
```html
<body hx-on:htmx:configRequest="
    let token = localStorage.getItem('auth_token');
    if (token) {
        evt.detail.headers['Authorization'] = 'Bearer ' + token;
    }
">
```

For token refresh on 401:
```javascript
document.body.addEventListener('htmx:responseError', function(evt) {
    if (evt.detail.xhr.status === 401) {
        // Refresh token, then retry
        refreshToken().then(newToken => {
            localStorage.setItem('auth_token', newToken);
            htmx.ajax('GET', evt.detail.requestConfig.path,
                       {target: evt.detail.target, swap: evt.detail.requestConfig.swap});
        });
    }
});
```

---

## Transitional Applications

The HTMX team advocates for "Transitional" apps — mixing hypermedia with JavaScript
components where appropriate. The rule of thumb:

**Use HTMX when**: the interaction is coarse-grained (adding/removing/editing items,
navigation, search, CRUD, forms, notifications). Most web apps are 80%+ this.

**Use a JS component when**: the interaction is fine-grained and requires rich
client-side state (spreadsheet cells, drawing canvas, map interactions, real-time
collaborative editing). Embed these as islands within the HTMX app.

Islands can communicate with the HTMX app via custom events:
```javascript
// React island dispatches event
document.dispatchEvent(new CustomEvent('mapLocationSelected',
    { detail: { lat: 40.7, lng: -74.0 } }));
```
```html
<!-- HTMX element listens -->
<div hx-get="/location-details"
     hx-trigger="mapLocationSelected from:document"
     hx-vals="js:{lat: event.detail.lat, lng: event.detail.lng}"
     hx-target="#location-info">
</div>
```
