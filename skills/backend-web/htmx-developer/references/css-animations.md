# CSS Animations & View Transitions for HTMX

## Table of Contents
1. [How HTMX CSS Transitions Work](#how-it-works)
2. [Swap & Settle Lifecycle](#lifecycle)
3. [Common Animation Recipes](#recipes)
4. [View Transitions API](#view-transitions)
5. [Loading Skeletons](#loading-skeletons)
6. [Loading Indicators](#loading-indicators)
7. [Page Transition Patterns](#page-transitions)

---

## How HTMX CSS Transitions Work

HTMX enables CSS transitions without JavaScript by exploiting CSS's transition mechanism.
The key requirement: **keep the element's `id` stable across requests**. When HTMX sees
an element with the same `id` in both old and new content, it:

1. Copies the old element's attributes onto the new element
2. Swaps the new element into the DOM (with old attributes)
3. After a "settle" delay (20ms default), applies the new attributes

This attribute-swap trick triggers CSS transitions automatically.

---

## Swap & Settle Lifecycle

CSS classes applied during the swap cycle:

```
Request starts → htmx-request added to element/indicator
    ↓
Response received → htmx-swapping added to target
    ↓ (swap delay, default 0ms)
Content swapped → htmx-swapping removed, htmx-settling added, htmx-added on new content
    ↓ (settle delay, default 20ms)
Settled → htmx-settling removed, htmx-added removed
```

You can customize the swap and settle delays:
```html
<div hx-get="/content" hx-swap="innerHTML swap:100ms settle:200ms">
```

---

## Common Animation Recipes

### Fade In New Content
```css
.fade-in {
    opacity: 0;
}
.fade-in.htmx-settling {
    opacity: 1;
    transition: opacity 0.5s ease-in;
}
/* Alternative using htmx-added */
.htmx-added {
    opacity: 0;
}
```

### Fade Out on Delete
```css
tr.htmx-swapping {
    opacity: 0;
    transition: opacity 0.5s ease-out;
}
```
```html
<button hx-delete="/item/1" hx-target="closest tr" hx-swap="outerHTML swap:500ms">Delete</button>
```
The `swap:500ms` delay gives the CSS transition time to complete before the element is removed.

### Slide Down (Accordion / Expand)
```css
.slide-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.4s ease-out;
}
.slide-content.htmx-settling {
    max-height: 500px;
}
```

### Slide In From Side
```css
.slide-in {
    transform: translateX(100%);
    transition: transform 0.3s ease-out;
}
.slide-in.htmx-settling {
    transform: translateX(0);
}
```

### Highlight Flash (Draw Attention to Updates)
```css
@keyframes highlight-flash {
    0% { background-color: #fef3c7; }
    100% { background-color: transparent; }
}
.htmx-added {
    animation: highlight-flash 1.5s ease-out;
}
```

### Scale / Bounce In
```css
@keyframes bounce-in {
    0% { transform: scale(0.3); opacity: 0; }
    50% { transform: scale(1.05); }
    70% { transform: scale(0.95); }
    100% { transform: scale(1); opacity: 1; }
}
.htmx-added {
    animation: bounce-in 0.4s ease;
}
```

### Staggered List Items
Using CSS variables and `nth-child` for staggered animation:
```css
.list-item.htmx-added {
    animation: slide-up 0.3s ease backwards;
}
.list-item.htmx-added:nth-child(1) { animation-delay: 0ms; }
.list-item.htmx-added:nth-child(2) { animation-delay: 50ms; }
.list-item.htmx-added:nth-child(3) { animation-delay: 100ms; }
.list-item.htmx-added:nth-child(4) { animation-delay: 150ms; }

@keyframes slide-up {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
```

### Toast Notification (Auto-Remove)
```css
@keyframes toast-enter { from { transform: translateX(120%); opacity: 0; } }
@keyframes toast-exit { to { transform: translateX(120%); opacity: 0; } }

.toast {
    animation: toast-enter 0.3s ease,
               toast-exit 0.3s ease 2.7s forwards;
}
```
Or use the `remove-me` extension for auto-removal:
```html
<div class="toast" remove-me="3s">Saved!</div>
```

---

## View Transitions API

The View Transitions API creates animated transitions between DOM states, giving HTMX
apps the buttery-smooth feel of SPAs. It works by capturing screenshots of old and new
state and cross-fading between them.

### Enabling View Transitions

**Per-element:**
```html
<a hx-get="/page" hx-swap="innerHTML transition:true" hx-target="#content">Navigate</a>
```

**Globally:**
```javascript
htmx.config.globalViewTransitions = true;
```

### Custom View Transition Animations
```css
/* Default cross-fade (built-in, no CSS needed) */

/* Custom: Slide transition */
@keyframes slide-from-right {
    from { transform: translateX(30px); opacity: 0; }
}
@keyframes slide-to-left {
    to { transform: translateX(-30px); opacity: 0; }
}

::view-transition-old(slide-it) {
    animation: 0.3s ease both slide-to-left;
}
::view-transition-new(slide-it) {
    animation: 0.3s ease both slide-from-right;
}

/* Bind transition to elements with this class */
.page-content {
    view-transition-name: slide-it;
}
```

### Named View Transitions
Different page areas can have independent transitions:
```css
.sidebar { view-transition-name: sidebar; }
.main-content { view-transition-name: main; }
.header { view-transition-name: header; }

/* Sidebar stays, main content fades */
::view-transition-old(sidebar),
::view-transition-new(sidebar) { animation: none; }

::view-transition-old(main) { animation: 0.2s fade-out; }
::view-transition-new(main) { animation: 0.2s fade-in; }
```

### Cancelling View Transitions
```javascript
document.body.addEventListener('htmx:beforeTransition', function(evt) {
    // Cancel transition for certain targets
    if (evt.detail.elt.id === 'small-widget') {
        evt.preventDefault();
    }
});
```

### Browser Support
View Transitions are supported in Chrome 111+, Edge 111+, and Safari 18+.
HTMX automatically falls back to non-animated swaps in unsupported browsers.

---

## Loading Skeletons

Show placeholder content while real content loads:

### Skeleton Pattern
```html
<div hx-get="/dashboard/stats"
     hx-trigger="load"
     hx-swap="outerHTML">
    <!-- Skeleton shown while loading -->
    <div class="skeleton-card">
        <div class="skeleton-line wide"></div>
        <div class="skeleton-line medium"></div>
        <div class="skeleton-line short"></div>
    </div>
</div>
```

```css
.skeleton-card {
    padding: 1.5rem;
    background: white;
    border-radius: 12px;
}

.skeleton-line {
    height: 1rem;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 4px;
    margin-bottom: 0.75rem;
}

.skeleton-line.wide { width: 100%; }
.skeleton-line.medium { width: 70%; }
.skeleton-line.short { width: 40%; }

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
```

### Server Returns Real Content
The server's response replaces the skeleton entirely (via `outerHTML`):
```html
<div class="stat-card">
    <h3>Revenue</h3>
    <p class="value">$34,521</p>
    <p class="trend">↑ 12% from last month</p>
</div>
```

---

## Loading Indicators

### Spinner (Default Pattern)
```html
<button hx-get="/data" hx-indicator="#spinner">Load Data</button>
<span id="spinner" class="htmx-indicator">
    <svg class="spinner" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"
                fill="none" stroke-dasharray="31.4 31.4" stroke-linecap="round">
            <animateTransform attributeName="transform" type="rotate"
                              dur="0.8s" from="0 12 12" to="360 12 12" repeatCount="indefinite"/>
        </circle>
    </svg>
</span>
```

### Button Loading State
```css
button.htmx-request {
    pointer-events: none;
    opacity: 0.7;
    position: relative;
}
button.htmx-request::after {
    content: '';
    position: absolute;
    right: 0.75rem;
    top: 50%;
    width: 1rem;
    height: 1rem;
    margin-top: -0.5rem;
    border: 2px solid rgba(255,255,255,0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
}
```

### Progress Bar (Top of Page, NProgress-Style)
```css
#page-progress {
    position: fixed;
    top: 0;
    left: 0;
    height: 3px;
    background: #4a90d9;
    width: 0%;
    transition: width 0.4s ease;
    z-index: 9999;
}
.htmx-request #page-progress {
    width: 90%;
}
```
After request completes, briefly set to 100% then hide.

---

## Page Transition Patterns

### Full-Page Slide (SPA Feel)
```css
/* With View Transitions API */
::view-transition-old(root) {
    animation: 0.25s ease both slide-out-left;
}
::view-transition-new(root) {
    animation: 0.25s ease both slide-in-right;
}

@keyframes slide-out-left {
    to { transform: translateX(-100%); opacity: 0; }
}
@keyframes slide-in-right {
    from { transform: translateX(100%); opacity: 0; }
}
```

### Morph-Based Transitions (Idiomorph)
Using morph swap for the smoothest possible updates — elements that don't change
stay in place, only differences are patched:
```html
<body hx-ext="morph">
    <main hx-get="/page" hx-swap="morph:innerHTML transition:true">
```
Combining morph + View Transitions gives the best of both worlds.
