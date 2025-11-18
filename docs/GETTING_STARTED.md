# Getting Started with attack2jira

Welcome to attack2jira! This guide will help you get up and running quickly with automating your MITRE ATT&CK coverage tracking in Jira.

## Table of Contents

- [What is attack2jira?](#what-is-attack2jira)
- [Why Use attack2jira?](#why-use-attack2jira)
- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [First-Time Setup](#first-time-setup)
- [Running Your First Sync](#running-your-first-sync)
- [Verifying Success](#verifying-success)
- [Common First-Time Issues](#common-first-time-issues)
- [Next Steps](#next-steps)

---

## What is attack2jira?

**attack2jira** is a Python-based automation tool that bridges the gap between the [MITRE ATT&CK Framework](https://attack.mitre.org) and [Jira Software Cloud](https://www.atlassian.com/software/jira). It automatically creates a complete Jira project populated with all ATT&CK techniques and sub-techniques, enabling security teams to:

- **Track defensive coverage** against real-world adversary tactics and techniques
- **Measure security posture** over time with a maturity model
- **Collaborate effectively** using Jira's project management features
- **Visualize coverage** with ATT&CK Navigator integration
- **Eliminate spreadsheets** and manual tracking processes

At the time of writing, the MITRE ATT&CK Framework covers over 600 techniques and sub-techniques across 14 tactics. Manually tracking coverage against this comprehensive framework is error-prone and time-consuming. attack2jira automates this entire process, standing up a production-ready Jira environment in minutes.

### Key Features

- **One-command initialization**: Automatically creates Jira project, custom fields, and all ATT&CK techniques
- **Hierarchical structure**: Sub-techniques are created as Jira Sub-tasks for proper organization
- **Maturity tracking**: Built-in 5-level maturity model (Not Tracked → Initial → Defined → Resilient → Optimized)
- **Navigator export**: Export your coverage as ATT&CK Navigator JSON layers for visualization
- **Data source mapping**: Links techniques to required data sources for detection engineering
- **Tactic organization**: Automatically organizes techniques by ATT&CK tactics

---

## Why Use attack2jira?

Security teams need structured, repeatable processes to track their defensive capabilities. attack2jira solves several critical challenges:

### Before attack2jira
- Manual spreadsheet maintenance
- No version control or audit trail
- Difficult collaboration across teams
- Time-consuming updates when ATT&CK changes
- Limited visualization options
- Hard to measure progress over time

### After attack2jira
- Automated project setup and maintenance
- Full Jira audit trail and workflow capabilities
- Seamless collaboration with assignments, comments, and notifications
- Easy re-sync when ATT&CK framework updates
- Direct integration with ATT&CK Navigator
- Quantifiable metrics and dashboards

---

## System Requirements

Before installing attack2jira, ensure your environment meets these requirements:

### Operating System
- **Linux**: Tested on Kali Linux 2018.4, Ubuntu 18.04+, Debian 10+
- **Windows**: Tested on Windows 10 build 1830+, Windows 11
- **macOS**: Should work on macOS 10.14+ (community tested)

### Python Environment
- **Python 3.6 or higher** (Python 3.7+ recommended)
- **pip3** (Python package installer)
- **virtualenv** (recommended for isolation)

Verify your Python version:
```bash
python3 --version
```

### Jira Requirements
- **Jira Software Cloud** environment (not Jira Server/Data Center)
- **Admin access** to create projects and custom fields
- **API token** for authentication
- **Free trial or paid subscription**

> **Note**: Jira Software Cloud offers a [free tier](https://www.atlassian.com/try/cloud/signup?bundle=jira-software&edition=free) for up to 10 users, which is perfect for testing attack2jira.

### Network Requirements
- Outbound HTTPS access to:
  - Your Jira Cloud instance (e.g., `yourcompany.atlassian.net`)
  - MITRE ATT&CK CTI API (`cti-taxii.mitre.org`)
- No inbound connections required

### Disk Space
- Minimal: ~50 MB for Python dependencies and tool files
- Jira storage: ~100 MB for full ATT&CK project (cloud-based)

---

## Installation Methods

Choose the installation method that best fits your environment:

### Method 1: Quick Install (Recommended for First-Time Users)

This method installs attack2jira and its dependencies directly into your system Python environment:

```bash
# Clone the repository
git clone https://github.com/mvelazc0/attack2jira.git
cd attack2jira

# Install dependencies
pip3 install -r requirements.txt
```

**Pros**: Simple, fast, works immediately
**Cons**: Installs packages globally (may conflict with other Python tools)

---

### Method 2: Virtual Environment Install (Recommended for Production)

This method creates an isolated Python environment for attack2jira:

```bash
# Clone the repository
git clone https://github.com/mvelazc0/attack2jira.git
cd attack2jira

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip3 install -r requirements.txt
```

**Pros**: Isolated environment, no conflicts, reproducible
**Cons**: Must activate venv before each use

---

### Method 3: Docker Install (Coming Soon)

Docker support is planned for future releases. Stay tuned!

---

## First-Time Setup

After installation, you need to configure your Jira environment.

### Step 1: Create a Jira API Token

1. Log into your Jira Cloud instance
2. Navigate to **Account Settings** → **Security** → **API Tokens**
3. Click **Create API Token**
4. Provide a label (e.g., "attack2jira")
5. **Copy the token immediately** (you won't see it again)

For detailed instructions, see: [Atlassian API Token Documentation](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)

### Step 2: Verify Connectivity

Test that you can reach your Jira instance and the MITRE ATT&CK API:

```bash
# Test Jira connectivity
curl https://yourcompany.atlassian.net/rest/api/2/myself

# Test MITRE ATT&CK API (via attackcti library)
python3 -c "from attackcti import attack_client; client = attack_client(); print('ATT&CK API accessible')"
```

### Step 3: Verify Admin Permissions

Ensure your Jira user account has:
- **Project creation** permissions
- **Custom field creation** permissions (requires Jira Admin role)
- **Issue creation** permissions

If you lack these permissions, contact your Jira administrator.

---

## Running Your First Sync

Now you're ready to initialize your ATT&CK project!

### Basic Initialization

Run attack2jira with default settings (creates project named "Mitre Attack Framework" with key "ATTACK"):

```bash
python3 attack2jira.py -url https://yourcompany.atlassian.net -u your-email@company.com -a initialize
```

When prompted, paste your Jira API token (input will be hidden for security).

### Custom Project Configuration

Specify a custom project name and key:

```bash
python3 attack2jira.py \
  -url https://yourcompany.atlassian.net \
  -u your-email@company.com \
  -a initialize \
  -p "Security Coverage Tracker" \
  -k SCT
```

### What Happens During Initialization?

The tool performs these steps automatically:

1. **Authenticates** to Jira Cloud using your credentials
2. **Creates project** with specified name and key
3. **Creates 6 custom fields**:
   - **Tactic**: ATT&CK tactic (select dropdown)
   - **Maturity**: Detection maturity level (select dropdown)
   - **URL**: Link to ATT&CK technique page
   - **Datasources**: Required data sources (multi-select)
   - **Id**: ATT&CK technique ID (e.g., T1055)
   - **Sub-Technique of**: Parent technique reference
4. **Populates field options** with ATT&CK tactics, data sources, and maturity levels
5. **Configures screen layout** to display custom fields appropriately
6. **Creates issues** for all ATT&CK techniques and sub-techniques
   - Parent techniques as **Tasks**
   - Sub-techniques as **Sub-tasks** linked to parents
7. **Populates metadata** for each issue (tactic, data sources, URLs)

This process typically takes **5-10 minutes** depending on network speed and Jira instance performance.

---

## Verifying Success

After initialization completes, verify your project:

### 1. Check Project Creation

Navigate to your Jira instance:
```
https://yourcompany.atlassian.net/jira/software/c/projects/ATTACK/issues/
```

You should see your new project listed.

### 2. Verify Issue Count

- Click into the project
- Check the total issue count (should be 600+)
- Verify both Tasks (parent techniques) and Sub-tasks are present

### 3. Inspect Custom Fields

Open any technique issue and confirm:
- **Id** field shows technique ID (e.g., T1059.001)
- **Tactic** field populated
- **Maturity** defaults to "Not Tracked"
- **URL** links to MITRE ATT&CK page
- **Datasources** shows required data sources

### 4. Test Navigation

- Click **Filters** → **View all issues**
- Group by **Tactic** to see techniques organized by ATT&CK tactics
- Expand a parent technique to see its sub-techniques

---

## Common First-Time Issues

### Issue: "401 Unauthorized" Error

**Cause**: Invalid credentials or API token
**Solution**:
- Verify your email address is correct
- Regenerate your API token in Jira
- Ensure there are no extra spaces when pasting the token

---

### Issue: "Unauthorized. Probably not enough permissions"

**Cause**: User lacks admin permissions
**Solution**:
- Request **Jira Administrator** role from your Jira admin
- Alternatively, have an admin run the initialization for you

---

### Issue: "Error creating Jira project. Does it already exist?"

**Cause**: Project with that key already exists
**Solution**:
- Choose a different project key using `-k` parameter
- Or delete the existing project if it's a test instance

---

### Issue: "Error connecting to Att&ck's API"

**Cause**: Network connectivity issue or MITRE API downtime
**Solution**:
- Check internet connectivity
- Verify firewall allows HTTPS to `cti-taxii.mitre.org`
- Retry in a few minutes (API may be temporarily down)

---

### Issue: Python Module Not Found

**Cause**: Dependencies not installed correctly
**Solution**:
```bash
pip3 install --upgrade -r requirements.txt
```

---

### Issue: SSL Certificate Verification Errors

**Cause**: Corporate proxy or firewall intercepting HTTPS
**Solution**:
- Note: The tool disables SSL warnings by default for compatibility
- For corporate environments, configure proxy settings:
  ```bash
  export HTTPS_PROXY=http://proxy.company.com:8080
  python3 attack2jira.py ...
  ```

---

## Next Steps

Congratulations! You've successfully initialized your attack2jira project. Here's what to do next:

### 1. Update Maturity Levels
- Open technique issues in Jira
- Change **Maturity** field from "Not Tracked" to appropriate levels based on your coverage
- Assign issues to team members for assessment

### 2. Export Navigator Layer
Generate an ATT&CK Navigator visualization:
```bash
python3 attack2jira.py -url https://yourcompany.atlassian.net -u your-email@company.com -a export
```

Upload `attack2jira.json` to [ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/) to visualize your coverage.

### 3. Customize Workflows
- Configure Jira workflows to match your assessment process
- Add transitions like "Under Review" → "Validated" → "Documented"
- Set up notifications and automations

### 4. Create Dashboards
- Build Jira dashboards to track coverage metrics
- Create filters for different maturity levels
- Monitor progress over time

### 5. Integrate with Tools
- Link techniques to detection rules in your SIEM
- Reference techniques in incident response playbooks
- Tag techniques in threat intelligence reports

---

## Learn More

- **[User Guide](USER_GUIDE.md)**: Comprehensive feature documentation
- **[Configuration Guide](CONFIGURATION_GUIDE.md)**: Advanced configuration options
- **[Workflows](WORKFLOWS.md)**: Real-world usage patterns
- **[API Reference](API_REFERENCE.md)**: Python API documentation
- **[Troubleshooting](TROUBLESHOOTING.md)**: Detailed problem resolution

---

**Welcome to automated ATT&CK coverage tracking! 🎯**
