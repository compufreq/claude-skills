# CKA Curriculum Snapshot — v1.34 (February 2025)

> **Source:** https://github.com/cncf/curriculum/blob/master/CKA_Curriculum_v1.34.pdf
> **Kubernetes version:** 1.34
> **Snapshot date:** March 2026
> **Note:** Always fetch the latest from GitHub before relying on this file. This is a fallback only.

## Domains and Weights

| Domain | Weight |
|--------|--------|
| Cluster Architecture, Installation and Configuration | 25% |
| Troubleshooting | 30% |
| Workloads and Scheduling | 15% |
| Services and Networking | 20% |
| Storage | 10% |

## Domain 1: Storage — 10%

- Implement storage classes and dynamic volume provisioning
- Configure volume types, access modes, and reclaim policies
- Manage persistent volumes and persistent volume claims

### Key concepts
- StorageClass, PV, PVC lifecycle
- Access modes: ReadWriteOnce, ReadOnlyMany, ReadWriteMany, ReadWriteOncePod
- Reclaim policies: Retain, Recycle, Delete
- Volume types: hostPath, emptyDir, nfs, csi
- Dynamic provisioning via StorageClass provisioner

## Domain 2: Troubleshooting — 30%

- Troubleshoot clusters and nodes
- Troubleshoot cluster components
- Monitor cluster and application resource usage
- Manage and evaluate container output streams
- Troubleshoot services and networking

### Key concepts
- Node status conditions (Ready, MemoryPressure, DiskPressure, PIDPressure)
- kubelet, kube-proxy, container runtime troubleshooting
- Control plane component logs: kube-apiserver, kube-scheduler, kube-controller-manager, etcd
- `kubectl logs`, `kubectl describe`, `kubectl get events`
- `kubectl top nodes`, `kubectl top pods` (requires metrics-server)
- Service endpoint resolution, DNS troubleshooting with CoreDNS
- Certificate and authentication issues
- Static pod manifests in /etc/kubernetes/manifests/

## Domain 3: Workloads and Scheduling — 15%

- Understand application deployments and how to perform rolling updates and rollbacks
- Use ConfigMaps and Secrets to configure applications
- Configure workload autoscaling (HPA, VPA)
- Understand the primitives used to create robust, self-healing application deployments
- Configure Pod admission and scheduling (limits, node affinity, taints/tolerations, etc.)

### Key concepts
- Deployment strategies: RollingUpdate, Recreate
- `kubectl rollout status`, `kubectl rollout undo`, `kubectl rollout history`
- ConfigMap and Secret creation (from literal, from file, from env-file)
- HorizontalPodAutoscaler (HPA) — requires metrics-server
- VerticalPodAutoscaler (VPA)
- Resource requests and limits (CPU, memory)
- NodeSelector, nodeAffinity, podAffinity, podAntiAffinity
- Taints and tolerations
- PodDisruptionBudget
- DaemonSets, StatefulSets, Jobs, CronJobs

## Domain 4: Cluster Architecture, Installation and Configuration — 25%

- Manage role-based access control (RBAC)
- Prepare underlying infrastructure for installing a Kubernetes cluster
- Create and manage Kubernetes clusters using kubeadm
- Manage the lifecycle of Kubernetes clusters
- Implement and configure a highly-available control plane
- Use Helm and Kustomize to install cluster components
- Understand extension interfaces (CNI, CSI, CRI, etc.)
- Understand CRDs, install and configure operators

### Key concepts
- RBAC: Role, ClusterRole, RoleBinding, ClusterRoleBinding
- ServiceAccount creation and binding
- kubeadm init, kubeadm join, kubeadm token, kubeadm upgrade
- etcd backup: `ETCDCTL_API=3 etcdctl snapshot save`
- etcd restore: `etcdctl snapshot restore`
- HA control plane: stacked vs external etcd topology
- Helm: `helm install`, `helm upgrade`, `helm rollback`, `helm repo add`
- Kustomize: `kubectl apply -k`, kustomization.yaml structure
- CNI plugins (Calico, Flannel, Cilium)
- CRI (containerd, CRI-O)
- CSI drivers
- CustomResourceDefinition (CRD) creation and usage
- Operator pattern

## Domain 5: Services and Networking — 20%

- Understand connectivity between Pods
- Define and enforce Network Policies
- Use ClusterIP, NodePort, LoadBalancer service types and endpoints
- Use the Gateway API to manage Ingress traffic
- Know how to use Ingress controllers and Ingress resources
- Understand and use CoreDNS

### Key concepts
- Pod networking model (every Pod gets its own IP, flat network)
- Service types: ClusterIP, NodePort, LoadBalancer, ExternalName
- Endpoints and EndpointSlices
- Network Policies: ingress/egress rules, podSelector, namespaceSelector, ipBlock
- Default deny policies
- Gateway API: Gateway, HTTPRoute, GatewayClass
- Ingress resources and Ingress controllers (nginx-ingress)
- CoreDNS: ConfigMap, forward, hosts plugins
- DNS resolution: `<service>.<namespace>.svc.cluster.local`
- kube-proxy modes: iptables, IPVS

## Exam Environment Details

- Browser-based terminal (PSI Secure Browser)
- Access to one or more pre-configured Kubernetes clusters
- Must switch contexts between clusters using `kubectl config use-context`
- Copy-paste works (single-click copy from question text)
- Allowed docs: kubernetes.io/docs, kubernetes.io/blog and subdomains
- No access to personal notes, bookmarks beyond kubernetes.io
- Webcam and screen sharing required for proctoring

## Key Changes in v1.34 (Feb 2025 Update)

Compared to pre-2025 versions:
- Consolidated from 10 domains down to 5 core areas
- Added Helm & Kustomize as required competencies
- Added CRDs and Operators
- Added Gateway API alongside traditional Ingress
- Added HPA and VPA for workload autoscaling
- Increased emphasis on troubleshooting (30% weight)
- Enhanced focus on RBAC and security configurations
