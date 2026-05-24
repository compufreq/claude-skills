# CKA Lab Exercises — Home Lab & KillerKoda

This reference contains lab exercise templates organized by domain. When generating labs for the user,
adapt these templates to their specific home lab setup and skill level.

## How to Generate Labs

For home lab exercises:
- Ask about their cluster topology (number of control-plane nodes, workers, CNI plugin)
- Generate setup scripts that create the initial broken or empty state
- Always provide verification scripts
- Include cleanup commands
- Suggest a time limit matching exam pacing (~5-7 minutes per question)

For KillerKoda recommendations:
- Link to https://killercoda.com/cka for CKA-specific scenarios
- Note which domain and competency each scenario covers
- KillerKoda environments are single-node; HA exercises should use the home lab

## Sample Exercises by Domain

### Domain 1: Cluster Architecture, Installation and Configuration (25%)

**Exercise: RBAC Configuration**
```
Objective: Create a ServiceAccount 'deploy-manager' in namespace 'production' that can
only create, list, and delete deployments and services in that namespace.

Tasks:
1. Create the namespace 'production' if it doesn't exist
2. Create the ServiceAccount 'deploy-manager' in 'production'
3. Create a Role with the specified permissions
4. Bind the Role to the ServiceAccount
5. Verify by running a kubectl command as the ServiceAccount

Verification:
kubectl auth can-i create deployments --as=system:serviceaccount:production:deploy-manager -n production
# Should return: yes
kubectl auth can-i create pods --as=system:serviceaccount:production:deploy-manager -n production
# Should return: no
kubectl auth can-i create deployments --as=system:serviceaccount:production:deploy-manager -n default
# Should return: no
```

**Exercise: etcd Backup and Restore**
```
Objective: Back up the etcd cluster, delete a deployment, then restore from backup.

Setup:
kubectl create deployment etcd-test --image=nginx --replicas=3 -n default

Tasks:
1. Take a snapshot of etcd to /tmp/etcd-snapshot.db
2. Verify the snapshot
3. Delete the etcd-test deployment
4. Restore etcd from the snapshot
5. Verify the deployment is back

Notes: This exercise is best done on the home lab since it requires
direct access to etcd certificates and the static pod manifest.
```

**Exercise: Cluster Upgrade with kubeadm**
```
Objective: Upgrade the cluster from the current version to the next minor version.

Tasks:
1. Check the current cluster version
2. Drain a worker node
3. Upgrade kubeadm on the worker
4. Upgrade the node configuration
5. Upgrade kubelet and kubectl
6. Uncordon the node
7. Verify the node shows the new version

Notes: This is a critical exam topic. Practice on the home lab.
```

**Exercise: Helm and Kustomize**
```
Objective: Install an application using Helm and customize it with Kustomize.

Tasks (Helm):
1. Add the bitnami Helm repo
2. Search for the nginx chart
3. Install nginx with custom values (replicas=2, service.type=NodePort)
4. Verify the installation
5. Upgrade the release to change replicas to 3

Tasks (Kustomize):
1. Create a base deployment YAML for nginx
2. Create a kustomization.yaml that adds a common label
3. Create an overlay that changes the replica count
4. Apply using kubectl apply -k
5. Verify the labels and replica count
```

### Domain 2: Troubleshooting (30%)

**Exercise: Broken Node**
```
Objective: A worker node is NotReady. Find and fix the issue.

Setup script (run on the worker node as root):
systemctl stop kubelet
# Or for a harder variant:
mv /etc/kubernetes/kubelet.conf /etc/kubernetes/kubelet.conf.bak

Tasks:
1. Identify which node is NotReady
2. SSH to the node
3. Diagnose the issue
4. Fix it
5. Verify the node returns to Ready state

Verification:
kubectl get nodes  # All nodes should be Ready
```

**Exercise: Broken Deployment**
```
Objective: A deployment is not creating pods successfully. Debug and fix.

Setup:
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: broken-app
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: broken-app
  template:
    metadata:
      labels:
        app: broken
    spec:
      containers:
      - name: app
        image: nginx:nonexistent-tag
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "999Gi"
EOF

Tasks:
1. Identify why pods are not running
2. There are multiple issues — find and fix all of them
3. Verify all 3 replicas are running

Issues to find:
- Label mismatch (selector vs template labels)
- Non-existent image tag
- Impossible memory request
```

**Exercise: DNS Troubleshooting**
```
Objective: Pods cannot resolve service names. Diagnose and fix CoreDNS.

Setup (run as admin):
kubectl scale deploy coredns -n kube-system --replicas=0

Tasks:
1. Create a test pod and verify DNS is broken
2. Identify the CoreDNS issue
3. Fix it
4. Verify DNS resolution works

Verification:
kubectl run dns-test --image=busybox:1.28 --rm -it --restart=Never -- nslookup kubernetes.default
# Should resolve successfully
```

### Domain 3: Workloads and Scheduling (15%)

**Exercise: Rolling Update and Rollback**
```
Objective: Perform a rolling update and then rollback.

Setup:
kubectl create deployment web-app --image=nginx:1.19 --replicas=4

Tasks:
1. Update the deployment to nginx:1.21 using a rolling update strategy
   with maxSurge=1 and maxUnavailable=1
2. Monitor the rollout status
3. Check rollout history
4. Rollback to the previous version
5. Verify the rollback

Verification:
kubectl rollout status deploy web-app
kubectl get deploy web-app -o jsonpath='{.spec.template.spec.containers[0].image}'
# Should show nginx:1.19
```

**Exercise: Pod Scheduling with Affinity and Taints**
```
Objective: Schedule pods based on node affinity and taints.

Tasks:
1. Label a worker node with 'disk=ssd'
2. Create a pod that uses nodeAffinity to only schedule on disk=ssd nodes
3. Taint another node with 'env=production:NoSchedule'
4. Create a pod with a toleration for that taint
5. Create a pod without the toleration and verify it doesn't schedule on the tainted node

Verification:
kubectl get pods -o wide  # Check node assignments
```

**Exercise: HPA Configuration**
```
Objective: Configure Horizontal Pod Autoscaler.

Prerequisites: metrics-server must be installed.

Tasks:
1. Create a deployment running an image that generates CPU load
2. Set resource requests (cpu: 100m)
3. Create an HPA with min=1, max=5, target CPU utilization=50%
4. Generate load and watch the HPA scale up
5. Remove load and watch it scale down

Verification:
kubectl get hpa
kubectl get pods  # Count should change based on load
```

### Domain 4: Services and Networking (20%)

**Exercise: Network Policies**
```
Objective: Implement network segmentation using Network Policies.

Setup:
kubectl create ns frontend
kubectl create ns backend
kubectl run web --image=nginx -n frontend --labels="app=web" --expose --port=80
kubectl run api --image=nginx -n backend --labels="app=api" --expose --port=80
kubectl run db --image=nginx -n backend --labels="app=db" --expose --port=80

Tasks:
1. Create a default-deny ingress policy for the backend namespace
2. Allow the 'api' pod to receive traffic from 'web' pods in the frontend namespace
3. Allow the 'db' pod to receive traffic only from 'api' pods in the same namespace
4. Verify web->api works, web->db is blocked, api->db works

Verification:
kubectl run test --image=busybox:1.28 --rm -it -n frontend --restart=Never -- wget -qO- --timeout=3 http://api.backend.svc:80
# Should succeed
kubectl run test --image=busybox:1.28 --rm -it -n frontend --restart=Never -- wget -qO- --timeout=3 http://db.backend.svc:80
# Should timeout/fail
```

**Exercise: Gateway API**
```
Objective: Configure Gateway API for traffic routing.

Prerequisites: A Gateway API controller must be installed (e.g., nginx-gateway).

Tasks:
1. Create a GatewayClass resource
2. Create a Gateway that listens on port 80
3. Create two deployments: 'app-v1' and 'app-v2'
4. Create HTTPRoute rules that split traffic 80/20 between v1 and v2
5. Verify traffic routing

Notes: If Gateway API controller is not available on the home lab,
use KillerKoda or focus on Ingress resources instead.
```

**Exercise: Service Types and Endpoints**
```
Objective: Create different service types and understand endpoint resolution.

Tasks:
1. Create a deployment with 3 replicas
2. Expose it as ClusterIP, verify internal access
3. Change to NodePort, verify external access via node IP
4. Create a headless service (clusterIP: None) and verify DNS returns pod IPs
5. Check endpoints for each service type

Verification:
kubectl get endpoints <service-name>
# Should show pod IPs
```

### Domain 5: Storage (10%)

**Exercise: Dynamic Volume Provisioning**
```
Objective: Set up dynamic volume provisioning with StorageClass.

Tasks:
1. Create a StorageClass with a provisioner appropriate for your environment
2. Create a PVC requesting 1Gi with the StorageClass
3. Create a Pod that mounts the PVC
4. Write data to the volume
5. Delete the Pod, create a new Pod mounting the same PVC
6. Verify the data persists

Verification:
kubectl get pv  # A PV should be auto-created
kubectl exec <new-pod> -- cat /data/test.txt  # Data should persist
```

**Exercise: PV and PVC Lifecycle**
```
Objective: Understand the PV-PVC binding lifecycle and reclaim policies.

Tasks:
1. Create a PV with 'Retain' reclaim policy, 2Gi capacity, ReadWriteOnce
2. Create a PVC requesting 1Gi — verify it binds to the PV
3. Create a Pod using the PVC
4. Delete the Pod and PVC
5. Observe the PV status (should be 'Released', not 'Available')
6. Manually reclaim the PV by removing the claimRef
7. Create a new PV with 'Delete' reclaim policy and repeat — observe auto-deletion

Verification:
kubectl get pv  # Check STATUS column through the lifecycle
```

## KillerKoda Scenario Recommendations

For each domain, recommend these KillerKoda categories:
- **Cluster Architecture:** kubeadm setup, RBAC, cluster upgrade scenarios
- **Troubleshooting:** Broken cluster, broken pod, networking issues
- **Workloads:** Deployment strategies, ConfigMaps, scheduling
- **Networking:** Services, Network Policies, DNS
- **Storage:** PV/PVC, StorageClass

Direct users to: https://killercoda.com/cka

Also recommend killer.sh (2 free attempts with exam purchase) as the most realistic exam simulator.

## Mock Exam Structure

When generating a full mock exam:
- 15-20 questions total
- 2-hour time limit
- Weight distribution matching the domains:
  - 4-5 questions on Cluster Architecture (25%)
  - 5-6 questions on Troubleshooting (30%)
  - 2-3 questions on Workloads (15%)
  - 3-4 questions on Networking (20%)
  - 1-2 questions on Storage (10%)
- Each question specifies: cluster context, namespace, weight, task
- Mix of difficulty levels
- Include at least one multi-part question
