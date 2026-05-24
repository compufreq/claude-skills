# Integrating HTMX with Other Libraries

## Table of Contents
1. [Alpine.js](#alpinejs)
2. [Hyperscript](#hyperscript)
3. [Tailwind CSS](#tailwind)
4. [Web Components](#web-components)
5. [Sortable.js & Other Plugins](#plugins)
6. [Chart Libraries](#charts)

---

## Alpine.js

Alpine.js and HTMX are a natural pairing — Alpine handles client-side reactivity
(toggling, counters, local state) while HTMX handles server communication.

### Setup
```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
```

### Pattern: Alpine for Local UI, HTMX for Server
```html
<div x-data="{ open: false, count: 0 }">
    <!-- Alpine toggles the dropdown visibility -->
    <button @click="open = !open" class="btn">
        Cart (<span x-text="count">0</span>)
    </button>

    <!-- HTMX loads the cart content from the server -->
    <div x-show="open" x-transition
         hx-get="/cart/preview"
         hx-trigger="cartUpdated from:body"
         hx-swap="innerHTML">
        <!-- Cart preview loads here -->
    </div>

    <!-- Listen for HTMX events to update Alpine state -->
    <div x-on:cart-updated.window="count = $event.detail.count"></div>
</div>
```

### Preserving Alpine State During HTMX Swaps
By default, HTMX replaces DOM elements, which destroys Alpine state.
Use the `alpine-morph` extension or Idiomorph to preserve state:

```html
<script src="https://cdn.jsdelivr.net/npm/idiomorph@0.3.0/dist/idiomorph-ext.min.js"></script>
<body hx-ext="morph">
    <div hx-get="/content" hx-swap="morph:innerHTML">
        <!-- Alpine state preserved through morphs -->
        <div x-data="{ expanded: true }">...</div>
    </div>
</body>
```

### Re-Initializing Alpine After HTMX Swap
If not using morph, Alpine needs to initialize new elements:
```javascript
document.body.addEventListener('htmx:afterSwap', function(evt) {
    // Alpine auto-initializes new elements with x-data in htmx 2.x
    // but if you need manual init:
    Alpine.initTree(evt.detail.target);
});
```

### Tabs Example (Alpine + HTMX)
```html
<div x-data="{ activeTab: 'overview' }">
    <nav>
        <button @click="activeTab = 'overview'"
                :class="{ 'active': activeTab === 'overview' }"
                hx-get="/tabs/overview"
                hx-target="#tab-content">Overview</button>
        <button @click="activeTab = 'details'"
                :class="{ 'active': activeTab === 'details' }"
                hx-get="/tabs/details"
                hx-target="#tab-content">Details</button>
    </nav>
    <div id="tab-content">
        <!-- Content loaded by HTMX -->
    </div>
</div>
```

### Dropdown with Server Search
```html
<div x-data="{ open: false, query: '' }" @click.outside="open = false">
    <input type="text" x-model="query" @focus="open = true"
           hx-get="/autocomplete"
           hx-trigger="input changed delay:300ms"
           hx-target="#suggestions"
           hx-indicator="#search-spinner"
           name="q">

    <div id="suggestions" x-show="open" x-transition>
        <!-- Server-rendered suggestions appear here -->
    </div>
</div>
```

---

## Hyperscript

Hyperscript (_hyperscript) is a scripting language designed by the HTMX creator
as a companion to HTMX. It's more readable than JavaScript for DOM manipulation.

### Setup
```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js"></script>
<script src="https://unpkg.com/hyperscript.org@0.9.12"></script>
```

### Pattern: Hyperscript for Client-Side Logic
```html
<!-- Toggle class on click -->
<button _="on click toggle .active on me">Toggle</button>

<!-- Remove parent after animation -->
<button _="on click
            add .fade-out to closest .notification
            wait 500ms
            remove closest .notification">
    Dismiss
</button>

<!-- Copy to clipboard -->
<button _="on click
            writeText(#code-block.innerText) into navigator.clipboard
            put 'Copied!' into me
            wait 2s
            put 'Copy' into me">
    Copy
</button>
```

### Hyperscript + HTMX Events
```html
<form hx-post="/submit"
      _="on htmx:afterRequest
            if event.detail.successful
                reset() me
                add .success to #status
            else
                add .error to #status">
```

### Form Reset After Successful Submit
```html
<form hx-post="/items"
      _="on htmx:afterOnLoad reset() me">
```

---

## Tailwind CSS

HTMX + Tailwind is a popular stack for building modern server-rendered apps.

### Key Patterns

**Loading States with Tailwind:**
```html
<style>
    .htmx-indicator { opacity: 0; transition: opacity 200ms; }
    .htmx-request .htmx-indicator { opacity: 1; }
    .htmx-request.htmx-indicator { opacity: 1; }
</style>

<button hx-get="/data"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700
               disabled:opacity-50 disabled:cursor-not-allowed"
        hx-disabled-elt="this">
    Load Data
    <svg class="htmx-indicator inline ml-2 w-4 h-4 animate-spin" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
                fill="none" opacity="0.25"/>
        <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z" opacity="0.75"/>
    </svg>
</button>
```

**Cards with HTMX Actions:**
```html
<div class="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
    <h3 class="text-lg font-semibold text-gray-900">{{ item.title }}</h3>
    <p class="text-gray-500 mt-2">{{ item.description }}</p>
    <div class="flex gap-2 mt-4">
        <button hx-get="/items/{{ item.id }}/edit"
                hx-target="closest div"
                hx-swap="outerHTML"
                class="text-sm text-blue-600 hover:text-blue-800">Edit</button>
        <button hx-delete="/items/{{ item.id }}"
                hx-target="closest div"
                hx-swap="outerHTML swap:300ms"
                hx-confirm="Delete?"
                class="text-sm text-red-600 hover:text-red-800">Delete</button>
    </div>
</div>
```

**Swap Animations with Tailwind:**
```html
<style>
    .htmx-swapping { @apply opacity-0 transition-opacity duration-300; }
    .htmx-added { @apply animate-fadeIn; }
</style>
```

### Tailwind + HTMX Class Considerations
Since HTMX dynamically adds classes like `htmx-request`, `htmx-indicator`, etc.,
make sure Tailwind's JIT compiler doesn't purge them. Add to your `tailwind.config.js`:
```javascript
module.exports = {
    safelist: [
        'htmx-indicator',
        'htmx-request',
        'htmx-settling',
        'htmx-swapping',
        'htmx-added',
    ],
}
```

---

## Web Components

HTMX works with Web Components and Shadow DOM.

### Using HTMX Inside Web Components
```javascript
class UserCard extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <div hx-get="/users/${this.getAttribute('user-id')}"
                 hx-trigger="load"
                 hx-swap="innerHTML">
                Loading...
            </div>
        `;
        htmx.process(this);  // Initialize HTMX on the new content
    }
}
customElements.define('user-card', UserCard);
```

Usage:
```html
<user-card user-id="42"></user-card>
```

### Important: Call htmx.process()
After dynamically adding HTMX-attributed elements via JavaScript, call
`htmx.process(element)` to initialize them.

---

## Plugins

### Sortable.js
See `advanced-patterns.md` for the drag-and-drop pattern.

### Flatpickr (Date Picker)
```html
<input type="text" name="date" class="flatpickr"
       hx-include="this" hx-get="/filter"
       hx-trigger="change" hx-target="#results">

<script>
    // Init on page load
    flatpickr('.flatpickr', { dateFormat: 'Y-m-d' });

    // Re-init after HTMX swaps
    document.body.addEventListener('htmx:afterSwap', function() {
        flatpickr('.flatpickr', { dateFormat: 'Y-m-d' });
    });
</script>
```

### Tom Select / Choices.js (Enhanced Selects)
Same pattern — initialize on load and re-initialize on `htmx:afterSwap` or `htmx:load`.

---

## Charts

### Chart.js with HTMX
```html
<canvas id="chart"
        hx-get="/api/chart-data"
        hx-trigger="load, every 30s"
        hx-swap="none"
        hx-on:htmx:afterRequest="updateChart(event)">
</canvas>

<script>
    let chart;

    function updateChart(evt) {
        const data = JSON.parse(evt.detail.xhr.responseText);
        if (chart) {
            chart.data = data;
            chart.update();
        } else {
            chart = new Chart(document.getElementById('chart'), {
                type: 'line', data: data,
                options: { animation: { duration: 500 } }
            });
        }
    }
</script>
```

Note: This is one case where `hx-swap="none"` is useful — you're consuming
the response in JavaScript rather than swapping HTML. For chart data, JSON
responses make more sense than HTML fragments.
