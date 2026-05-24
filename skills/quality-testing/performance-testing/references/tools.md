# Performance Testing Tools Reference

## 1. Tool Comparison

| Feature | k6 | Locust | JMeter | Artillery |
|---------|-----|--------|--------|----------|
| Language | JavaScript | Python | GUI/XML | YAML/JS |
| Protocol | HTTP, WS, gRPC | HTTP, custom | HTTP, JDBC, FTP+ | HTTP, WS, Socket.io |
| Scripting | Excellent | Excellent | Limited | Good |
| Cloud | Grafana Cloud k6 | Locust.io | BlazeMeter | Artillery Cloud |
| CI integration | Excellent | Good | Medium | Excellent |
| Resource usage | Very low (Go) | Medium | High (Java) | Medium |
| Best for | Developers, CI/CD | Python teams | Enterprise, GUI | Quick YAML tests |

**Recommendation:** k6 for most teams (developer-friendly, CI-native, efficient).

## 2. k6

### Load Test
```javascript
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const orderDuration = new Trend('order_duration');

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 50 },   // Stay at 50
    { duration: '2m', target: 100 },  // Ramp to 100
    { duration: '5m', target: 100 },  // Stay at 100
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
    errors: ['rate<0.05'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://api.example.com';

export default function () {
  // Login
  const loginRes = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
    email: `user${__VU}@example.com`,
    password: 'testpassword',
  }), { headers: { 'Content-Type': 'application/json' } });

  check(loginRes, {
    'login successful': (r) => r.status === 200,
    'has token': (r) => r.json('token') !== undefined,
  }) || errorRate.add(1);

  const token = loginRes.json('token');
  const authHeaders = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };

  sleep(1);

  // Browse products
  group('Browse Products', () => {
    const productsRes = http.get(`${BASE_URL}/api/products?page=1&limit=20`, { headers: authHeaders });
    check(productsRes, {
      'products loaded': (r) => r.status === 200,
      'has products': (r) => r.json('items').length > 0,
    });
  });

  sleep(2);

  // Place order
  group('Place Order', () => {
    const start = Date.now();
    const orderRes = http.post(`${BASE_URL}/api/orders`, JSON.stringify({
      items: [{ sku: 'WIDGET-001', quantity: 1 }],
    }), { headers: authHeaders });

    orderDuration.add(Date.now() - start);
    check(orderRes, {
      'order created': (r) => r.status === 201,
      'has order id': (r) => r.json('id') !== undefined,
    }) || errorRate.add(1);
  });

  sleep(3);
}
```

### k6 Stress Test
```javascript
export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 500 },
    { duration: '5m', target: 500 },
    { duration: '2m', target: 1000 },  // Push to breaking point
    { duration: '5m', target: 1000 },
    { duration: '5m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],  // Relaxed for stress test
    http_req_failed: ['rate<0.10'],     // Allow up to 10% errors
  },
};
```

### k6 in CI (GitHub Actions)
```yaml
- name: Performance Test
  uses: grafana/k6-action@v0.3.1
  with:
    filename: tests/performance/load-test.js
  env:
    BASE_URL: ${{ env.STAGING_URL }}
    K6_CLOUD_TOKEN: ${{ secrets.K6_CLOUD_TOKEN }}
```

## 3. Locust

### Load Test
```python
from locust import HttpUser, task, between, events
import json

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)
    host = "https://api.example.com"

    def on_start(self):
        """Login on start."""
        response = self.client.post("/api/auth/login", json={
            "email": f"user{self.environment.runner.user_count}@example.com",
            "password": "testpassword",
        })
        self.token = response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(5)  # Weight: 5x more likely than other tasks
    def browse_products(self):
        self.client.get("/api/products?page=1&limit=20", headers=self.headers)

    @task(3)
    def search_products(self):
        self.client.get("/api/products/search?q=widget", headers=self.headers)

    @task(1)
    def place_order(self):
        self.client.post("/api/orders", json={
            "items": [{"sku": "WIDGET-001", "quantity": 1}]
        }, headers=self.headers)
```

### Run Locust
```bash
# Web UI mode
locust -f tests/performance/locustfile.py --host=https://api.example.com

# Headless (CI-friendly)
locust -f tests/performance/locustfile.py \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 10m \
  --host https://api.example.com \
  --csv results \
  --html report.html
```

## 4. JMeter (CLI for CI)

```bash
# Run JMeter in non-GUI mode
jmeter -n \
  -t tests/performance/load-test.jmx \
  -l results.jtl \
  -e -o report/ \
  -Jthreads=100 \
  -Jrampup=60 \
  -Jduration=600

# Docker
docker run --rm -v $(pwd)/tests:/tests \
  justb4/jmeter:5.5 \
  -n -t /tests/load-test.jmx -l /tests/results.jtl
```

## 5. Test Data Management

### Strategies

| Strategy | Pros | Cons |
|----------|------|------|
| Shared test accounts | Simple setup | Contention, unrealistic |
| Pre-generated users | Realistic, no contention | Requires setup/cleanup |
| Dynamic creation | Most realistic | Adds overhead, needs cleanup |
| Production-like seed | Best data distribution | Privacy concerns, setup effort |

### k6 Data File
```javascript
import { SharedArray } from 'k6/data';
import papaparse from 'https://jslib.k6.io/papaparse/5.1.1/index.js';

const users = new SharedArray('users', function () {
  return papaparse.parse(open('./test-users.csv'), { header: true }).data;
});

export default function () {
  const user = users[__VU % users.length];
  http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
    email: user.email,
    password: user.password,
  }));
}
```



---

<!-- Script: scripts/generate_perf_tests.py -->

# Script: generate_perf_tests.py

```python
#!/usr/bin/env python3
"""Generate performance test scripts and configurations."""

import argparse, os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")

def gen_k6(project, output):
    create_file(os.path.join(output, "load-test.js"), f"""import http from 'k6/http';
import {{ check, sleep }} from 'k6';
import {{ Rate, Trend }} from 'k6/metrics';

const errorRate = new Rate('errors');
const responseTime = new Trend('response_time');

export const options = {{
  scenarios: {{
    // Ramp-up load test
    load_test: {{
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        {{ duration: '2m', target: 50 }},   // Ramp up
        {{ duration: '5m', target: 50 }},   // Steady state
        {{ duration: '2m', target: 100 }},  // Peak
        {{ duration: '5m', target: 100 }},  // Sustained peak
        {{ duration: '2m', target: 0 }},    // Ramp down
      ],
    }},
  }},
  thresholds: {{
    http_req_duration: ['p(95)<500', 'p(99)<1000'],  // 95th < 500ms, 99th < 1s
    errors: ['rate<0.01'],                             // Error rate < 1%
    http_req_failed: ['rate<0.01'],
  }},
}};

const BASE_URL = __ENV.BASE_URL || 'https://staging.example.com';

export default function () {{
  // GET - List endpoint
  const listRes = http.get(`${{BASE_URL}}/api/items`, {{
    headers: {{ 'Authorization': `Bearer ${{__ENV.API_TOKEN}}` }},
  }});
  check(listRes, {{
    'list status 200': (r) => r.status === 200,
    'list response < 500ms': (r) => r.timings.duration < 500,
  }});
  errorRate.add(listRes.status !== 200);
  responseTime.add(listRes.timings.duration);

  sleep(1);

  // POST - Create endpoint
  const payload = JSON.stringify({{
    name: `item-${{Math.random().toString(36).substr(2, 9)}}`,
    value: Math.floor(Math.random() * 1000),
  }});
  const createRes = http.post(`${{BASE_URL}}/api/items`, payload, {{
    headers: {{
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${{__ENV.API_TOKEN}}`,
    }},
  }});
  check(createRes, {{
    'create status 201': (r) => r.status === 201,
    'create response < 1s': (r) => r.timings.duration < 1000,
  }});
  errorRate.add(createRes.status !== 201);

  sleep(1);
}}
""")

    create_file(os.path.join(output, "stress-test.js"), f"""import http from 'k6/http';
import {{ check, sleep }} from 'k6';

export const options = {{
  scenarios: {{
    stress: {{
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        {{ duration: '2m', target: 100 }},
        {{ duration: '5m', target: 100 }},
        {{ duration: '2m', target: 200 }},
        {{ duration: '5m', target: 200 }},
        {{ duration: '2m', target: 300 }},    // Push beyond expected capacity
        {{ duration: '5m', target: 300 }},
        {{ duration: '5m', target: 0 }},      // Recovery
      ],
    }},
  }},
  thresholds: {{
    http_req_duration: ['p(99)<2000'],
    http_req_failed: ['rate<0.05'],  // Stress test allows higher error rate
  }},
}};

const BASE_URL = __ENV.BASE_URL || 'https://staging.example.com';

export default function () {{
  const res = http.get(`${{BASE_URL}}/api/health`);
  check(res, {{ 'status 200': (r) => r.status === 200 }});
  sleep(0.5);
}}
""")

    create_file(os.path.join(output, "spike-test.js"), """import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    spike: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 10 },     // Warm up
        { duration: '30s', target: 500 },    // Spike!
        { duration: '2m', target: 500 },     // Stay at spike
        { duration: '30s', target: 10 },     // Drop back
        { duration: '2m', target: 10 },      // Recovery
      ],
    },
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://staging.example.com';

export default function () {
  const res = http.get(`${BASE_URL}/api/health`);
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(0.3);
}
""")

def gen_locust(project, output):
    create_file(os.path.join(output, "locustfile.py"), f"""from locust import HttpUser, task, between, tag
import json, random, string

class APIUser(HttpUser):
    wait_time = between(1, 3)
    host = "https://staging.example.com"

    def on_start(self):
        # Login and get token
        resp = self.client.post("/api/auth/login", json={{
            "email": "loadtest@example.com",
            "password": "test-password",
        }})
        self.token = resp.json().get("token", "")
        self.headers = {{"Authorization": f"Bearer {{self.token}}"}}

    @tag("read")
    @task(5)  # 5x more likely than write
    def list_items(self):
        self.client.get("/api/items", headers=self.headers, name="/api/items [GET]")

    @tag("read")
    @task(3)
    def get_item(self):
        item_id = random.randint(1, 100)
        self.client.get(f"/api/items/{{item_id}}", headers=self.headers, name="/api/items/[id] [GET]")

    @tag("write")
    @task(1)
    def create_item(self):
        name = ''.join(random.choices(string.ascii_lowercase, k=8))
        self.client.post("/api/items", json={{
            "name": f"item-{{name}}",
            "value": random.randint(1, 1000),
        }}, headers=self.headers, name="/api/items [POST]")
""")

def gen_ci(tool, output):
    configs = {
        "k6": """# .github/workflows/performance.yml
name: Performance Tests
on:
  schedule:
    - cron: '0 4 * * 1'  # Weekly Monday 4 AM
  workflow_dispatch:
    inputs:
      vus:
        description: 'Virtual users'
        default: '50'

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: grafana/k6-action@v0.3.1
        with:
          filename: performance/load-test.js
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}
          API_TOKEN: ${{ secrets.LOAD_TEST_TOKEN }}
      - uses: actions/upload-artifact@v4
        with:
          name: k6-results
          path: k6-results/
""",
        "locust": """# .github/workflows/performance.yml
name: Performance Tests
on:
  schedule:
    - cron: '0 4 * * 1'
  workflow_dispatch:

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install locust
      - run: |
          locust -f performance/locustfile.py \\
            --headless -u 50 -r 10 --run-time 5m \\
            --host ${{ secrets.STAGING_URL }} \\
            --csv performance/results
      - uses: actions/upload-artifact@v4
        with:
          name: locust-results
          path: performance/results*
""",
    }
    create_file(os.path.join(output, f"ci-{tool}.yml"), configs.get(tool, configs["k6"]))

def gen_budget(project, output):
    create_file(os.path.join(output, f"performance-budget-{project}.md"), f"""# Performance Budget — {project}

## API Performance Targets

| Endpoint | p50 | p95 | p99 | Max RPS | Error Rate |
|----------|-----|-----|-----|---------|-----------|
| GET /api/items | < 100ms | < 300ms | < 500ms | 1000 | < 0.1% |
| GET /api/items/:id | < 50ms | < 200ms | < 400ms | 2000 | < 0.1% |
| POST /api/items | < 200ms | < 500ms | < 1000ms | 500 | < 0.5% |
| GET /api/search | < 300ms | < 800ms | < 1500ms | 200 | < 0.5% |

## Infrastructure Limits

| Resource | Capacity | Alert Threshold |
|----------|----------|----------------|
| CPU | 80% avg | 70% for 5 min |
| Memory | 85% | 80% for 5 min |
| DB connections | 200 | 150 |
| DB query time (avg) | < 50ms | > 100ms |
| Cache hit rate | > 85% | < 80% |

## Load Test Schedule

| Test Type | Frequency | Duration | VUs |
|-----------|-----------|----------|-----|
| Load test | Weekly | 15 min | 50-100 |
| Stress test | Monthly | 30 min | 100-300 |
| Spike test | Quarterly | 10 min | 10→500→10 |
| Soak test | Quarterly | 4 hours | 50 |
""")

def main():
    p = argparse.ArgumentParser(description="Generate Performance Test Configuration")
    p.add_argument("--tool", choices=["k6", "locust", "all"], required=True)
    p.add_argument("--project", default="myapp")
    p.add_argument("--output", default="./performance")
    a = p.parse_args()

    print(f"\n⚡ Generating {a.tool} performance tests for {a.project}\n")
    if a.tool in ("k6", "all"):
        gen_k6(a.project, a.output)
        gen_ci("k6", a.output)
    if a.tool in ("locust", "all"):
        gen_locust(a.project, a.output)
        gen_ci("locust", a.output)
    gen_budget(a.project, a.output)
    print(f"\n✅ Generated at: {a.output}/")

if __name__ == "__main__":
    main()

```
