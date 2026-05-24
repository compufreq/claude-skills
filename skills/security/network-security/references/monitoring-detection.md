# Network Monitoring & Threat Detection Reference

## 1. Network Monitoring Tools

| Tool | Type | Use Case |
|------|------|---------|
| **VPC Flow Logs / NSG Flow Logs** | Cloud-native | All cloud network traffic metadata |
| **Wireshark / tshark** | Packet capture | Deep packet analysis |
| **tcpdump** | Packet capture | Quick CLI capture |
| **Zeek (Bro)** | Network analysis | Protocol analysis, anomaly detection |
| **GuardDuty** | AWS threat detection | Automated threat intelligence |
| **Defender for Cloud** | Azure threat detection | Automated security alerts |

## 2. VPC Flow Log Analysis

### AWS VPC Flow Logs
```hcl
resource "aws_flow_log" "main" {
  vpc_id          = module.vpc.vpc_id
  traffic_type    = "ALL"
  iam_role_arn    = aws_iam_role.flow_log.arn
  log_destination = aws_cloudwatch_log_group.flow_log.arn

  tags = { Name = "${var.project}-flow-logs" }
}
```

### CloudWatch Insights Queries for Threat Detection
```sql
-- Top talkers (potential data exfiltration)
fields @timestamp, srcAddr, dstAddr, bytes
| stats sum(bytes) as totalBytes by srcAddr, dstAddr
| sort totalBytes desc
| limit 20

-- Rejected connections (potential scanning)
fields @timestamp, srcAddr, dstAddr, dstPort, action
| filter action = "REJECT"
| stats count(*) as rejections by srcAddr, dstPort
| sort rejections desc
| limit 20

-- Unusual ports (potential backdoor)
fields @timestamp, srcAddr, dstAddr, dstPort
| filter dstPort not in [22, 80, 443, 5432, 6379, 8080]
| filter action = "ACCEPT"
| stats count(*) as connections by dstPort
| sort connections desc

-- Traffic to known-bad IPs (integrate threat intel)
fields @timestamp, srcAddr, dstAddr, dstPort, bytes
| filter dstAddr in ["1.2.3.4", "5.6.7.8"]
| sort @timestamp desc
```

## 3. AWS GuardDuty
```hcl
resource "aws_guardduty_detector" "main" {
  enable = true

  datasources {
    s3_logs      { enable = true }
    kubernetes   { audit_logs { enable = true } }
    malware_protection { scan_ec2_instance_with_findings { ebs_volumes { enable = true } } }
  }
}
```

### Common GuardDuty Finding Types
| Finding | Severity | Meaning |
|---------|----------|---------|
| `UnauthorizedAccess:EC2/MaliciousIPCaller` | High | EC2 communicating with known bad IP |
| `Recon:EC2/PortProbeUnprotectedPort` | Low | Port scan detected |
| `CryptoCurrency:EC2/BitcoinTool` | High | Crypto mining detected |
| `UnauthorizedAccess:IAMUser/MaliciousIPCaller` | Medium | API calls from suspicious IP |
| `Backdoor:EC2/C&CActivity` | High | Command and control communication |

## 4. DDoS Protection

### AWS Shield + WAF
```hcl
# Shield Advanced (for critical workloads)
resource "aws_shield_protection" "alb" {
  name         = "${var.project}-alb-shield"
  resource_arn = aws_lb.app.arn
}

# WAF rate limiting (basic DDoS mitigation)
# See web-app-security skill for WAF configuration
```

### Azure DDoS Protection
```hcl
resource "azurerm_network_ddos_protection_plan" "main" {
  name                = "${var.project}-ddos"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_virtual_network" "main" {
  # ...
  ddos_protection_plan {
    id     = azurerm_network_ddos_protection_plan.main.id
    enable = true
  }
}
```

## 5. Incident Detection Playbook

### Network Security Alert Response
```
1. DETECT — Alert fires (GuardDuty, IDS, flow log anomaly)
2. TRIAGE — Is this a true positive? Check context, recent changes
3. CONTAIN — Block source IP (SG/NACL/NSG), isolate affected instance
4. INVESTIGATE — Analyze flow logs, packet captures, system logs
5. ERADICATE — Remove threat (malware, backdoor, compromised creds)
6. RECOVER — Restore from clean backup, verify integrity
7. LESSONS — Post-incident review, update detection rules
```



---
