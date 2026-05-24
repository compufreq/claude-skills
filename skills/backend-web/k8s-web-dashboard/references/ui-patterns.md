# UI Patterns Reference

HTMX recipes specifically designed for Kubernetes dashboard interfaces. These patterns
combine HTMX 2.x with Tailwind CSS to create professional, responsive, real-time UIs
with minimal JavaScript.

## Table of Contents

1. [Base Layout & Navigation](#1-base-layout--navigation)
2. [Cluster Switcher](#2-cluster-switcher)
3. [Namespace Selector](#3-namespace-selector)
4. [Resource Tables](#4-resource-tables)
5. [Live Log Viewer](#5-live-log-viewer)
6. [Real-Time Event Feed](#6-real-time-event-feed)
7. [Status Badges](#7-status-badges)
8. [YAML Editor](#8-yaml-editor)
9. [Destructive Action Confirmations](#9-destructive-action-confirmations)
10. [Toast Notifications](#10-toast-notifications)
11. [Loading States](#11-loading-states)
12. [Search & Filtering](#12-search--filtering)

---

## 1. Base Layout & Navigation

The shell template that wraps all pages. Uses HTMX boost for SPA-like navigation
without full page reloads.

```html
<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }} — {{ app_name }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/htmx-ext-sse@2.2.4"></script>
    <script src="https://cdn.jsdelivr.net/npm/htmx-ext-ws@2.0.0/dist/ws.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/htmx-ext-response-targets@2.0.2/response-targets.js"></script>
    <link rel="stylesheet" href="/static/css/app.css">
</head>
<body class="h-full bg-gray-50 dark:bg-gray-900"
      hx-boost="true"
      hx-ext="response-targets">

  <!-- Top bar -->
  <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-3">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <h1 class="text-lg font-semibold text-gray-900 dark:text-white">{{ app_name }}</h1>
        {% include "components/cluster_switcher.html" %}
      </div>
      <div class="flex items-center gap-4">
        {% include "components/namespace_selector.html" %}
        <button onclick="document.documentElement.classList.toggle('dark')"
                class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
          🌓
        </button>
      </div>
    </div>
  </header>

  <div class="flex h-[calc(100vh-57px)]">
    <!-- Sidebar navigation -->
    <nav class="w-56 bg-white dark:bg-gray-800 border-r border-gray-200
                dark:border-gray-700 py-4 overflow-y-auto">
      {% set nav_items = [
        ("overview", "Overview", "/clusters/" ~ cluster.id ~ "/overview"),
        ("workloads", "Workloads", "/clusters/" ~ cluster.id ~ "/workloads"),
        ("pods", "Pods", "/clusters/" ~ cluster.id ~ "/pods"),
        ("services", "Services", "/clusters/" ~ cluster.id ~ "/services"),
        ("configmaps", "Config", "/clusters/" ~ cluster.id ~ "/configmaps"),
        ("rbac", "RBAC", "/clusters/" ~ cluster.id ~ "/rbac"),
        ("namespaces", "Namespaces", "/clusters/" ~ cluster.id ~ "/namespaces"),
        ("events", "Events", "/clusters/" ~ cluster.id ~ "/events"),
      ] %}
      {% for id, label, href in nav_items %}
        <a href="{{ href }}"
           hx-target="#main-content"
           hx-push-url="true"
           class="block px-6 py-2 text-sm
                  {% if active_page == id %}
                    bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300
                    border-r-2 border-blue-700
                  {% else %}
                    text-gray-700 dark:text-gray-300 hover:bg-gray-50
                    dark:hover:bg-gray-700/50
                  {% endif %}">
          {{ label }}
        </a>
      {% endfor %}
    </nav>

    <!-- Main content area -->
    <main id="main-content" class="flex-1 overflow-y-auto p-6">
      {% block content %}{% endblock %}
    </main>
  </div>

  <!-- Toast container (fixed bottom-right) -->
  <div id="toast-container"
       class="fixed bottom-4 right-4 flex flex-col gap-2 z-50">
  </div>

  <script src="/static/js/app.js"></script>
</body>
</html>
```

## 2. Cluster Switcher

Dropdown that switches the active cluster. Triggers a full content reload since
all data changes.

```html
<!-- components/cluster_switcher.html -->
<div class="relative">
  <select name="cluster_id"
          hx-post="/clusters/switch"
          hx-target="#main-content"
          hx-swap="innerHTML"
          hx-indicator="#cluster-loading"
          class="bg-gray-100 dark:bg-gray-700 border-0 rounded-lg px-3 py-1.5
                 text-sm font-medium text-gray-700 dark:text-gray-200
                 focus:ring-2 focus:ring-blue-500">
    {% for c in clusters %}
      <option value="{{ c.id }}"
              {% if c.id == current_cluster.id %}selected{% endif %}>
        {{ c.name }}
        {% if c.is_healthy %}✓{% else %}⚠{% endif %}
      </option>
    {% endfor %}
  </select>
  <span id="cluster-loading" class="htmx-indicator ml-2">
    <svg class="animate-spin h-4 w-4 text-blue-500" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
              fill="none" opacity="0.25"/>
      <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z"/>
    </svg>
  </span>
</div>
```

## 3. Namespace Selector

Global namespace selector that updates all visible panels via OOB swaps.

```html
<!-- components/namespace_selector.html -->
<select name="namespace"
        hx-post="/namespaces/switch"
        hx-target="#main-content"
        hx-swap="innerHTML"
        hx-indicator="#ns-loading"
        id="namespace-selector"
        class="bg-gray-100 dark:bg-gray-700 border-0 rounded-lg px-3 py-1.5
               text-sm text-gray-700 dark:text-gray-200">
  <option value="">All Namespaces</option>
  {% for ns in namespaces %}
    <option value="{{ ns }}" {% if ns == current_namespace %}selected{% endif %}>
      {{ ns }}
    </option>
  {% endfor %}
</select>
<span id="ns-loading" class="htmx-indicator">
  <span class="text-xs text-gray-400">switching...</span>
</span>
```

## 4. Resource Tables

The most common UI pattern. Sortable, filterable tables with polling refresh
that preserve user interactions during updates.

```html
<!-- components/resource_table.html -->
<div id="{{ table_id }}"
     hx-get="{{ refresh_url }}"
     hx-trigger="every {{ poll_interval | default('5s') }}"
     hx-swap="innerHTML"
     hx-select="#{{ table_id }} > table"
     hx-indicator="#{{ table_id }}-loading">

  <!-- Header with search and refresh indicator -->
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
      {{ title }}
      <span class="text-sm font-normal text-gray-500">({{ items | length }})</span>
    </h2>
    <div class="flex items-center gap-3">
      <input type="search"
             name="search"
             placeholder="Filter {{ title | lower }}..."
             hx-get="{{ search_url }}"
             hx-trigger="input changed delay:300ms"
             hx-target="#{{ table_id }}"
             hx-swap="innerHTML"
             class="text-sm rounded-lg border-gray-300 dark:border-gray-600
                    dark:bg-gray-700 px-3 py-1.5">
      <span id="{{ table_id }}-loading" class="htmx-indicator">
        <span class="inline-block w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
      </span>
    </div>
  </div>

  <table class="w-full text-sm">
    <thead>
      <tr class="text-left text-xs uppercase text-gray-500 dark:text-gray-400
                 border-b border-gray-200 dark:border-gray-700">
        {% for col in columns %}
          <th class="py-3 px-4 font-medium">
            <a href="#" hx-get="{{ sort_url }}?sort={{ col.key }}"
               hx-target="#{{ table_id }}"
               class="hover:text-gray-700 dark:hover:text-gray-200">
              {{ col.label }}
              {% if sort_key == col.key %}
                {{ "↑" if sort_dir == "asc" else "↓" }}
              {% endif %}
            </a>
          </th>
        {% endfor %}
        <th class="py-3 px-4 font-medium">Actions</th>
      </tr>
    </thead>
    <tbody id="{{ table_id }}-body">
      {% for item in items %}
        {% include row_template %}
      {% endfor %}
    </tbody>
  </table>

  {% include "components/pagination.html" %}
</div>
```

## 5. Live Log Viewer

SSE-based log viewer with auto-scroll, pause, container selector, and tail-lines control.

```html
<!-- components/log_viewer.html -->
<div class="flex flex-col h-[600px]" id="log-viewer">
  <!-- Controls bar -->
  <div class="flex items-center justify-between bg-gray-100 dark:bg-gray-800
              rounded-t-lg px-4 py-2 border border-gray-200 dark:border-gray-700">
    <div class="flex items-center gap-3">
      <!-- Container selector (for multi-container pods) -->
      {% if containers | length > 1 %}
        <select id="log-container"
                hx-get="/clusters/{{ cluster_id }}/pods/{{ pod_name }}/logs"
                hx-target="#log-viewer"
                hx-swap="outerHTML"
                hx-include="[name='tail_lines']"
                class="text-xs rounded border-gray-300 dark:border-gray-600
                       dark:bg-gray-700 px-2 py-1"
                name="container">
          {% for c in containers %}
            <option value="{{ c }}" {% if c == current_container %}selected{% endif %}>
              {{ c }}
            </option>
          {% endfor %}
        </select>
      {% endif %}

      <select name="tail_lines" class="text-xs rounded border-gray-300
              dark:border-gray-600 dark:bg-gray-700 px-2 py-1">
        <option value="50">50 lines</option>
        <option value="100" selected>100 lines</option>
        <option value="500">500 lines</option>
        <option value="1000">1000 lines</option>
      </select>
    </div>

    <div class="flex items-center gap-2">
      <span class="inline-block w-2 h-2 rounded-full bg-green-500 animate-pulse"
            id="log-status"></span>
      <span class="text-xs text-gray-500">Streaming</span>
      <button onclick="toggleAutoScroll()" id="scroll-toggle"
              class="text-xs px-2 py-1 rounded bg-gray-200 dark:bg-gray-700
                     hover:bg-gray-300 dark:hover:bg-gray-600">
        Auto-scroll: ON
      </button>
      <button onclick="clearLogs()"
              class="text-xs px-2 py-1 rounded bg-gray-200 dark:bg-gray-700
                     hover:bg-gray-300 dark:hover:bg-gray-600">
        Clear
      </button>
    </div>
  </div>

  <!-- Log output area with SSE connection -->
  <div id="log-output"
       hx-ext="sse"
       sse-connect="/clusters/{{ cluster_id }}/pods/{{ pod_name }}/logs/stream?container={{ current_container }}&tail_lines=100"
       sse-swap="message"
       hx-swap="beforeend"
       class="flex-1 overflow-y-auto bg-gray-900 text-green-400
              font-mono text-xs p-4 rounded-b-lg border-x border-b
              border-gray-200 dark:border-gray-700
              scroll-smooth">
    <!-- Log lines appended here by SSE -->
  </div>
</div>

<script>
  // Auto-scroll logic
  let autoScroll = true;
  const logOutput = document.getElementById('log-output');

  // Use MutationObserver to scroll on new content
  const observer = new MutationObserver(() => {
    if (autoScroll) {
      logOutput.scrollTop = logOutput.scrollHeight;
    }
  });
  observer.observe(logOutput, { childList: true });

  function toggleAutoScroll() {
    autoScroll = !autoScroll;
    document.getElementById('scroll-toggle').textContent =
      `Auto-scroll: ${autoScroll ? 'ON' : 'OFF'}`;
  }

  function clearLogs() {
    logOutput.innerHTML = '';
  }
</script>
```

## 6. Real-Time Event Feed

WebSocket-based event stream with filtering.

```html
<!-- components/event_feed.html -->
<div id="event-feed"
     hx-ext="ws"
     ws-connect="/clusters/{{ cluster_id }}/events/stream?namespace={{ namespace }}">

  <!-- Filter controls -->
  <div class="flex items-center gap-3 mb-4">
    <button class="text-xs px-3 py-1.5 rounded-full
                   {% if severity_filter == 'all' %}bg-blue-100 text-blue-700{% else %}bg-gray-100 text-gray-600{% endif %}"
            onclick="filterEvents('all')">
      All
    </button>
    <button class="text-xs px-3 py-1.5 rounded-full
                   {% if severity_filter == 'Warning' %}bg-amber-100 text-amber-700{% else %}bg-gray-100 text-gray-600{% endif %}"
            onclick="filterEvents('Warning')">
      ⚠ Warnings
    </button>
    <button class="text-xs px-3 py-1.5 rounded-full
                   {% if severity_filter == 'Normal' %}bg-green-100 text-green-700{% else %}bg-gray-100 text-gray-600{% endif %}"
            onclick="filterEvents('Normal')">
      ✓ Normal
    </button>
  </div>

  <!-- Event table -->
  <table class="w-full text-sm">
    <thead>
      <tr class="text-left text-xs uppercase text-gray-500 border-b">
        <th class="py-2 px-3 w-20">Type</th>
        <th class="py-2 px-3 w-32">Reason</th>
        <th class="py-2 px-3 w-48">Object</th>
        <th class="py-2 px-3">Message</th>
        <th class="py-2 px-3 w-36">Time</th>
      </tr>
    </thead>
    <tbody id="events-body">
      <!-- New events prepended here via WebSocket OOB swap -->
    </tbody>
  </table>
</div>

<script>
  function filterEvents(severity) {
    // Send filter command via WebSocket
    const ws = htmx.find('#event-feed');
    // HTMX WS extension handles the connection
    htmx.trigger(ws, 'ws:send', {
      detail: { type: 'filter', severity: severity }
    });
  }
</script>
```

## 7. Status Badges

Color-coded badges for K8s resource phases and conditions.

```html
<!-- components/status_badge.html -->
<!-- Usage: {% include "components/status_badge.html" with status=pod.status %} -->

{% set badge_colors = {
  "Running": "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  "Succeeded": "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  "Pending": "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  "ContainerCreating": "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  "Failed": "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  "CrashLoopBackOff": "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  "Error": "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  "Terminating": "bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300",
  "Unknown": "bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300",
  "Available": "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  "Progressing": "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  "Degraded": "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
} %}

<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
             {{ badge_colors.get(status, 'bg-gray-100 text-gray-700') }}">
  <span class="w-1.5 h-1.5 rounded-full mr-1.5
    {% if status in ['Running', 'Succeeded', 'Available'] %}bg-green-500
    {% elif status in ['Pending', 'ContainerCreating'] %}bg-yellow-500 animate-pulse
    {% elif status in ['Failed', 'CrashLoopBackOff', 'Error', 'Degraded'] %}bg-red-500
    {% elif status == 'Progressing' %}bg-blue-500 animate-pulse
    {% else %}bg-gray-500{% endif %}">
  </span>
  {{ status }}
</span>
```

## 8. YAML Editor

Server-side YAML editing with validation feedback.

```html
<!-- components/yaml_editor.html -->
<div id="yaml-editor-{{ resource_type }}-{{ resource_name }}">
  <div class="flex items-center justify-between mb-2">
    <h3 class="text-sm font-medium">YAML</h3>
    <div class="flex gap-2">
      <button hx-put="/clusters/{{ cluster_id }}/{{ resource_type }}/{{ resource_name }}/yaml"
              hx-include="#yaml-content-{{ resource_name }}"
              hx-target="#yaml-editor-{{ resource_type }}-{{ resource_name }}"
              hx-swap="outerHTML"
              hx-target-422="#yaml-errors-{{ resource_name }}"
              hx-confirm="Apply this YAML change to {{ resource_name }}?"
              class="text-xs px-3 py-1.5 bg-blue-600 text-white rounded-lg
                     hover:bg-blue-700 disabled:opacity-50">
        Apply
      </button>
      <button onclick="copyYaml('{{ resource_name }}')"
              class="text-xs px-3 py-1.5 bg-gray-200 dark:bg-gray-700 rounded-lg
                     hover:bg-gray-300 dark:hover:bg-gray-600">
        Copy
      </button>
    </div>
  </div>

  <textarea id="yaml-content-{{ resource_name }}"
            name="yaml_content"
            rows="20"
            spellcheck="false"
            class="w-full font-mono text-xs bg-gray-900 text-gray-100
                   border border-gray-700 rounded-lg p-4
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent">
{{ yaml_content }}
  </textarea>

  <div id="yaml-errors-{{ resource_name }}"
       class="mt-2 text-sm text-red-500">
  </div>
</div>
```

## 9. Destructive Action Confirmations

Use `hx-confirm` for simple confirmations. For critical operations (delete namespace,
scale to 0), use a modal pattern.

```html
<!-- Simple confirmation -->
<button hx-delete="/clusters/{{ cluster_id }}/pods/{{ pod_name }}"
        hx-target="closest tr"
        hx-swap="outerHTML swap:300ms"
        hx-confirm="Delete pod {{ pod_name }}? This action cannot be undone."
        class="text-xs text-red-600 hover:text-red-800">
  Delete
</button>

<!-- Scale to zero (extra cautious) -->
<button hx-get="/clusters/{{ cluster_id }}/workloads/deployments/{{ name }}/scale-confirm?replicas=0"
        hx-target="#modal-container"
        hx-swap="innerHTML"
        class="text-xs text-amber-600 hover:text-amber-800">
  Scale to 0
</button>

<!-- Modal container (in base.html) -->
<div id="modal-container"></div>

<!-- The confirmation modal returned by the server -->
<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
     id="confirm-modal">
  <div class="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md shadow-xl">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
      Scale {{ name }} to 0 replicas?
    </h3>
    <p class="text-sm text-gray-500 mb-6">
      This will terminate all running pods for this deployment.
      The deployment will have zero replicas until manually scaled back up.
    </p>
    <div class="flex justify-end gap-3">
      <button onclick="htmx.find('#modal-container').innerHTML = ''"
              class="px-4 py-2 text-sm rounded-lg border border-gray-300
                     hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-700">
        Cancel
      </button>
      <button hx-post="/clusters/{{ cluster_id }}/workloads/deployments/{{ name }}/scale"
              hx-vals='{"replicas": 0}'
              hx-target="#deploy-row-{{ name }}"
              hx-swap="outerHTML"
              class="px-4 py-2 text-sm rounded-lg bg-red-600 text-white
                     hover:bg-red-700">
        Scale to 0
      </button>
    </div>
  </div>
</div>
```

## 10. Toast Notifications

Triggered by the `HX-Trigger` response header for async operation feedback.

```html
<!-- In app.js -->
<script>
  // Listen for toast events triggered by HX-Trigger response header
  document.body.addEventListener('showToast', function(evt) {
    const { message, type } = evt.detail;
    const colors = {
      success: 'bg-green-500',
      error: 'bg-red-500',
      warning: 'bg-amber-500',
      info: 'bg-blue-500',
    };

    const toast = document.createElement('div');
    toast.className = `${colors[type] || colors.info} text-white px-4 py-3
                       rounded-lg shadow-lg text-sm max-w-sm
                       transform transition-all duration-300
                       translate-y-2 opacity-0`;
    toast.textContent = message;
    document.getElementById('toast-container').appendChild(toast);

    // Animate in
    requestAnimationFrame(() => {
      toast.classList.remove('translate-y-2', 'opacity-0');
    });

    // Auto-remove after 4 seconds
    setTimeout(() => {
      toast.classList.add('translate-y-2', 'opacity-0');
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  });
</script>
```

Server-side: return the `HX-Trigger` header to show a toast after an action:

```python
from fastapi.responses import HTMLResponse

response = HTMLResponse(content=html_fragment)
response.headers["HX-Trigger"] = json.dumps({
    "showToast": {"message": "Deployment scaled to 3 replicas", "type": "success"}
})
return response
```

## 11. Loading States

Use HTMX indicator classes and skeleton placeholders.

```html
<!-- Skeleton loader for a resource table -->
<div class="animate-pulse">
  {% for _ in range(5) %}
    <div class="flex items-center gap-4 py-3 border-b border-gray-100 dark:border-gray-800">
      <div class="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
      <div class="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
      <div class="h-4 w-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
      <div class="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
    </div>
  {% endfor %}
</div>
```

## 12. Search & Filtering

Debounced active search pattern for filtering resources.

```html
<!-- Active search with debounce -->
<input type="search"
       name="q"
       placeholder="Search pods by name, status, or label..."
       hx-get="/clusters/{{ cluster_id }}/pods"
       hx-trigger="input changed delay:300ms, search"
       hx-target="#pod-table-body"
       hx-swap="innerHTML"
       hx-include="[name='namespace'], [name='status_filter']"
       hx-indicator="#search-spinner"
       class="w-full rounded-lg border-gray-300 dark:border-gray-600
              dark:bg-gray-700 text-sm px-4 py-2
              focus:ring-2 focus:ring-blue-500">

<!-- Status filter pills -->
<div class="flex gap-2 mt-3" id="status-filters">
  {% for status in ["All", "Running", "Pending", "Failed", "Succeeded"] %}
    <button name="status_filter"
            value="{{ status if status != 'All' else '' }}"
            hx-get="/clusters/{{ cluster_id }}/pods"
            hx-target="#pod-table-body"
            hx-swap="innerHTML"
            hx-include="[name='namespace'], [name='q']"
            class="text-xs px-3 py-1 rounded-full border
                   {% if status_filter == status or (not status_filter and status == 'All') %}
                     bg-blue-100 border-blue-300 text-blue-700
                   {% else %}
                     bg-gray-100 border-gray-200 text-gray-600 hover:bg-gray-200
                   {% endif %}">
      {{ status }}
    </button>
  {% endfor %}
</div>
```

## CSS Essentials (app.css)

```css
/* K8s Dashboard custom styles — extend Tailwind */

/* Smooth transitions for HTMX swaps */
.htmx-swapping { opacity: 0; transition: opacity 300ms ease-out; }
.htmx-settling { opacity: 1; transition: opacity 300ms ease-in; }
.htmx-added { opacity: 0; }

/* Log viewer lines */
.log-line {
  padding: 1px 0;
  white-space: pre-wrap;
  word-break: break-all;
  border-bottom: 1px solid rgba(255,255,255,0.03);
}
.log-line:hover { background: rgba(255,255,255,0.05); }
.log-error { color: #ef4444; font-weight: 500; }

/* HTMX indicator default hidden state */
.htmx-indicator { opacity: 0; transition: opacity 200ms ease-in; }
.htmx-request .htmx-indicator, .htmx-request.htmx-indicator { opacity: 1; }

/* Dark mode transitions */
html { transition: background-color 200ms ease; }
html.dark { color-scheme: dark; }
```
