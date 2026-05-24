# CKA Exam Doc Navigation: URLs, Search Keywords & Page Sections

> **Allowed resources during CKA exam (official):**
> - https://kubernetes.io/docs/ (search bar allowed, must NOT follow external results)
> - https://kubernetes.io/blog/
> - https://helm.sh/docs/
> - https://gateway-api.sigs.k8s.io/
> - Task-specific Quick Reference box links
>
> Source: https://docs.linuxfoundation.org/tc-docs/certification/certification-resources-allowed

Every practice question and solution should reference the specific page, search keywords, and
section heading where the user can find the answer in the allowed docs. This trains exam-speed
doc navigation.

---

## Domain 1: Cluster Architecture, Installation & Configuration (25%)

### RBAC
| What | Search keywords | URL | Section |
|------|----------------|-----|---------|
| RBAC overview | `rbac` | https://kubernetes.io/docs/reference/access-authn-authz/rbac/ | "Role and ClusterRole" |
| Create Role | `rbac` | same | "Role example" |
| Create ClusterRole | `rbac` | same | "ClusterRole example" |
| RoleBinding | `rbac` | same | "RoleBinding and ClusterRoleBinding" |
| ServiceAccount | `service accounts` | https://kubernetes.io/docs/concepts/security/service-accounts/ | "Create a ServiceAccount" |
| kubectl create role | `kubectl cheat sheet` | https://kubernetes.io/docs/reference/kubectl/cheatsheet/ | search for "role" on page |

### kubeadm
| What | Search keywords | URL | Section |
|------|----------------|-----|---------|
| kubeadm init | `kubeadm init` | https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-init/ | full page |
| kubeadm join | `kubeadm join` | https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-join/ | full page |
| kubeadm upgrade | `kubeadm upgrade` | https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/ | "Upgrading control plane nodes" |
| kubeadm token | `kubeadm token` | https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-token/ | full page |
| HA topology | `ha topology` | https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/ha-topology/ | "Stacked etcd" and "External etcd" |
| Create HA cluster | `high availability kubeadm` | https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/high-availability/ | full page |

### etcd
| What | Search keywords | URL | Section |
|------|----------------|-----|---------|
| etcd backup | `etcd backup` | https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/ | "Backing up an etcd cluster" |
| etcd restore | `etcd backup` | same | "Restoring an etcd cluster" |
| etcd snapshot save | `etcd backup` | same | look for `etcdctl snapshot save` |

### Cluster upgrade
| What | Search keywords | URL | Section |
|------|----------------|-----|---------|
| Upgrade procedure | `upgrade kubeadm` | https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/ | "Upgrading control plane nodes" then "Upgrade worker nodes" |
| Drain node | `drain` | https://kubernetes.io/docs/reference/kubectl/generated/kubectl_drain/ | or search `safely drain node` |
| Cordon/uncordon | `cordon` | https://kubernetes.io/docs/reference/kubectl/generated/kubectl_cordon/ | full page |

### Helm
| What | Search keywords (helm.sh) | URL | Section |
|------|--------------------------|-----|---------|
| helm install | `helm install` | https://helm.sh/docs/helm/helm_install/ | full page |
| helm upgrade | `helm upgrade` | https://helm.sh/docs/helm/helm_upgrade/ | full page |
| helm rollback | `helm rollback` | https://helm.sh/docs/helm/helm_rollback/ | full page |
| helm repo add | `helm repo` | https://helm.sh/docs/helm/helm_repo_add/ | full page |
| helm list | `helm list` | https://helm.sh/docs/helm/helm_list/ | full page |
| helm uninstall | `helm uninstall` | https://helm.sh/docs/helm/helm_uninstall/ | full page |
| helm show values | `helm show` | https://helm.sh/docs/helm/helm_show_values/ | full page |
| Quickstart | `quickstart` | https://helm.sh/docs/intro/quickstart/ | "Initialize a Helm Chart Repository" |
| Using Helm | `using helm` | https://helm.sh/docs/intro/using_helm/ | covers install, upgrade, rollback |

### Kustomize
| What | Search keywords | URL | Section |
|------|----------------|-----|---------|
| Kustomize overview | `kustomize` | https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/ | full page |
| Apply with -k | `kustomize` | same | "Apply / View / Delete Objects using Kustomize" |
| configMapGenerator | `kustomize` | same | "Generating Resources" → "configMapGenerator" |
| Bases and overlays | `kustomize` | same | "Bases and Overlays" |
| Set images | `kustomize` | same | "Setting images" |

### CRDs & Operators
| What | Search keywords | URL | Section |
|------|----------------|-----|---------|
| CRD concepts | `custom resources` | https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/ | full page |
| Create a CRD | `custom resource definition` | https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/ | "Create a CustomResourceDefinition" |
| Operator pattern | `operator pattern` | https://kubernetes.io/docs/concepts/extend-kubernetes/operator/ | full page |

### Extension interfaces
| What | Search keywords | URL | Section |
|------|----------------|-----|---------|
| CNI | `network plugins` | https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/network-plugins/ | "CNI" |
| CSI | `csi` | https://kubernetes.io/docs/concepts/storage/volumes/#csi | "CSI" |
| CRI | `container runtime` | https://kubernetes.io/docs/setup/production-environment/container-runtimes/ | full page |

---

## Domain 2: Troubleshooting (30%)

| What | Search keywords | URL | Section |
|------|----------------|-----|---------|
| Troubleshoot clusters | `troubleshoot clusters` | https://kubernetes.io/docs/tasks/debug/debug-cluster/ | full page |
| Troubleshoot applications | `troubleshoot application` | https://kubernetes.io/docs/tasks/debug/debug-application/ | full page |
| Debug pods | `debug pods` | https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/ | "My pod stays pending/waiting/crashing" |
| Debug services | `debug service` | https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/ | full page — step by step |
| Debug DNS | `debug dns resolution` | https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/ | "Check the local DNS configuration first" |
| Node not ready | `troubleshoot clusters` | https://kubernetes.io/docs/tasks/debug/debug-cluster/ | "Node" section |
| Pod logs | `kubectl logs` or `kubectl cheat sheet` | https://kubernetes.io/docs/reference/kubectl/cheatsheet/ | "Interacting with running Pods" |
| Events | `kubectl cheat sheet` | same | search for "events" on page |
| Resource usage | `metrics server` | https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/ | "Metrics API" |

---

## Domain 3: Workloads & Scheduling (15%)

| What | Search keywords | URL | Section |
|------|----------------|-----|---------|
| Deployments | `deployment` | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ | "Creating a Deployment" |
| Rolling update | `deployment` | same | "Updating a Deployment" |
| Rollback | `deployment` | same | "Rolling Back a Deployment" |
| ConfigMaps | `configmap` | https://kubernetes.io/docs/concepts/configuration/configmap/ | "Using ConfigMaps" |
| Secrets | `secret` | https://kubernetes.io/docs/concepts/configuration/secret/ | "Using Secrets" |
| HPA | `horizontal pod autoscaler` | https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/ | full page |
| HPA walkthrough | `horizontal pod autoscale walkthrough` | https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/ | step-by-step |
| VPA | `vertical pod autoscaler` | https://kubernetes.io/docs/concepts/workloads/autoscaling/ | "Scaling workloads vertically" |
| Resource requests/limits | `resource management` | https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/ | "Requests and limits" |
| Node affinity | `assign pods node` | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ | "Node affinity" |
| Taints & tolerations | `taints tolerations` | https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ | full page |
| DaemonSet | `daemonset` | https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/ | full page |
| StatefulSet | `statefulset` | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | full page |
| Jobs | `job` | https://kubernetes.io/docs/concepts/workloads/controllers/job/ | full page |
| CronJob | `cronjob` | https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/ | full page |

---

## Domain 4: Services & Networking (20%)

| What | Search keywords | URL | Section |
|------|----------------|-----|---------|
| Services | `service` | https://kubernetes.io/docs/concepts/services-networking/service/ | "Defining a Service" |
| Service types | `service` | same | "Type ClusterIP", "Type NodePort", "Type LoadBalancer" |
| Endpoints | `service` | same | "Endpoints" |
| Network Policies | `network policy` | https://kubernetes.io/docs/concepts/services-networking/network-policies/ | full page |
| NetworkPolicy examples | `network policy` | same | "Default policies" — default deny examples |
| Ingress | `ingress` | https://kubernetes.io/docs/concepts/services-networking/ingress/ | "The Ingress resource" |
| Ingress controllers | `ingress controllers` | https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/ | full page |
| Gateway API overview | `gateway` (on gateway-api.sigs.k8s.io) | https://gateway-api.sigs.k8s.io/concepts/api-overview/ | full page |
| HTTPRoute | `httproute` (on gateway-api.sigs.k8s.io) | https://gateway-api.sigs.k8s.io/api-types/httproute/ | full page |
| GatewayClass | `gatewayclass` (on gateway-api.sigs.k8s.io) | https://gateway-api.sigs.k8s.io/api-types/gatewayclass/ | full page |
| CoreDNS | `coredns` or `dns` | https://kubernetes.io/docs/tasks/administer-cluster/coredns/ | "About CoreDNS" |
| CoreDNS customization | `coredns` | same | "Configuration of Stub-domain and upstream nameserver" |
| Debug DNS | `debug dns` | https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/ | full page |
| DNS for Services | `dns services pods` | https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/ | "Services" section for FQDN format |
| Pod connectivity | `cluster networking` | https://kubernetes.io/docs/concepts/cluster-administration/networking/ | "The Kubernetes network model" |

---

## Domain 5: Storage (10%)

| What | Search keywords | URL | Section |
|------|----------------|-----|---------|
| Persistent Volumes | `persistent volumes` | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ | full page |
| PV access modes | `persistent volumes` | same | "Access Modes" |
| PV reclaim policy | `persistent volumes` | same | "Reclaiming" |
| PVC | `persistent volumes` | same | "PersistentVolumeClaims" |
| Storage Classes | `storage classes` | https://kubernetes.io/docs/concepts/storage/storage-classes/ | full page |
| Dynamic provisioning | `dynamic provisioning` | https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/ | full page |
| Volume types | `volumes` | https://kubernetes.io/docs/concepts/storage/volumes/ | "Types of volumes" |

---

## Cross-Domain: kubectl Cheat Sheet

The cheat sheet is the single most useful page in the exam. Know how to find it:

**Search:** `cheat sheet` on kubernetes.io
**URL:** https://kubernetes.io/docs/reference/kubectl/cheatsheet/

Key sections to know:
- "Kubectl context and configuration" — switching contexts, namespaces
- "Creating objects" — imperative creates
- "Updating resources" — set image, rollout, scale
- "Interacting with running Pods" — exec, logs, port-forward
- "Interacting with Nodes and cluster" — drain, cordon, taint

---

## How to Search During the Exam

1. **Use the kubernetes.io search bar** (top of the docs page). Type the keywords from the table above.
2. **Only click results that stay on kubernetes.io** — clicking external links is a violation.
3. **Use `Ctrl+F` inside the page** to jump to the right section (e.g., `Ctrl+F` → "Backing up").
4. **Prefer `/docs/tasks/` pages** over `/docs/concepts/` — tasks pages have copy-paste-ready commands.
5. **Helm docs:** Use the left sidebar navigation or search bar at https://helm.sh/docs/.
6. **Gateway API docs:** Use the left sidebar at https://gateway-api.sigs.k8s.io/.
7. **`kubectl explain` is often faster than docs** for field-level questions:
   ```bash
   k explain pod.spec.dnsPolicy
   k explain deploy.spec.strategy
   k explain networkpolicy.spec --recursive
   k explain pv.spec.accessModes
   ```
