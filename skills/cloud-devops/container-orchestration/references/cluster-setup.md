# Cluster Setup Reference

## Table of Contents
1. Managed vs Self-Hosted
2. AWS EKS
3. Google GKE
4. Azure AKS
5. Essential Add-ons
6. Cluster Sizing

---

## 1. Managed vs Self-Hosted

| Factor | Managed (EKS/GKE/AKS) | Self-Hosted (kubeadm/k3s) |
|--------|----------------------|--------------------------|
| Control plane | Cloud-managed (HA, patched) | You manage everything |
| Cost | Higher (control plane fee + nodes) | Lower (just compute) |
| Operations | Minimal — upgrades, patches handled | Full ops burden |
| Compliance | Cloud certifications (SOC2, HIPAA) | You handle compliance |
| Customization | Limited | Full control |
| Best for | Most production workloads | Edge, air-gapped, cost-sensitive |

**Recommendation:** Use managed Kubernetes unless you have a specific reason not to.

---

## 2. AWS EKS

### Terraform Setup
```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "production"
  cluster_version = "1.31"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets

  cluster_endpoint_public_access = true

  # Managed node groups
  eks_managed_node_groups = {
    general = {
      instance_types = ["m6i.xlarge"]
      min_size       = 3
      max_size       = 10
      desired_size   = 3

      labels = { role = "general" }

      block_device_mappings = {
        xvda = {
          device_name = "/dev/xvda"
          ebs = {
            volume_size = 100
            volume_type = "gp3"
            encrypted   = true
          }
        }
      }
    }
  }

  # Cluster add-ons
  cluster_addons = {
    coredns    = { most_recent = true }
    kube-proxy = { most_recent = true }
    vpc-cni    = { most_recent = true }
    ebs-csi    = { most_recent = true, service_account_role_arn = module.ebs_csi_irsa.iam_role_arn }
  }

  # IRSA (IAM Roles for Service Accounts)
  enable_irsa = true

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}
```

### EKS Essential Setup
```bash
# Configure kubectl
aws eks update-kubeconfig --name production --region us-east-1

# Install AWS Load Balancer Controller
helm install aws-load-balancer-controller \
  eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=production

# Install External DNS
helm install external-dns \
  bitnami/external-dns \
  -n kube-system \
  --set provider=aws
```

### EKS Node Group Types

| Type | Use Case |
|------|---------|
| **Managed Node Group** | General workloads, easy scaling (recommended) |
| **Fargate** | Serverless pods, no node management |
| **Karpenter** | Advanced auto-scaling, spot instances |
| **Self-managed** | Custom AMIs, GPU nodes |

---

## 3. Google GKE

### Terraform Setup
```hcl
resource "google_container_cluster" "primary" {
  name     = "production"
  location = "us-central1"

  # Autopilot (recommended for most workloads)
  enable_autopilot = true

  # Or Standard mode:
  # initial_node_count = 3
  # remove_default_node_pool = true

  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  release_channel {
    channel = "REGULAR"
  }

  addons_config {
    http_load_balancing { disabled = false }
    gce_persistent_disk_csi_driver_config { enabled = true }
  }
}

# Standard mode node pool
resource "google_container_node_pool" "general" {
  name       = "general"
  cluster    = google_container_cluster.primary.name
  location   = "us-central1"

  autoscaling {
    min_node_count = 3
    max_node_count = 10
  }

  node_config {
    machine_type = "e2-standard-4"
    disk_size_gb = 100
    disk_type    = "pd-ssd"

    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }
}
```

### GKE Modes

| Mode | Best For |
|------|---------|
| **Autopilot** | Most workloads — Google manages nodes, scaling, security |
| **Standard** | Custom node configs, GPU, special requirements |

---

## 4. Azure AKS

### Terraform Setup
```hcl
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "production"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "production"
  kubernetes_version  = "1.31"

  default_node_pool {
    name                = "general"
    vm_size             = "Standard_D4s_v3"
    min_count           = 3
    max_count           = 10
    enable_auto_scaling = true
    os_disk_size_gb     = 100
    os_disk_type        = "Managed"
    vnet_subnet_id      = azurerm_subnet.aks.id
    zones               = [1, 2, 3]
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    network_policy    = "azure"
    load_balancer_sku = "standard"
    service_cidr      = "10.0.0.0/16"
    dns_service_ip    = "10.0.0.10"
  }

  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.aks.id
  }

  key_vault_secrets_provider {
    secret_rotation_enabled = true
  }

  tags = { Environment = "production" }
}
```

---

## 5. Essential Add-ons

Install these after cluster creation:

| Add-on | Purpose | Install Method |
|--------|---------|---------------|
| **Ingress Controller** | Route external traffic | Helm (nginx-ingress or cloud-specific) |
| **cert-manager** | TLS certificate automation | Helm |
| **External Secrets Operator** | Sync secrets from cloud vaults | Helm |
| **Prometheus + Grafana** | Monitoring & dashboards | Helm (kube-prometheus-stack) |
| **Loki** | Log aggregation | Helm |
| **ArgoCD / Flux** | GitOps deployment | Helm or CLI |
| **External DNS** | DNS record automation | Helm |
| **Karpenter** (EKS) | Advanced node auto-scaling | Helm |
| **Metrics Server** | HPA support | kubectl apply |

### kube-prometheus-stack (Monitoring)
```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f monitoring-values.yaml
```

### cert-manager
```bash
helm install cert-manager jetstack/cert-manager \
  -n cert-manager --create-namespace \
  --set crds.enabled=true
```

---

## 6. Cluster Sizing

### Node Sizing Guidelines

| Workload Type | Instance Type (AWS) | vCPU | Memory |
|--------------|-------------------|------|--------|
| General API | m6i.xlarge | 4 | 16 GB |
| Memory-intensive | r6i.xlarge | 4 | 32 GB |
| Compute-intensive | c6i.xlarge | 4 | 8 GB |
| GPU (ML) | p3.2xlarge | 8 | 61 GB + V100 |
| Cost-optimized | t3.xlarge | 4 | 16 GB |

### Cluster Sizing Formula
```
Nodes needed = Total pod resource requests / (Node capacity × 0.7)

0.7 factor accounts for:
- System pods (kubelet, kube-proxy, CNI) ~15%
- Overhead (OS, buffers) ~10%
- Headroom for scaling ~5%
```

### Multi-AZ / Multi-Zone
- Always spread nodes across 3+ availability zones
- Use `topologySpreadConstraints` on pods
- PDBs ensure availability during node maintenance
- Minimum 3 nodes (one per AZ) for production



---
