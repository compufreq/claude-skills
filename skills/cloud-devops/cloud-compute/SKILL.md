---
name: cloud-compute
description: >
  Comprehensive cloud compute skill covering virtual machines, serverless functions, container
  compute, and auto-scaling across AWS and Azure. Use this skill whenever the user mentions EC2,
  launch template, auto scaling group, ASG, spot instance, reserved instance, savings plan,
  Lambda, serverless function, Azure Functions, cold start, function trigger, event-driven,
  ECS, Fargate, App Runner, Azure Container Instances, ACI, Azure App Service, container compute,
  auto-scaling, target tracking, step scaling, predictive scaling, HPA, VMSS, scale set,
  compute optimization, right-sizing, spot fleet, or any request involving provisioning compute
  resources, designing serverless architectures, running containers as a service, or implementing
  auto-scaling strategies. Also trigger when the user asks about instance type selection, cost
  optimization for compute, serverless vs containers decisions, or multi-cloud compute patterns.
---

# Cloud Compute

A production-grade skill for provisioning and managing compute resources across AWS and Azure,
covering VMs, serverless, containers, and auto-scaling.

## Quick Reference

| Compute Type | AWS | Azure | Reference |
|-------------|-----|-------|-----------|
| Virtual Machines | EC2 | Virtual Machines | `references/virtual-machines.md` |
| Serverless | Lambda | Azure Functions | `references/serverless.md` |
| Containers | ECS/Fargate, App Runner | ACI, App Service | `references/container-compute.md` |
| Auto-Scaling | ASG, Lambda concurrency | VMSS, Function scaling | `references/auto-scaling.md` |

## Compute Decision Framework

```
What's your workload?
│
├── Stateless HTTP API
│   ├── < 15 min per request → Lambda / Azure Functions
│   ├── Always running, < 10 containers → App Runner / App Service
│   └── Complex orchestration → ECS Fargate / AKS
│
├── Background Processing
│   ├── Event-driven, < 15 min → Lambda / Azure Functions
│   ├── Long-running workers → ECS Fargate / ACI
│   └── GPU / ML inference → EC2 GPU / Azure GPU VMs
│
├── Stateful Application
│   ├── Database → RDS / Azure SQL (managed)
│   ├── Legacy app → EC2 / Azure VMs
│   └── Stateful containers → ECS + EBS / AKS + Managed Disks
│
└── Batch Processing
    ├── Parallel, fault-tolerant → AWS Batch / Azure Batch
    ├── Spot-friendly → Spot Instances + ASG
    └── Event-driven → Lambda + SQS / Functions + Queue
```

### Compute Type Comparison

| Factor | VMs | Containers (Fargate) | Serverless |
|--------|-----|---------------------|-----------|
| Startup time | Minutes | Seconds | Milliseconds-seconds |
| Max runtime | Unlimited | Unlimited | 15 min (Lambda) |
| Scaling speed | Minutes | Seconds | Milliseconds |
| Min cost | ~$7/mo (t4g.nano) | ~$10/mo (0.25 vCPU) | $0 (pay per invoke) |
| Ops burden | High (patching, updates) | Medium | Low |
| Control | Full OS access | Container-level | Function-level |
| Best for | Legacy, GPU, stateful | Microservices, APIs | Event-driven, glue code |

---

## Cost Optimization

### AWS Pricing Models

| Model | Savings | Commitment | Best For |
|-------|---------|-----------|---------|
| On-Demand | 0% | None | Dev, unpredictable, short-term |
| Spot | 60-90% | None (can be interrupted) | Batch, fault-tolerant, CI/CD |
| Reserved (1yr) | 30-40% | 1 year | Steady-state production |
| Reserved (3yr) | 50-60% | 3 years | Stable, long-term workloads |
| Savings Plans | 30-60% | $/hr commitment | Flexible across instance types |

### Azure Pricing Models

| Model | Savings | Commitment | Best For |
|-------|---------|-----------|---------|
| Pay-as-you-go | 0% | None | Dev, unpredictable |
| Spot VMs | 60-90% | None (evictable) | Batch, fault-tolerant |
| Reserved (1yr) | 30-40% | 1 year | Steady-state |
| Reserved (3yr) | 50-60% | 3 years | Stable workloads |
| Azure Hybrid Benefit | 40-80% | Existing licenses | Windows/SQL Server |

### Right-Sizing Checklist
1. Monitor CPU utilization — target 40-60% average for production
2. Check memory usage — switch to memory-optimized if > 80%
3. Analyze network I/O — use network-optimized for high throughput
4. Review storage IOPS — match instance to storage needs
5. Use AWS Compute Optimizer / Azure Advisor recommendations
6. Review monthly — workloads change over time

---

## Scripts

### generate_compute_terraform.py
```bash
python scripts/generate_compute_terraform.py \
  --provider aws|azure \
  --compute-type vm|serverless|container \
  --environment production \
  --project myapp \
  --output ./compute/
```

---

## Best Practices

1. **Use managed services first** — Lambda/Functions before EC2/VMs
2. **Right-size everything** — review quarterly with cloud advisor tools
3. **Spot for fault-tolerant workloads** — 60-90% savings
4. **Reserved/Savings Plans for baseline** — commit to steady-state usage
5. **Auto-scale everything** — never manually adjust capacity
6. **Immutable deployments** — replace, don't update (new AMIs, new task definitions)
7. **Multi-AZ for production** — spread across failure domains
8. **Use ARM/Graviton** — 20-40% better price/performance
9. **Monitor cold starts** — optimize for serverless latency-sensitive workloads
10. **Tag all compute** — cost allocation, ownership, environment



---
