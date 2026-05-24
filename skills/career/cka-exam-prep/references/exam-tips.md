# CKA Exam Tips, Tricks & Speed Techniques

## Shell Setup — Do This First in the Exam

The exam environment already has `kubectl` aliased to `k` with bash autocompletion pre-configured on
all SSH hosts. You do NOT need to set up the basic alias. But spend 60-90 seconds adding these extras:

```bash
# The k alias and bash completion are ALREADY set up in the exam environment.
# These additional shortcuts save you more time:

# Dry-run shortcut — generates YAML without creating the resource
export do="--dry-run=client -o yaml"
# Example: k run nginx --image=nginx $do > pod.yaml

# Force delete shortcut — for when you need to quickly remove something
export now="--force --grace-period 0"
# Example: k delete pod nginx $now

# Namespace shortcut
alias kn='kubectl config set-context --current --namespace'

# Quick status checks
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgn='kubectl get nodes'
alias kd='kubectl describe'
alias kaf='kubectl apply -f'

# Vim setup for YAML editing
cat >> ~/.vimrc << 'EOF'
set tabstop=2
set shiftwidth=2
set expandtab
set number
set autoindent
EOF
```

### Exam environment keyboard shortcuts (memorize these!)

These are specific to the PSI Secure Browser remote desktop environment:

- **Terminal copy:** `Ctrl+Shift+C` (NOT Ctrl+C!)
- **Terminal paste:** `Ctrl+Shift+V` (NOT Ctrl+V!)
- **Other apps copy/paste:** `Ctrl+C` / `Ctrl+V` as normal
- **NEVER use Ctrl+W** — it closes the browser tab! Use `Ctrl+Alt+W` instead
- **Locate cursor:** `Ctrl+Alt+K`
- **INSERT key is disabled** — use `i` for vim insert mode
- **Find in Firefox docs:** `Ctrl+F` (resize browser first to see the search bar)

### Pre-installed tools on exam SSH hosts

You don't need to install these — they're already there:
- `kubectl` (aliased to `k` with bash autocompletion)
- `yq` for YAML processing
- `curl` and `wget` for testing web services
- `man` and man pages

**Important:** The base system (hostname `base`) does NOT have these tools. Always SSH to the
designated host specified in each question before starting work.

## Speed Techniques

### Imperative commands save minutes
Instead of writing YAML from scratch, use imperative commands and pipe to YAML only when needed:

```bash
# Create a pod
k run nginx --image=nginx

# Create a deployment
k create deploy myapp --image=nginx --replicas=3

# Expose a deployment as a service
k expose deploy myapp --port=80 --target-port=8080 --type=NodePort

# Create a configmap
k create cm myconfig --from-literal=key1=val1 --from-literal=key2=val2

# Create a secret
k create secret generic mysecret --from-literal=password=s3cr3t

# Create a service account
k create sa mysa

# Create a role
k create role pod-reader --verb=get,list,watch --resource=pods

# Create a rolebinding
k create rolebinding read-pods --role=pod-reader --serviceaccount=default:mysa

# Create a clusterrole
k create clusterrole node-reader --verb=get,list,watch --resource=nodes

# Create a clusterrolebinding
k create clusterrolebinding read-nodes --clusterrole=node-reader --serviceaccount=default:mysa

# Generate YAML template and edit
k run nginx --image=nginx $do > pod.yaml
# Then edit pod.yaml and apply
```

### kubectl explain is faster than searching docs
```bash
# Get fields for a resource
k explain pod.spec.containers
k explain deploy.spec.strategy
k explain pv.spec

# Recursive — shows all nested fields
k explain pod.spec --recursive | grep -i volume
k explain networkpolicy.spec --recursive
```

### Quick resource lookups
```bash
# List all API resources and their shortnames
k api-resources

# Common shortnames to memorize
# po = pods, deploy = deployments, svc = services, ns = namespaces
# no = nodes, pv = persistentvolumes, pvc = persistentvolumeclaims
# cm = configmaps, sa = serviceaccounts, ing = ingresses
# netpol = networkpolicies, sc = storageclasses, ep = endpoints
```

### Context and namespace management
```bash
# Switch cluster context (CRITICAL — do this for every question)
k config use-context <context-name>

# Set default namespace to avoid -n flag
k config set-context --current --namespace=<namespace>

# Verify current context
k config current-context
```

## Debugging Workflow

When troubleshooting, follow this systematic approach:

### Node-level issues
```bash
# Check node status
k get nodes -o wide
k describe node <node-name>

# SSH to the node and check kubelet
systemctl status kubelet
journalctl -u kubelet -f
# Check kubelet config
cat /var/lib/kubelet/config.yaml

# Check container runtime
systemctl status containerd
crictl ps
crictl logs <container-id>
```

### Control plane issues
```bash
# Check control plane pods (they're static pods)
k get pods -n kube-system
k logs -n kube-system kube-apiserver-<node>
k logs -n kube-system kube-scheduler-<node>
k logs -n kube-system kube-controller-manager-<node>
k logs -n kube-system etcd-<node>

# Static pod manifests location
ls /etc/kubernetes/manifests/

# Check certificates
kubeadm certs check-expiration
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -dates
```

### Pod-level issues
```bash
# Check pod status and events
k get pod <pod> -o wide
k describe pod <pod>
k logs <pod> [-c <container>]
k logs <pod> --previous  # logs from previous crashed container

# Exec into a pod for debugging
k exec -it <pod> -- /bin/sh

# Check if pod is scheduled
k get pod <pod> -o jsonpath='{.spec.nodeName}'
```

### Service and networking issues
```bash
# Check if service has endpoints
k get endpoints <svc>
k describe svc <svc>

# Test DNS resolution
k run test --image=busybox:1.28 --rm -it --restart=Never -- nslookup <svc>.<ns>.svc.cluster.local

# Test connectivity
k run test --image=busybox:1.28 --rm -it --restart=Never -- wget -qO- http://<svc>:<port>

# Check network policies
k get netpol -A
k describe netpol <policy>
```

## etcd Backup and Restore

This comes up frequently and is worth memorizing:

```bash
# Backup
ETCDCTL_API=3 etcdctl snapshot save /tmp/etcd-backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify backup
ETCDCTL_API=3 etcdctl snapshot status /tmp/etcd-backup.db --write-table

# Restore (to a new data directory)
ETCDCTL_API=3 etcdctl snapshot restore /tmp/etcd-backup.db \
  --data-dir=/var/lib/etcd-restored

# Then update the etcd static pod manifest to point to the new data dir
# Edit /etc/kubernetes/manifests/etcd.yaml:
# - Change --data-dir to /var/lib/etcd-restored
# - Update the hostPath volume to /var/lib/etcd-restored
```

## kubeadm Cluster Upgrade

Another high-frequency exam topic:

```bash
# On the control plane node
# 1. Update kubeadm
apt-get update && apt-get install -y kubeadm=1.xx.y-*

# 2. Verify upgrade plan
kubeadm upgrade plan

# 3. Apply upgrade
kubeadm upgrade apply v1.xx.y

# 4. Drain the node
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data

# 5. Update kubelet and kubectl
apt-get install -y kubelet=1.xx.y-* kubectl=1.xx.y-*

# 6. Restart kubelet
systemctl daemon-reload
systemctl restart kubelet

# 7. Uncordon the node
kubectl uncordon <node>

# On worker nodes — repeat steps 1, 4, 5, 6, 7 (skip 2 and 3)
# Use `kubeadm upgrade node` instead of `kubeadm upgrade apply` on workers
```

## Time Management Strategy

### The two-pass approach
**Pass 1 (first 90 minutes):** Work through all questions in order. If a question takes more than 5 minutes
and you're stuck, flag it and move on. Complete all questions you know how to do.

**Pass 2 (final 30 minutes):** Return to flagged questions. With remaining time, attempt partial solutions
even if you can't complete them — partial credit is possible.

### Weight-aware prioritization
Not all questions are worth the same. A 7% question deserves more time than a 2% question. Read the weight
before starting and calibrate your effort:
- 1-3% weight: Spend max 3-4 minutes
- 4-6% weight: Spend max 5-7 minutes
- 7%+ weight: Worth up to 10 minutes

### The verification habit
After completing each question, spend 15-20 seconds verifying:
```bash
k get <resource> -n <namespace>   # Does it exist?
k describe <resource>             # Is it configured correctly?
```
This catches silly mistakes that would cost you points.

## Common Mistakes That Cost Points

1. **Wrong namespace** — Always check which namespace the question specifies
2. **Wrong context** — Always run `kubectl config use-context` as specified
3. **YAML indentation** — Use `kubectl create --dry-run=client -o yaml` to generate templates
4. **Forgetting labels/selectors** — Services and Network Policies rely on label matching
5. **Not waiting for pods to be Running** — Verify with `kubectl get pods -w`
6. **Mixing up PV and PVC** — PV is the actual storage, PVC is the request
7. **Network Policy default behavior** — By default, all traffic is allowed. Creating any
   NetworkPolicy on a pod makes it deny-all except what's explicitly allowed
8. **Case sensitivity** — Resource names, labels, and namespace names are case-sensitive

## Documentation You Can Use in the Exam

These are ALL the websites allowed during the CKA exam (per official LF docs). Practice navigating
them quickly — you won't have time to browse during the exam.

**Kubernetes docs (https://kubernetes.io/docs/):**
- kubectl cheat sheet: `/docs/reference/kubectl/cheatsheet/`
- Pod specification: `/docs/concepts/workloads/pods/`
- Deployments: `/docs/concepts/workloads/controllers/deployment/`
- Services: `/docs/concepts/services-networking/service/`
- Network Policies: `/docs/concepts/services-networking/network-policies/`
- Persistent Volumes: `/docs/concepts/storage/persistent-volumes/`
- RBAC: `/docs/reference/access-authn-authz/rbac/`
- kubeadm: `/docs/setup/production-environment/tools/kubeadm/`
- etcd backup: `/docs/tasks/administer-cluster/configure-upgrade-etcd/`
- HPA: `/docs/tasks/run-application/horizontal-pod-autoscale/`
- ConfigMaps: `/docs/concepts/configuration/configmap/`
- Secrets: `/docs/concepts/configuration/secret/`
- Taints and Tolerations: `/docs/concepts/scheduling-eviction/taint-and-toleration/`
- Node Affinity: `/docs/concepts/scheduling-eviction/assign-pod-node/`

**Helm docs (https://helm.sh/docs/) — also allowed:**
- Helm install: `/docs/helm/helm_install/`
- Helm upgrade: `/docs/helm/helm_upgrade/`
- Helm repo: `/docs/helm/helm_repo/`

**Gateway API docs (https://gateway-api.sigs.k8s.io/) — CKA only:**
- HTTPRoute: `/docs/api-types/httproute/`
- Gateway: `/docs/api-types/gateway/`
- GatewayClass: `/docs/api-types/gatewayclass/`

**Kubernetes Blog (https://kubernetes.io/blog/):**
- Searchable, useful for finding specific feature announcements

**Pro tip:** Use `Ctrl+F` in the Firefox browser within the exam VM to search within pages.
Use the kubernetes.io search bar to find topics, but NEVER follow external search results.
