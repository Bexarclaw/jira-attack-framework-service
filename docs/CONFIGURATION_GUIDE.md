# attack2jira Configuration Guide

Comprehensive guide to configuring attack2jira for production use.

## Table of Contents

- [Overview](#overview)
- [Jira Cloud Requirements](#jira-cloud-requirements)
- [API Token Generation](#api-token-generation)
- [Environment Variables](#environment-variables)
- [MITRE ATT&CK Configuration](#mitre-attck-configuration)
- [Advanced Configuration](#advanced-configuration)
- [Security Best Practices](#security-best-practices)
- [Network Configuration](#network-configuration)
- [Troubleshooting Configuration](#troubleshooting-configuration)

---

## Overview

attack2jira uses a minimal configuration approach. Unlike many tools, it does **not** require configuration files. All settings are provided via:

1. **Command-line parameters** (required)
2. **Interactive prompts** (API token only)
3. **Optional environment variables** (for automation)

This design prioritizes security (no credentials on disk) while maintaining simplicity.

---

## Jira Cloud Requirements

### Supported Jira Products

| Product | Supported | Notes |
|---------|-----------|-------|
| **Jira Software Cloud** | ✅ Yes | **Required** - Official support |
| Jira Service Management Cloud | ⚠️ Partial | Works if Jira Software features enabled |
| Jira Work Management Cloud | ⚠️ Partial | Works if Jira Software features enabled |
| Jira Server | ❌ No | API differences prevent compatibility |
| Jira Data Center | ❌ No | API differences prevent compatibility |

**Recommendation**: Use Jira Software Cloud for full compatibility.

---

### Required Jira Permissions

The Jira user account running attack2jira must have:

#### Global Permissions
- **Jira Administrators** global permission (required for custom field creation)

#### Project Permissions (Auto-granted to Admins)
- **Administer Projects** permission
- **Create Issues** permission
- **Edit Issues** permission

#### Verification

Check your permissions:
1. Log into Jira
2. Navigate to **Jira Settings** → **System** → **Global permissions**
3. Verify your user or group is listed under **Jira Administrators**

If you lack admin permissions:
- Contact your Jira administrator
- Request "Jira Administrators" permission
- Alternatively, have an admin run attack2jira for you

---

### Jira Cloud Instance URL

Your Jira Cloud URL follows this format:
```
https://<site-name>.atlassian.net
```

**Examples:**
- `https://acmecorp.atlassian.net`
- `https://security-team.atlassian.net`
- `https://redteam2024.atlassian.net`

**Finding Your URL:**
1. Log into Jira
2. Copy the URL from your browser address bar
3. Remove everything after `.net` (e.g., remove `/jira/software/...`)

**Common Mistakes:**
- ❌ `https://jira.acmecorp.com` (custom domain, not Cloud)
- ❌ `http://acmecorp.atlassian.net` (HTTP instead of HTTPS)
- ❌ `https://acmecorp.atlassian.net/jira` (includes path)
- ✅ `https://acmecorp.atlassian.net` (correct)

---

## API Token Generation

Jira Cloud requires API tokens for authentication (passwords are not supported).

### Creating an API Token

#### Step 1: Access Token Management

1. Log into your Jira Cloud instance
2. Click your **profile icon** (top-right)
3. Select **Account settings** (or go to [id.atlassian.com](https://id.atlassian.com))
4. Navigate to **Security** tab
5. Click **Create and manage API tokens**

**Direct link**: [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

#### Step 2: Create Token

1. Click **Create API token**
2. Provide a descriptive label:
   - Example: `attack2jira production`
   - Example: `attack2jira automation bot`
3. Click **Create**
4. **Copy token immediately** (you won't see it again)

#### Step 3: Store Securely

**Never** store tokens in:
- Source code
- Configuration files committed to Git
- Shell history
- Plain text files

**Recommended storage:**
- Password manager (1Password, LastPass, Bitwarden)
- Secrets management system (HashiCorp Vault, AWS Secrets Manager)
- OS keychain (macOS Keychain, Windows Credential Manager)

---

### Token Security Best Practices

#### 1. Use Dedicated Service Accounts

Create a dedicated Jira user for automation:

```
Email: attack2jira-bot@acmecorp.com
Name: attack2jira Automation
```

**Benefits:**
- Audit trail shows automation actions separately
- Revoke access without affecting human users
- Assign minimal required permissions

#### 2. Rotate Tokens Regularly

Schedule token rotation:
- **Quarterly**: For production environments
- **Annually**: For test/dev environments
- **Immediately**: If token possibly compromised

#### 3. Revoke Unused Tokens

Remove tokens that are no longer needed:
1. Go to [API token management](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Revoke** next to unused tokens
3. Confirm revocation

#### 4. Monitor Token Usage

Jira audit logs show API token usage:
1. **Jira Settings** → **System** → **Audit log**
2. Filter by user account
3. Review API actions

---

### Testing API Token

Verify your token works:

```bash
curl -u your-email@company.com:your-api-token \
  https://yourcompany.atlassian.net/rest/api/2/myself
```

**Expected response:**
```json
{
  "self": "https://yourcompany.atlassian.net/rest/api/2/user?accountId=...",
  "accountId": "...",
  "emailAddress": "your-email@company.com",
  "displayName": "Your Name",
  "active": true
}
```

**Error responses:**
- `401 Unauthorized`: Invalid token or email
- `403 Forbidden`: Account lacks permissions
- `404 Not Found`: Invalid Jira URL

---

## Environment Variables

While attack2jira doesn't directly support environment variables, you can use shell variables for convenience.

### Shell Variable Configuration

**Linux/macOS (.bashrc or .zshrc):**
```bash
# attack2jira configuration
export ATTACK2JIRA_URL="https://acmecorp.atlassian.net"
export ATTACK2JIRA_USER="security@acmecorp.com"

# Convenience alias
alias attack2jira='python3 /opt/attack2jira/attack2jira.py -url $ATTACK2JIRA_URL -u $ATTACK2JIRA_USER'
```

**Usage:**
```bash
attack2jira -a initialize
attack2jira -a export
```

---

### Windows Environment Variables

**PowerShell Profile:**
```powershell
# Edit profile
notepad $PROFILE

# Add:
$env:ATTACK2JIRA_URL = "https://acmecorp.atlassian.net"
$env:ATTACK2JIRA_USER = "security@acmecorp.com"

function attack2jira {
    python3 C:\tools\attack2jira\attack2jira.py `
        -url $env:ATTACK2JIRA_URL `
        -u $env:ATTACK2JIRA_USER `
        @args
}
```

**Usage:**
```powershell
attack2jira -a initialize
```

---

### Automating API Token Input

**Current limitation**: attack2jira uses `getpass()` for secure token input, which doesn't support automation.

**Workaround**: Modify source code to accept environment variable.

**Edit attack2jira.py line 261:**

```python
# Original
pswd = getpass('Jira API Token for '+user+":")

# Modified for automation
import os
pswd = os.environ.get('JIRA_API_TOKEN') or getpass('Jira API Token for '+user+":")
```

**Then use:**
```bash
export JIRA_API_TOKEN="your-token-here"
python3 attack2jira.py -url https://acme.atlassian.net -u user@acme.com -a initialize
```

**Security warning**: Only use this in secure environments (e.g., CI/CD with secret management).

---

## MITRE ATT&CK Configuration

attack2jira uses the [attackcti](https://github.com/Cyb3rWard0g/ATTACK-Python-Client) library to fetch ATT&CK data.

### ATT&CK Matrix Selection

**Current behavior**: attack2jira fetches **Enterprise ATT&CK** only.

**Supported matrices:**
- ✅ **Enterprise** (default)
- ❌ Mobile (requires code modification)
- ❌ ICS (requires code modification)

---

### Customizing ATT&CK Source

**Default endpoint**: MITRE's official TAXII server (`cti-taxii.mitre.org`)

**Using a custom ATT&CK source:**

Edit `/lib/jirahandler.py` lines 399, 406, 431:

```python
# Original
client = attack_client()

# Custom TAXII server
client = attack_client(server="https://your-taxii-server.com")
```

**Use cases:**
- Internal ATT&CK mirror
- Custom ATT&CK fork
- Rate-limited access

---

### ATT&CK Version Pinning

**Current behavior**: Fetches latest ATT&CK version from MITRE.

**To pin a specific version**, use attackcti's version parameter:

```python
# In jirahandler.py
client = attack_client()
techniques = client.get_techniques(version="v10.1")  # Specify version
```

**Recommendation**: Use latest version unless you need reproducibility.

---

## Advanced Configuration

### Custom Field Customization

Modify custom fields created by attack2jira.

**Edit `/lib/jirahandler.py` lines 71-126:**

#### Example: Add "NIST Control" Field

```python
# Add after custom_field6_dict
custom_field7_dict = {
    "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
    "name": "NIST Control",
    "description": "Mapped NIST 800-53 Control",
    "type": "com.atlassian.jira.plugin.system.customfieldtypes:textfield"
}
custom_fields.append(custom_field7_dict)
```

**Then update technique creation** in `attack2jira.py` to populate this field.

---

### Maturity Level Customization

Modify maturity levels to match your framework.

**Edit `/lib/jirahandler.py` line 157:**

**Original (5-level model):**
```python
payload=[
    {"name":"Not Tracked"},
    {"name":"Initial"},
    {"name":"Defined"},
    {"name":"Resilient"},
    {"name":"Optimized"}
]
```

**Example: CMMI-based model:**
```python
payload=[
    {"name":"Level 0 - Incomplete"},
    {"name":"Level 1 - Initial"},
    {"name":"Level 2 - Managed"},
    {"name":"Level 3 - Defined"},
    {"name":"Level 4 - Quantitatively Managed"},
    {"name":"Level 5 - Optimizing"}
]
```

**Important**: Also update color mappings in `generate_json_layer()` (attack2jira.py lines 208-218).

---

### Project Template Customization

Change the Jira project template used.

**Edit `/lib/jirahandler.py` line 51:**

**Original (Scrum template):**
```python
'templateKey': "com.pyxis.greenhopper.jira:gh-simplified-basic",
```

**Options:**
- **Scrum**: `com.pyxis.greenhopper.jira:gh-simplified-scrum`
- **Kanban**: `com.pyxis.greenhopper.jira:gh-simplified-kanban`
- **Basic**: `com.pyxis.greenhopper.jira:gh-simplified-basic` (default)

---

### Screen Layout Customization

Modify which fields appear on issue screens.

**Edit `/lib/jirahandler.py` line 243:**

**Current layout:**
- **Primary (right sidebar)**: Assignee, Reporter, Labels, Maturity, Datasources
- **Content (main area)**: Tactic, Id, URL, Sub-Technique of, Description
- **Hidden**: Priority, Time tracking, Components, Fix versions, etc.

**To show Priority field**, move it from `alwaysHidden` to `secondary`:

```python
# Find in line 243:
"alwaysHidden":[..., {"id":"priority","type":"FIELD"}, ...]

# Change to:
"secondary":[{"id":"priority","type":"FIELD"}]
```

---

## Security Best Practices

### 1. Principle of Least Privilege

Create dedicated service account with minimal permissions:

1. Create Jira user: `attack2jira-bot@acme.com`
2. Grant **only** Jira Administrator permission (required for custom fields)
3. Do **not** grant:
   - Confluence access
   - Jira product admin
   - Billing access

---

### 2. Network Segmentation

Run attack2jira from trusted networks:

- ✅ Internal corporate network
- ✅ Bastion host / jump box
- ✅ Dedicated automation server
- ❌ Personal laptop on public WiFi
- ❌ Shared development machines

---

### 3. Audit Logging

Monitor attack2jira activity:

1. Enable Jira audit log:
   - **Jira Settings** → **System** → **Audit log**
2. Filter by attack2jira service account
3. Review actions weekly
4. Alert on unexpected behavior

---

### 4. Token Expiration

Implement token lifecycle:

```
Create → Use → Rotate → Revoke
  ↑                        ↓
  └────────────────────────┘
       (90-day cycle)
```

**Automation example:**
```bash
# Reminder script (run via cron monthly)
echo "Token rotation due: $(date -d '+60 days')" | mail -s "Rotate attack2jira token" security@acme.com
```

---

### 5. Secure Storage

**Never** commit credentials:

**Check `.gitignore` includes:**
```
*.env
config.json
credentials.txt
.secrets/
```

**Verify no secrets in Git history:**
```bash
git log -p | grep -i "atlassian.net"
```

---

## Network Configuration

### Proxy Configuration

For corporate environments with HTTP proxies:

**Set environment variables:**
```bash
export HTTP_PROXY="http://proxy.acmecorp.com:8080"
export HTTPS_PROXY="http://proxy.acmecorp.com:8080"
export NO_PROXY="localhost,127.0.0.1"

python3 attack2jira.py -url https://acme.atlassian.net -u user@acme.com -a initialize
```

**With authentication:**
```bash
export HTTPS_PROXY="http://user:password@proxy.acmecorp.com:8080"
```

---

### Firewall Rules

Ensure outbound HTTPS access:

| Destination | Port | Protocol | Purpose |
|-------------|------|----------|---------|
| `*.atlassian.net` | 443 | HTTPS | Jira API access |
| `cti-taxii.mitre.org` | 443 | HTTPS | ATT&CK data retrieval |
| `github.com` | 443 | HTTPS | Repository cloning (installation only) |
| `pypi.org` | 443 | HTTPS | Python package download (installation only) |

**No inbound connections required.**

---

### TLS/SSL Configuration

attack2jira disables SSL warnings by default (line 6 of `lib/jirahandler.py`):

```python
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

**To enforce strict SSL verification**, comment out this line:

```python
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

**Then ensure CA certificates are up to date:**
```bash
sudo apt install ca-certificates
sudo update-ca-certificates
```

---

## Troubleshooting Configuration

### Issue: "401 Unauthorized"

**Causes:**
1. Invalid API token
2. Incorrect email address
3. Token revoked

**Solutions:**
- Regenerate API token
- Verify email matches Jira account
- Test token with curl (see [Testing API Token](#testing-api-token))

---

### Issue: "Unauthorized. Probably not enough permissions"

**Cause**: User lacks Jira Administrator permission

**Solution**:
1. Request admin access from Jira admin
2. Or have admin run initialization
3. Verify permissions: **Jira Settings** → **System** → **Global permissions**

---

### Issue: "Error creating custom fields"

**Causes:**
1. Custom fields already exist
2. Insufficient permissions
3. Jira Cloud plan doesn't support custom fields

**Solutions:**
- Check existing custom fields: **Jira Settings** → **Issues** → **Custom Fields**
- Upgrade Jira plan if on Free tier with limitations
- Manually delete conflicting custom fields

---

### Issue: "Error connecting to Att&ck's API"

**Causes:**
1. Network connectivity issue
2. Firewall blocking HTTPS to MITRE
3. MITRE API downtime

**Solutions:**
```bash
# Test connectivity
curl -I https://cti-taxii.mitre.org

# Test via Python
python3 -c "from attackcti import attack_client; client = attack_client(); print('OK')"

# Check proxy settings
echo $HTTPS_PROXY
```

---

**Configuration complete! Ready for production deployment. 🔧**
