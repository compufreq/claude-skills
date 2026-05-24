# Priority Topics Deep-Dive: CoreDNS, Helm, Kustomize & Cluster Lifecycle

These topics were flagged as areas of concern. They are newer additions to the CKA curriculum (Feb 2025)
and carry significant weight across two domains: Cluster Architecture (25%) and Services & Networking (20%).

Read this reference whenever the user asks about any of these topics, or when generating study plans
(allocate extra time to these).

---

## 1. CoreDNS — Domain: Services & Networking (20%)

CoreDNS is the default cluster DNS since Kubernetes v1.13. The CKA exam tests both understanding
and troubleshooting of CoreDNS. This is a frequent exam topic because DNS issues affect everything.

### How CoreDNS works in Kubernetes

- CoreDNS runs as a Deployment in `kube-system` namespace (typically 2 replicas)
- Exposed via a ClusterIP Service called `kube-dns` in `kube-system`
- Every Pod's `/etc/resolv.conf` points to the `kube-dns` service IP
- CoreDNS reads its configuration from a ConfigMap called `coredns` in `kube-system`

### DNS resolution format

Services: `<service-name>.<namespace>.svc.cluster.local`
Pods: `<pod-ip-with-dashes>.<namespace>.pod.cluster.local`

```bash
# Test DNS resolution from inside a pod
k run dnstest --image=busybox:1.28 --rm -it --restart=Never -- nslookup kubernetes.default
k run dnstest --image=busybox:1.28 --rm -it --restart=Never -- nslookup myservice.mynamespace.svc.cluster.local

# Check what resolv.conf looks like inside a pod
k run dnstest --image=busybox:1.28 --rm -it --restart=Never -- cat /etc/resolv.conf
```

### The Corefile (CoreDNS ConfigMap)

```bash
# View the CoreDNS configuration
k get cm coredns -n kube-system -o yaml
```

Default Corefile structure:
```
.:53 {
    errors                          # Log errors
    health {                        # Health check endpoint on :8080/health
        lameduck 5s
    }
    ready                           # Readiness endpoint on :8181/ready
    kubernetes cluster.local in-addr.arpa ip6.arpa {  # Kubernetes plugin
        pods insecure               # Resolve Pod DNS records
        fallthrough in-addr.arpa ip6.arpa
        ttl 30                      # Cache TTL for DNS records
    }
    prometheus :9153                # Prometheus metrics endpoint
    forward . /etc/resolv.conf     # Forward external queries to upstream DNS
    cache 30                        # Cache DNS responses for 30 seconds
    loop                            # Detect and break forwarding loops
    reload                          # Auto-reload Corefile changes
    loadbalance                     # Round-robin DNS responses
}
```

### Common CoreDNS exam tasks

**Task type 1: Fix broken DNS**
```bash
# Check if CoreDNS pods are running
k get pods -n kube-system -l k8s-app=kube-dns
k describe pod -n kube-system -l k8s-app=kube-dns
k logs -n kube-system -l k8s-app=kube-dns

# Check if CoreDNS deployment is scaled to 0
k get deploy coredns -n kube-system

# Check if the kube-dns service exists and has endpoints
k get svc kube-dns -n kube-system
k get endpoints kube-dns -n kube-system
```

**Task type 2: Add custom DNS entries**
```bash
# Edit the CoreDNS ConfigMap to add custom DNS forwarding
k edit cm coredns -n kube-system

# Example: Forward example.com to a custom DNS server
# Add this block inside the Corefile data:
# example.com {
#     forward . 10.0.0.1
# }

# After editing, restart CoreDNS to pick up changes
k rollout restart deploy coredns -n kube-system
```

**Task type 3: Configure Pod DNS settings**
```yaml
# Pod with custom DNS config
apiVersion: v1
kind: Pod
metadata:
  name: custom-dns-pod
spec:
  dnsPolicy: "None"        # Override default DNS settings
  dnsConfig:
    nameservers:
      - 8.8.8.8
    searches:
      - custom.local
    options:
      - name: ndots
        value: "2"
  containers:
  - name: app
    image: nginx
```

**dnsPolicy options to know:**
- `Default` — inherit DNS from the node
- `ClusterFirst` — use cluster DNS (kube-dns), fall back to node DNS for external
- `ClusterFirstWithHostNet` — for pods with hostNetwork: true
- `None` — no auto DNS; must specify dnsConfig

### CoreDNS troubleshooting checklist

1. Are CoreDNS pods running? `k get pods -n kube-system -l k8s-app=kube-dns`
2. Are there enough replicas? `k get deploy coredns -n kube-system`
3. Does kube-dns service have endpoints? `k get ep kube-dns -n kube-system`
4. Is the CoreDNS ConfigMap correct? `k get cm coredns -n kube-system -o yaml`
5. Check CoreDNS logs for errors: `k logs -n kube-system -l k8s-app=kube-dns`
6. Test from inside a pod: `nslookup kubernetes.default`
7. Check Pod's /etc/resolv.conf: verify nameserver points to kube-dns ClusterIP
8. Is there a NetworkPolicy blocking DNS traffic on port 53?

### Exam doc reference
https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/
https://kubernetes.io/docs/tasks/administer-cluster/coredns/

---

## 2. Helm — Domain: Cluster Architecture, Installation and Configuration (25%)

Helm is now a required competency since the Feb 2025 curriculum update. The exam allows access to
https://helm.sh/docs/ during the test. Focus on practical commands, not Helm chart authoring.

### Essential Helm commands for the CKA exam

```bash
# Add a chart repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add stable https://charts.helm.sh/stable
helm repo update

# Search for charts
helm search repo nginx
helm search repo bitnami/nginx --versions

# Install a chart
helm install my-release bitnami/nginx
helm install my-release bitnami/nginx --namespace mynamespace --create-namespace

# Install with custom values
helm install my-release bitnami/nginx --set replicaCount=3
helm install my-release bitnami/nginx --set service.type=NodePort
helm install my-release bitnami/nginx -f custom-values.yaml

# List installed releases
helm list
helm list -A          # All namespaces
helm list -n mynamespace

# Get release information
helm status my-release
helm get values my-release
helm get manifest my-release

# Upgrade a release
helm upgrade my-release bitnami/nginx --set replicaCount=5
helm upgrade my-release bitnami/nginx -f new-values.yaml

# Rollback a release
helm rollback my-release 1    # Rollback to revision 1
helm history my-release       # View release history

# Uninstall a release
helm uninstall my-release
helm uninstall my-release -n mynamespace

# Show chart information (useful during exam for finding values)
helm show values bitnami/nginx    # Show default values
helm show chart bitnami/nginx     # Show chart metadata
helm show readme bitnami/nginx    # Show README

# Generate manifests without installing (dry run)
helm template my-release bitnami/nginx --set replicaCount=3
helm install my-release bitnami/nginx --dry-run --debug
```

### Common CKA Helm tasks

- Install a specific application using Helm with custom values
- Upgrade an existing Helm release to change configuration
- Rollback a Helm release to a previous version
- List and inspect Helm releases in a specific namespace

### Key concepts

- **Release:** A specific instance of a chart running in the cluster
- **Chart:** A package of Kubernetes resource templates
- **Repository:** A place where charts are stored and shared
- **Values:** Configuration that customizes a chart (override with `--set` or `-f`)
- **Revision:** Each install/upgrade creates a new revision for rollback

### Exam doc reference
https://helm.sh/docs/ (allowed in CKA exam)

---

## 3. Kustomize — Domain: Cluster Architecture, Installation and Configuration (25%)

Kustomize is built into kubectl (`kubectl apply -k`). It lets you customize YAML without templates.
The exam tests your ability to use it, not author complex overlays.

### How Kustomize works

Kustomize uses a `kustomization.yaml` file that references base resources and applies
transformations (patches, labels, prefixes, replicas, images, etc.) without modifying originals.

### Essential Kustomize commands for the CKA exam

```bash
# Apply resources with kustomize
kubectl apply -k <directory>
kubectl apply -k ./overlays/production

# Preview what kustomize will generate (dry run)
kubectl kustomize <directory>
kubectl kustomize ./overlays/production

# Delete resources managed by kustomize
kubectl delete -k <directory>
```

### Creating a basic kustomization

**Step 1: Create base resources**

```bash
mkdir -p base
```

`base/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: nginx:1.21
        ports:
        - containerPort: 80
```

`base/service.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 80
```

`base/kustomization.yaml`:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml
commonLabels:
  environment: base
```

**Step 2: Create an overlay**

```bash
mkdir -p overlays/production
```

`overlays/production/kustomization.yaml`:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../base
namePrefix: prod-
commonLabels:
  environment: production
replicas:
- name: myapp
  count: 3
images:
- name: nginx
  newTag: "1.25"
```

```bash
# Preview the production overlay
kubectl kustomize overlays/production

# Apply the production overlay
kubectl apply -k overlays/production
```

### Common kustomization.yaml fields

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:          # Base YAML files or directories to include
- deployment.yaml
- service.yaml

namePrefix: dev-    # Add prefix to all resource names
nameSuffix: -v2     # Add suffix to all resource names
namespace: staging  # Set namespace for all resources

commonLabels:       # Add labels to all resources and selectors
  team: backend

commonAnnotations:  # Add annotations to all resources
  owner: devteam

replicas:           # Override replica count
- name: myapp
  count: 5

images:             # Override container images
- name: nginx
  newName: custom-registry/nginx
  newTag: "2.0"

configMapGenerator: # Generate ConfigMaps
- name: app-config
  literals:
  - DB_HOST=mysql
  - DB_PORT=3306

secretGenerator:    # Generate Secrets
- name: app-secrets
  literals:
  - password=s3cr3t

patches:            # Apply strategic merge or JSON patches
- path: patch-replicas.yaml
  target:
    kind: Deployment
    name: myapp
```

### Common CKA Kustomize tasks

- Apply a set of resources using `kubectl apply -k`
- Add common labels or namespace to a group of resources
- Change the replica count or image tag via an overlay
- Generate ConfigMaps from literal values

### Exam doc reference
https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/

---

## 4. Cluster Lifecycle: Upgrade and Downgrade — Domain: Cluster Architecture (25%)

This is one of the highest-value exam topics. kubeadm cluster upgrades are predictable, procedural,
and carry significant weight. Master this sequence and you'll earn easy points.

### The Golden Rule

Kubernetes supports upgrading **one minor version at a time**. You cannot skip versions.
- OK: 1.33 → 1.34
- NOT OK: 1.33 → 1.35 (must go 1.33 → 1.34 → 1.35)

### Full Upgrade Procedure — Control Plane Node

```bash
# Step 0: Check current version
kubectl get nodes
kubeadm version
kubelet --version

# Step 1: Find available versions
# On Ubuntu/Debian:
apt update
apt-cache madison kubeadm | head
# On RHEL/CentOS:
yum list --showduplicates kubeadm | head

# Step 2: Upgrade kubeadm to target version
# Ubuntu/Debian:
apt-mark unhold kubeadm
apt-get update && apt-get install -y kubeadm=1.XX.Y-*
apt-mark hold kubeadm

# RHEL/CentOS:
yum install -y kubeadm-1.XX.Y --disableexcludes=kubernetes

# Step 3: Verify the upgrade plan
kubeadm upgrade plan

# Step 4: Apply the upgrade (control plane node ONLY)
sudo kubeadm upgrade apply v1.XX.Y
# For additional control plane nodes use:
# sudo kubeadm upgrade node

# Step 5: Drain the node
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Step 6: Upgrade kubelet and kubectl
# Ubuntu/Debian:
apt-mark unhold kubelet kubectl
apt-get update && apt-get install -y kubelet=1.XX.Y-* kubectl=1.XX.Y-*
apt-mark hold kubelet kubectl

# RHEL/CentOS:
yum install -y kubelet-1.XX.Y kubectl-1.XX.Y --disableexcludes=kubernetes

# Step 7: Restart kubelet
sudo systemctl daemon-reload
sudo systemctl restart kubelet

# Step 8: Uncordon the node
kubectl uncordon <node-name>

# Step 9: Verify
kubectl get nodes
```

### Full Upgrade Procedure — Worker Nodes

```bash
# Step 1: Upgrade kubeadm on the worker (SSH to the worker node)
apt-mark unhold kubeadm
apt-get update && apt-get install -y kubeadm=1.XX.Y-*
apt-mark hold kubeadm

# Step 2: Upgrade the node configuration
sudo kubeadm upgrade node
# Note: This is DIFFERENT from control plane — do NOT use "kubeadm upgrade apply"

# Step 3: Drain the worker (from the control plane node or anywhere with kubectl access)
kubectl drain <worker-node> --ignore-daemonsets --delete-emptydir-data

# Step 4: Upgrade kubelet and kubectl on the worker
apt-mark unhold kubelet kubectl
apt-get update && apt-get install -y kubelet=1.XX.Y-* kubectl=1.XX.Y-*
apt-mark hold kubelet kubectl

# Step 5: Restart kubelet
sudo systemctl daemon-reload
sudo systemctl restart kubelet

# Step 6: Uncordon the worker
kubectl uncordon <worker-node>
```

### Key differences to remember

| Action | Control Plane | Worker Node |
|--------|---------------|-------------|
| kubeadm upgrade | `kubeadm upgrade apply v1.XX.Y` | `kubeadm upgrade node` |
| Order | Must be done FIRST | After all control plane nodes |
| Drain | Drain before kubelet upgrade | Drain before kubelet upgrade |

### Downgrade Procedure

Downgrading follows the REVERSE order — **workers first, then control plane** — and uses
the same commands but targeting the lower version number.

```bash
# IMPORTANT: Downgrade workers first, then control plane
# The procedure is identical to upgrade, just with the lower version number

# On the worker node:
apt-get install -y kubeadm=1.LOWER.Y-*
sudo kubeadm upgrade node
kubectl drain <worker-node> --ignore-daemonsets --delete-emptydir-data
apt-get install -y kubelet=1.LOWER.Y-* kubectl=1.LOWER.Y-*
sudo systemctl daemon-reload
sudo systemctl restart kubelet
kubectl uncordon <worker-node>

# Then on the control plane node:
apt-get install -y kubeadm=1.LOWER.Y-*
sudo kubeadm upgrade apply v1.LOWER.Y
kubectl drain <cp-node> --ignore-daemonsets --delete-emptydir-data
apt-get install -y kubelet=1.LOWER.Y-* kubectl=1.LOWER.Y-*
sudo systemctl daemon-reload
sudo systemctl restart kubelet
kubectl uncordon <cp-node>
```

### etcd Backup Before Upgrade (best practice, often tested)

Always back up etcd before any cluster upgrade:

```bash
ETCDCTL_API=3 etcdctl snapshot save /tmp/etcd-pre-upgrade.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify the backup
ETCDCTL_API=3 etcdctl snapshot status /tmp/etcd-pre-upgrade.db --write-table
```

### HA Cluster Upgrade — Additional Considerations

On a multi-control-plane HA cluster (like your home lab):

1. Upgrade the **first** control plane node with `kubeadm upgrade apply`
2. Upgrade **additional** control plane nodes with `kubeadm upgrade node` (NOT apply)
3. Upgrade each worker node
4. Always upgrade one node at a time to maintain availability
5. Verify cluster health between each node upgrade: `kubectl get nodes`, `kubectl get pods -A`

### Common exam mistakes on upgrade questions

1. Forgetting `apt-mark hold` / `apt-mark unhold` — packages auto-upgrade without this
2. Using `kubeadm upgrade apply` on worker nodes (should be `kubeadm upgrade node`)
3. Forgetting `systemctl daemon-reload` before `systemctl restart kubelet`
4. Not draining the node before upgrading kubelet
5. Not uncordoning the node after the upgrade
6. Trying to skip minor versions (must upgrade one at a time)
7. Forgetting to upgrade kubectl along with kubelet

### Exam doc reference
https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/

---

## Practice Lab Suggestions for These Topics

### On your HA home lab (recommended):
1. **CoreDNS:** Scale CoreDNS to 0, debug and fix. Edit Corefile to add custom forwarding rules.
   Create pods with different dnsPolicy settings. Break DNS with a NetworkPolicy and fix it.
2. **Helm:** Add bitnami repo, install nginx with custom values, upgrade the release, rollback.
   List releases across namespaces. Use `helm show values` to find configurable options.
3. **Kustomize:** Create a base deployment, build dev/staging/prod overlays with different
   replicas and image tags. Apply with `kubectl apply -k` and verify.
4. **Cluster upgrade:** Practice the full upgrade cycle on your HA cluster — etcd backup,
   control plane upgrade, worker upgrade, verification. Then practice downgrade.

### On KillerKoda:
- Challenge 04: ETCD Backup & Restore (cluster lifecycle)
- Challenge 08: Kubernetes Upgrade (cluster upgrade)
- Challenge 21: Install Redis Using Helm (Helm)
- Killer Shell CKA scenarios (https://killercoda.com/killer-shell-cka) — CoreDNS and DNS debugging
