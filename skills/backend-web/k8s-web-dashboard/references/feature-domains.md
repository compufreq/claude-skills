# Feature Domains Reference

## Table of Contents

1. [Cluster Overview Dashboard](#1-cluster-overview-dashboard)
2. [Workload Management](#2-workload-management)
3. [Pod Operations](#3-pod-operations)
4. [Services & Networking](#4-services--networking)
5. [ConfigMaps & Secrets](#5-configmaps--secrets)
6. [RBAC Viewer](#6-rbac-viewer)
7. [Namespace Management](#7-namespace-management)
8. [Events & Alerts](#8-events--alerts)

Each domain section follows the same structure: endpoints, service layer pattern,
key K8s API calls, and template structure. All code uses kubernetes-asyncio for
non-blocking operations.

---

## 1. Cluster Overview Dashboard

The landing page showing cluster health at a glance — node status, resource
utilization, workload counts, and recent events.

### Endpoints

```python
@router.get("/overview")
async def cluster_overview(
    request: Request,
    cluster: ClusterConnection = Depends(get_current_cluster),
    k8s: ApiClient = Depends(get_k8s_client),
):
    """Render the cluster overview dashboard.

    Aggregates node health, resource usage, workload counts, and recent
    events into a single dashboard view. Returns a full page for direct
    navigation or an HTMX fragment for partial updates.
    """
    service = OverviewService(k8s)
    summary = await service.get_cluster_summary()

    if is_htmx(request):
        return templates.TemplateResponse("components/overview_cards.html", {
            "request": request, "summary": summary,
        })
    return templates.TemplateResponse("pages/overview.html", {
        "request": request, "summary": summary, "cluster": cluster,
    })
```

### Service Layer

```python
"""Cluster overview service aggregating health data from multiple API groups."""

from dataclasses import dataclass
from kubernetes_asyncio.client import CoreV1Api, AppsV1Api
import humanize


@dataclass
class ClusterSummary:
    """Aggregated cluster health snapshot."""
    kubernetes_version: str
    node_count: int
    nodes_ready: int
    nodes_not_ready: int
    total_cpu_capacity: str
    total_memory_capacity: str
    cpu_usage_percent: float
    memory_usage_percent: float
    pod_count: int
    deployment_count: int
    service_count: int
    namespace_count: int
    recent_events: list[dict]
    warnings: list[str]


class OverviewService:
    """Gathers cluster-wide health metrics and resource summaries."""

    def __init__(self, api_client: ApiClient) -> None:
        self.core = CoreV1Api(api_client)
        self.apps = AppsV1Api(api_client)

    async def get_cluster_summary(self) -> ClusterSummary:
        """Build a complete cluster health summary.

        Fetches nodes, pods, deployments, services, and events in parallel
        using asyncio.gather for minimal latency.
        """
        import asyncio

        nodes, pods, deploys, services, namespaces, events = await asyncio.gather(
            self.core.list_node(),
            self.core.list_pod_for_all_namespaces(limit=1000),
            self.apps.list_deployment_for_all_namespaces(),
            self.core.list_service_for_all_namespaces(),
            self.core.list_namespace(),
            self.core.list_event_for_all_namespaces(limit=20),
        )

        ready = sum(
            1 for n in nodes.items
            if any(c.type == "Ready" and c.status == "True" for c in n.status.conditions)
        )

        return ClusterSummary(
            kubernetes_version="",  # Fetched separately via VersionApi
            node_count=len(nodes.items),
            nodes_ready=ready,
            nodes_not_ready=len(nodes.items) - ready,
            total_cpu_capacity=self._sum_cpu(nodes.items),
            total_memory_capacity=self._sum_memory(nodes.items),
            cpu_usage_percent=0.0,   # Requires metrics-server
            memory_usage_percent=0.0,
            pod_count=len(pods.items),
            deployment_count=len(deploys.items),
            service_count=len(services.items),
            namespace_count=len(namespaces.items),
            recent_events=[self._format_event(e) for e in events.items[:10]],
            warnings=self._collect_warnings(nodes.items, pods.items),
        )
```

### Template Structure

```
pages/overview.html         → Full page with cards grid
components/
  overview_cards.html        → Resource count cards (poll-refreshable)
  node_status_table.html     → Node list with status indicators
  recent_events_feed.html    → Last 10 events (poll-refreshable)
  resource_usage_bars.html   → CPU/Memory utilization bars
```

---

## 2. Workload Management

CRUD operations for Deployments, StatefulSets, DaemonSets, Jobs, and CronJobs.
Supports scaling, restart (rollout restart), and viewing rollout status.

### Endpoints

```python
@router.get("/workloads")
async def list_workloads(request, namespace, k8s, workload_type="deployments"):
    """List workloads in a namespace, filterable by type."""

@router.get("/workloads/deployments/{name}")
async def deployment_detail(request, namespace, name, k8s):
    """Deployment detail with replica status, conditions, and revision history."""

@router.post("/workloads/deployments/{name}/scale")
async def scale_deployment(request, namespace, name, replicas: int, k8s):
    """Scale a deployment. Returns updated deployment row as HTMX fragment."""

@router.post("/workloads/deployments/{name}/restart")
async def restart_deployment(request, namespace, name, k8s):
    """Trigger a rollout restart by patching the pod template annotation."""
```

### Key K8s API Operations

```python
"""Workload management service for Deployments, StatefulSets, etc."""

from datetime import datetime, timezone
from kubernetes_asyncio.client import AppsV1Api, BatchV1Api


class WorkloadService:
    """Manages Kubernetes workload resources."""

    def __init__(self, api_client: ApiClient) -> None:
        self.apps = AppsV1Api(api_client)
        self.batch = BatchV1Api(api_client)

    async def scale_deployment(
        self, name: str, namespace: str, replicas: int
    ) -> dict:
        """Scale a deployment to the specified replica count.

        Args:
            name: Deployment name.
            namespace: Target namespace.
            replicas: Desired replica count.

        Returns:
            Updated deployment status dict.
        """
        body = {"spec": {"replicas": replicas}}
        result = await self.apps.patch_namespaced_deployment_scale(
            name=name, namespace=namespace, body=body,
        )
        return self._format_deployment(result)

    async def restart_deployment(self, name: str, namespace: str) -> dict:
        """Trigger a rollout restart by patching the pod template annotation.

        This is equivalent to `kubectl rollout restart deployment/<name>`.
        """
        now = datetime.now(timezone.utc).isoformat()
        body = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt": now
                        }
                    }
                }
            }
        }
        result = await self.apps.patch_namespaced_deployment(
            name=name, namespace=namespace, body=body,
        )
        return self._format_deployment(result)
```

### Template Features

- Resource table with columns: Name, Namespace, Ready (replicas), Up-to-date, Age, Actions
- Action buttons: Scale (inline input), Restart (with confirmation), View YAML
- Status badges: green (available), yellow (progressing), red (degraded)
- Quick-scale input using `hx-post` with `hx-include` to send the new replica count

---

## 3. Pod Operations

The most feature-rich domain. Covers listing, detail view, live log streaming,
and container exec.

### Endpoints

```python
@router.get("/pods")
async def list_pods(request, namespace, k8s, status_filter=None, search=None):
    """List pods with optional status and name filtering."""

@router.get("/pods/{name}")
async def pod_detail(request, namespace, name, k8s):
    """Pod detail: containers, conditions, events, labels, volumes."""

@router.get("/pods/{name}/logs")
async def pod_logs_page(request, namespace, name, container=None):
    """Render the log viewer page with SSE connection setup."""

@router.get("/pods/{name}/logs/stream")
async def pod_logs_stream(namespace, name, container, k8s, tail_lines=100):
    """SSE endpoint streaming live pod logs."""

@router.websocket("/pods/{name}/exec")
async def pod_exec(ws, namespace, name, container, k8s):
    """WebSocket endpoint for interactive container exec."""
```

### Live Log Streaming (SSE)

This is one of the most valuable features. Use FastAPI's StreamingResponse with the
K8s watch API to stream logs in real-time.

```python
"""Pod log streaming via Server-Sent Events.

Uses the K8s watch API to follow container logs and streams them
as SSE events. Each log line becomes an SSE data event that HTMX
appends to the log viewer div.
"""

import asyncio
from fastapi.responses import StreamingResponse
from kubernetes_asyncio.client import CoreV1Api
from kubernetes_asyncio import watch as k8s_watch


async def stream_pod_logs(
    api_client: ApiClient,
    namespace: str,
    pod_name: str,
    container: str | None = None,
    tail_lines: int = 100,
):
    """Async generator yielding SSE-formatted pod log lines.

    Args:
        api_client: Authenticated K8s ApiClient.
        namespace: Pod namespace.
        pod_name: Pod name.
        container: Specific container (required for multi-container pods).
        tail_lines: Number of historical lines to show initially.

    Yields:
        SSE-formatted strings: 'data: <html-escaped-line>\\n\\n'
    """
    core = CoreV1Api(api_client)
    w = k8s_watch.Watch()

    kwargs = {
        "name": pod_name,
        "namespace": namespace,
        "follow": True,
        "tail_lines": tail_lines,
        "timestamps": True,
        "_preload_content": False,
    }
    if container:
        kwargs["container"] = container

    try:
        async for line in w.stream(core.read_namespaced_pod_log, **kwargs):
            # Escape HTML to prevent XSS in log output
            import html
            escaped = html.escape(str(line))
            yield f"data: <div class=\"log-line\">{escaped}</div>\n\n"
    except asyncio.CancelledError:
        await w.close()
        raise
    except Exception as e:
        yield f"data: <div class=\"log-line log-error\">Stream error: {html.escape(str(e))}</div>\n\n"
    finally:
        await w.close()


@router.get("/pods/{name}/logs/stream")
async def pod_logs_sse(
    name: str,
    namespace: str = Query(...),
    container: str = Query(None),
    tail_lines: int = Query(100),
    k8s: ApiClient = Depends(get_k8s_client),
):
    """SSE endpoint for live pod log streaming."""
    return StreamingResponse(
        stream_pod_logs(k8s, namespace, name, container, tail_lines),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

### Container Exec (WebSocket)

```python
"""WebSocket-based container exec for interactive terminal sessions.

Bridges a browser WebSocket to the K8s exec API, forwarding stdin/stdout
between the user's terminal widget and the container process.
"""

from kubernetes_asyncio.client import CoreV1Api
from kubernetes_asyncio.stream import WsApiClient


async def exec_in_container(
    ws: WebSocket,
    api_client: ApiClient,
    namespace: str,
    pod_name: str,
    container: str,
    command: list[str] = None,
):
    """Bridge browser WebSocket to K8s container exec.

    Args:
        ws: FastAPI WebSocket connection from the browser.
        api_client: Authenticated K8s ApiClient.
        namespace: Pod namespace.
        pod_name: Pod name.
        container: Container to exec into.
        command: Command to run. Defaults to ['/bin/sh'].
    """
    command = command or ["/bin/sh"]
    core = CoreV1Api(api_client)

    resp = await core.connect_get_namespaced_pod_exec(
        name=pod_name,
        namespace=namespace,
        container=container,
        command=command,
        stderr=True,
        stdin=True,
        stdout=True,
        tty=True,
        _preload_content=False,
    )

    # Bidirectional forwarding
    import asyncio

    async def forward_stdin():
        async for msg in ws.iter_text():
            resp.write_stdin(msg)

    async def forward_stdout():
        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stdout():
                await ws.send_text(resp.read_stdout())
            if resp.peek_stderr():
                await ws.send_text(resp.read_stderr())
            await asyncio.sleep(0.1)

    await asyncio.gather(forward_stdin(), forward_stdout())
```

---

## 4. Services & Networking

Read-only views for Services, Ingresses, and NetworkPolicies. Shows endpoint
mappings, external IPs, and ingress rules.

### Endpoints

```python
@router.get("/services")
async def list_services(request, namespace, k8s):
    """List services with type, cluster IP, external IP, ports."""

@router.get("/services/{name}")
async def service_detail(request, namespace, name, k8s):
    """Service detail: endpoints, selector, ports, associated pods."""

@router.get("/ingresses")
async def list_ingresses(request, namespace, k8s):
    """List ingresses with hosts, paths, backends, TLS status."""

@router.get("/networkpolicies")
async def list_network_policies(request, namespace, k8s):
    """List NetworkPolicies with ingress/egress rule summaries."""
```

### Key Data Transformations

Services need special formatting for the UI:
- Map service type (ClusterIP, NodePort, LoadBalancer, ExternalName) to display styles
- Resolve endpoints to show actual pod IPs behind each service
- Format port mappings as `port:targetPort/protocol` (e.g., `80:8080/TCP`)
- For LoadBalancer, show external IP/hostname with a link

Ingresses:
- Parse rules into a readable table: Host → Path → Backend Service:Port
- Show TLS status (icon) per host
- Show ingress class annotation

---

## 5. ConfigMaps & Secrets

CRUD for ConfigMaps with full data visibility. Secrets are read-only with masked
values and explicit reveal.

### Endpoints

```python
@router.get("/configmaps")
async def list_configmaps(request, namespace, k8s):
    """List ConfigMaps with data key count and age."""

@router.get("/configmaps/{name}")
async def configmap_detail(request, namespace, name, k8s):
    """Show ConfigMap data with editable key-value pairs."""

@router.put("/configmaps/{name}")
async def update_configmap(request, namespace, name, k8s, data: dict):
    """Update a ConfigMap's data. Returns updated detail fragment."""

@router.get("/secrets")
async def list_secrets(request, namespace, k8s, type_filter=None):
    """List Secrets with type, key count, age. Values always masked."""

@router.get("/secrets/{name}")
async def secret_detail(request, namespace, name, k8s):
    """Show Secret with masked values. Each value has a 'reveal' button."""

@router.get("/secrets/{name}/reveal/{key}")
async def reveal_secret_value(request, namespace, name, key, k8s):
    """Reveal a single Secret value. Requires explicit user action."""
```

### Secret Masking Pattern

Never send secret values in the initial HTML. The reveal flow:
1. Initial render shows `***masked***` for each value
2. Each value has an HTMX "Reveal" button: `hx-get="/secrets/{name}/reveal/{key}"`
3. The reveal endpoint returns the base64-decoded value in a `<code>` block
4. The button is replaced with the revealed value + a "Hide" button
5. The "Hide" button is pure client-side (just toggles visibility, no request)

---

## 6. RBAC Viewer

Read-only visualization of Roles, ClusterRoles, and their bindings. Helps answer
"who can do what?" across the cluster.

### Endpoints

```python
@router.get("/rbac/roles")
async def list_roles(request, namespace, k8s):
    """List namespace-scoped Roles with rule summaries."""

@router.get("/rbac/clusterroles")
async def list_cluster_roles(request, k8s):
    """List ClusterRoles with rule summaries."""

@router.get("/rbac/roles/{name}/rules")
async def role_rules(request, namespace, name, k8s):
    """Expanded view of a Role's rules: apiGroups × resources × verbs."""

@router.get("/rbac/bindings")
async def list_bindings(request, namespace, k8s):
    """List RoleBindings and ClusterRoleBindings with subject details."""
```

### Rule Formatting

RBAC rules are complex nested structures. Format them as tables:
- Columns: API Groups, Resources, Verbs
- Color-code verbs: read verbs (get, list, watch) in green, write verbs
  (create, update, patch) in yellow, destructive verbs (delete, deletecollection)
  in red, wildcard (*) in red bold

---

## 7. Namespace Management

Namespace listing, creation, resource quota viewing, and context switching.
The namespace selector affects all other views via an OOB swap.

### Endpoints

```python
@router.get("/namespaces")
async def list_namespaces(request, k8s):
    """List all namespaces with status, age, labels, resource quotas."""

@router.post("/namespaces")
async def create_namespace(request, name: str, labels: dict, k8s):
    """Create a new namespace. Returns updated namespace list."""

@router.get("/namespaces/{name}/quotas")
async def namespace_quotas(request, name, k8s):
    """Show ResourceQuotas and LimitRanges for a namespace."""

@router.post("/namespaces/switch")
async def switch_namespace(request, namespace: str):
    """Switch the active namespace. Returns OOB updates for all panels."""
```

### Namespace Switching Pattern

When the user switches namespaces, every resource view on the page needs to update.
Use HTMX out-of-band (OOB) swaps to update all panels simultaneously:

```python
@router.post("/namespaces/switch")
async def switch_namespace(request: Request, namespace: str = Form(...)):
    """Switch namespace and return OOB fragments for all visible panels.

    The response contains the updated namespace selector plus OOB fragments
    that update the pod table, deployment table, and other visible panels
    without a full page reload.
    """
    # Store selected namespace in session
    request.session["namespace"] = namespace

    # Return main content + OOB updates
    return templates.TemplateResponse("components/namespace_switch_response.html", {
        "request": request,
        "namespace": namespace,
        # Each panel will be fetched fresh via the included OOB triggers
    })
```

---

## 8. Events & Alerts

Real-time cluster event streaming via WebSocket. Shows event type, reason,
involved object, message, and timestamp.

### Endpoints

```python
@router.get("/events")
async def events_page(request, namespace, k8s):
    """Render the events page with WebSocket connection setup."""

@router.websocket("/events/stream")
async def events_stream(ws, namespace, k8s):
    """WebSocket endpoint streaming real-time cluster events."""
```

### Event Streaming (WebSocket)

```python
"""Real-time K8s event streaming via WebSocket.

Watches the K8s Events API and pushes HTML fragments to connected
clients. Supports namespace filtering and event type filtering
(Normal, Warning) via WebSocket messages from the client.
"""

from kubernetes_asyncio import watch as k8s_watch
from kubernetes_asyncio.client import CoreV1Api


async def watch_events(
    ws: WebSocket,
    api_client: ApiClient,
    namespace: str | None = None,
):
    """Stream cluster events as HTML fragments over WebSocket.

    The client can send JSON filter commands:
    {"type": "filter", "namespace": "kube-system", "severity": "Warning"}

    Args:
        ws: FastAPI WebSocket connection.
        api_client: Authenticated K8s ApiClient.
        namespace: Initial namespace filter. None = all namespaces.
    """
    core = CoreV1Api(api_client)
    w = k8s_watch.Watch()

    current_ns = namespace

    async def watch_loop():
        nonlocal current_ns
        watch_fn = (
            core.list_namespaced_event if current_ns
            else core.list_event_for_all_namespaces
        )
        kwargs = {"namespace": current_ns} if current_ns else {}

        async for event in w.stream(watch_fn, **kwargs):
            ev = event["object"]
            html = render_event_row(ev)
            await ws.send_text(html)

    import asyncio

    watch_task = asyncio.create_task(watch_loop())

    try:
        # Listen for filter commands from the client
        async for message in ws.iter_json():
            if message.get("type") == "filter":
                current_ns = message.get("namespace")
                watch_task.cancel()
                try:
                    await watch_task
                except asyncio.CancelledError:
                    pass
                watch_task = asyncio.create_task(watch_loop())
    except WebSocketDisconnect:
        watch_task.cancel()
    finally:
        await w.close()


def render_event_row(event) -> str:
    """Format a K8s Event as an HTML table row.

    Color-codes by type: Normal (blue), Warning (amber).
    """
    import html as html_mod
    type_class = "text-amber-500" if event.type == "Warning" else "text-blue-500"
    return f"""
    <tr id="event-{event.metadata.uid}" hx-swap-oob="afterbegin:#events-body">
      <td class="{type_class} font-semibold">{event.type}</td>
      <td>{html_mod.escape(event.reason or "")}</td>
      <td>{html_mod.escape(event.involved_object.kind)}/{html_mod.escape(event.involved_object.name)}</td>
      <td class="text-sm">{html_mod.escape(event.message or "")}</td>
      <td class="text-xs text-gray-500">{event.metadata.creation_timestamp}</td>
    </tr>
    """
```

### Template Features

- Auto-scrolling event feed with pause button
- Event type filter (Normal, Warning, All)
- Namespace filter via the global namespace selector
- Event count badges by severity
- Click an event to see full details in a slide-over panel
