# attack2jira API Reference

Complete Python API documentation for extending and integrating attack2jira.

## Table of Contents

- [Overview](#overview)
- [Attack2Jira Class](#attack2jira-class)
- [JiraHandler Class](#jirahandler-class)
- [Integration Examples](#integration-examples)
- [Error Handling](#error-handling)
- [Custom Extensions](#custom-extensions)

---

## Overview

attack2jira consists of two primary classes:

1. **Attack2Jira**: Orchestration layer - manages workflow and MITRE ATT&CK integration
2. **JiraHandler**: Jira API client - handles all Jira Cloud REST API interactions

---

## Attack2Jira Class

Main orchestration class for attack2jira operations.

**Location**: `attack2jira.py`

### Constructor

```python
Attack2Jira(url, username, password)
```

**Parameters:**
- `url` (str): Jira Cloud instance URL (e.g., `https://acme.atlassian.net`)
- `username` (str): Jira user email address
- `password` (str): Jira API token

**Returns**: Attack2Jira instance

**Example:**
```python
from attack2jira import Attack2Jira

attack2jira = Attack2Jira(
    url="https://acme.atlassian.net",
    username="security@acme.com",
    password="your-api-token-here"
)
```

---

### Methods

#### get_attack_techniques()

**Deprecated** - Kept for backward compatibility.

Fetches all enterprise techniques from MITRE ATT&CK.

```python
def get_attack_techniques(self)
```

**Parameters**: None

**Returns**:
- List of dictionaries containing technique data
- None if error occurs

**Example:**
```python
techniques = attack2jira.get_attack_techniques()
for technique in techniques:
    print(f"{technique['external_references'][0]['external_id']}: {technique['name']}")
```

**Note**: Use `create_attack_techniques_and_subtechniques()` instead for hierarchical structure.

---

#### create_attack_techniques()

**Deprecated** - Creates flat technique list without sub-technique hierarchy.

```python
def create_attack_techniques(self, key)
```

**Parameters:**
- `key` (str): Jira project key

**Returns**: None

**Note**: Use `create_attack_techniques_and_subtechniques()` instead.

---

#### create_attack_techniques_and_subtechniques()

**Primary method** - Creates hierarchical technique structure with sub-techniques.

```python
def create_attack_techniques_and_subtechniques(self, key)
```

**Parameters:**
- `key` (str): Jira project key (e.g., "ATTACK")

**Returns**: None

**Behavior**:
1. Fetches all enterprise techniques from MITRE ATT&CK
2. Sorts techniques by ID to ensure parent-child ordering
3. Creates parent techniques as Jira **Tasks**
4. Creates sub-techniques as Jira **Sub-tasks** linked to parents
5. Populates custom fields (Id, Tactic, Maturity, URL, Datasources)

**Example:**
```python
attack2jira = Attack2Jira(url, username, token)
attack2jira.jirahandler.create_project("ATT&CK Coverage", "ATTACK")
attack2jira.create_attack_techniques_and_subtechniques("ATTACK")
```

**Output:**
```
[*] Creating Jira issues for ATT&CK's techniques...
    [!] Successfully created Jira issue for T1001
    [!] Successfully created Jira issue for T1001.001
    [!] Successfully created Jira issue for T1001.002
    ...
[*] Done!
```

---

#### generate_json_layer()

Exports ATT&CK Navigator JSON layer based on Jira maturity levels.

```python
def generate_json_layer(self, hideDisabled)
```

**Parameters:**
- `hideDisabled` (bool): If True, hides "Not Tracked" techniques in Navigator

**Returns**: None (writes `attack2jira.json` to disk)

**JSON Structure:**
```json
{
  "domain": "mitre-enterprise",
  "name": "Attack2Jira",
  "description": "Attack2Jira",
  "version": "2.2",
  "hideDisabled": false,
  "gradient": {
    "colors": ["#DCDCDC", "#03ad03"]
  },
  "techniques": [
    {
      "techniqueID": "T1055",
      "enabled": true,
      "color": "#49fc49"
    }
  ]
}
```

**Color Mapping:**
- `#DCDCDC` - Not Tracked (gray)
- `#e1fce1` - Initial (lightest green)
- `#81fc81` - Defined (light green)
- `#49fc49` - Resilient (green)
- `#03ad03` - Optimized (dark green)

**Example:**
```python
attack2jira.generate_json_layer(hideDisabled=False)
# Creates attack2jira.json in current directory
```

---

#### set_up_jira_automated()

Complete automated setup workflow. Calls all necessary methods in sequence.

```python
def set_up_jira_automated(self, project, key)
```

**Parameters:**
- `project` (str): Jira project display name
- `key` (str): Jira project key (2-10 uppercase letters)

**Returns**: None

**Workflow:**
1. Create Jira project
2. Create 6 custom fields
3. Populate field options (tactics, maturity, data sources)
4. Add custom fields to screen
5. Hide unnecessary default fields
6. Create all ATT&CK techniques and sub-techniques

**Example:**
```python
attack2jira = Attack2Jira(url, username, token)
attack2jira.set_up_jira_automated("Security Coverage", "SEC")
```

---

## JiraHandler Class

Jira Cloud REST API client.

**Location**: `lib/jirahandler.py`

### Constructor

```python
JiraHandler(url, username, password)
```

**Parameters:**
- `url` (str): Jira Cloud instance URL
- `username` (str): Jira user email
- `password` (str): Jira API token

**Returns**: JiraHandler instance

**Automatically calls `login()` method**

---

### Authentication Methods

#### login()

Authenticates to Jira Cloud and validates credentials.

```python
def login(self, url, username, apitoken)
```

**Parameters:**
- `url` (str): Jira Cloud URL
- `username` (str): Email address
- `apitoken` (str): API token

**Returns**: None (exits on failure)

**Example:**
```python
handler = JiraHandler(
    url="https://acme.atlassian.net",
    username="user@acme.com",
    apitoken="your-token"
)
# Automatically authenticates
```

**Output:**
```
[*] Authenticating to https://acme.atlassian.net...
[!] Success!
```

---

### Project Management Methods

#### create_project()

Creates a new Jira Software project.

```python
def create_project(self, project, key)
```

**Parameters:**
- `project` (str): Project display name
- `key` (str): Project key (2-10 uppercase letters)

**Returns**: None (exits on failure)

**API Endpoint**: `POST /rest/simplified/latest/project`

**Example:**
```python
handler.create_project("ATT&CK Coverage", "ATTACK")
```

**Template**: Uses Scrum template (`com.pyxis.greenhopper.jira:gh-simplified-basic`)

---

#### get_project_id()

Retrieves project ID by project key.

```python
def get_project_id(self, key)
```

**Parameters:**
- `key` (str): Project key

**Returns**:
- `str`: Project ID
- `0`: If project not found

**Example:**
```python
project_id = handler.get_project_id("ATTACK")
print(f"Project ID: {project_id}")
```

---

### Custom Field Methods

#### create_custom_fields()

Creates 6 custom fields for ATT&CK metadata.

```python
def create_custom_fields(self)
```

**Parameters**: None

**Returns**: None

**Fields Created:**
1. **Tactic** - Select (dropdown)
2. **Maturity** - Select (dropdown)
3. **Url** - URL field
4. **Datasources** - Multi-select
5. **Id** - Text field
6. **Sub-Technique of** - Text field

**API Endpoint**: `POST /rest/api/3/field`

**Example:**
```python
handler.create_custom_fields()
```

**Output:**
```
[*] Creating custom fields ...
    [!] Successfully created 'Tactic' custom field.
    [!] Successfully created 'Maturity' custom field.
    ...
```

---

#### get_custom_fields()

Retrieves custom field IDs by name.

```python
def get_custom_fields(self)
```

**Parameters**: None

**Returns**: Dictionary mapping field names to field IDs

**Example:**
```python
custom_fields = handler.get_custom_fields()
print(custom_fields)
# Output: {'Tactic': 'customfield_10090', 'Maturity': 'customfield_10091', ...}
```

**Usage in issue creation:**
```python
issue_dict = {
    "fields": {
        custom_fields['Maturity']: {'value': 'Defined'},
        custom_fields['Id']: 'T1055'
    }
}
```

---

#### add_custom_field_options()

Populates dropdown options for Tactic, Maturity, and Datasources fields.

```python
def add_custom_field_options(self)
```

**Parameters**: None

**Returns**: None

**Options Added:**
- **Maturity**: Not Tracked, Initial, Defined, Resilient, Optimized
- **Tactic**: Fetched from MITRE ATT&CK (14 tactics)
- **Datasources**: Fetched from MITRE ATT&CK techniques

**API Endpoint**: `POST /rest/globalconfig/1/customfieldoptions/{field_id}`

---

#### do_custom_fields_exist()

Checks if attack2jira custom fields already exist.

```python
def do_custom_fields_exist(self)
```

**Parameters**: None

**Returns**:
- `True`: All 6 custom fields exist
- `False`: One or more fields missing

**Example:**
```python
if handler.do_custom_fields_exist():
    print("Custom fields already configured")
else:
    handler.create_custom_fields()
```

---

### Issue Management Methods

#### create_issue()

Creates a Jira issue (Task or Sub-task).

```python
def create_issue(self, issue_dict, id)
```

**Parameters:**
- `issue_dict` (dict): Jira issue payload (JSON)
- `id` (str): Technique ID for logging (e.g., "T1055")

**Returns**:
- Dictionary with `id` and `key` of created issue
- Exits on failure

**API Endpoint**: `POST /rest/api/2/issue`

**Example (Parent Technique):**
```python
issue_dict = {
    "fields": {
        "project": {"key": "ATTACK"},
        "summary": "Process Injection",
        "description": "Adversaries may inject code...",
        "issuetype": {"name": "Task"},
        custom_fields['Id']: "T1055",
        custom_fields['Tactic']: {"value": "privilege-escalation"},
        custom_fields['Maturity']: {"value": "Not Tracked"},
        custom_fields['Url']: "https://attack.mitre.org/techniques/T1055/",
        custom_fields['Datasources']: [{"value": "Process Monitoring"}]
    }
}
parent = handler.create_issue(issue_dict, "T1055")
print(f"Created: {parent['key']}")  # ATTACK-123
```

**Example (Sub-technique):**
```python
issue_dict = {
    "fields": {
        "parent": {"id": parent['id']},
        "project": {"key": "ATTACK"},
        "summary": "DLL Injection",
        "description": "Adversaries may inject DLLs...",
        "issuetype": {"name": "Sub-task"},
        custom_fields['Id']: "T1055.001",
        custom_fields['Sub-Technique of']: f"https://acme.atlassian.net/browse/{parent['key']}"
    }
}
handler.create_issue(issue_dict, "T1055.001")
```

---

#### get_technique_maturity()

Retrieves maturity levels for all techniques in ATTACK project.

```python
def get_technique_maturity(self)
```

**Parameters**: None

**Returns**: Dictionary mapping technique IDs to maturity objects

**API Endpoint**: `GET /rest/api/3/search?jql=project=ATTACK&startAt={offset}`

**Example:**
```python
maturity_map = handler.get_technique_maturity()
print(maturity_map)
# Output: {'T1055': {'value': 'Defined'}, 'T1055.001': {'value': 'Initial'}, ...}
```

**Pagination**: Automatically handles large result sets (50 issues per page)

---

### ATT&CK Data Methods

#### get_attack_tactics()

Fetches all tactics from MITRE ATT&CK.

```python
def get_attack_tactics(self)
```

**Parameters**: None

**Returns**: List of dictionaries with tactic names

**Example:**
```python
tactics = handler.get_attack_tactics()
print(tactics)
# [{'name': 'initial-access'}, {'name': 'execution'}, ...]
```

---

#### get_attack_datasources()

Fetches all data sources from MITRE ATT&CK techniques.

```python
def get_attack_datasources(self)
```

**Parameters**: None

**Returns**: List of dictionaries with data source names

**Note**: Uses workaround due to ATT&CK API inconsistencies

**Example:**
```python
datasources = handler.get_attack_datasources()
print(datasources)
# [{'name': 'Process Monitoring'}, {'name': 'File Monitoring'}, ...]
```

---

### Screen Management Methods

#### add_custom_fields_to_screen()

Adds custom fields to Jira issue screens.

```python
def add_custom_fields_to_screen(self, key)
```

**Parameters:**
- `key` (str): Project key

**Returns**: None

**API Endpoint**: `POST /rest/api/3/screens/{screen_id}/tabs/{tab_id}/fields`

---

#### hide_unwanted_fields()

Configures field visibility in issue layout.

```python
def hide_unwanted_fields(self, key)
```

**Parameters:**
- `key` (str): Project key

**Returns**: None

**Hidden Fields**: Priority (moved), Time tracking, Components, Fix versions, etc.

**Visible Fields**: Custom ATT&CK fields, Description, Assignee, Reporter, Labels

---

## Integration Examples

### Example 1: Custom Maturity Assessment Script

```python
from lib.jirahandler import JiraHandler

# Initialize
handler = JiraHandler(
    url="https://acme.atlassian.net",
    username="user@acme.com",
    apitoken="token"
)

# Get current maturity
maturity_map = handler.get_technique_maturity()

# Calculate coverage percentage
total = len(maturity_map)
tracked = sum(1 for v in maturity_map.values() if v['value'] != "Not Tracked")
coverage_pct = (tracked / total) * 100

print(f"Coverage: {coverage_pct:.1f}% ({tracked}/{total} techniques)")
```

---

### Example 2: Bulk Update Maturity Levels

```python
import requests

handler = JiraHandler(url, username, token)
custom_fields = handler.get_custom_fields()

# Update all T1055.* sub-techniques to "Initial"
for technique_id in ["T1055.001", "T1055.002", "T1055.003"]:
    # Find issue by technique ID
    jql = f"project=ATTACK AND Id~'{technique_id}'"
    r = requests.get(
        f"{handler.url}/rest/api/3/search?jql={jql}",
        auth=(handler.username, handler.apitoken)
    )
    issue_key = r.json()['issues'][0]['key']

    # Update maturity
    update_payload = {
        "fields": {
            custom_fields['Maturity']: {"value": "Initial"}
        }
    }
    requests.put(
        f"{handler.url}/rest/api/3/issue/{issue_key}",
        json=update_payload,
        auth=(handler.username, handler.apitoken)
    )
    print(f"Updated {technique_id} to Initial")
```

---

### Example 3: Export Coverage Report

```python
from attack2jira import Attack2Jira

attack2jira = Attack2Jira(url, username, token)
attack2jira.generate_json_layer(hideDisabled=True)

# Parse generated JSON
import json
with open('attack2jira.json') as f:
    layer = json.load(f)

# Generate summary report
maturity_counts = {}
for technique in layer['techniques']:
    color = technique['color']
    maturity_counts[color] = maturity_counts.get(color, 0) + 1

print("Maturity Distribution:")
print(f"  Optimized: {maturity_counts.get('#03ad03', 0)}")
print(f"  Resilient: {maturity_counts.get('#49fc49', 0)}")
print(f"  Defined: {maturity_counts.get('#81fc81', 0)}")
print(f"  Initial: {maturity_counts.get('#e1fce1', 0)}")
```

---

## Error Handling

All methods use basic error handling with `try/except` blocks and `sys.exit()` on critical failures.

**Recommendation**: Wrap calls in your own error handling for production use:

```python
try:
    attack2jira.set_up_jira_automated("ATT&CK", "ATTACK")
except Exception as e:
    logging.error(f"Initialization failed: {e}")
    # Send alert
    # Retry logic
    # Rollback
```

---

## Custom Extensions

### Adding New Custom Fields

1. Edit `/lib/jirahandler.py` method `create_custom_fields()`
2. Add field definition
3. Update `get_custom_fields()` to include new field
4. Modify `create_attack_techniques_and_subtechniques()` to populate field

---

### Integrating with SIEM

Link techniques to detection rules:

```python
# After creating issue, add SIEM rule link
issue_key = handler.create_issue(issue_dict, technique_id)['key']

# Add comment with SIEM rule reference
comment = {
    "body": f"Splunk Rule: correlation_T1055_process_injection"
}
requests.post(
    f"{handler.url}/rest/api/3/issue/{issue_key}/comment",
    json=comment,
    auth=(handler.username, handler.apitoken)
)
```

---

**API Reference complete! Build powerful integrations with attack2jira. 🛠️**
