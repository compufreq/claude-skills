# Cluster Connectivity Reference

## Table of Contents

1. [Kubeconfig-Based Connections](#1-kubeconfig-based-connections)
2. [In-Cluster ServiceAccount](#2-in-cluster-serviceaccount)
3. [Cloud Provider Auth](#3-cloud-provider-auth)
4. [Uploaded Kubeconfig](#4-uploaded-kubeconfig)
5. [Multi-Cluster Management](#5-multi-cluster-management)
6. [Client Lifecycle & Health Checks](#6-client-lifecycle--health-checks)
7. [Configuration Schema](#7-configuration-schema)
8. [Docker Compose & Kubeconfig Mounting](#8-docker-compose--kubeconfig-mounting)

---

## 1. Kubeconfig-Based Connections

The most common method. The dashboard reads `~/.kube/config` (or a custom path) and
lists available contexts as connectable clusters.

```python
"""Kubeconfig loader that discovers clusters from a kubeconfig file.

Parses the kubeconfig to extract cluster contexts and creates
authenticated ApiClient instances per context.
"""

from pathlib import Path
from kubernetes_asyncio import config
from kubernetes_asyncio.client import ApiClient
from kubernetes_asyncio.config.kube_config import KubeConfigLoader
import yaml


async def discover_contexts(kubeconfig_path: str | None = None) -> list[dict]:
    """Parse a kubeconfig file and return available contexts.

    Args:
        kubeconfig_path: Path to kubeconfig. Defaults to ~/.kube/config.

    Returns:
        List of dicts with context name, cluster name, user, and namespace.
    """
    path = kubeconfig_path or str(Path.home() / ".kube" / "config")
    with open(path) as f:
        kube_config = yaml.safe_load(f)

    contexts = []
    current = kube_config.get("current-context", "")
    for ctx in kube_config.get("contexts", []):
        contexts.append({
            "name": ctx["name"],
            "cluster": ctx["context"].get("cluster", ""),
            "user": ctx["context"].get("user", ""),
            "namespace": ctx["context"].get("namespace", "default"),
            "is_current": ctx["name"] == current,
        })
    return contexts


async def client_from_context(
    context: str,
    kubeconfig_path: str | None = None,
) -> ApiClient:
    """Create an async ApiClient for a specific kubeconfig context.

    Args:
        context: The kubeconfig context name to use.
        kubeconfig_path: Optional path to kubeconfig file.

    Returns:
        Configured ApiClient ready for API calls.
    """
    path = kubeconfig_path or str(Path.home() / ".kube" / "config")
    await config.load_kube_config(config_file=path, context=context)
    return ApiClient()
```

## 2. In-Cluster ServiceAccount

When the dashboard runs inside a Kubernetes pod, it uses the mounted ServiceAccount
token. This is auto-detected by checking for the token file.

```python
"""In-cluster authentication using mounted ServiceAccount credentials.

The kubelet mounts the token at a well-known path. The kubernetes-asyncio
library handles token refresh for projected service account tokens.
"""

from pathlib import Path
from kubernetes_asyncio import config
from kubernetes_asyncio.client import ApiClient

SA_TOKEN_PATH = Path("/var/run/secrets/kubernetes.io/serviceaccount/token")
SA_CA_PATH = Path("/var/run/secrets/kubernetes.io/serviceaccount/ca.crt")
SA_NS_PATH = Path("/var/run/secrets/kubernetes.io/serviceaccount/namespace")


def is_in_cluster() -> bool:
    """Detect if running inside a Kubernetes pod."""
    return SA_TOKEN_PATH.exists() and SA_CA_PATH.exists()


async def client_from_serviceaccount() -> ApiClient:
    """Create an ApiClient using in-cluster ServiceAccount credentials.

    Raises:
        FileNotFoundError: If not running inside a Kubernetes pod.
    """
    if not is_in_cluster():
        raise FileNotFoundError("Not running in-cluster; SA token not found")
    config.load_incluster_config()
    return ApiClient()


def get_current_namespace() -> str:
    """Read the namespace this pod is running in."""
    if SA_NS_PATH.exists():
        return SA_NS_PATH.read_text().strip()
    return "default"
```

### Required RBAC for the Dashboard ServiceAccount

When deploying in-cluster, create a ClusterRole with read access to the resources
the dashboard needs:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: k8s-dashboard
  namespace: k8s-dashboard
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: k8s-dashboard-viewer
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log", "services", "endpoints", "configmaps",
                "secrets", "namespaces", "nodes", "events",
                "persistentvolumeclaims", "resourcequotas"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments", "statefulsets", "daemonsets", "replicasets"]
    verbs: ["get", "list", "watch", "patch", "update"]
  - apiGroups: ["batch"]
    resources: ["jobs", "cronjobs"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["networking.k8s.io"]
    resources: ["ingresses", "networkpolicies"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["rbac.authorization.k8s.io"]
    resources: ["roles", "clusterroles", "rolebindings", "clusterrolebindings"]
    verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: k8s-dashboard-viewer-binding
subjects:
  - kind: ServiceAccount
    name: k8s-dashboard
    namespace: k8s-dashboard
roleRef:
  kind: ClusterRole
  name: k8s-dashboard-viewer
  apiGroup: rbac.authorization.k8s.io
```

For management operations (scale, restart, delete), add a separate ClusterRole with
write permissions and bind it only when the user needs management capabilities.

## 3. Cloud Provider Auth

### EKS (AWS)

EKS uses IAM-based authentication. The dashboard needs AWS credentials and generates
a presigned token via STS.

```python
"""EKS authentication using AWS STS presigned URLs.

Generates a token compatible with aws-iam-authenticator by creating
a presigned GetCallerIdentity URL with the correct cluster header.
"""

import base64
import boto3
from botocore.signers import RequestSigner
from kubernetes_asyncio.client import ApiClient, Configuration


def get_eks_token(cluster_name: str, region: str = "eu-central-1") -> str:
    """Generate a bearer token for EKS authentication.

    Uses the STS presigned URL approach (same as aws-iam-authenticator).

    Args:
        cluster_name: Name of the EKS cluster.
        region: AWS region where the cluster runs.

    Returns:
        Bearer token string starting with 'k8s-aws-v1.'
    """
    session = boto3.Session()
    sts = session.client("sts", region_name=region)
    service_id = sts.meta.service_model.service_id

    signer = RequestSigner(service_id, region, "sts",
                           "v4", session.get_credentials(), session.events)

    params = {
        "method": "GET",
        "url": f"https://sts.{region}.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15",
        "body": {},
        "headers": {"x-k8s-aws-id": cluster_name},
        "context": {},
    }
    signed_url = signer.generate_presigned_url(
        params, region_name=region, expires_in=60, operation_name=""
    )
    return "k8s-aws-v1." + base64.urlsafe_b64encode(
        signed_url.encode("utf-8")
    ).decode("utf-8").rstrip("=")
```

### GKE (Google Cloud)

```python
"""GKE authentication using Google Cloud credentials.

Uses the google-auth library to obtain access tokens for the
Kubernetes API server.
"""

import google.auth
import google.auth.transport.requests


def get_gke_token() -> str:
    """Get a GKE access token from application default credentials."""
    credentials, project = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(google.auth.transport.requests.Request())
    return credentials.token
```

### AKS (Azure)

```python
"""AKS authentication using Azure Identity credentials."""

from azure.identity import DefaultAzureCredential


def get_aks_token() -> str:
    """Get an AKS access token from Azure default credentials."""
    credential = DefaultAzureCredential()
    token = credential.get_token("6dae42f8-4368-4678-94ff-3960e28e3630/.default")
    return token.token
```

## 4. Uploaded Kubeconfig

Allow users to upload a kubeconfig file through the dashboard UI for ad-hoc connections.

```python
"""Handle kubeconfig file uploads for ad-hoc cluster connections.

Validates uploaded kubeconfig content, extracts contexts, and stores
the file securely with restricted permissions.
"""

import tempfile
from pathlib import Path
import yaml


async def validate_kubeconfig(content: bytes) -> dict:
    """Validate an uploaded kubeconfig and extract cluster info.

    Args:
        content: Raw bytes of the uploaded kubeconfig file.

    Returns:
        Parsed kubeconfig dict if valid.

    Raises:
        ValueError: If the file is not a valid kubeconfig.
    """
    try:
        kube_config = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML: {e}")

    required_keys = {"apiVersion", "clusters", "contexts", "users"}
    if not required_keys.issubset(kube_config.keys()):
        raise ValueError(f"Missing required keys: {required_keys - kube_config.keys()}")

    return kube_config


async def store_kubeconfig(content: bytes, cluster_id: str) -> Path:
    """Store uploaded kubeconfig with restricted file permissions.

    Args:
        content: Validated kubeconfig bytes.
        cluster_id: Unique identifier for the cluster connection.

    Returns:
        Path to the stored kubeconfig file.
    """
    config_dir = Path(tempfile.gettempdir()) / "k8s-dashboard" / "kubeconfigs"
    config_dir.mkdir(parents=True, exist_ok=True)

    config_path = config_dir / f"{cluster_id}.yaml"
    config_path.write_bytes(content)
    config_path.chmod(0o600)  # Owner-only read/write
    return config_path
```

## 5. Multi-Cluster Management

The client factory (shown in SKILL.md) manages multiple cluster connections. The
configuration is loaded at startup from environment variables or a config file:

```python
"""Multi-cluster configuration loaded from environment or config file.

Supports defining clusters via CLUSTERS_CONFIG env var (JSON) or
a clusters.yaml config file. Each entry specifies the auth method
and connection parameters.
"""

from pydantic_settings import BaseSettings


class ClusterConfig(BaseModel):
    """Configuration for a single cluster connection."""
    id: str
    name: str
    auth_method: Literal["kubeconfig", "in_cluster", "eks", "gke", "aks"]
    kubeconfig_path: str | None = None
    context: str | None = None
    aws_region: str | None = None
    aws_cluster_name: str | None = None
    gke_project: str | None = None
    aks_resource_group: str | None = None
    aks_cluster_name: str | None = None


class Settings(BaseSettings):
    """Application settings with cluster configuration."""
    app_name: str = "K8s Dashboard"
    clusters_config: list[ClusterConfig] = []
    default_cluster_id: str | None = None
    kubeconfig_path: str | None = None
    in_cluster: bool = False
    allow_kubeconfig_upload: bool = True

    model_config = SettingsConfigDict(env_prefix="K8S_DASH_")
```

## 6. Client Lifecycle & Health Checks

```python
"""Lifespan management for K8s clients — startup, health checks, shutdown.

Integrates with FastAPI's lifespan context manager to ensure all
ApiClient instances are properly closed on shutdown.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage K8s client connections across app lifecycle."""
    factory = K8sClientFactory()

    # Load configured clusters
    settings = get_settings()
    if settings.in_cluster:
        await factory.register_in_cluster()
    else:
        for cluster_cfg in settings.clusters_config:
            await factory.register(cluster_cfg)

    # Auto-discover from default kubeconfig if no explicit config
    if not factory.has_clusters() and settings.kubeconfig_path:
        await factory.discover_from_kubeconfig(settings.kubeconfig_path)

    app.state.k8s_factory = factory

    yield

    # Cleanup: close all ApiClient sessions
    await factory.close_all()
```

## 7. Configuration Schema

### Environment Variables (.env.example)

```bash
# App
K8S_DASH_APP_NAME="K8s Dashboard"
K8S_DASH_SECRET_KEY="change-me-in-production"
K8S_DASH_DEBUG=false

# Cluster connectivity
K8S_DASH_IN_CLUSTER=false
K8S_DASH_KUBECONFIG_PATH=/home/user/.kube/config
K8S_DASH_ALLOW_KUBECONFIG_UPLOAD=true

# Multi-cluster (JSON array)
K8S_DASH_CLUSTERS_CONFIG='[
  {"id": "prod", "name": "Production", "auth_method": "kubeconfig", "context": "prod-context"},
  {"id": "staging", "name": "Staging", "auth_method": "eks", "aws_region": "eu-central-1", "aws_cluster_name": "staging-cluster"}
]'
K8S_DASH_DEFAULT_CLUSTER_ID=prod

# Caching
K8S_DASH_CACHE_TTL_SECONDS=30

# Auth (for dashboard login, not K8s auth)
K8S_DASH_AUTH_ENABLED=false
K8S_DASH_AUTH_USERNAME=admin
K8S_DASH_AUTH_PASSWORD_HASH=""
```

## 8. Docker Compose & Kubeconfig Mounting

```yaml
services:
  dashboard:
    build: .
    ports:
      - "8080:8080"
    volumes:
      # Mount host kubeconfig (read-only)
      - ${HOME}/.kube/config:/home/app/.kube/config:ro
      # Or mount a specific kubeconfig directory
      # - ./kubeconfig:/app/kubeconfig:ro
    environment:
      - K8S_DASH_KUBECONFIG_PATH=/home/app/.kube/config
      - K8S_DASH_APP_NAME=My K8s Dashboard
    # For cloud provider auth, pass credentials:
    # AWS EKS:
    #   - AWS_ACCESS_KEY_ID
    #   - AWS_SECRET_ACCESS_KEY
    #   - AWS_DEFAULT_REGION=eu-central-1
    # GKE:
    #   volumes:
    #     - ${HOME}/.config/gcloud:/home/app/.config/gcloud:ro

  # Optional: Redis for caching and session storage
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### In-Cluster Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: k8s-dashboard
  namespace: k8s-dashboard
spec:
  replicas: 1
  selector:
    matchLabels:
      app: k8s-dashboard
  template:
    metadata:
      labels:
        app: k8s-dashboard
    spec:
      serviceAccountName: k8s-dashboard
      containers:
        - name: dashboard
          image: k8s-dashboard:latest
          ports:
            - containerPort: 8080
          env:
            - name: K8S_DASH_IN_CLUSTER
              value: "true"
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8080
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: k8s-dashboard
  namespace: k8s-dashboard
spec:
  selector:
    app: k8s-dashboard
  ports:
    - port: 80
      targetPort: 8080
```
