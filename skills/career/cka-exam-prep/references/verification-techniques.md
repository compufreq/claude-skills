# CKA Exam Verification Techniques

Verifying your work is essential in the CKA exam. The grading is automated — if your config doesn't
function, you score zero on that question even if the YAML looks correct. Spend 15-30 seconds verifying
each completed task.

## The Universal Test Pod

Memorize this pattern. You'll use it for nearly every verification:

```bash
k run test --image=busybox:1.28 --rm -it --restart=Never -- <command>
k run test --image=busybox:1.28 --rm -it --restart=Never -n <namespace> -- <command>
```

Why busybox:1.28 specifically: newer versions changed nslookup output format. This version
works reliably for DNS tests, wget, and shell commands.

Flags: `--rm` (auto-cleanup), `-it` (interactive), `--restart=Never` (Pod, not Deployment).

## Service Verification

```bash
# Is the service reachable?
k run t --image=busybox:1.28 --rm -it --restart=Never -- wget -qO- http://SVC.NS:PORT --timeout=3

# Does the service have endpoints?
k get ep SVC -n NS
# If <none> → selector doesn't match any pod labels

# NodePort from outside
curl http://<node-ip>:<nodePort>
k get svc SVC -o jsonpath='{.spec.ports[0].nodePort}'
```

## DNS Verification

```bash
# Service DNS
k run t --image=busybox:1.28 --rm -it --restart=Never -- nslookup SVC.NS.svc.cluster.local

# General cluster DNS
k run t --image=busybox:1.28 --rm -it --restart=Never -- nslookup kubernetes.default

# Pod's DNS config
k run t --image=busybox:1.28 --rm -it --restart=Never -- cat /etc/resolv.conf

# CoreDNS health
k get deploy coredns -n kube-system
k get ep kube-dns -n kube-system
```

## Network Policy Verification

```bash
# Test ALLOWED traffic (use labels matching the policy's allowed selector)
k run t --image=busybox:1.28 --rm -it --restart=Never -n SOURCE_NS --labels="app=allowed" -- wget -qO- http://TARGET_SVC.TARGET_NS:PORT --timeout=3
# Should return content

# Test BLOCKED traffic (use labels that DON'T match)
k run t --image=busybox:1.28 --rm -it --restart=Never -n SOURCE_NS --labels="app=blocked" -- wget -qO- http://TARGET_SVC.TARGET_NS:PORT --timeout=3
# Should timeout

# ALWAYS use --timeout to avoid hanging on blocked connections
```

## RBAC Verification

```bash
# Can a ServiceAccount do something?
k auth can-i VERB RESOURCE --as=system:serviceaccount:NS:SA_NAME -n NS

# Examples
k auth can-i create pods --as=system:serviceaccount:default:mysa -n default
k auth can-i get secrets --as=system:serviceaccount:prod:deploy-bot -n prod
k auth can-i delete nodes --as=system:serviceaccount:default:mysa  # cluster-scoped

# List all permissions
k auth can-i --list --as=system:serviceaccount:NS:SA_NAME -n NS
```

## Storage Verification

```bash
# PV/PVC bound?
k get pv
k get pvc -n NS
# Both should show STATUS=Bound

# Can a pod read/write the volume?
k exec POD -n NS -- sh -c 'echo "test" > /mount/path/test.txt && cat /mount/path/test.txt'

# Data persists after pod restart?
k exec POD -- sh -c 'echo "persistent" > /data/test.txt'
k delete pod POD
k get pods -w    # Wait for new pod
k exec NEW_POD -- cat /data/test.txt
```

## Deployment / Workload Verification

```bash
# Rollout status
k rollout status deploy NAME -n NS

# Correct image?
k get deploy NAME -o jsonpath='{.spec.template.spec.containers[0].image}'

# All pods running correct image?
k get pods -l app=LABEL -o jsonpath='{range .items[*]}{.spec.containers[0].image}{"\n"}{end}'

# ConfigMap/Secret mounted?
k exec POD -- env | grep VARIABLE          # env var
k exec POD -- cat /path/to/mount/KEY       # volume mount

# Pod scheduled on correct node?
k get pod POD -o wide                      # check NODE column
k get node NODE --show-labels | grep LABEL  # verify node labels

# HPA active?
k get hpa -n NS
```

## Cluster Lifecycle Verification

```bash
# After upgrade — check node version
kubectl get nodes
# VERSION column should show new version

# Control plane healthy?
kubectl get pods -n kube-system
# All should be Running

# etcd backup valid?
ETCDCTL_API=3 etcdctl snapshot status /path/to/backup.db --write-table

# After etcd restore — resources recovered?
kubectl get deployments -A
kubectl get services -A

# Helm release installed?
helm list -n NS
helm status RELEASE -n NS
helm get values RELEASE -n NS
```

## Troubleshooting Verification

```bash
# Node healthy?
k get nodes                                # STATUS=Ready
k describe node NODE | grep -A5 Conditions # All conditions normal

# Kubelet running?
systemctl status kubelet
journalctl -u kubelet --no-pager | tail -20

# Pod issues?
k get events --sort-by='.lastTimestamp' -n NS
k describe pod POD -n NS                  # Events section
k logs POD -n NS                          # Current logs
k logs POD -n NS --previous               # Previous container logs
```

## Speed Patterns (exam muscle memory)

| What to verify | Command |
|----------------|---------|
| Service works | `k run t --image=busybox:1.28 --rm -it --restart=Never -- wget -qO- http://SVC.NS:PORT --timeout=3` |
| DNS works | `k run t --image=busybox:1.28 --rm -it --restart=Never -- nslookup SVC.NS.svc.cluster.local` |
| Traffic blocked | `k run t --image=busybox:1.28 --rm -it --restart=Never -n NS --labels="app=X" -- wget -qO- http://TARGET --timeout=3` |
| RBAC works | `k auth can-i VERB RESOURCE --as=system:serviceaccount:NS:SA -n NS` |
| Data persisted | `k exec POD -- cat /mount/path/file` |
| Right image | `k get deploy NAME -o jsonpath='{.spec.template.spec.containers[0].image}'` |
| Endpoints exist | `k get ep SVC -n NS` |
