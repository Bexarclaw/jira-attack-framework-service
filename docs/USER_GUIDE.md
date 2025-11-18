# attack2jira User Guide

Complete guide to using attack2jira for tracking MITRE ATT&CK coverage in Jira Software Cloud.

## Table of Contents

- [Overview](#overview)
- [Command Reference](#command-reference)
- [Configuration](#configuration)
- [Syncing Techniques](#syncing-techniques)
- [Working with Custom Fields](#working-with-custom-fields)
- [Maturity Tracking](#maturity-tracking)
- [Exporting Navigator JSON](#exporting-navigator-json)
- [Viewing Results in Jira](#viewing-results-in-jira)
- [Customization Options](#customization-options)
- [Tips & Tricks](#tips--tricks)
- [Best Practices](#best-practices)

---

## Overview

attack2jira automates the creation and maintenance of a Jira project for tracking your organization's defensive coverage against the MITRE ATT&CK Framework. This guide covers all features and usage patterns for production deployments.

### Core Capabilities

1. **Project Initialization**: Automated Jira project creation with ATT&CK structure
2. **Technique Synchronization**: Import all ATT&CK techniques and sub-techniques
3. **Custom Field Management**: ATT&CK-specific fields for metadata tracking
4. **Maturity Assessment**: Five-level maturity model for coverage tracking
5. **Navigator Export**: Generate ATT&CK Navigator JSON layers for visualization
6. **Hierarchical Organization**: Sub-techniques as Jira Sub-tasks

---

## Command Reference

attack2jira provides a command-line interface with two primary actions: `initialize` and `export`.

### Help Menu

Display all available options:

```bash
python3 attack2jira.py -h
```

**Output:**
```
usage: attack2jira.py [-h] [-url URL] [-u USER] [-a ACTION] [-p PROJECT] [-k KEY] [-hide]

optional arguments:
  -h, --help    show this help message and exit
  -url URL      Url of Jira instance
  -u USER       Username
  -a ACTION     action to execute
                Two supported:
                'initialize' will create the JIRA entities.
                'export' will export the JSON layer.
  -p PROJECT    Name of the Jira project to create.
  -k KEY        Project Key.(default='ATTACK')
  -hide         If set, 'Not Tracked' techniques will be hidden
```

---

### Initialize Command

Creates a new Jira project with complete ATT&CK framework.

#### Basic Syntax

```bash
python3 attack2jira.py -url <JIRA_URL> -u <EMAIL> -a initialize
```

#### Parameters

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| `-url` | Yes | Jira Cloud instance URL | None |
| `-u` | Yes | Jira user email address | None |
| `-a` | Yes | Action (must be `initialize`) | None |
| `-p` | No | Project display name | "Mitre Attack Framework" |
| `-k` | No | Project key (2-10 uppercase letters) | "ATTACK" |

#### Examples

**Default project:**
```bash
python3 attack2jira.py \
  -url https://acme.atlassian.net \
  -u security@acme.com \
  -a initialize
```
Creates project: "Mitre Attack Framework" with key "ATTACK"

**Custom project name and key:**
```bash
python3 attack2jira.py \
  -url https://acme.atlassian.net \
  -u security@acme.com \
  -a initialize \
  -p "Red Team Coverage 2024" \
  -k RTC24
```
Creates project: "Red Team Coverage 2024" with key "RTC24"

**Multiple projects for different domains:**
```bash
# Enterprise ATT&CK
python3 attack2jira.py -url https://acme.atlassian.net -u security@acme.com -a initialize -p "Enterprise ATT&CK" -k ENT

# Future: Mobile ATT&CK (requires code modification for different matrix)
# python3 attack2jira.py -url https://acme.atlassian.net -u security@acme.com -a initialize -p "Mobile ATT&CK" -k MOB
```

#### What Happens During Initialize?

1. **Authentication** (2-5 seconds)
   - Validates credentials against Jira REST API
   - Establishes authenticated session

2. **Project Creation** (5-10 seconds)
   - Creates Jira Software project with specified name and key
   - Configures default issue types (Task, Sub-task)

3. **Custom Field Creation** (10-15 seconds)
   - Creates 6 custom fields for ATT&CK metadata
   - Configures field types and search capabilities

4. **Field Option Population** (15-30 seconds)
   - Fetches tactics from MITRE ATT&CK API
   - Fetches data sources from MITRE ATT&CK API
   - Populates dropdown and multi-select options

5. **Screen Configuration** (10-20 seconds)
   - Adds custom fields to issue screens
   - Hides unnecessary default Jira fields
   - Optimizes layout for ATT&CK workflow

6. **Technique Import** (3-8 minutes)
   - Fetches all enterprise techniques from MITRE ATT&CK
   - Filters out revoked techniques
   - Sorts by technique ID for parent-child ordering
   - Creates ~600+ Jira issues (Tasks and Sub-tasks)

**Total Time**: Approximately 5-10 minutes

---

### Export Command

Generates ATT&CK Navigator JSON layer based on current Jira maturity levels.

#### Basic Syntax

```bash
python3 attack2jira.py -url <JIRA_URL> -u <EMAIL> -a export
```

#### Parameters

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| `-url` | Yes | Jira Cloud instance URL | None |
| `-u` | Yes | Jira user email address | None |
| `-a` | Yes | Action (must be `export`) | None |
| `-hide` | No | Hide "Not Tracked" techniques | False |

#### Examples

**Standard export (shows all techniques):**
```bash
python3 attack2jira.py \
  -url https://acme.atlassian.net \
  -u security@acme.com \
  -a export
```

Output: `attack2jira.json` (includes all techniques, even "Not Tracked")

**Filtered export (hide untracked techniques):**
```bash
python3 attack2jira.py \
  -url https://acme.atlassian.net \
  -u security@acme.com \
  -a export \
  -hide
```

Output: `attack2jira.json` (only shows tracked techniques)

#### Color Mapping

The export uses the following color scheme to visualize maturity:

| Maturity Level | Color Code | Visual Appearance |
|----------------|------------|-------------------|
| Not Tracked | `#DCDCDC` | Gray (disabled if `-hide` used) |
| Initial | `#e1fce1` | Lightest green |
| Defined | `#81fc81` | Light green |
| Resilient | `#49fc49` | Green |
| Optimized | `#03ad03` | Dark green |

#### Using Exported JSON

1. Navigate to [ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/)
2. Click **Open Existing Layer** → **Upload from local**
3. Select `attack2jira.json`
4. Visualize your coverage with color-coded heatmap

---

## Configuration

attack2jira uses command-line parameters for configuration. No configuration files are required.

### Environment Variables

While not directly supported, you can use shell environment variables for convenience:

```bash
# Set environment variables
export JIRA_URL="https://acme.atlassian.net"
export JIRA_USER="security@acme.com"

# Use in commands
python3 attack2jira.py -url $JIRA_URL -u $JIRA_USER -a initialize
```

### Credential Management

**API Token Entry:**
- Prompted securely via `getpass` (input is hidden)
- Never stored on disk or in command history
- Must be entered for each execution

**Best Practice:**
Store API token in a secure credential manager:
```bash
# macOS Keychain
security add-generic-password -a $USER -s attack2jira -w <API_TOKEN>
JIRA_TOKEN=$(security find-generic-password -a $USER -s attack2jira -w)

# Linux secret-tool
secret-tool store --label="attack2jira" service jira username $JIRA_USER
JIRA_TOKEN=$(secret-tool lookup service jira username $JIRA_USER)
```

Then modify script to read from credential manager (requires code changes).

---

## Syncing Techniques

attack2jira creates techniques in a hierarchical structure matching ATT&CK's organization.

### Flat vs. Hierarchical Sync

**attack2jira uses hierarchical sync:**
- **Parent Techniques**: Created as Jira **Tasks**
- **Sub-Techniques**: Created as Jira **Sub-tasks** linked to parent

Example:
- **T1055** - Process Injection (Task)
  - **T1055.001** - Dynamic-link Library Injection (Sub-task of T1055)
  - **T1055.002** - Portable Executable Injection (Sub-task of T1055)
  - **T1055.003** - Thread Execution Hijacking (Sub-task of T1055)

### Technique Metadata

Each created issue includes:

| Field | Description | Example |
|-------|-------------|---------|
| **Summary** | Technique name | "Process Injection" |
| **Description** | Full ATT&CK description | "Adversaries may inject code..." |
| **Id** | ATT&CK technique ID | "T1055" |
| **Tactic** | Primary tactic | "privilege-escalation" |
| **Maturity** | Detection maturity | "Not Tracked" (default) |
| **URL** | Link to ATT&CK page | `https://attack.mitre.org/techniques/T1055/` |
| **Datasources** | Required data sources | ["Process Monitoring", "API Monitoring"] |
| **Sub-Technique of** | Parent reference (sub-techniques only) | Link to parent issue |

### Sorting Logic

Techniques are sorted by ID before creation to ensure:
1. Parent techniques created before sub-techniques
2. Proper parent-child linking
3. Numerical ordering (T1055 before T1055.001)

---

## Working with Custom Fields

attack2jira creates 6 custom fields to track ATT&CK metadata.

### Custom Field Definitions

#### 1. Tactic (Select - Single)
- **Purpose**: Primary ATT&CK tactic for the technique
- **Type**: Dropdown (single selection)
- **Options**: Populated from MITRE ATT&CK API
- **Example Values**:
  - initial-access
  - execution
  - persistence
  - privilege-escalation
  - defense-evasion
  - credential-access
  - discovery
  - lateral-movement
  - collection
  - command-and-control
  - exfiltration
  - impact

**Note**: Techniques with multiple tactics show only the first tactic.

---

#### 2. Maturity (Select - Single)
- **Purpose**: Track detection/prevention maturity level
- **Type**: Dropdown (single selection)
- **Options**: 5-level maturity model
- **Default**: "Not Tracked"

**Maturity Levels Explained:**

| Level | Meaning | Typical Criteria |
|-------|---------|------------------|
| **Not Tracked** | No detection capability | No monitoring, detection, or prevention |
| **Initial** | Ad-hoc detection | Basic alerts exist but not tested; high false positives |
| **Defined** | Documented detection | Detection logic documented and tested; moderate false positives |
| **Resilient** | Validated detection | Regularly tested; low false positives; some prevention |
| **Optimized** | Automated prevention | Automated blocking; minimal false positives; continuous testing |

**Usage Workflow:**
1. Assign technique to analyst
2. Analyst assesses current detection capabilities
3. Update **Maturity** field to reflect current state
4. Document findings in issue comments
5. Track improvements over time

---

#### 3. URL (URL Field)
- **Purpose**: Direct link to ATT&CK technique page
- **Type**: URL field (clickable link in Jira)
- **Example**: `https://attack.mitre.org/techniques/T1055/`
- **Benefit**: Quick reference to official documentation

---

#### 4. Datasources (Multi-Select)
- **Purpose**: Required data sources for detecting the technique
- **Type**: Multi-select dropdown
- **Options**: Populated from MITRE ATT&CK API
- **Example Values**:
  - Process Monitoring
  - API Monitoring
  - File Monitoring
  - Network Traffic
  - Windows Event Logs
  - Authentication Logs

**Usage:**
- Identify which data sources you need to collect
- Prioritize techniques based on available data sources
- Plan data collection infrastructure

---

#### 5. Id (Text Field)
- **Purpose**: ATT&CK technique identifier
- **Type**: Single-line text
- **Example**: "T1055.001"
- **Benefit**: Enables filtering and searching by technique ID

**Search Example:**
```
project = ATTACK AND Id ~ "T1055*"
```
Returns all T1055 techniques (parent and sub-techniques).

---

#### 6. Sub-Technique of (Text Field)
- **Purpose**: Reference to parent technique (for sub-techniques only)
- **Type**: Single-line text (contains URL to parent issue)
- **Example**: `https://acme.atlassian.net/browse/ATTACK-123`
- **Benefit**: Quick navigation to parent technique

---

### Customizing Fields

While attack2jira creates default fields, you can add additional fields:

**Via Jira UI:**
1. Go to **Jira Settings** → **Issues** → **Custom Fields**
2. Click **Create Custom Field**
3. Add fields like:
   - **Coverage Notes**: Multi-line text for detailed findings
   - **Test Date**: Date field for last assessment
   - **Risk Score**: Number field for prioritization

**Important**: Modifying attack2jira's default fields may break the export functionality.

---

## Maturity Tracking

The core value of attack2jira is tracking your defensive maturity over time.

### Assessment Process

#### Step 1: Assign Techniques
Use Jira's assignment feature:
- Assign techniques to specific analysts
- Group by tactic or data source
- Use bulk operations for efficiency

#### Step 2: Conduct Assessment
For each assigned technique:
1. Open the issue in Jira
2. Click the ATT&CK **URL** to review official documentation
3. Check if you have relevant **Datasources** available
4. Assess current detection/prevention capabilities
5. Determine appropriate **Maturity** level

#### Step 3: Document Findings
Add comments to the issue:
```
Current State: Initial
- We have Windows Event Log 4688 (process creation) enabled
- Basic alert triggers on suspicious process names
- High false positive rate (~30%)
- Not tested against actual adversary techniques

Next Steps:
- Implement Sysmon for enhanced process telemetry
- Tune detection logic using HELK
- Test against Atomic Red Team T1055 tests
- Target: Defined maturity by Q3 2024
```

#### Step 4: Update Regularly
Schedule periodic reassessments:
- Quarterly for "Not Tracked" and "Initial"
- Semi-annually for "Defined" and "Resilient"
- Annually for "Optimized" (with continuous monitoring)

### Tracking Progress

**Create Jira Filters:**
```
# Show all untracked techniques
project = ATTACK AND Maturity = "Not Tracked"

# Show techniques improving this quarter
project = ATTACK AND updated >= startOfQuarter()

# Show high-maturity techniques
project = ATTACK AND Maturity IN ("Resilient", "Optimized")
```

**Build Dashboards:**
- Pie chart: Maturity distribution
- Bar chart: Coverage by tactic
- Trend chart: Maturity improvements over time

---

## Exporting Navigator JSON

ATT&CK Navigator is a web application for visualizing coverage across the ATT&CK framework.

### Export Process

1. **Ensure techniques have maturity levels set** (not all "Not Tracked")
2. **Run export command:**
   ```bash
   python3 attack2jira.py -url https://acme.atlassian.net -u security@acme.com -a export
   ```
3. **Locate generated file:** `attack2jira.json` in current directory
4. **Upload to Navigator:**
   - Visit https://mitre-attack.github.io/attack-navigator/
   - Click **+ Create New Layer** → **Open Existing Layer** → **Upload from local**
   - Select `attack2jira.json`

### Navigator Features

Once loaded:
- **Color-coded heatmap**: Visual coverage representation
- **Filter by tactic**: Focus on specific attack stages
- **Search techniques**: Find specific techniques quickly
- **Export images**: Generate PNG/SVG for reports
- **Compare layers**: Compare coverage across teams or time periods

### Advanced: Automated Export

Schedule regular exports for reporting:

```bash
#!/bin/bash
# export_coverage.sh

DATE=$(date +%Y%m%d)
OUTPUT_DIR="/path/to/exports"

python3 /path/to/attack2jira.py \
  -url https://acme.atlassian.net \
  -u security@acme.com \
  -a export

mv attack2jira.json "$OUTPUT_DIR/coverage_$DATE.json"
echo "Coverage exported to coverage_$DATE.json"
```

Run via cron:
```cron
# Export coverage every Monday at 8 AM
0 8 * * 1 /path/to/export_coverage.sh
```

---

## Viewing Results in Jira

Maximize productivity by leveraging Jira's features.

### Project Views

**Board View:**
- Visualize techniques as cards
- Drag-and-drop to change status
- Group by Tactic, Maturity, or Assignee

**List View:**
- Spreadsheet-style view
- Bulk edit multiple techniques
- Export to CSV/Excel

**Backlog View:**
- Prioritize technique assessments
- Sprint planning for periodic reviews

### Filters and JQL

**Jira Query Language (JQL) Examples:**

```sql
-- Find all privilege escalation techniques
project = ATTACK AND Tactic = "privilege-escalation"

-- Find unassessed techniques
project = ATTACK AND Maturity = "Not Tracked"

-- Find techniques requiring specific data source
project = ATTACK AND Datasources = "Process Monitoring"

-- Find recently updated techniques
project = ATTACK AND updated >= -7d

-- Find sub-techniques only
project = ATTACK AND issuetype = Sub-task

-- Find high-priority techniques (requires custom field)
project = ATTACK AND Priority = High AND Maturity IN ("Not Tracked", "Initial")
```

### Automation Rules

**Example: Notify when technique reaches "Optimized":**
1. Go to **Project Settings** → **Automation**
2. Create rule:
   - **Trigger**: Field value changed
   - **Condition**: Maturity changed to "Optimized"
   - **Action**: Send email to security-team@acme.com

---

## Customization Options

Extend attack2jira to fit your organization's needs.

### Custom Maturity Models

Modify `/lib/jirahandler.py` line 157 to use custom maturity levels:

```python
# Original
payload=[{"name":"Not Tracked"},{"name":"Initial"},{"name":"Defined"},{"name":"Resilient"},{"name":"Optimized"}]

# Custom Example: NIST Cybersecurity Framework alignment
payload=[
    {"name":"Not Implemented"},
    {"name":"Partial"},
    {"name":"Implemented"},
    {"name":"Managed"},
    {"name":"Adaptive"}
]
```

**Important**: Also update `generate_json_layer()` color mappings.

### Adding Custom Fields

Modify `/lib/jirahandler.py` to add additional custom fields:

```python
# Add after line 126
custom_field7_dict = {
    "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
    "name": "SIEM Rule ID",
    "description": "Splunk/Elastic alert rule identifier",
    "type": "com.atlassian.jira.plugin.system.customfieldtypes:textfield"
}
custom_fields.append(custom_field7_dict)
```

### Linking to Detection Rules

Add links to your SIEM detection rules using Jira's link feature or custom URL fields.

---

## Tips & Tricks

### Tip 1: Bulk Update Maturity Levels

Use Jira's bulk edit feature:
1. Filter techniques (e.g., by tactic)
2. Select all (Ctrl+A)
3. **...** → **Bulk change** → **Edit issues**
4. Change **Maturity** field
5. Confirm changes

### Tip 2: Track Remediation Tasks

Create linked issues for remediation:
1. Open a technique issue
2. Click **Link** → **Create linked issue**
3. Issue type: **Story** or **Task**
4. Summary: "Implement detection for T1055"
5. Link type: **is blocked by**

Now you can track remediation progress separately.

### Tip 3: Use Labels for Categorization

Add labels for additional categorization:
- `datasource:windows-logs`
- `priority:high`
- `team:soc`
- `coverage:partial`

### Tip 4: Integrate with Incident Response

Reference ATT&CK techniques in incident tickets:
```
Incident #1234: Suspected ransomware

Observed Techniques:
- [ATTACK-123] T1486: Data Encrypted for Impact
- [ATTACK-456] T1490: Inhibit System Recovery
```

Jira automatically creates clickable links to technique issues.

---

## Best Practices

### 1. Regular Assessments
- Schedule quarterly "ATT&CK assessment sprints"
- Assign techniques systematically
- Track progress in Jira dashboards

### 2. Document Everything
- Use comments for assessment notes
- Attach evidence (screenshots, SIEM queries)
- Link to related documentation

### 3. Version Control Exports
- Export Navigator JSON after major assessments
- Store in Git repository
- Track changes over time

### 4. Align with Threat Intelligence
- Prioritize techniques used by relevant threat actors
- Tag techniques with threat actor names
- Focus assessments on likely attack paths

### 5. Integrate with Detection Engineering
- Link techniques to SIEM detection rules
- Track rule coverage in custom fields
- Use Jira to manage detection rule lifecycle

---

**You now have comprehensive knowledge of attack2jira's features. Happy tracking! 🎯**
