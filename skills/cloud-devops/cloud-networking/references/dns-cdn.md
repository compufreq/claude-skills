# DNS Reference

## Table of Contents
1. AWS Route 53
2. Azure DNS
3. Routing Policies
4. Domain Management
5. Certificate Management

---

## 1. AWS Route 53

### Hosted Zone
```hcl
resource "aws_route53_zone" "main" {
  name = "example.com"
}

# Private hosted zone (internal DNS)
resource "aws_route53_zone" "internal" {
  name = "internal.example.com"
  vpc { vpc_id = module.vpc.vpc_id }
}

# A record → ALB
resource "aws_route53_record" "app" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "app.example.com"
  type    = "A"
  alias {
    name                   = aws_lb.app.dns_name
    zone_id                = aws_lb.app.zone_id
    evaluate_target_health = true
  }
}

# A record → CloudFront
resource "aws_route53_record" "cdn" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "cdn.example.com"
  type    = "A"
  alias {
    name                   = aws_cloudfront_distribution.main.domain_name
    zone_id                = aws_cloudfront_distribution.main.hosted_zone_id
    evaluate_target_health = false
  }
}

# MX record
resource "aws_route53_record" "mx" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "example.com"
  type    = "MX"
  ttl     = 300
  records = [
    "10 mail1.example.com",
    "20 mail2.example.com",
  ]
}

# TXT record (SPF, DKIM, verification)
resource "aws_route53_record" "spf" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "example.com"
  type    = "TXT"
  ttl     = 300
  records = ["v=spf1 include:_spf.google.com ~all"]
}
```

### Health Checks
```hcl
resource "aws_route53_health_check" "app" {
  fqdn              = "app.example.com"
  port               = 443
  type               = "HTTPS"
  resource_path      = "/health"
  failure_threshold  = 3
  request_interval   = 30
  measure_latency    = true

  tags = { Name = "app-health-check" }
}
```

---

## 2. Azure DNS

### DNS Zone
```hcl
resource "azurerm_dns_zone" "main" {
  name                = "example.com"
  resource_group_name = azurerm_resource_group.main.name
}

# A record → Public IP
resource "azurerm_dns_a_record" "app" {
  name                = "app"
  zone_name           = azurerm_dns_zone.main.name
  resource_group_name = azurerm_resource_group.main.name
  ttl                 = 300
  target_resource_id  = azurerm_public_ip.agw.id
}

# CNAME record
resource "azurerm_dns_cname_record" "www" {
  name                = "www"
  zone_name           = azurerm_dns_zone.main.name
  resource_group_name = azurerm_resource_group.main.name
  ttl                 = 300
  record              = "app.example.com"
}

# Private DNS Zone (internal)
resource "azurerm_private_dns_zone" "internal" {
  name                = "internal.example.com"
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "main" {
  name                  = "vnet-link"
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.internal.name
  virtual_network_id    = azurerm_virtual_network.main.id
  registration_enabled  = true  # Auto-register VM DNS names
}
```

---

## 3. Routing Policies

### AWS Route 53 Routing

| Policy | Use Case | Example |
|--------|---------|---------|
| **Simple** | Single resource | One ALB |
| **Weighted** | A/B testing, gradual migration | 90% primary, 10% canary |
| **Latency** | Multi-region, best performance | Route to nearest region |
| **Failover** | Active-passive HA | Primary + DR site |
| **Geolocation** | Country/region-based | EU users → EU servers |
| **Multi-value** | Multiple healthy endpoints | Up to 8 IPs, health-checked |

```hcl
# Weighted routing (canary)
resource "aws_route53_record" "app_primary" {
  zone_id        = aws_route53_zone.main.zone_id
  name           = "app.example.com"
  type           = "A"
  set_identifier = "primary"

  weighted_routing_policy { weight = 90 }

  alias {
    name                   = aws_lb.primary.dns_name
    zone_id                = aws_lb.primary.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "app_canary" {
  zone_id        = aws_route53_zone.main.zone_id
  name           = "app.example.com"
  type           = "A"
  set_identifier = "canary"

  weighted_routing_policy { weight = 10 }

  alias {
    name                   = aws_lb.canary.dns_name
    zone_id                = aws_lb.canary.zone_id
    evaluate_target_health = true
  }
}

# Failover routing
resource "aws_route53_record" "app_failover_primary" {
  zone_id        = aws_route53_zone.main.zone_id
  name           = "app.example.com"
  type           = "A"
  set_identifier = "primary"

  failover_routing_policy { type = "PRIMARY" }
  health_check_id = aws_route53_health_check.primary.id

  alias {
    name                   = aws_lb.primary.dns_name
    zone_id                = aws_lb.primary.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "app_failover_secondary" {
  zone_id        = aws_route53_zone.main.zone_id
  name           = "app.example.com"
  type           = "A"
  set_identifier = "secondary"

  failover_routing_policy { type = "SECONDARY" }

  alias {
    name                   = aws_lb.secondary.dns_name
    zone_id                = aws_lb.secondary.zone_id
    evaluate_target_health = true
  }
}

# Latency-based routing (multi-region)
resource "aws_route53_record" "app_us" {
  zone_id        = aws_route53_zone.main.zone_id
  name           = "app.example.com"
  type           = "A"
  set_identifier = "us-east-1"

  latency_routing_policy { region = "us-east-1" }

  alias {
    name                   = aws_lb.us.dns_name
    zone_id                = aws_lb.us.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "app_eu" {
  zone_id        = aws_route53_zone.main.zone_id
  name           = "app.example.com"
  type           = "A"
  set_identifier = "eu-west-1"

  latency_routing_policy { region = "eu-west-1" }

  alias {
    name                   = aws_lb.eu.dns_name
    zone_id                = aws_lb.eu.zone_id
    evaluate_target_health = true
  }
}
```

### Azure Traffic Manager (DNS-level routing)
```hcl
resource "azurerm_traffic_manager_profile" "main" {
  name                   = "${var.project}-tm"
  resource_group_name    = azurerm_resource_group.main.name
  traffic_routing_method = "Performance"    # or Priority, Weighted, Geographic

  dns_config {
    relative_name = var.project
    ttl           = 60
  }

  monitor_config {
    protocol = "HTTPS"
    port     = 443
    path     = "/health"
  }
}

resource "azurerm_traffic_manager_azure_endpoint" "primary" {
  name               = "primary"
  profile_id         = azurerm_traffic_manager_profile.main.id
  target_resource_id = azurerm_public_ip.primary.id
  priority           = 1
  weight             = 100
}
```

---

## 4. Domain Management

### Domain Registration Best Practices
1. Register domains with the cloud provider (Route 53, Azure) or a dedicated registrar
2. Enable DNSSEC for domain integrity
3. Enable domain lock (transfer protection)
4. Set up auto-renewal
5. Use separate accounts for domain registration (security isolation)
6. Document all domains in a registry

### DNS TTL Guidelines

| Record Type | Recommended TTL | Why |
|------------|----------------|-----|
| Production A/AAAA | 60-300s | Fast failover |
| CNAME | 300-3600s | Moderate change frequency |
| MX | 3600s | Rarely changes |
| TXT (SPF, DKIM) | 3600s | Rarely changes |
| NS | 86400s (24h) | Very rarely changes |
| During migration | 60s | Fast rollback if needed |

---

## 5. Certificate Management

### AWS Certificate Manager (ACM)
```hcl
resource "aws_acm_certificate" "main" {
  domain_name               = "example.com"
  subject_alternative_names = ["*.example.com"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.main.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  zone_id = aws_route53_zone.main.zone_id
  name    = each.value.name
  type    = each.value.type
  ttl     = 60
  records = [each.value.record]
}

resource "aws_acm_certificate_validation" "main" {
  certificate_arn         = aws_acm_certificate.main.arn
  validation_record_fqdns = [for r in aws_route53_record.cert_validation : r.fqdn]
}
```

### Cert-Manager on Kubernetes
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: certs@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
      - http01:
          ingress:
            class: nginx
      - dns01:
          route53:
            region: us-east-1
            hostedZoneID: Z1234567890
```



---
