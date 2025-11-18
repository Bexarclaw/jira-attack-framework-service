# attack2jira Installation Guide

Complete installation instructions for all supported platforms and deployment methods.

## Table of Contents

- [System Requirements](#system-requirements)
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
  - [Local Installation (Python venv)](#local-installation-python-venv)
  - [System-Wide Installation](#system-wide-installation)
  - [Docker Installation](#docker-installation)
  - [VPS Deployment](#vps-deployment)
- [Verification Steps](#verification-steps)
- [Troubleshooting Installation](#troubleshooting-installation)
- [Upgrading](#upgrading)
- [Uninstallation](#uninstallation)

---

## System Requirements

### Hardware Requirements

**Minimum:**
- CPU: 1 core
- RAM: 512 MB
- Disk: 100 MB free space
- Network: Internet connectivity (HTTPS)

**Recommended:**
- CPU: 2+ cores (faster technique import)
- RAM: 1 GB
- Disk: 500 MB free space (for logs and exports)
- Network: 5+ Mbps (for API calls to Jira and MITRE)

### Operating System Support

| OS | Version | Status | Notes |
|----|---------|--------|-------|
| **Kali Linux** | 2018.4+ | ✅ Tested | Official test platform |
| **Ubuntu** | 18.04+ | ✅ Tested | Recommended for production |
| **Debian** | 10+ | ✅ Compatible | Should work (community tested) |
| **CentOS/RHEL** | 7+ | ✅ Compatible | Requires EPEL repository |
| **Windows 10/11** | 1830+ | ✅ Tested | PowerShell or WSL recommended |
| **macOS** | 10.14+ | ✅ Compatible | Community tested |

---

## Prerequisites

### 1. Python Installation

attack2jira requires Python 3.6 or higher.

**Check Python version:**
```bash
python3 --version
```

Expected output: `Python 3.6.x` or higher

**Install Python if missing:**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**CentOS/RHEL:**
```bash
sudo yum install python3 python3-pip
```

**Windows:**
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer
3. Check "Add Python to PATH"
4. Verify: `python --version`

**macOS:**
```bash
# Using Homebrew
brew install python3
```

---

### 2. Git Installation

Required to clone the repository.

**Check Git version:**
```bash
git --version
```

**Install Git if missing:**

**Ubuntu/Debian:**
```bash
sudo apt install git
```

**CentOS/RHEL:**
```bash
sudo yum install git
```

**Windows:**
Download from [git-scm.com](https://git-scm.com/download/win)

**macOS:**
```bash
brew install git
```

---

### 3. Network Access

Ensure outbound HTTPS access to:
- **Jira Cloud**: `*.atlassian.net` (port 443)
- **MITRE ATT&CK CTI**: `cti-taxii.mitre.org` (port 443)
- **GitHub**: `github.com` (port 443, for cloning repository)

**Test connectivity:**
```bash
curl -I https://yourcompany.atlassian.net
curl -I https://cti-taxii.mitre.org
```

---

### 4. Jira Software Cloud Account

- **Jira Software Cloud** instance (not Server/Data Center)
- **Admin access** to create projects and custom fields
- **API token** for authentication

**Get a free trial:**
[https://www.atlassian.com/try/cloud/signup?bundle=jira-software&edition=free](https://www.atlassian.com/try/cloud/signup?bundle=jira-software&edition=free)

---

## Installation Methods

Choose the method that best fits your environment.

---

## Local Installation (Python venv)

**Recommended for most users**. Isolates attack2jira dependencies from other Python tools.

### Step 1: Clone Repository

```bash
# Navigate to your preferred installation directory
cd /opt  # or ~/tools, or any directory you prefer

# Clone the repository
git clone https://github.com/mvelazc0/attack2jira.git
cd attack2jira
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment named 'venv'
python3 -m venv venv
```

This creates an isolated Python environment in the `venv/` directory.

### Step 3: Activate Virtual Environment

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

Your prompt should change to show `(venv)`:
```
(venv) user@host:/opt/attack2jira$
```

### Step 4: Install Dependencies

```bash
pip3 install -r requirements.txt
```

**Expected output:**
```
Collecting attackcti
  Downloading attackcti-X.X.X-py3-none-any.whl
Collecting requests>=2.20.0
  Using cached requests-2.XX.X-py3-none-any.whl
...
Successfully installed attackcti-X.X.X requests-2.XX.X ...
```

### Step 5: Verify Installation

```bash
python3 attack2jira.py -h
```

You should see the help menu.

### Step 6: Create Convenience Alias (Optional)

**Linux/macOS (.bashrc or .zshrc):**
```bash
echo 'alias attack2jira="cd /opt/attack2jira && source venv/bin/activate && python3 attack2jira.py"' >> ~/.bashrc
source ~/.bashrc
```

Now you can run:
```bash
attack2jira -url https://acme.atlassian.net -u user@acme.com -a initialize
```

---

## System-Wide Installation

**Not recommended** due to potential conflicts with other Python packages. Use only if virtual environments are not feasible.

### Step 1: Clone Repository

```bash
cd /opt
git clone https://github.com/mvelazc0/attack2jira.git
cd attack2jira
```

### Step 2: Install Dependencies Globally

```bash
sudo pip3 install -r requirements.txt
```

**Warning**: This installs packages system-wide and may conflict with OS package management.

### Step 3: Create Symlink (Optional)

```bash
sudo ln -s /opt/attack2jira/attack2jira.py /usr/local/bin/attack2jira
sudo chmod +x /opt/attack2jira/attack2jira.py
```

Now you can run:
```bash
attack2jira -url https://acme.atlassian.net -u user@acme.com -a initialize
```

---

## Docker Installation

**Status**: Not yet officially supported. Community contributions welcome!

### Planned Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY attack2jira.py .
COPY lib/ ./lib/

ENTRYPOINT ["python3", "attack2jira.py"]
```

### Planned Usage

```bash
docker build -t attack2jira .

docker run -it attack2jira \
  -url https://acme.atlassian.net \
  -u user@acme.com \
  -a initialize
```

**Want to contribute?** Submit a PR with Docker support!

---

## VPS Deployment

Deploy attack2jira on a cloud VPS for scheduled syncs and centralized management.

### Supported VPS Providers

- **AWS EC2**: Ubuntu 22.04 LTS (t2.micro eligible for free tier)
- **DigitalOcean**: Droplet with Ubuntu 22.04
- **Hostinger VPS**: Ubuntu 22.04
- **Linode**: Nanode 1GB with Ubuntu 22.04
- **Azure VM**: B1s with Ubuntu 22.04

### Example: Hostinger VPS Setup

#### Step 1: Provision VPS

1. Log into Hostinger account
2. Create new VPS:
   - **OS**: Ubuntu 22.04 LTS
   - **Plan**: 1 vCPU, 2 GB RAM (sufficient)
   - **Region**: Closest to your Jira instance
3. Note SSH credentials

#### Step 2: SSH into VPS

```bash
ssh root@your-vps-ip
```

#### Step 3: Update System

```bash
apt update && apt upgrade -y
```

#### Step 4: Install Prerequisites

```bash
apt install python3 python3-pip python3-venv git -y
```

#### Step 5: Create Service User

```bash
# Create dedicated user
useradd -m -s /bin/bash attack2jira
su - attack2jira
```

#### Step 6: Install attack2jira

```bash
cd ~
git clone https://github.com/mvelazc0/attack2jira.git
cd attack2jira
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

#### Step 7: Configure Credentials

Store API token securely:

```bash
# Create credentials file (restrict permissions)
mkdir -p ~/.config/attack2jira
cat > ~/.config/attack2jira/config.env <<EOF
JIRA_URL="https://acme.atlassian.net"
JIRA_USER="automation@acme.com"
JIRA_TOKEN="your-api-token-here"
EOF

chmod 600 ~/.config/attack2jira/config.env
```

#### Step 8: Create Wrapper Script

```bash
cat > ~/run_attack2jira.sh <<'EOF'
#!/bin/bash
set -e

# Load configuration
source ~/.config/attack2jira/config.env

# Activate virtual environment
cd ~/attack2jira
source venv/bin/activate

# Run attack2jira
python3 attack2jira.py \
  -url "$JIRA_URL" \
  -u "$JIRA_USER" \
  -a "$1" \
  "${@:2}"
EOF

chmod +x ~/run_attack2jira.sh
```

#### Step 9: Test

```bash
# This will prompt for API token (not yet automated)
~/run_attack2jira.sh initialize
```

**Note**: Full automation requires modifying `attack2jira.py` to accept API token via environment variable instead of `getpass()`.

#### Step 10: Schedule Automated Exports (Optional)

```bash
crontab -e
```

Add:
```cron
# Export ATT&CK coverage every Monday at 6 AM
0 6 * * 1 /home/attack2jira/run_attack2jira.sh export > /var/log/attack2jira_export.log 2>&1
```

---

## Verification Steps

After installation, verify everything works correctly.

### 1. Verify Python Version

```bash
python3 --version
```

Expected: `Python 3.6.x` or higher

### 2. Verify Dependencies

```bash
pip3 list | grep attackcti
```

Expected output:
```
attackcti    X.X.X
```

### 3. Test MITRE ATT&CK API Access

```bash
python3 -c "from attackcti import attack_client; client = attack_client(); print('ATT&CK API accessible')"
```

Expected output:
```
ATT&CK API accessible
```

### 4. Test Jira Connectivity

```bash
curl -u your-email@company.com:your-api-token \
  https://yourcompany.atlassian.net/rest/api/2/myself
```

Expected: JSON response with your user details

### 5. Run Help Command

```bash
python3 attack2jira.py -h
```

Expected: Help menu displays without errors

### 6. Perform Test Initialization (Optional)

Create a test project on a trial Jira instance:

```bash
python3 attack2jira.py \
  -url https://yourtest.atlassian.net \
  -u test@company.com \
  -a initialize \
  -p "Test Attack Project" \
  -k TEST
```

Expected: Project created successfully with all techniques

---

## Troubleshooting Installation

### Issue: "python3: command not found"

**Cause**: Python 3 not installed or not in PATH

**Solution**:
```bash
# Ubuntu/Debian
sudo apt install python3

# Verify
which python3
```

---

### Issue: "pip3: command not found"

**Cause**: pip not installed

**Solution**:
```bash
# Ubuntu/Debian
sudo apt install python3-pip

# Verify
which pip3
```

---

### Issue: "No module named 'venv'"

**Cause**: venv module not installed

**Solution**:
```bash
# Ubuntu/Debian
sudo apt install python3-venv
```

---

### Issue: Permission Denied During Installation

**Cause**: Insufficient permissions

**Solution**:
```bash
# Don't use sudo with venv installation
# Instead, install in user directory
pip3 install --user -r requirements.txt
```

---

### Issue: "SSL: CERTIFICATE_VERIFY_FAILED"

**Cause**: Corporate proxy or outdated CA certificates

**Solution**:
```bash
# Update CA certificates
sudo apt install ca-certificates
sudo update-ca-certificates

# Or set proxy
export HTTPS_PROXY=http://proxy.company.com:8080
```

---

### Issue: attackcti Installation Fails

**Cause**: Network issue or PyPI unavailable

**Solution**:
```bash
# Retry with verbose output
pip3 install -v attackcti

# Or install from GitHub directly
pip3 install git+https://github.com/Cyb3rWard0g/ATTACK-Python-Client.git
```

---

### Issue: "Cannot activate virtual environment" (Windows)

**Cause**: PowerShell execution policy

**Solution**:
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
venv\Scripts\Activate.ps1
```

---

## Upgrading

Update attack2jira when new versions are released.

### Upgrade Steps

```bash
cd /opt/attack2jira

# Deactivate virtual environment if active
deactivate

# Pull latest changes
git pull origin main

# Reactivate virtual environment
source venv/bin/activate

# Update dependencies
pip3 install --upgrade -r requirements.txt

# Verify
python3 attack2jira.py -h
```

### Check for Updates

```bash
cd /opt/attack2jira
git fetch origin
git status
```

If updates available:
```
Your branch is behind 'origin/main' by X commits
```

---

## Uninstallation

Remove attack2jira completely.

### Virtual Environment Installation

```bash
# Deactivate if active
deactivate

# Remove directory
rm -rf /opt/attack2jira

# Remove alias if created
# Edit ~/.bashrc and remove attack2jira alias line
```

### System-Wide Installation

```bash
# Remove packages
sudo pip3 uninstall attackcti requests urllib3

# Remove directory
rm -rf /opt/attack2jira

# Remove symlink if created
sudo rm /usr/local/bin/attack2jira
```

### Jira Project Cleanup

attack2jira uninstallation does NOT remove Jira projects. To remove:

1. Log into Jira
2. Go to **Project Settings** → **Details**
3. Click **Move to trash**
4. Go to **Jira Settings** → **Issues** → **Custom Fields**
5. Delete attack2jira custom fields (Tactic, Maturity, etc.)

**Warning**: Deleting custom fields is permanent and affects ALL projects using them.

---

## Post-Installation

After successful installation:

1. **Read**: [Getting Started Guide](GETTING_STARTED.md)
2. **Configure**: [Configuration Guide](CONFIGURATION_GUIDE.md)
3. **Initialize**: Create your first ATT&CK project
4. **Learn**: [User Guide](USER_GUIDE.md) for advanced features

---

**Installation complete! Ready to track ATT&CK coverage. 🚀**
