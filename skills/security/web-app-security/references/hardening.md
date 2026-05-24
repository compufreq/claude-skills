# WAF & Security Headers Hardening Reference

## 1. Security Headers

### Essential Headers
```nginx
# Nginx configuration
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "0" always;  # Deprecated but set to 0
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# Content Security Policy (tune per application)
add_header Content-Security-Policy "
  default-src 'self';
  script-src 'self' https://cdn.example.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self' https://fonts.gstatic.com;
  connect-src 'self' https://api.example.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
" always;
```

### Header Explanation

| Header | Purpose | Value |
|--------|---------|-------|
| `X-Content-Type-Options` | Prevent MIME sniffing | `nosniff` |
| `X-Frame-Options` | Prevent clickjacking | `DENY` or `SAMEORIGIN` |
| `Strict-Transport-Security` | Force HTTPS | `max-age=31536000; includeSubDomains` |
| `Content-Security-Policy` | Prevent XSS, data injection | Allowlist sources |
| `Referrer-Policy` | Control referrer info leakage | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | Disable browser features | `camera=(), microphone=()` |
| `X-XSS-Protection` | Deprecated XSS filter | `0` (disable, use CSP instead) |

### CORS Configuration
```python
# ❌ NEVER allow * with credentials
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true  # This combination is blocked by browsers

# ✅ Specific origins with credentials
CORS_ORIGINS = ["https://app.example.com", "https://admin.example.com"]

@app.after_request
def add_cors(response):
    origin = request.headers.get('Origin')
    if origin in CORS_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '3600'
    return response
```

## 2. WAF Configuration

### AWS WAF Rules (Essential)
```hcl
resource "aws_wafv2_web_acl" "main" {
  name  = "api-protection"
  scope = "REGIONAL"
  default_action { allow {} }

  # OWASP Core Rule Set
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 1
    override_action { none {} }
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesCommonRuleSet"
      }
    }
    visibility_config { cloudwatch_metrics_enabled = true; metric_name = "common"; sampled_requests_enabled = true }
  }

  # SQL Injection
  rule {
    name     = "SQLiRuleSet"
    priority = 2
    override_action { none {} }
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesSQLiRuleSet"
      }
    }
    visibility_config { cloudwatch_metrics_enabled = true; metric_name = "sqli"; sampled_requests_enabled = true }
  }

  # Known Bad Inputs
  rule {
    name     = "KnownBadInputsRuleSet"
    priority = 3
    override_action { none {} }
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
      }
    }
    visibility_config { cloudwatch_metrics_enabled = true; metric_name = "badinputs"; sampled_requests_enabled = true }
  }

  # IP Rate Limiting
  rule {
    name     = "RateLimit"
    priority = 4
    action   { block {} }
    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }
    visibility_config { cloudwatch_metrics_enabled = true; metric_name = "ratelimit"; sampled_requests_enabled = true }
  }

  # Bot Control (optional, additional cost)
  rule {
    name     = "BotControl"
    priority = 5
    override_action { none {} }
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesBotControlRuleSet"
        managed_rule_group_configs {
          aws_managed_rules_bot_control_rule_set {
            inspection_level = "COMMON"
          }
        }
      }
    }
    visibility_config { cloudwatch_metrics_enabled = true; metric_name = "botcontrol"; sampled_requests_enabled = true }
  }

  visibility_config { cloudwatch_metrics_enabled = true; metric_name = "waf"; sampled_requests_enabled = true }
}
```



---
