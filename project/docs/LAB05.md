# Lab 05 - Ansible Fundamentals Documentation

## Overview

Lab 05 is about **Configuration Management** using Ansible: automating VM provisioning and application deployment through reusable roles.

**Goal**: Automatically set up a VM with Docker and deploy a containerized Python app using Ansible.

## 1. Infrastructure & Technology Stack

### Target Environment

- **Control Node**: macOS (local machine)
- **Target Node**: Yandex Cloud VM
- **OS**: Ubuntu 24.04 LTS
- **VM IP**: 89.169.154.122
- **SSH**: Key-based authentication

### Technology Stack

- **Ansible**: 2.16.3
- **Docker**: 27.x (installed by Ansible)
- **Application**: Python FastAPI app (peplxx/devops-info-service)
- **Registry**: Docker Hub

### Project Structure

```
ansible/
├── inventory/
│   └── hosts.ini              # VM connection details
├── roles/
│   ├── common/                # System packages
│   ├── docker/                # Docker installation
│   └── app_deploy/            # App deployment
├── playbooks/
│   ├── site.yml               # Full setup
│   ├── provision.yml          # System only
│   └── deploy.yml             # App only
├── group_vars/
│   └── all.yml               # Encrypted secrets (Vault)
└── ansible.cfg               # Ansible config
```

### Why Roles?

**Without roles** (monolithic approach):
- All tasks in one giant playbook
- Hard to reuse
- Difficult to test
- Poor organization

**With roles** (modular approach):
- Each role = one responsibility
- Reusable across projects
- Easy to test independently
- Clean separation of concerns

## 2. Ansible Configuration

### Control Node Setup

```bash
# Install Ansible (macOS)
brew install ansible

# Verify
ansible --version
# ansible [core 2.16.3]
```

### Configuration File

**File**: `ansible.cfg`

```ini
[defaults]
inventory = inventory/hosts.ini
roles_path = roles
host_key_checking = False
remote_user = ubuntu
retry_files_enabled = False
interpreter_python = auto_silent
vault_password_file = .vault_pass

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False
```

**Key settings**:
- `vault_password_file` - automatic vault decryption
- `become = True` - sudo by default
- `host_key_checking = False` - skip SSH host key check (lab convenience)

### Inventory

**File**: `inventory/hosts.ini`

```ini
[webservers]
my-vm ansible_host=89.169.154.122 ansible_user=ubuntu

[webservers:vars]
ansible_python_interpreter=/usr/bin/python3
```

**Connection test**:

```bash
$ ansible all -m ping
my-vm | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

## 3. Roles Implementation

### Role 1: common

**Purpose**: Install essential system packages.

**Location**: `roles/common/`

**Variables** (`defaults/main.yml`):

```yaml
common_packages:
  - python3-pip
  - curl
  - git
  - vim
  - htop
  - wget
  - net-tools
  - ca-certificates
  - gnupg
  - lsb-release

timezone: "Europe/Moscow"
```

**Tasks** (`tasks/main.yml`):

```yaml
---
- name: Update apt cache
  apt:
    update_cache: yes
    cache_valid_time: 3600

- name: Install common packages
  apt:
    name: "{{ common_packages }}"
    state: present

- name: Set timezone
  timezone:
    name: "{{ timezone }}"

- name: Ensure pip is installed
  apt:
    name: python3-pip
    state: present
```

**What it does**:
- Updates package cache (max once per hour)
- Installs development tools
- Sets timezone
- Ensures pip is available

---

### Role 2: docker

**Purpose**: Install and configure Docker.

**Location**: `roles/docker/`

**Variables** (`defaults/main.yml`):

```yaml
docker_user: "{{ ansible_user }}"

docker_packages:
  - docker-ce
  - docker-ce-cli
  - containerd.io

docker_python_packages:
  - docker
  - docker-compose
```

**Tasks** (`tasks/main.yml`):

```yaml
---
- name: Install prerequisites for Docker repository
  apt:
    name:
      - ca-certificates
      - curl
      - gnupg
      - lsb-release
    state: present

- name: Create directory for Docker GPG key
  file:
    path: /etc/apt/keyrings
    state: directory
    mode: '0755'

- name: Add Docker GPG key
  apt_key:
    url: https://download.docker.com/linux/ubuntu/gpg
    keyring: /etc/apt/keyrings/docker.gpg
    state: present

- name: Add Docker repository
  apt_repository:
    repo: "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable"
    state: present
    filename: docker

- name: Update apt cache after adding Docker repo
  apt:
    update_cache: yes

- name: Install Docker packages
  apt:
    name: "{{ docker_packages }}"
    state: present
  notify: restart docker

- name: Ensure Docker service is started and enabled
  service:
    name: docker
    state: started
    enabled: yes

- name: Add user to docker group
  user:
    name: "{{ docker_user }}"
    groups: docker
    append: yes

- name: Install Python Docker libraries
  pip:
    name: "{{ docker_python_packages }}"
    state: present
    executable: pip3

- name: Reset SSH connection for docker group to take effect
  meta: reset_connection
```

**Handlers** (`handlers/main.yml`):

```yaml
---
- name: restart docker
  service:
    name: docker
    state: restarted
  listen: "restart docker"
```

**What it does**:
- Adds Docker's official APT repository
- Installs Docker CE (Community Edition)
- Starts and enables Docker service
- Adds user to docker group (non-root access)
- Installs Python libraries for Ansible docker modules

---

### Role 3: app_deploy

**Purpose**: Deploy containerized application from Docker Hub.

**Location**: `roles/app_deploy/`

**Variables** (`defaults/main.yml`):

```yaml
container_state: started
container_restart_policy: unless-stopped
container_recreate: yes
container_pull: yes

health_check_url: "http://localhost:{{ app_port }}/health"
health_check_retries: 5
health_check_delay: 5
```

**Sensitive Variables** (from `group_vars/all.yml`, encrypted with Vault):

```yaml
---
dockerhub_username: peplxx
dockerhub_password: dckr_pat_XXXXXXXXXXXXX

app_name: devops-info-service
docker_image: "{{ dockerhub_username }}/{{ app_name }}"
docker_image_tag: latest
app_port: 5000
app_container_name: "{{ app_name }}-container"

app_env:
  HOST: "0.0.0.0"
  PORT: "5000"
  DEBUG: "false"
  APP_NAME: "devops-info-service"
  APP_VERSION: "1.0.0"
  APP_DESCRIPTION: "DevOps course info service"
```

**Note**: All env values must be strings! `DEBUG: "false"` not `DEBUG: false`.

**Tasks** (`tasks/main.yml`):

```yaml
---
- name: Log in to Docker Hub
  docker_login:
    username: "{{ dockerhub_username }}"
    password: "{{ dockerhub_password }}"
    registry_url: https://index.docker.io/v1/
  become: no
  no_log: true

- name: Pull Docker image
  docker_image:
    name: "{{ docker_image }}"
    tag: "{{ docker_image_tag }}"
    source: pull
    force_source: "{{ container_pull | default(true) }}"

- name: Ensure old container is removed
  docker_container:
    name: "{{ app_container_name }}"
    state: absent
  ignore_errors: yes

- name: Run application container
  docker_container:
    name: "{{ app_container_name }}"
    image: "{{ docker_image }}:{{ docker_image_tag }}"
    state: started
    restart_policy: unless-stopped
    ports:
      - "{{ app_port }}:{{ app_port }}"
    env: "{{ app_env }}"
    recreate: yes
    pull: no
  notify: verify application health

- name: Wait for application port to be available
  wait_for:
    host: localhost
    port: "{{ app_port }}"
    delay: 2
    timeout: 60
    state: started

- name: Verify application is responding
  uri:
    url: "http://localhost:{{ app_port }}/health"
    status_code: 200
    timeout: 10
  retries: 5
  delay: 5
  register: health_check
  until: health_check.status == 200
```

**Handlers** (`handlers/main.yml`):

```yaml
---
- name: verify application health
  uri:
    url: "{{ health_check_url }}"
    status_code: 200
  retries: 3
  delay: 5
  listen: "verify application health"
```

**What it does**:
- Logs in to Docker Hub (with encrypted credentials)
- Pulls latest image (peplxx/devops-info-service)
- Removes old container if exists
- Starts new container with env variables
- Waits for port to be available
- Verifies health endpoint responds
- Triggers health check handler

**Security**:
- `no_log: true` prevents password in logs
- `become: no` for docker login (doesn't need sudo)
- Credentials encrypted with Ansible Vault

## 4. Ansible Vault (Secrets Management)

### Why Vault?

**Problem**: Docker Hub credentials can't be stored in plaintext in Git.

**Solution**: Ansible Vault encrypts sensitive files with AES256.

### Setup

```bash
# Create password file
echo "SecureVaultPassword123" > .vault_pass
chmod 600 .vault_pass

# Add to .gitignore
echo ".vault_pass" >> .gitignore
```

### Creating Encrypted Variables

```bash
# Create encrypted file
ansible-vault create group_vars/all.yml --vault-password-file .vault_pass

# Edit encrypted file
ansible-vault edit group_vars/all.yml --vault-password-file .vault_pass

# View encrypted file
ansible-vault view group_vars/all.yml --vault-password-file .vault_pass
```

### Encrypted File Example

```bash
$ cat group_vars/all.yml
$ANSIBLE_VAULT;1.1;AES256
66396661303663613566383739363039373362623666306435366434393835616265306134353866
35613537383737623163643639623037333066343261333665373566656330613833613332626665
[... more encrypted content ...]
```

File is **safe to commit** - it's encrypted!

### Automatic Decryption

In `ansible.cfg`:

```ini
[defaults]
vault_password_file = .vault_pass
```

Now playbooks decrypt automatically without prompting for password.

## 5. Playbooks

### playbooks/provision.yml

**Purpose**: Install system packages and Docker.

```yaml
---
- name: Provision web servers
  hosts: webservers
  become: yes
  
  roles:
    - common
    - docker

  post_tasks:
    - name: Verify Docker installation
      command: docker --version
      register: docker_version
      changed_when: false

    - name: Display Docker version
      debug:
        msg: "Docker installed: {{ docker_version.stdout }}"
```

**Usage**:

```bash
ansible-playbook playbooks/provision.yml
```

---

### playbooks/deploy.yml

**Purpose**: Deploy application container.

```yaml
---
- name: Deploy application
  hosts: webservers
  become: yes

  roles:
    - app_deploy

  post_tasks:
    - name: Get container status
      command: docker ps -f name={{ app_container_name }}
      register: container_status
      changed_when: false

    - name: Display container status
      debug:
        msg: "{{ container_status.stdout_lines }}"
```

**Usage**:

```bash
ansible-playbook playbooks/deploy.yml
```

---

### playbooks/site.yml

**Purpose**: Full setup (provision + deploy).

```yaml
---
- name: Complete infrastructure setup
  import_playbook: provision.yml

- name: Deploy application
  import_playbook: deploy.yml
```

**Usage** (recommended for full deployment):

```bash
ansible-playbook playbooks/site.yml
```

## 6. Idempotency Demonstration

### What is Idempotency?

**Definition**: Running the same playbook multiple times produces the same result without breaking things.

**Ansible's approach**: Check current state → only change if needed.

### First Run (Fresh VM)

```bash
$ ansible-playbook playbooks/provision.yml

PLAY [Provision web servers] **************************************************

TASK [common : Update apt cache] **********************************************
changed: [my-vm]

TASK [common : Install common packages] ***************************************
changed: [my-vm]

TASK [docker : Add Docker GPG key] ********************************************
changed: [my-vm]

TASK [docker : Install Docker packages] ***************************************
changed: [my-vm]

TASK [docker : Add user to docker group] **************************************
changed: [my-vm]

# ... more tasks ...

PLAY RECAP ********************************************************************
my-vm : ok=15 changed=12 unreachable=0 failed=0
```

**Result**: 12 changes (yellow) - system was modified.

### Second Run (Idempotency Check)

```bash
$ ansible-playbook playbooks/provision.yml

PLAY [Provision web servers] **************************************************

TASK [common : Update apt cache] **********************************************
ok: [my-vm]

TASK [common : Install common packages] ***************************************
ok: [my-vm]

TASK [docker : Add Docker GPG key] ********************************************
ok: [my-vm]

TASK [docker : Install Docker packages] ***************************************
ok: [my-vm]

TASK [docker : Add user to docker group] **************************************
ok: [my-vm]

# ... more tasks ...

PLAY RECAP ********************************************************************
my-vm : ok=15 changed=0 unreachable=0 failed=0
```

**Result**: 0 changes (green) - perfect idempotency! ✅

### Why It's Idempotent

**Good practices used**:

1. **Stateful modules**:
   ```yaml
   # ✅ Checks if package already installed
   - name: Install Docker
     apt:
       name: docker-ce
       state: present
   ```

2. **Cache validity**:
   ```yaml
   # ✅ Only updates if cache older than 1 hour
   - name: Update apt cache
     apt:
       update_cache: yes
       cache_valid_time: 3600
   ```

3. **Service state**:
   ```yaml
   # ✅ Checks if already running
   - name: Ensure Docker running
     service:
       name: docker
       state: started
   ```

**Bad practices** (avoided):

```yaml
# ❌ Always runs, not idempotent
- name: Install Docker
  command: apt-get install docker-ce

# ❌ Always restarts, even if not needed
- name: Restart Docker
  command: systemctl restart docker
```

## 7. Deployment Verification

### Deployment Output

```bash
$ ansible-playbook playbooks/deploy.yml

PLAY [Deploy application] *****************************************************

TASK [app_deploy : Log in to Docker Hub] *************************************
ok: [my-vm]

TASK [app_deploy : Pull Docker image] *****************************************
changed: [my-vm]

TASK [app_deploy : Ensure old container is removed] **************************
changed: [my-vm]

TASK [app_deploy : Run application container] *********************************
changed: [my-vm]

TASK [app_deploy : Wait for application port to be available] ****************
ok: [my-vm]

TASK [app_deploy : Verify application is responding] *************************
ok: [my-vm]

RUNNING HANDLER [app_deploy : verify application health] **********************
ok: [my-vm]

PLAY RECAP ********************************************************************
my-vm : ok=10 changed=3 unreachable=0 failed=0
```

### Container Status

```bash
$ ansible webservers -a "docker ps"
my-vm | CHANGED | rc=0 >>
CONTAINER ID   IMAGE                                 STATUS         PORTS
75d127897678   peplxx/devops-info-service:latest     Up 3 minutes   0.0.0.0:5000->5000/tcp
```

Container running successfully ✅

### Environment Variables Check

```bash
$ ansible webservers -a "docker exec devops-info-service-container env"
my-vm | CHANGED | rc=0 >>
HOST=0.0.0.0
PORT=5000
DEBUG=false
APP_NAME=devops-info-service
APP_VERSION=1.0.0
APP_DESCRIPTION=DevOps course info service
PYTHON_VERSION=3.13.12
```

All variables injected correctly ✅

### Application Health Check

```bash
$ curl http://89.169.154.122:5000/health
{                                                                                                                                                               "status": "healthy",                                                                                                                                          "timestamp": "2026-02-25T21:59:26.921170+00:00",
  "uptime_seconds": 763
}

$ curl http://89.169.154.122:5000/
{
  "service": {
    "name": "devops-info-service",
    "version": "1.0.0",
    "description": "DevOps course info service",
    "framework": "FastAPI"
  },
  "system": {
    "hostname": "75d127897678",
    "platform": "Linux",
    "platform_version": "#100-Ubuntu SMP PREEMPT_DYNAMIC Tue Jan 13 16:40:06 UTC 2026",
    "architecture": "x86_64",
    "cpu_count": 2,
    "python_version": "3.13.12"
  },
  "runtime": {
    "uptime_seconds": 172,
    "uptime_human": "0 hours, 2 minutes",
    "current_time": "2026-02-25T21:49:35.297073+00:00",
    "timezone": "UTC"
  },
  "request": {
    "client_ip": "31.56.27.32",
    "user_agent": "curl/8.7.1",
    "method": "GET",
    "path": "/"
  },
  "endpoints": [
    {
      "path": "/",
      "method": "GET",
      "description": "Service information"
    },
    {
      "path": "/health",
      "method": "GET",
      "description": "Health check"
    }
  ]
}
```

Application responding correctly with full system information ✅

**Key observations**:
- Container hostname: `75d127897678` (matches Docker container ID)
- Python version: `3.13.12` (latest stable)
- Framework: FastAPI (modern async framework)
- CPU count: 2 (matching VM specs)
- Uptime tracking working
- Client IP properly captured
- All endpoints documented

### Container Logs

```bash
$ ansible webservers -a "docker logs devops-info-service-container --tail 10"
my-vm | CHANGED | rc=0 >>
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5000
INFO:     31.56.27.32:52184 - "GET /health HTTP/1.1" 200 OK
INFO:     31.56.27.32:52186 - "GET / HTTP/1.1" 200 OK
```

No errors in logs ✅

## 8. Key Decisions

### Q1: Why use roles instead of plain playbooks?

**Answer**: Roles provide modularity and reusability.

- **Monolithic playbook**: 200 lines, hard to maintain
- **Role-based**: 3 roles × 30 lines each, easy to reuse

Example: `docker` role can be used in other projects without changes.

### Q2: How do roles improve reusability?

**Answer**: 
- Each role is self-contained (tasks + variables + handlers)
- Standardized structure
- Can be shared via Ansible Galaxy
- Easy to test independently

Example from this lab: `docker` role works on any Ubuntu VM, `app_deploy` works with any containerized app.

### Q3: What makes a task idempotent?

**Answer**: Using modules that check state before acting.

```yaml
# ✅ Idempotent - checks if package exists
apt:
  name: docker-ce
  state: present

# ❌ Not idempotent - always runs
command: apt-get install docker-ce
```

### Q4: How do handlers improve efficiency?

**Answer**: Handlers only run when notified and only run once.

Example: Docker service only restarts if configuration changed, not on every run.

```yaml
# Task notifies handler
- name: Update Docker config
  copy:
    src: daemon.json
    dest: /etc/docker/daemon.json
  notify: restart docker

# Handler only runs if task changed
handlers:
  - name: restart docker
    service:
      name: docker
      state: restarted
```

### Q5: Why is Ansible Vault necessary?

**Answer**: To safely store secrets in Git.

- ✅ Encrypted files safe to commit
- ✅ Team can update secrets
- ✅ CI/CD can access secrets
- ✅ No plaintext passwords in repository

Without Vault: credentials exposed in Git history forever.

## 9. Challenges & Solutions

### Challenge 1: Module docker_container error with stop

**Problem**:
```
Cannot create container when image is not specified!
```

**Cause**: Using `docker_container` with `state: stopped` requires `image` parameter.

**Solution**: Use `state: absent` to remove container, or use `command` module:

```yaml
# Solution 1: Use absent state
- name: Remove old container
  docker_container:
    name: "{{ app_container_name }}"
    state: absent

# Solution 2: Use command
- name: Stop container
  command: docker stop {{ app_container_name }}
  when: container_exists
  ignore_errors: yes
```

### Challenge 2: Environment variable type error

**Problem**:
```
Non-string value found for env option. Key: DEBUG
```

**Cause**: `DEBUG: false` is boolean, Docker expects string.

**Solution**: Quote all environment values:

```yaml
app_env:
  DEBUG: "false"  # ✅ String
  PORT: "5000"    # ✅ String
  # DEBUG: false  # ❌ Boolean - fails!
```

### Challenge 3: Vault variables not found

**Problem**: Variables work in ad-hoc commands but not in playbooks.

**Cause**: Vault password file not configured in `ansible.cfg`.

**Solution**: Add to `ansible.cfg`:

```ini
[defaults]
vault_password_file = .vault_pass
```

Or use `--vault-password-file .vault_pass` flag.

## 10. Summary

### What Was Accomplished

✅ **Role-based Ansible project** with 3 reusable roles
✅ **Idempotent provisioning** (0 changes on second run)
✅ **Secure credential management** with Ansible Vault
✅ **Automated Docker installation** from official repository
✅ **Container deployment** with health checks and environment variables
✅ **Full verification** of deployed FastAPI application
✅ **Complete documentation** of decisions and process

### Application Details

- **Image**: peplxx/devops-info-service:latest
- **Framework**: FastAPI (Python 3.13.12)
- **Features**: System info, health checks, uptime tracking
- **Container Name**: devops-info-service-container
- **Accessibility**: http://89.169.154.122:5000

### Key Takeaways

1. **Roles = Reusability**: Each role can be used in other projects
2. **Idempotency = Safety**: Can re-run playbooks without fear
3. **Vault = Security**: Secrets encrypted in Git
4. **Handlers = Efficiency**: Only run when needed
5. **Modules > Commands**: Use stateful modules for idempotency

### Files to Commit

✅ **Safe to commit**:
- All role files (`roles/*/tasks/main.yml`, etc.)
- All playbooks
- `group_vars/all.yml` (encrypted!)
- `ansible.cfg`
- `inventory/hosts.ini`
- Documentation

❌ **Never commit**:
- `.vault_pass` (in `.gitignore`)
- Unencrypted credentials
- SSH private keys

### Lab 06 Preview

Next lab will extend this foundation with:
- Error handling (blocks/rescue)
- Tags for selective execution
- Docker Compose for multi-container apps
- CI/CD automation with GitHub Actions

---

**Lab completed successfully!** 🎉

**Application accessible at**: http://89.169.154.122:5000
