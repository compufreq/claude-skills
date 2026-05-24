# Testing & Debugging HTMX Applications

## Table of Contents
1. [Debugging Techniques](#debugging)
2. [Common Pitfalls](#common-pitfalls)
3. [Server-Side Testing](#server-testing)
4. [Browser-Based Testing](#browser-testing)
5. [End-to-End Testing](#e2e-testing)

---

## Debugging Techniques

### 1. htmx.logAll()
The fastest way to see what HTMX is doing — call in the browser console:
```javascript
htmx.logAll();
```
This logs every HTMX event (configRequest, beforeSwap, afterSwap, etc.) with full detail.

### 2. Debug Extension
Add to a specific element for targeted logging:
```html
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-debug/dist/debug.min.js"></script>
<div hx-ext="debug" hx-get="/data">This element logs everything</div>
```

### 3. Network Tab
The browser's Network tab is your best friend. Look for:
- **Request headers**: `HX-Request: true`, `HX-Target`, `HX-Trigger`
- **Response headers**: `HX-Trigger`, `HX-Push-Url`, `HX-Retarget`
- **Response body**: Should be HTML fragments, not JSON (unless using client-side-templates)
- **Status codes**: 200 for success, 422 for validation, 286 to stop polling

### 4. Event Listeners
Listen for specific HTMX events to debug issues:
```javascript
document.body.addEventListener('htmx:beforeRequest', e => console.log('Request:', e.detail));
document.body.addEventListener('htmx:afterSwap', e => console.log('Swapped:', e.detail));
document.body.addEventListener('htmx:responseError', e => console.log('Error:', e.detail));
document.body.addEventListener('htmx:swapError', e => console.log('Swap failed:', e.detail));
```

### 5. HTMX Config Inspection
```javascript
console.log(htmx.config);  // See all current settings
```

---

## Common Pitfalls

### Pitfall 1: Target Not Found
**Symptom**: Content doesn't appear after request.
**Cause**: `hx-target` CSS selector doesn't match any element.
**Fix**: Verify the target exists in the DOM at request time:
```javascript
document.body.addEventListener('htmx:targetError', e => {
    console.error('Target not found:', e.detail);
});
```

### Pitfall 2: Response Replaces the Wrong Thing
**Symptom**: Unexpected content appears or content disappears.
**Cause**: Default swap is `innerHTML` — if your response IS the element, use `outerHTML`.
**Fix**: Match your swap strategy to your response:
```html
<!-- Response IS a new <tr> → use outerHTML on the existing <tr> -->
<tr hx-get="/row" hx-swap="outerHTML">

<!-- Response is CONTENT for a <div> → use innerHTML (default) -->
<div hx-get="/content" hx-swap="innerHTML">
```

### Pitfall 3: Form Submits Twice
**Symptom**: Two requests fire on form submit.
**Cause**: Both the form's native submit AND an htmx attribute are triggering.
**Fix**: HTMX automatically prevents the default form submit when it handles the request.
If using `hx-trigger="submit"` on a form that already has `hx-post`, you're double-triggering.
Remove the explicit trigger — forms trigger on submit by default.

### Pitfall 4: Events Not Firing After Swap
**Symptom**: Event listeners stop working after content is swapped.
**Cause**: New elements don't have the old event listeners.
**Fix**: Use event delegation or `htmx:load` event:
```javascript
// Event delegation (preferred)
document.body.addEventListener('click', function(e) {
    if (e.target.matches('.my-button')) { /* handle */ }
});

// Or re-init after swap
document.body.addEventListener('htmx:load', function(e) {
    // e.detail.elt is the new content — re-initialize plugins here
    initTooltips(e.detail.elt);
});
```

### Pitfall 5: 422 Response Not Showing Errors
**Symptom**: Validation errors return 422 but nothing appears.
**Cause**: By default, HTMX only swaps 2xx responses.
**Fix**: Use the `response-targets` extension, or configure `htmx:beforeSwap`:
```javascript
document.body.addEventListener('htmx:beforeSwap', function(evt) {
    if (evt.detail.xhr.status === 422) {
        evt.detail.shouldSwap = true;
        evt.detail.isError = false;
    }
});
```

### Pitfall 6: SSE/WebSocket Connection Drops
**Symptom**: Real-time updates stop after a while.
**Cause**: Server timeout, proxy timeout, or network interruption.
**Fix**: The SSE extension auto-reconnects. For WebSockets, implement heartbeats:
```javascript
// Server-side: send a ping every 30 seconds
// Client-side: the ws extension handles reconnection automatically
```

### Pitfall 7: History Cache Showing Stale Content
**Symptom**: Back button shows outdated data.
**Cause**: HTMX caches full page snapshots in localStorage.
**Fix**: Disable for dynamic pages, or set a lower cache size:
```html
<body hx-history="false">  <!-- disable for this page -->
```
```javascript
htmx.config.historyCacheSize = 0;  // disable globally
```

### Pitfall 8: Boosted Links Not Working in Swapped Content
**Symptom**: New links loaded via HTMX don't use boost.
**Cause**: `hx-boost` is processed when HTMX initializes. New content IS processed automatically.
**Real cause**: Usually a typo or the `hx-boost` is on a parent that's outside the swap target.
**Fix**: Ensure `hx-boost="true"` is on the `<body>` or a parent that persists across swaps.

### Pitfall 9: Extension Not Loading
**Symptom**: Extension attributes are ignored.
**Cause**: Extension script loaded after HTMX, or `hx-ext` not set.
**Fix**: Extensions must be loaded AFTER htmx.js, and `hx-ext` must be on the element or a parent:
```html
<script src="htmx.min.js"></script>
<script src="extension.js"></script>  <!-- AFTER htmx -->
<body hx-ext="extension-name">       <!-- ACTIVATE -->
```

### Pitfall 10: CORS Issues
**Symptom**: Requests fail to external APIs.
**Cause**: `selfRequestsOnly` is `true` by default in 2.x.
**Fix**: If you genuinely need cross-origin requests:
```javascript
htmx.config.selfRequestsOnly = false;
```
And configure CORS headers on the server.

---

## Server-Side Testing

Test your endpoints independently — they're just HTTP endpoints returning HTML.

### Python (pytest + Flask)
```python
def test_search_returns_fragment(client):
    response = client.get('/search?q=test', headers={'HX-Request': 'true'})
    assert response.status_code == 200
    assert '<div class="result">' in response.data.decode()
    assert '<!DOCTYPE html>' not in response.data.decode()  # Fragment, not full page

def test_search_returns_full_page_without_htmx(client):
    response = client.get('/search?q=test')
    assert response.status_code == 200
    assert '<!DOCTYPE html>' in response.data.decode()  # Full page

def test_create_returns_trigger_header(client):
    response = client.post('/items', data={'name': 'Test'}, headers={'HX-Request': 'true'})
    assert response.status_code == 200
    assert 'HX-Trigger' in response.headers

def test_validation_returns_422(client):
    response = client.post('/items', data={'name': ''}, headers={'HX-Request': 'true'})
    assert response.status_code == 422
    assert 'error' in response.data.decode().lower()
```

### Go (httptest)
```go
func TestSearchHTMXRequest(t *testing.T) {
    req := httptest.NewRequest("GET", "/search?q=test", nil)
    req.Header.Set("HX-Request", "true")
    w := httptest.NewRecorder()
    handler.ServeHTTP(w, req)
    
    if w.Code != 200 { t.Fatalf("got %d", w.Code) }
    if strings.Contains(w.Body.String(), "<!DOCTYPE html>") {
        t.Fatal("HTMX request should return fragment, not full page")
    }
}
```

---

## Browser-Based Testing

### Playwright (Recommended for HTMX)
Playwright works well because it handles real browser behavior including HTMX swaps:
```javascript
const { test, expect } = require('@playwright/test');

test('search filters results', async ({ page }) => {
    await page.goto('/');
    await page.fill('input[name="q"]', 'htmx');
    // Wait for HTMX to swap in results (debounce + request)
    await page.waitForSelector('#results .result-item');
    const count = await page.locator('#results .result-item').count();
    expect(count).toBeGreaterThan(0);
});

test('delete removes row with animation', async ({ page }) => {
    await page.goto('/');
    const row = page.locator('#item-1');
    await expect(row).toBeVisible();
    
    // Accept the confirm dialog
    page.on('dialog', dialog => dialog.accept());
    await page.click('#item-1 .delete-btn');
    
    // Row should fade out and be removed
    await expect(row).not.toBeVisible({ timeout: 2000 });
});
```

### Cypress
```javascript
describe('HTMX Todo App', () => {
    it('adds a todo', () => {
        cy.visit('/');
        cy.get('input[name="text"]').type('New todo');
        cy.get('form').submit();
        cy.get('#todo-list').should('contain', 'New todo');
    });
    
    it('toggles completion', () => {
        cy.get('.todo-item input[type="checkbox"]').first().click();
        cy.get('.todo-item').first().should('have.class', 'done');
    });
});
```

---

## End-to-End Testing

### Testing SSE
```python
import sseclient
import requests

def test_sse_stream():
    response = requests.get('http://localhost:8000/events', stream=True)
    client = sseclient.SSEClient(response)
    
    for event in client.events():
        assert event.event == 'notification'
        assert '<div' in event.data  # HTML fragment
        break  # Just test first event
```

### Testing WebSocket
```python
import websockets
import asyncio

async def test_ws_chat():
    async with websockets.connect('ws://localhost:8080/ws') as ws:
        await ws.send('message=Hello')
        response = await ws.recv()
        assert 'Hello' in response
        assert 'hx-swap-oob' in response  # OOB swap included
```
