# attack2jira Deployment Guide

Production deployment guide for attack2jira across various platforms and automation scenarios.

## Table of Contents

- [Deployment Overview](#deployment-overview)
- [Local Deployment](#local-deployment)
- [Docker Deployment](#docker-deployment)
- [VPS Deployment](#vps-deployment)
- [CI/CD Integration](#cicd-integration)
- [Monitoring & Logging](#monitoring--logging)
- [Backup Strategy](#backup-strategy)
- [Disaster Recovery](#disaster-recovery)
- [Performance Tuning](#performance-tuning)
- [Security Hardening](#security-hardening)

---

## Deployment Overview

attack2jira can be deployed in several configurations depending on your requirements:

| Deployment Type | Use Case | Complexity | Automation |
|----------------|----------|------------|------------|
| **Local Workstation** | One-time setup, manual exports | Low | Manual |
| **VPS/Cloud Server** | Scheduled syncs, team access | Medium | Automated |
| **Docker Container** | Isolated environment, portability | Medium | Semi-automated |
| **CI/CD Pipeline** | GitOps workflow, version control | High | Fully automated |

---

## Local Deployment

Best for: Initial setup, testing, manual operation

### Prerequisites

- Python 3.6+
- Jira Software Cloud admin access
- API token
- Internet connectivity

### Deployment Steps

#### 1. Install attack2jira

```bash
cd /opt
git clone https://github.com/mvelazc0/attack2jira.git
cd attack2jira
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

#### 2. Create Configuration Script

```bash
cat > ~/run_attack2jira.sh <<'EOF'
#!/bin/bash
set -e

# Configuration
JIRA_URL="https://acmecorp.atlassian.net"
JIRA_USER="security@acmecorp.com"
ATTACK2JIRA_DIR="/opt/attack2jira"

# Activate virtual environment
cd "$ATTACK2JIRA_DIR"
source venv/bin/activate

# Run attack2jira
python3 attack2jira.py \
  -url "$JIRA_URL" \
  -u "$JIRA_USER" \
  "$@"

deactivate
EOF

chmod +x ~/run_attack2jira.sh
```

#### 3. Test Deployment

```bash
~/run_attack2jira.sh -a initialize -p "Test Project" -k TEST
```

#### 4. Create Convenience Alias

```bash
echo "alias attack2jira='~/run_attack2jira.sh'" >> ~/.bashrc
source ~/.bashrc
```

**Usage:**
```bash
attack2jira -a export
attack2jira -a initialize -p "Production ATT&CK" -k PROD
```

---

## Docker Deployment

Best for: Consistent environments, portability, isolation

### Creating a Dockerfile

Create `Dockerfile` in the attack2jira directory:

```dockerfile
FROM python:3.9-slim

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY attack2jira.py .
COPY lib/ ./lib/

# Create non-root user
RUN useradd -m -u 1000 attack2jira && \
    chown -R attack2jira:attack2jira /app
USER attack2jira

# Set working directory
WORKDIR /app

# Default command
ENTRYPOINT ["python3", "attack2jira.py"]
CMD ["-h"]
```

### Building the Image

```bash
cd /opt/attack2jira
docker build -t attack2jira:latest .
```

### Running the Container

**Interactive mode (for initialization):**
```bash
docker run -it --rm \
  attack2jira:latest \
  -url https://acmecorp.atlassian.net \
  -u security@acmecorp.com \
  -a initialize
```

**Export with volume mount:**
```bash
docker run -it --rm \
  -v $(pwd)/exports:/app/exports \
  attack2jira:latest \
  -url https://acmecorp.atlassian.net \
  -u security@acmecorp.com \
  -a export
```

### Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  attack2jira:
    build: .
    image: attack2jira:latest
    container_name: attack2jira
    environment:
      - JIRA_URL=https://acmecorp.atlassian.net
      - JIRA_USER=security@acmecorp.com
      # Note: API token still requires interactive input or code modification
    volumes:
      - ./exports:/app/exports
    command: ["-h"]
```

**Usage:**
```bash
docker-compose run attack2jira -a export
```

---

## VPS Deployment

Best for: Production, scheduled automation, team collaboration

### Supported Platforms

- **AWS EC2** (Ubuntu 22.04 LTS)
- **DigitalOcean Droplet**
- **Hostinger VPS**
- **Linode**
- **Azure Virtual Machine**
- **Google Cloud Compute Engine**

### Example: Ubuntu 22.04 VPS Deployment

#### Step 1: Provision VPS

**Minimum specifications:**
- 1 vCPU
- 1 GB RAM
- 10 GB SSD
- Ubuntu 22.04 LTS

#### Step 2: Initial Server Setup

```bash
# SSH into server
ssh root@your-vps-ip

# Update system
apt update && apt upgrade -y

# Install prerequisites
apt install -y python3 python3-pip python3-venv git curl

# Create service user
useradd -m -s /bin/bash attack2jira
```

#### Step 3: Install attack2jira

```bash
# Switch to service user
su - attack2jira

# Clone repository
cd ~
git clone https://github.com/mvelazc0/attack2jira.git
cd attack2jira

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

#### Step 4: Configure Credentials

**Important**: Modify `attack2jira.py` to support environment variables (see Configuration Guide).

```bash
# Create credentials directory
mkdir -p ~/.config/attack2jira
chmod 700 ~/.config/attack2jira

# Store credentials securely
cat > ~/.config/attack2jira/credentials.env <<EOF
JIRA_URL="https://acmecorp.atlassian.net"
JIRA_USER="automation@acmecorp.com"
JIRA_API_TOKEN="your-api-token-here"
EOF

chmod 600 ~/.config/attack2jira/credentials.env
```

#### Step 5: Create Execution Script

```bash
cat > ~/attack2jira_wrapper.sh <<'EOF'
#!/bin/bash
set -euo pipefail

# Load credentials
source ~/.config/attack2jira/credentials.env

# Activate virtual environment
cd ~/attack2jira
source venv/bin/activate

# Set JIRA_API_TOKEN for modified attack2jira.py
export JIRA_API_TOKEN

# Run attack2jira
python3 attack2jira.py \
  -url "$JIRA_URL" \
  -u "$JIRA_USER" \
  "$@"
EOF

chmod +x ~/attack2jira_wrapper.sh
```

#### Step 6: Test Execution

```bash
~/attack2jira_wrapper.sh -a export
```

#### Step 7: Configure Scheduled Exports

```bash
# Edit crontab
crontab -e

# Add scheduled export (every Monday at 6 AM UTC)
0 6 * * 1 /home/attack2jira/attack2jira_wrapper.sh -a export > /home/attack2jira/logs/export_$(date +\%Y\%m\%d).log 2>&1
```

**Create log directory:**
```bash
mkdir -p ~/logs
```

#### Step 8: Configure Logrotate

```bash
# As root
sudo cat > /etc/logrotate.d/attack2jira <<EOF
/home/attack2jira/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

---

## CI/CD Integration

Best for: GitOps workflows, version-controlled coverage tracking

### GitHub Actions Workflow

Create `.github/workflows/attack2jira-export.yml`:

```yaml
name: ATT&CK Coverage Export

on:
  schedule:
    # Run every Monday at 6 AM UTC
    - cron: '0 6 * * 1'
  workflow_dispatch:  # Allow manual triggers

jobs:
  export:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Export ATT&CK coverage
        env:
          JIRA_URL: ${{ secrets.JIRA_URL }}
          JIRA_USER: ${{ secrets.JIRA_USER }}
          JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
        run: |
          # Note: Requires modification to accept env vars
          python3 attack2jira.py \
            -url "$JIRA_URL" \
            -u "$JIRA_USER" \
            -a export

      - name: Archive coverage layer
        uses: actions/upload-artifact@v3
        with:
          name: attack2jira-coverage
          path: attack2jira.json
          retention-days: 90

      - name: Commit coverage to repository
        run: |
          DATE=$(date +%Y%m%d)
          mkdir -p coverage-history
          cp attack2jira.json coverage-history/coverage_$DATE.json

          git config user.name "attack2jira-bot"
          git config user.email "automation@acmecorp.com"
          git add coverage-history/
          git commit -m "Update ATT&CK coverage - $DATE" || echo "No changes"
          git push
```

**Configure GitHub Secrets:**
1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Add secrets:
   - `JIRA_URL`: `https://acmecorp.atlassian.net`
   - `JIRA_USER`: `automation@acmecorp.com`
   - `JIRA_API_TOKEN`: (your API token)

---

### GitLab CI/CD Pipeline

Create `.gitlab-ci.yml`:

```yaml
stages:
  - export

export_coverage:
  stage: export
  image: python:3.9-slim

  before_script:
    - pip install -r requirements.txt

  script:
    - python3 attack2jira.py -url "$JIRA_URL" -u "$JIRA_USER" -a export

  artifacts:
    paths:
      - attack2jira.json
    expire_in: 90 days

  only:
    - schedules
```

**Configure CI/CD Variables:**
- **Settings** → **CI/CD** → **Variables**
- Add: `JIRA_URL`, `JIRA_USER`, `JIRA_API_TOKEN`

---

### Jenkins Pipeline

Create `Jenkinsfile`:

```groovy
pipeline {
    agent any

    environment {
        JIRA_URL = credentials('jira-url')
        JIRA_USER = credentials('jira-user')
        JIRA_API_TOKEN = credentials('jira-api-token')
    }

    triggers {
        cron('0 6 * * 1')  // Weekly on Monday 6 AM
    }

    stages {
        stage('Setup') {
            steps {
                sh 'pip3 install -r requirements.txt'
            }
        }

        stage('Export Coverage') {
            steps {
                sh '''
                    python3 attack2jira.py \
                        -url "$JIRA_URL" \
                        -u "$JIRA_USER" \
                        -a export
                '''
            }
        }

        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'attack2jira.json', fingerprint: true
            }
        }
    }
}
```

---

## Monitoring & Logging

### Application Logging

Enhance attack2jira with structured logging.

**Modify attack2jira.py to add logging:**

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/attack2jira/attack2jira.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('attack2jira')
```

**Create log directory:**
```bash
sudo mkdir -p /var/log/attack2jira
sudo chown attack2jira:attack2jira /var/log/attack2jira
```

---

### Monitoring with Systemd

Create systemd service for automated execution.

**Create `/etc/systemd/system/attack2jira-export.service`:**

```ini
[Unit]
Description=attack2jira Coverage Export
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=attack2jira
WorkingDirectory=/home/attack2jira/attack2jira
Environment="PATH=/home/attack2jira/attack2jira/venv/bin:/usr/bin"
EnvironmentFile=/home/attack2jira/.config/attack2jira/credentials.env
ExecStart=/home/attack2jira/attack2jira/venv/bin/python3 attack2jira.py -url ${JIRA_URL} -u ${JIRA_USER} -a export
StandardOutput=journal
StandardError=journal
SyslogIdentifier=attack2jira

[Install]
WantedBy=multi-user.target
```

**Create timer `/etc/systemd/system/attack2jira-export.timer`:**

```ini
[Unit]
Description=attack2jira Weekly Export Timer

[Timer]
OnCalendar=Mon *-*-* 06:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable attack2jira-export.timer
sudo systemctl start attack2jira-export.timer

# Check timer status
sudo systemctl list-timers attack2jira-export.timer
```

---

### Monitoring Execution

**View logs:**
```bash
journalctl -u attack2jira-export.service -f
```

**Check last run:**
```bash
systemctl status attack2jira-export.service
```

---

## Backup Strategy

### Jira Project Backup

Jira Cloud provides automatic backups, but export your configuration:

**Backup custom fields:**
```bash
curl -u user@acme.com:api-token \
  https://acme.atlassian.net/rest/api/3/field > custom_fields_backup.json
```

**Backup project configuration:**
```bash
curl -u user@acme.com:api-token \
  https://acme.atlassian.net/rest/api/3/project/ATTACK > project_backup.json
```

---

### Coverage History Backup

**Store exports in version control:**
```bash
#!/bin/bash
# backup_coverage.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/var/backups/attack2jira"

mkdir -p "$BACKUP_DIR"
cp attack2jira.json "$BACKUP_DIR/coverage_$DATE.json"

# Keep 90 days of history
find "$BACKUP_DIR" -type f -mtime +90 -delete
```

---

### Restore Procedure

**To restore maturity levels:**
1. Export coverage from backup: `coverage_YYYYMMDD.json`
2. Upload to ATT&CK Navigator
3. Manually update Jira maturity fields based on visual comparison
4. Or script bulk updates via Jira API

---

## Disaster Recovery

### Scenario: Lost Jira Project

**Recovery steps:**
1. Re-run `attack2jira.py -a initialize` to recreate project
2. Restore maturity levels from latest backup
3. Use Jira's CSV importer to bulk update fields

---

### Scenario: Lost API Token

**Recovery steps:**
1. Generate new API token in Atlassian account
2. Update credentials in:
   - CI/CD secrets
   - VPS credentials file
   - Password manager
3. Test authentication
4. Revoke old token

---

### Scenario: Corrupted Custom Fields

**Recovery steps:**
1. Manually delete corrupted fields: **Jira Settings** → **Issues** → **Custom Fields**
2. Re-run initialization (custom fields will be recreated)
3. Restore field values from backup

---

## Performance Tuning

### Optimization Tips

#### 1. Reduce API Call Frequency

Avoid running initialization repeatedly:
- Initialize once
- Use export for regular monitoring

#### 2. Pagination Tuning

Modify `/lib/jirahandler.py` line 383 to increase page size:

```python
# Current: 50 issues per page
read_issues+=50
startAt+=50

# Optimized: 100 issues per page
read_issues+=100
startAt+=100
```

#### 3. Parallel Processing (Advanced)

For large-scale deployments, implement multithreading in technique creation.

---

### Network Performance

**Use VPS in same region as Jira:**
- Jira US East → AWS us-east-1
- Jira EU → AWS eu-west-1

**Expected execution times:**
- **Initialize**: 5-10 minutes (600+ issues)
- **Export**: 30-60 seconds (query + JSON generation)

---

## Security Hardening

### VPS Security

```bash
# Disable root SSH
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Enable firewall (allow SSH only)
sudo ufw allow 22/tcp
sudo ufw enable

# Install fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

---

### Secrets Management

Use dedicated secrets manager:

**AWS Secrets Manager:**
```bash
# Store token
aws secretsmanager create-secret \
  --name attack2jira/jira-token \
  --secret-string "your-api-token"

# Retrieve in script
JIRA_API_TOKEN=$(aws secretsmanager get-secret-value \
  --secret-id attack2jira/jira-token \
  --query SecretString \
  --output text)
```

---

**Production deployment complete! Your attack2jira instance is now enterprise-ready. 🚀**
