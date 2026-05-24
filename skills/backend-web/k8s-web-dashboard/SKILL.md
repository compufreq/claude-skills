---
name: k8s-web-dashboard
description: >
  Build professional Kubernetes cluster monitoring and management web apps using FastAPI +
  HTMX + the official Kubernetes Python client. Connects to any cluster (on-prem, EKS, GKE,
  AKS, minikube/kind/k3s) via kubeconfig or in-cluster ServiceAccount. Covers cluster
  overview, workload management, pod operations (live logs via SSE, exec), services &
  networking, ConfigMaps & Secrets, RBAC, namespaces, and real-time events. Multi-cluster
  switching. Produces complete runnable projects or modular features. Use whenever the user
  mentions Kubernetes dashboard, K8s web UI, cluster monitoring tool, pod log viewer, kubectl
  web interface, K8s admin panel, cluster health dashboard, RBAC viewer, K8s event stream,
  container log viewer, or building a web tool for managing Kubernetes clusters. Also trigger
  for "web UI for my cluster", "browser-based kubectl", "self-hosted K8s dashboard", or
  "alternative to Lens/Headlamp".
---

# Kubernetes Web Dashboard Builder

You build professional, production-ready Kubernetes management web applications using
FastAPI (backend) + HTMX (frontend) + the official Kubernetes Python client. The result
is a lightweight, real-time cluster dashboard that runs anywhere — no heavy JS frameworks,
no complex build pipelines. Server-rendered HTML fragments with live updates via SSE and
WebSockets.

## Prerequisite Skills

This skill orchestrates two existing skills and adds Kubernetes-specific integration:

1. **fastapi-backend** — Follow its project structure, async patterns, Pydantic schemas,
   error handling, and deployment patterns for all backend code.
2. **htmx-developer** — Follow its HTMX 2.x patterns, SSE/WebSocket extensions, swap
   strategies, and Tailwind integration for all frontend code.

Read both skills before generating code. This skill adds the Kubernetes layer on top:
how to connect to clusters, how to map K8s API resources to FastAPI endpoints, and how
to render cluster state as interactive HTMX-driven HTML.

## Core Dependencies (in addition to fastapi-backend deps)

```toml
dependencies = [
    # ... all fastapi-backend deps ...
    "kubernetes>=31.0.0",          # Official K8s Python client (async support)
    "kubernetes-asyncio>=31.0.0",  # Async K8s client for watch streams
    "pyyaml>=6.0.0",               # YAML parsing for manifests
    "humanize>=4.11.0",            # Human-readable sizes, times
    "cachetools>=5.5.0",           # TTL caching for expensive API calls
]
```

## Architecture Overview

```
Browser (HTMX + Tailwind CSS)
  │
  ├── GET /clusters/{id}/pods      → HTML fragment (pod table)
  ├── GET /clusters/{id}/pod/{name}/logs  → SSE stream (live logs)
  ├── WS  /clusters/{id}/events    → WebSocket (real-time events)
  ├── POST /clusters/{id}/deploy/{name}/scale  → HTML fragment (updated row)
  └── ...
  │
FastAPI Backend
  │
  ├── api/v1/          → Route handlers (return HTML via Jinja2)
  ├── services/        → Business logic (K8s operations)
  ├── k8s/             → Kubernetes client management
  │   ├── client.py    → Multi-cluster client factory
  │   ├── auth.py      → Auth strategies (kubeconfig, SA, cloud)
  │   └── watch.py     → Async watch stream helpers
  ├── templates/        → Jinja2 HTML templates (HTMX fragments)
  │   ├── base.html
  │   ├── components/   → Reusable HTMX partials
  │   └── pages/        → Full page templates
  └── static/           → Tailwind CSS, HTMX JS, icons
  │
Kubernetes API Server(s)
  ├── On-prem cluster
  ├── EKS / GKE / AKS
  └── Local (minikube / kind / k3s)
```

## Project Structure

Extend the fastapi-backend enforced structure with these Kubernetes-specific additions:

```
k8s-dashboard/
├── app/
│   ├── main.py
│   ├── config.py              # Add: KUBECONFIG_PATH, CLUSTER_CONFIGS, IN_CLUSTER
│   ├── dependencies.py        # Add: get_k8s_client, get_current_cluster
│   ├── k8s/                   # NEW: Kubernetes integration layer
│   │   ├── __init__.py
│   │   ├── client.py          # Multi-cluster client factory & lifecycle
│   │   ├── auth.py            # Auth strategies: kubeconfig, SA, cloud tokens
│   │   ├── watch.py           # Async watch/stream helpers for SSE
│   │   └── resources.py       # K8s resource type registry & helpers
│   ├── api/v1/
│   │   ├── clusters.py        # Cluster connection management
│   │   ├── overview.py        # Cluster overview dashboard
│   │   ├── workloads.py       # Deployments, StatefulSets, DaemonSets, Jobs
│   │   ├── pods.py            # Pod list, detail, logs (SSE), exec (WS)
│   │   ├── networking.py      # Services, Ingresses, NetworkPolicies
│   │   ├── config.py          # ConfigMaps, Secrets
│   │   ├── rbac.py            # Roles, ClusterRoles, Bindings
│   │   ├── namespaces.py      # Namespace management, ResourceQuotas
│   │   ├── events.py          # Real-time event stream (WebSocket)
│   │   └── health.py          # App health + cluster connectivity check
│   ├── services/
│   │   ├── cluster_service.py
│   │   ├── workload_service.py
│   │   ├── pod_service.py
│   │   ├── network_service.py
│   │   ├── config_service.py
│   │   ├── rbac_service.py
│   │   ├── namespace_service.py
│   │   └── event_service.py
│   ├── schemas/               # Pydantic models for K8s resources
│   │   ├── cluster.py
│   │   ├── workload.py
│   │   ├── pod.py
│   │   ├── network.py
│   │   └── ...
│   ├── templates/             # Jinja2 + HTMX templates
│   │   ├── base.html          # Shell: nav, cluster switcher, notification area
│   │   ├── components/        # Reusable HTMX partials
│   │   │   ├── resource_table.html
│   │   │   ├── status_badge.html
│   │   │   ├── log_viewer.html
│   │   │   ├── yaml_editor.html
│   │   │   ├── cluster_switcher.html
│   │   │   ├── namespace_selector.html
│   │   │   ├── pagination.html
│   │   │   └── toast.html
│   │   └── pages/
│   │       ├── overview.html
│   │       ├── workloads.html
│   │       ├── pods.html
│   │       ├── pod_detail.html
│   │       ├── services.html
│   │       ├── configmaps.html
│   │       ├── secrets.html
│   │       ├── rbac.html
│   │       ├── namespaces.html
│   │       └── events.html
│   └── static/
│       ├── css/
│       │   └── app.css        # Tailwind + custom K8s status colors
│       └── js/
│           └── app.js         # Minimal JS: theme toggle, toast handler
├── docker-compose.yml         # Dashboard + optional Redis for caching
├── Dockerfile
└── kubeconfig/                # Mount point for kubeconfig files
```

## Cluster Connectivity

This is the critical integration piece. Read `references/cluster-connectivity.md` for
the full implementation guide covering all auth strategies.

### Supported Connection Methods

1. **Kubeconfig file** — Default `~/.kube/config` or custom path. Supports multiple
   contexts for multi-cluster.
2. **In-cluster ServiceAccount** — Auto-detected when running inside a K8s pod.
   Uses mounted token at `/var/run/secrets/kubernetes.io/serviceaccount/`.
3. **Cloud provider auth** — EKS (IAM/IRSA), GKE (Workload Identity), AKS (Azure AD).
   Handles token refresh automatically.
4. **Uploaded kubeconfig** — User uploads a kubeconfig via the UI for ad-hoc connections.

### Multi-Cluster Client Factory Pattern

```python
"""Kubernetes client factory managing connections to multiple clusters.

Each cluster gets its own ApiClient instance with the appropriate auth
configuration. Clients are created lazily and cached with health checks.
"""

from dataclasses import dataclass, field
from kubernetes_asyncio import client, config
from kubernetes_asyncio.client import ApiClient


@dataclass
class ClusterConnection:
    """Represents a connection to a single Kubernetes cluster."""
    id: str
    name: str
    context: str | None = None
    kubeconfig_path: str | None = None
    in_cluster: bool = False
    api_client: ApiClient | None = field(default=None, repr=False)
    is_healthy: bool = False


class K8sClientFactory:
    """Creates and caches async Kubernetes API clients per cluster.

    Supports kubeconfig contexts, in-cluster auth, and uploaded configs.
    Performs health checks via the /version endpoint before returning clients.
    """

    def __init__(self) -> None:
        self._connections: dict[str, ClusterConnection] = {}

    async def get_client(self, cluster_id: str) -> ApiClient:
        """Get or create an authenticated ApiClient for a cluster."""
        conn = self._connections.get(cluster_id)
        if not conn:
            raise ClusterNotFoundError(cluster_id)
        if not conn.api_client:
            conn.api_client = await self._create_client(conn)
            conn.is_healthy = await self._health_check(conn.api_client)
        return conn.api_client

    async def _create_client(self, conn: ClusterConnection) -> ApiClient:
        """Build an ApiClient using the connection's auth strategy."""
        if conn.in_cluster:
            config.load_incluster_config()
            return ApiClient()
        kubeconfig = conn.kubeconfig_path or str(Path.home() / ".kube" / "config")
        await config.load_kube_config(
            config_file=kubeconfig,
            context=conn.context,
        )
        return ApiClient()

    async def _health_check(self, api_client: ApiClient) -> bool:
        """Verify cluster connectivity via the /version endpoint."""
        try:
            v1 = client.VersionApi(api_client)
            await v1.get_code()
            return True
        except Exception:
            return False
```

## Feature Domains

There are eight feature domains the skill covers. Read `references/feature-domains.md`
for detailed endpoint designs, service patterns, and template structures for each domain.

### Quick Reference

| Domain | Key Endpoints | Real-time | Reference Section |
|--------|--------------|-----------|-------------------|
| Cluster Overview | `GET /overview` | Polling (5s) | §1 |
| Workloads | `GET/POST /workloads/*` | Polling | §2 |
| Pods | `GET /pods`, `GET /pods/{name}/logs` | SSE (logs) | §3 |
| Networking | `GET /services`, `GET /ingresses` | Polling | §4 |
| Config & Secrets | `GET/POST /configmaps`, `/secrets` | — | §5 |
| RBAC | `GET /roles`, `/clusterroles` | — | §6 |
| Namespaces | `GET/POST /namespaces` | — | §7 |
| Events | `WS /events/stream` | WebSocket | §8 |

## HTMX Patterns for Kubernetes UIs

Read `references/ui-patterns.md` for comprehensive HTMX pattern recipes specific to
Kubernetes dashboard UIs, including:

- Live log streaming via SSE with auto-scroll and pause
- Real-time event feed via WebSocket
- Resource tables with polling refresh, sort, filter, and pagination
- Namespace selector with OOB updates across all panels
- Cluster switcher that reloads the entire dashboard context
- Status badges with color-coded K8s resource phases
- YAML editor with server-side validation
- Confirmation dialogs for destructive operations (delete, scale to 0)
- Toast notifications for async operation results

## Output Modes

Adapt output to what the user asks for:

### Full Project Mode
When the user asks for a complete dashboard or management tool, generate the full
project structure above with all files. Include:
- Working `docker-compose.yml` with the app and optional Redis
- `Dockerfile` with multi-stage build
- `.env.example` with all configuration options
- `README.md` with setup instructions
- At minimum, implement the cluster overview + one feature domain the user emphasizes

### Modular Feature Mode
When the user asks for a specific feature (e.g., "build me a pod log viewer"), generate
only the relevant pieces:
- The route handler(s)
- The service class
- The Jinja2 template(s) and HTMX fragments
- Integration instructions showing where to mount in an existing project

### Extending an Existing Project
When the user has an existing K8s dashboard and wants to add a feature domain, follow
the established patterns and add the new domain files without regenerating everything.

## Critical Implementation Rules

1. **Always use kubernetes-asyncio, not kubernetes (sync)**. FastAPI is async-first and
   blocking K8s calls will stall the event loop. The only exception is simple scripts or
   CLI tools where async isn't needed.

2. **Never expose Secrets in plain text by default**. Always mask Secret values in the UI
   (`***`) and require an explicit "reveal" action with confirmation. The reveal action
   should be a separate HTMX request so the value isn't in the initial HTML.

3. **Namespace-scoped by default**. All resource views should be namespace-scoped with a
   namespace selector. Cluster-scoped views (Nodes, ClusterRoles, PVs) are separate
   sections.

4. **Handle API errors gracefully**. The K8s API returns 403 (RBAC denied), 404 (not found),
   409 (conflict), 422 (invalid). Map these to user-friendly HTML error fragments using
   the response-targets HTMX extension.

5. **Cache expensive calls**. Node lists, namespace lists, and cluster version info change
   rarely. Use `cachetools.TTLCache` with 30-60s TTL to avoid hammering the API server.

6. **SSE for logs, WebSocket for events, polling for resource lists**. Match the real-time
   strategy to the data pattern:
   - Pod logs: SSE (unidirectional server→client stream)
   - Cluster events: WebSocket (allows filtering commands from the client)
   - Resource lists: HTMX polling (`hx-trigger="every 5s"`) — simple and sufficient

7. **Jinja2 templates live in `app/templates/`**. Configure FastAPI with:
   ```python
   from fastapi.templating import Jinja2Templates
   templates = Jinja2Templates(directory="app/templates")
   ```
   Return `TemplateResponse` for full pages, raw `HTMLResponse` for HTMX fragments.

8. **Detect HTMX requests** to return fragments vs full pages:
   ```python
   def is_htmx(request: Request) -> bool:
       return request.headers.get("HX-Request") == "true"
   ```

## Workflow

When the user asks to build a K8s management tool:

1. **Read prerequisite skills**: Read `fastapi-backend` and `htmx-developer` SKILL.md files.
2. **Read relevant references**: Based on the request, read the appropriate reference files
   from this skill.
3. **Determine output mode**: Full project, modular feature, or extension.
4. **Determine cluster connectivity**: What auth method(s) does the user need?
5. **Determine feature scope**: Which of the 8 domains does the request cover?
6. **Generate code** following all three skills' patterns simultaneously:
   - FastAPI project structure and async patterns from fastapi-backend
   - HTMX 2.x patterns and Tailwind styling from htmx-developer
   - Kubernetes connectivity and resource mapping from this skill
7. **Include deployment artifacts**: Dockerfile, docker-compose.yml, .env.example
8. **Test connectivity**: If the user has a live cluster, offer to test the /health endpoint

## Reference Files

| File | When to Read |
|------|-------------|
| `references/cluster-connectivity.md` | Implementing cluster auth, multi-cluster, cloud provider tokens |
| `references/feature-domains.md` | Implementing any of the 8 feature domains (endpoints, services, templates) |
| `references/ui-patterns.md` | HTMX recipes for K8s-specific UI patterns (log viewer, event stream, YAML editor) |
