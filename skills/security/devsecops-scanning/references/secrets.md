# Secret Scanning Reference

## 1. Secret Scanning Tools

### TruffleHog
```yaml
# GitHub Actions — scan PR diff
- uses: trufflesecurity/trufflehog@v3
  with:
    path: ./
    base: ${{ github.event.pull_request.base.sha }}
    head: ${{ github.event.pull_request.head.sha }}
    extra_args: --only-verified    # Only alert on verified secrets
```

```bash
# CLI — full history scan
trufflehog git https://github.com/org/repo --only-verified

# Scan filesystem
trufflehog filesystem ./src/ --only-verified

# Scan specific commit range
trufflehog git file://. --since-commit abc1234 --branch main
```

### GitLeaks
```yaml
# GitHub Actions
- uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

```bash
# CLI
gitleaks detect --source . --verbose
gitleaks detect --source . --log-opts="--since=2024-01-01"

# Pre-commit hook
gitleaks protect --staged
```

### GitLeaks Configuration
```toml
# .gitleaks.toml
[allowlist]
description = "Global allowlist"
paths = [
    '''\.test\.''',
    '''test/fixtures/''',
    '''__mocks__/''',
]

[[rules]]
id = "custom-api-key"
description = "Custom API key pattern"
regex = '''MYAPP_API_KEY_[A-Za-z0-9]{32}'''
tags = ["key", "api"]

[[rules.allowlist]]
description = "Test keys"
regexes = ['''MYAPP_API_KEY_test_[a-z]+''']
```

### Pre-commit Integration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.4
    hooks:
      - id: gitleaks

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

### GitHub Push Protection
Enable in: Repository → Settings → Code Security → Secret scanning → Push protection.
Blocks pushes containing known secret patterns (API keys, tokens, passwords).

---
