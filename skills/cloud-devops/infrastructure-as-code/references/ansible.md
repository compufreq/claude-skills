# Ansible Reference

## Table of Contents
1. Playbook Structure
2. Inventory
3. Roles
4. Variables & Vault
5. Common Modules
6. Best Practices

---

## 1. Playbook Structure

### Basic Playbook
```yaml
# playbooks/webservers.yml
---
- name: Configure web servers
  hosts: webservers
  become: true
  vars:
    app_name: myapp
    app_port: 8080

  pre_tasks:
    - name: Update apt cache
      apt:
        update_cache: true
        cache_valid_time: 3600
      when: ansible_os_family == "Debian"

  roles:
    - common
    - nginx
    - app

  post_tasks:
    - name: Verify application is running
      uri:
        url: "http://localhost:{{ app_port }}/health"
        status_code: 200
      retries: 5
      delay: 10

  handlers:
    - name: Restart nginx
      service:
        name: nginx
        state: restarted
```

### Site Playbook (Master)
```yaml
# playbooks/site.yml
---
- import_playbook: common.yml
- import_playbook: webservers.yml
- import_playbook: databases.yml
- import_playbook: monitoring.yml
```

---

## 2. Inventory

### Static Inventory
```yaml
# inventory/production/hosts.yml
all:
  children:
    webservers:
      hosts:
        web1.example.com:
          ansible_host: 10.0.1.10
        web2.example.com:
          ansible_host: 10.0.1.11
      vars:
        nginx_worker_processes: 4

    databases:
      hosts:
        db1.example.com:
          ansible_host: 10.0.2.10
          db_role: primary
        db2.example.com:
          ansible_host: 10.0.2.11
          db_role: replica

    monitoring:
      hosts:
        monitor.example.com:

  vars:
    ansible_user: deploy
    ansible_ssh_private_key_file: ~/.ssh/deploy_key
    ansible_python_interpreter: /usr/bin/python3
```

### Dynamic Inventory (AWS)
```yaml
# inventory/aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
filters:
  tag:Environment: production
  instance-state-name: running
keyed_groups:
  - key: tags.Role
    prefix: role
  - key: placement.availability_zone
    prefix: az
compose:
  ansible_host: private_ip_address
```

---

## 3. Roles

### Role Structure
```
roles/nginx/
├── tasks/
│   ├── main.yml
│   ├── install.yml
│   └── configure.yml
├── handlers/
│   └── main.yml
├── templates/
│   ├── nginx.conf.j2
│   └── site.conf.j2
├── files/
│   └── ssl-params.conf
├── vars/
│   └── main.yml
├── defaults/
│   └── main.yml         # Default variables (overridable)
├── meta/
│   └── main.yml         # Role dependencies
└── tests/
    └── test.yml
```

### Role Tasks
```yaml
# roles/nginx/tasks/main.yml
---
- name: Install nginx
  apt:
    name: nginx
    state: present
  notify: Restart nginx

- name: Deploy nginx config
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
    validate: nginx -t -c %s
  notify: Restart nginx

- name: Deploy site config
  template:
    src: site.conf.j2
    dest: /etc/nginx/sites-available/{{ app_name }}
  notify: Reload nginx

- name: Enable site
  file:
    src: /etc/nginx/sites-available/{{ app_name }}
    dest: /etc/nginx/sites-enabled/{{ app_name }}
    state: link
  notify: Reload nginx

- name: Ensure nginx is running
  service:
    name: nginx
    state: started
    enabled: true
```

### Role Handlers
```yaml
# roles/nginx/handlers/main.yml
---
- name: Restart nginx
  service:
    name: nginx
    state: restarted

- name: Reload nginx
  service:
    name: nginx
    state: reloaded
```

### Nginx Template
```nginx
# roles/nginx/templates/site.conf.j2
upstream {{ app_name }} {
{% for host in groups['webservers'] %}
    server {{ hostvars[host]['ansible_host'] }}:{{ app_port }};
{% endfor %}
}

server {
    listen 80;
    server_name {{ domain_name }};

    location / {
        proxy_pass http://{{ app_name }};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://{{ app_name }}/health;
        access_log off;
    }
}
```

---

## 4. Variables & Vault

### Variable Precedence (low → high)
1. Role defaults (`roles/x/defaults/main.yml`)
2. Inventory group vars (`inventory/group_vars/all.yml`)
3. Inventory host vars (`inventory/host_vars/web1.yml`)
4. Playbook vars (`vars:` in playbook)
5. Role vars (`roles/x/vars/main.yml`)
6. Extra vars (`-e "var=value"`) — highest priority

### Ansible Vault (Encrypted Secrets)
```bash
# Create encrypted file
ansible-vault create group_vars/production/vault.yml

# Edit encrypted file
ansible-vault edit group_vars/production/vault.yml

# Encrypt existing file
ansible-vault encrypt secrets.yml

# Decrypt
ansible-vault decrypt secrets.yml

# Run playbook with vault
ansible-playbook site.yml --ask-vault-pass
ansible-playbook site.yml --vault-password-file ~/.vault_pass
```

### Vault Variables Pattern
```yaml
# group_vars/production/vault.yml (encrypted)
vault_db_password: "supersecret123"
vault_api_key: "abc123def456"
vault_ssl_cert: |
  -----BEGIN CERTIFICATE-----
  ...
  -----END CERTIFICATE-----

# group_vars/production/vars.yml (references vault vars)
db_password: "{{ vault_db_password }}"
api_key: "{{ vault_api_key }}"
```

---

## 5. Common Modules

| Module | Purpose | Example |
|--------|---------|---------|
| `apt` / `yum` | Package management | `apt: name=nginx state=present` |
| `service` / `systemd` | Service management | `service: name=nginx state=started enabled=true` |
| `template` | Deploy Jinja2 templates | `template: src=app.conf.j2 dest=/etc/app.conf` |
| `copy` | Copy files | `copy: src=file.txt dest=/etc/file.txt` |
| `file` | File/directory management | `file: path=/app state=directory mode='0755'` |
| `user` / `group` | User management | `user: name=deploy groups=sudo` |
| `lineinfile` | Edit lines in files | `lineinfile: path=/etc/hosts line="10.0.1.1 db"` |
| `command` / `shell` | Run commands | `command: /opt/app/migrate.sh` |
| `uri` | HTTP requests | `uri: url=http://localhost/health status_code=200` |
| `docker_container` | Docker management | `docker_container: name=app image=myapp:latest` |
| `git` | Git operations | `git: repo=https://... dest=/app version=main` |
| `cron` | Cron jobs | `cron: name="backup" minute="0" hour="2" job="/backup.sh"` |
| `wait_for` | Wait for condition | `wait_for: port=8080 delay=5 timeout=60` |

### Conditional Execution
```yaml
- name: Install on Debian
  apt: name=nginx
  when: ansible_os_family == "Debian"

- name: Install on RedHat
  yum: name=nginx
  when: ansible_os_family == "RedHat"

- name: Only in production
  template: src=prod.conf.j2 dest=/etc/app.conf
  when: env == "production"
```

### Loops
```yaml
- name: Install packages
  apt:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - postgresql-client
    - redis-tools
    - curl

- name: Create users
  user:
    name: "{{ item.name }}"
    groups: "{{ item.groups }}"
    shell: /bin/bash
  loop:
    - { name: deploy, groups: sudo }
    - { name: monitor, groups: monitoring }
```

---

## 6. Best Practices

1. **Idempotent tasks** — running twice produces the same result
2. **Use roles** — never put everything in one playbook
3. **Variables in defaults** — make roles configurable
4. **Vault for secrets** — never plain-text passwords
5. **Test with `--check --diff`** — dry run before applying
6. **Tag tasks** — `tags: [nginx, config]` for selective runs
7. **Use `become: true` explicitly** — don't run everything as root
8. **Template validation** — `validate:` parameter on template tasks
9. **Handlers for restarts** — avoid unnecessary service restarts
10. **Pin versions** — `apt: name=nginx=1.24.0-1` not just `nginx`



---
