# Firewall & IDS/IPS Reference

## 1. Firewall Architecture

### Defense-in-Depth Layers
```
Internet → Edge Firewall/WAF → Load Balancer → Application Firewall
    → Security Groups/NSGs → Host Firewall → Application
```

### Cloud Security Groups (Best Practices)

| Principle | Implementation |
|-----------|---------------|
| Default deny | Start with no rules, add only what's needed |
| Least privilege | Allow specific ports, protocols, and source CIDRs |
| Reference by SG | `source_security_group_id` not CIDR where possible |
| Separate by function | Different SGs for ALB, app, DB, cache |
| Document every rule | Description field on every rule |
| No 0.0.0.0/0 ingress | Except for public-facing LBs (port 80/443) |
| Restrict egress | Only allow necessary outbound (HTTPS, DB, DNS) |

### Security Group Design Pattern
```
ALB SG:     Ingress: 443 from 0.0.0.0/0
            Egress:  8080 to App SG

App SG:     Ingress: 8080 from ALB SG
            Egress:  5432 to DB SG, 6379 to Cache SG, 443 to 0.0.0.0/0

DB SG:      Ingress: 5432 from App SG
            Egress:  None (or DNS only)

Cache SG:   Ingress: 6379 from App SG
            Egress:  None
```

## 2. IDS/IPS

### IDS vs IPS
| Feature | IDS (Detection) | IPS (Prevention) |
|---------|----------------|-----------------|
| Action | Alert only | Alert + block |
| Placement | Out-of-band (mirror) | Inline |
| Risk | None (passive) | False positives may block legitimate traffic |
| Use case | Monitoring, forensics | Active protection |

### Suricata Rules (Example)
```yaml
# Alert on SQL injection attempt
alert http any any -> $HOME_NET any (msg:"SQL Injection Attempt"; flow:to_server; content:"' OR '1'='1"; sid:1000001; rev:1;)

# Alert on reverse shell
alert tcp $HOME_NET any -> $EXTERNAL_NET any (msg:"Possible Reverse Shell"; flow:established; content:"/bin/sh"; sid:1000002; rev:1;)

# Alert on SSH brute force
alert tcp $EXTERNAL_NET any -> $HOME_NET 22 (msg:"SSH Brute Force"; flow:to_server; threshold:type both, track by_src, count 5, seconds 60; sid:1000003;)
```

### AWS Network Firewall
```hcl
resource "aws_networkfirewall_firewall" "main" {
  name                = "${var.project}-firewall"
  firewall_policy_arn = aws_networkfirewall_firewall_policy.main.arn
  vpc_id              = module.vpc.vpc_id

  subnet_mapping {
    subnet_id = aws_subnet.firewall[0].id
  }
  subnet_mapping {
    subnet_id = aws_subnet.firewall[1].id
  }
}

resource "aws_networkfirewall_rule_group" "block_domains" {
  capacity = 100
  name     = "block-malicious-domains"
  type     = "STATEFUL"
  rule_group {
    rule_variables {
      ip_sets {
        key = "HOME_NET"
        ip_set { definition = [module.vpc.vpc_cidr_block] }
      }
    }
    rules_source {
      rules_source_list {
        generated_rules_type = "DENYLIST"
        target_types         = ["TLS_SNI", "HTTP_HOST"]
        targets              = [".malware.com", ".phishing.net"]
      }
    }
  }
}
```



---
