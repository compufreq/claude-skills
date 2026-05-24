# SEO, Modern Design & Accessibility for HTMX

## Table of Contents
1. [SEO Advantages of HTMX](#seo-advantages)
2. [SEO Best Practices](#seo-best-practices)
3. [Structured Data & Meta Tags](#structured-data)
4. [Performance & Core Web Vitals](#core-web-vitals)
5. [Modern Frontend Design Patterns](#modern-design)
6. [Accessibility (a11y)](#accessibility)
7. [Progressive Enhancement](#progressive-enhancement)

---

## SEO Advantages of HTMX

HTMX apps have a fundamental SEO advantage over SPAs: **the server renders real HTML**.
Search engine crawlers see fully-formed content on the first request without needing
JavaScript execution. This means:

- **No JavaScript rendering required** — Googlebot and other crawlers see your content
  immediately. SPAs need SSR/SSG or risk invisible content.
- **Canonical URLs work naturally** — `hx-push-url` and `hx-boost` update the URL bar,
  and each URL returns a complete page when accessed directly.
- **No hydration mismatch** — What the server sends is what the crawler sees.
- **Faster Time to First Byte (TTFB)** — No client-side rendering overhead.
- **Smaller JavaScript payload** — htmx is ~14KB gzipped vs 100KB+ for React/Vue.

---

## SEO Best Practices

### 1. Every URL Must Return a Full Page
The most important rule: every URL that appears in the browser's address bar must
return a complete, crawlable HTML page when accessed directly (without `HX-Request` header).

```python
@app.route("/products/<int:id>")
def product_detail(product_id):
    product = get_product(product_id)
    if is_htmx():
        return render_template("partials/product_detail.html", product=product)
    return render_template("product_page.html", product=product)  # Full page for crawlers
```

### 2. Use Semantic HTML
Crawlers and screen readers rely on semantic structure:
```html
<header>
    <nav aria-label="Main navigation">
        <a href="/" hx-boost="true">Home</a>
        <a href="/products" hx-boost="true">Products</a>
        <a href="/about" hx-boost="true">About</a>
    </nav>
</header>

<main>
    <article>
        <h1>{{ product.name }}</h1>
        <p>{{ product.description }}</p>
        <section aria-label="Reviews">
            <h2>Customer Reviews</h2>
            <!-- lazy-loaded reviews are fine — the heading tells crawlers what's here -->
            <div hx-get="/products/{{ product.id }}/reviews"
                 hx-trigger="revealed"
                 hx-swap="innerHTML">
                <p>Loading reviews...</p>
            </div>
        </section>
    </article>
</main>

<footer><!-- site footer --></footer>
```

### 3. Title & Meta Tags
Update the page title and meta description on navigation. HTMX 2.x handles `<title>`
automatically when using `hx-boost` or full-page swaps. For partial swaps, use
the head-support extension or `HX-Trigger` with JavaScript:

```python
# Server response header
response.headers["HX-Trigger"] = json.dumps({
    "updateMeta": {
        "title": "Product Name — My Store",
        "description": "Buy Product Name at the best price..."
    }
})
```
```javascript
document.body.addEventListener('updateMeta', function(evt) {
    document.title = evt.detail.title;
    document.querySelector('meta[name="description"]')
        ?.setAttribute('content', evt.detail.description);
});
```

### 4. Canonical URLs
Always include a canonical URL:
```html
<link rel="canonical" href="https://example.com/products/42">
```
Update it on navigation via head-support extension or OOB swap:
```html
<link rel="canonical" href="/products/42" hx-swap-oob="true" id="canonical-link">
```

### 5. Sitemap & robots.txt
Since every URL is a real server route, standard sitemaps work perfectly:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>https://example.com/</loc></url>
    <url><loc>https://example.com/products</loc></url>
    <url><loc>https://example.com/products/42</loc></url>
</urlset>
```

### 6. Open Graph & Social Sharing
Include OG tags in the full page template:
```html
<head>
    <meta property="og:title" content="{{ product.name }}">
    <meta property="og:description" content="{{ product.description[:160] }}">
    <meta property="og:image" content="{{ product.image_url }}">
    <meta property="og:url" content="https://example.com/products/{{ product.id }}">
    <meta property="og:type" content="product">
    <meta name="twitter:card" content="summary_large_image">
</head>
```

### 7. Lazy-Loaded Content SEO
Content loaded via `hx-trigger="revealed"` or `hx-trigger="load"` won't be in the
initial HTML. For SEO-critical content, include it in the initial server response
and use HTMX only for updates:

```html
<!-- SEO-critical: rendered in initial HTML -->
<h1>{{ product.name }}</h1>
<p>{{ product.description }}</p>
<span>{{ product.price }}</span>

<!-- Non-critical: can be lazy-loaded -->
<div hx-get="/products/{{ product.id }}/recommendations"
     hx-trigger="revealed">
    Loading recommendations...
</div>
```

---

## Structured Data

### JSON-LD (Recommended)
```html
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "{{ product.name }}",
    "description": "{{ product.description }}",
    "image": "{{ product.image_url }}",
    "offers": {
        "@type": "Offer",
        "price": "{{ product.price }}",
        "priceCurrency": "USD",
        "availability": "https://schema.org/InStock"
    },
    "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "{{ product.avg_rating }}",
        "reviewCount": "{{ product.review_count }}"
    }
}
</script>
```

### Breadcrumbs
```html
<nav aria-label="Breadcrumb">
    <ol itemscope itemtype="https://schema.org/BreadcrumbList">
        <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
            <a itemprop="item" href="/" hx-boost="true"><span itemprop="name">Home</span></a>
            <meta itemprop="position" content="1">
        </li>
        <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
            <a itemprop="item" href="/products" hx-boost="true"><span itemprop="name">Products</span></a>
            <meta itemprop="position" content="2">
        </li>
        <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
            <span itemprop="name">{{ product.name }}</span>
            <meta itemprop="position" content="3">
        </li>
    </ol>
</nav>
```

---

## Performance & Core Web Vitals

HTMX naturally excels at Core Web Vitals because of server-side rendering.

### Largest Contentful Paint (LCP)
- Server-rendered HTML means LCP content is in the initial response
- No waiting for JavaScript to download, parse, and render
- Use `<link rel="preload">` for hero images and critical fonts

### First Input Delay (FID) / Interaction to Next Paint (INP)
- HTMX is ~14KB — minimal JavaScript to parse
- No hydration step blocking interactivity
- Elements are interactive as soon as htmx.js loads

### Cumulative Layout Shift (CLS)
- Server-rendered content doesn't shift — dimensions are known upfront
- For lazy-loaded content, reserve space with CSS:
```css
.lazy-placeholder {
    min-height: 200px; /* Reserve space to prevent layout shift */
}
```
- Use `hx-swap="outerHTML"` to replace placeholders seamlessly

### Performance Headers
```html
<head>
    <!-- Preload critical resources -->
    <link rel="preload" href="/static/js/htmx.min.js" as="script">
    <link rel="preload" href="/static/css/style.css" as="style">
    <link rel="preload" href="/static/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>

    <!-- Preconnect to CDN if using one -->
    <link rel="preconnect" href="https://cdn.jsdelivr.net">

    <!-- DNS prefetch for external resources -->
    <link rel="dns-prefetch" href="https://analytics.example.com">
</head>
```

---

## Modern Frontend Design Patterns

### Rich, Attractive Interfaces Without SPAs
HTMX + Tailwind (or any CSS framework) + View Transitions can produce interfaces
indistinguishable from SPAs:

**Smooth page transitions:**
```html
<body hx-boost="true">
    <main class="page-content" style="view-transition-name: main;">
```
```css
::view-transition-old(main) { animation: 0.2s ease-out fade-slide-out; }
::view-transition-new(main) { animation: 0.2s ease-out fade-slide-in; }
```

**Instant feedback:**
- Loading indicators on buttons (`htmx-request` class)
- Skeleton screens for lazy content
- Optimistic UI updates (see advanced-patterns.md)
- Toast notifications via `HX-Trigger`

**Micro-interactions:**
- Hover-to-preload links (preload extension)
- Click-to-edit inline (no page navigation)
- Drag-and-drop reordering (Sortable.js)
- Animated counters and badges (OOB swaps + CSS)

**Modal & Sheet Patterns:**
```html
<button hx-get="/edit/42"
        hx-target="#modal-container"
        hx-swap="innerHTML transition:true">
    Edit
</button>

<div id="modal-container">
    <!-- Server returns a full modal with backdrop -->
</div>
```

### Design System Integration
HTMX works with any CSS framework or design system:
- **Tailwind CSS** — most popular pairing (see integrations.md)
- **Bootstrap** — `hx-boost` upgrades Bootstrap's links and forms automatically
- **Pico CSS** — classless CSS framework, perfect for minimal HTMX apps
- **DaisyUI** — Tailwind component library, all classes work with HTMX
- **Shoelace / Web Awesome** — Web Component libraries, use with `htmx.process()`

---

## Accessibility (a11y)

### ARIA Live Regions for Dynamic Content
When HTMX swaps content, screen readers may not notice. Use `aria-live` regions:
```html
<!-- Announce search results to screen readers -->
<div id="search-results" aria-live="polite" aria-atomic="false">
    <!-- HTMX swaps results here -->
</div>

<!-- Announce toast notifications -->
<div id="toast-container" role="alert" aria-live="assertive">
    <!-- Toasts appear here -->
</div>
```

### Focus Management After Swaps
After content is swapped, focus should move to the new content or remain logical:
```javascript
document.body.addEventListener('htmx:afterSwap', function(evt) {
    // Focus the first focusable element in the new content
    const focusable = evt.detail.target.querySelector(
        'input, textarea, select, button, [tabindex]:not([tabindex="-1"])'
    );
    if (focusable) focusable.focus();
});
```

Or use Idiomorph (`hx-swap="morph:innerHTML"`) which preserves focus automatically.

### Skip Navigation
```html
<body>
    <a href="#main-content" class="sr-only focus:not-sr-only">Skip to content</a>
    <nav>...</nav>
    <main id="main-content" tabindex="-1">
        <!-- HTMX content area -->
    </main>
</body>
```

### Form Accessibility
```html
<form hx-post="/register" hx-target="#form-result">
    <div>
        <label for="email">Email</label>
        <input type="email" id="email" name="email" required
               aria-describedby="email-help email-error"
               hx-post="/validate/email"
               hx-trigger="blur"
               hx-target="#email-error">
        <small id="email-help">We'll never share your email.</small>
        <span id="email-error" role="alert" aria-live="polite"></span>
    </div>
    <button type="submit">Register</button>
</form>
```

### Indicator Accessibility
```html
<button hx-get="/data" hx-indicator="#spinner" aria-busy="false"
        hx-on:htmx:beforeRequest="this.setAttribute('aria-busy', 'true')"
        hx-on:htmx:afterRequest="this.setAttribute('aria-busy', 'false')">
    Load Data
</button>
<span id="spinner" class="htmx-indicator" role="status" aria-label="Loading">
    <svg><!-- spinner --></svg>
</span>
```

### Confirm Dialogs
`hx-confirm` uses the browser's native `confirm()` which is accessible by default.
For custom dialogs, ensure keyboard navigation and ARIA roles:
```html
<div role="alertdialog" aria-modal="true" aria-labelledby="dialog-title">
    <h2 id="dialog-title">Confirm Deletion</h2>
    <p>This action cannot be undone.</p>
    <button autofocus>Cancel</button>
    <button hx-delete="/item/42">Delete</button>
</div>
```

---

## Progressive Enhancement

HTMX excels at progressive enhancement — the page works without JavaScript,
then HTMX upgrades it.

### Pattern: Forms That Work Without JS
```html
<!-- Without JS: regular form POST, full page reload -->
<!-- With JS: HTMX intercepts, does AJAX, swaps result -->
<form action="/search" method="get"
      hx-get="/search"
      hx-target="#results"
      hx-push-url="true">
    <input name="q" type="search">
    <button type="submit">Search</button>
</form>
```

### Pattern: Links That Work Without JS
```html
<!-- hx-boost upgrades these links to AJAX, but they work as regular links too -->
<body hx-boost="true">
    <a href="/about">About</a>         <!-- Works without JS -->
    <a href="/contact">Contact</a>     <!-- Works without JS -->
</body>
```

### Noscript Fallback
```html
<noscript>
    <style>
        .htmx-indicator { display: none; }
        .js-only { display: none; }
    </style>
</noscript>
```

### Server-Side: Detect and Degrade Gracefully
```python
@app.route("/search")
def search():
    results = do_search(request.args.get("q", ""))
    if is_htmx():
        return render_template("partials/results.html", results=results)
    # Non-JS: return full page with results
    return render_template("search.html", results=results)
```

This ensures crawlers, users with JS disabled, and HTMX users all get the right experience.
