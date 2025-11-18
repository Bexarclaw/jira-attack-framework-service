# attack2jira Architecture

Technical architecture documentation for attack2jira.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Module Structure](#module-structure)
- [Data Flow](#data-flow)
- [API Interactions](#api-interactions)
- [Error Handling](#error-handling)
- [Retry Logic](#retry-logic)
- [Logging & Monitoring](#logging--monitoring)
- [Extensibility](#extensibility)
- [Design Decisions](#design-decisions)

---

## Overview

attack2jira is a Python-based command-line tool that bridges two systems:

1. **MITRE ATT&CK Framework** - Source of adversary tactics and techniques
2. **Jira Software Cloud** - Project management platform

The architecture follows a **service-oriented design** with clear separation between orchestration logic and API communication.

---

## System Architecture

### High-Level Architecture

```
┌─────────────────┐
│  Command Line   │
│    Interface    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Attack2Jira    │  ← Orchestration Layer
│     Class       │
└────────┬────────┘
         │
         ├──────────────────┬──────────────────┐
         v                  v                  v
┌─────────────────┐  ┌─────────────┐  ┌──────────────┐
│  JiraHandler    │  │  attackcti  │  │  JSON Export │
│     Class       │  │   Library   │  │    Module    │
└────────┬────────┘  └──────┬──────┘  └──────────────┘
         │                  │
         v                  v
┌─────────────────┐  ┌─────────────────┐
│  Jira Cloud     │  │  MITRE ATT&CK   │
│   REST API      │  │   TAXII Server  │
└─────────────────┘  └─────────────────┘
```

---

### Component Layers

| Layer | Components | Responsibility |
|-------|-----------|----------------|
| **CLI Layer** | `main()`, `argparse` | Parse arguments, invoke workflows |
| **Orchestration Layer** | `Attack2Jira` class | Coordinate workflows, business logic |
| **Service Layer** | `JiraHandler` class | Jira API communication |
| **Integration Layer** | `attackcti` library | MITRE ATT&CK data retrieval |
| **Export Layer** | `generate_json_layer()` | Navigator JSON generation |

---

## Module Structure

### File Organization

```
attack2jira/
├── attack2jira.py          # Main entry point, orchestration
├── lib/
│   ├── __init__.py         # Package initialization
│   └── jirahandler.py      # Jira API client
├── requirements.txt        # Python dependencies
├── README.md              # User documentation
└── docs/                  # Documentation suite
    ├── GETTING_STARTED.md
    ├── USER_GUIDE.md
    ├── INSTALLATION_GUIDE.md
    ├── CONFIGURATION_GUIDE.md
    ├── DEPLOYMENT_GUIDE.md
    ├── API_REFERENCE.md
    ├── TROUBLESHOOTING.md
    ├── WORKFLOWS.md
    ├── ARCHITECTURE.md
    ├── FAQ.md
    └── README.md
```

---

### attack2jira.py

**Purpose**: Orchestration and ATT&CK integration

**Key Classes:**
- `Attack2Jira`: Main orchestrator

**Key Methods:**
- `get_attack_techniques()`: Fetch techniques from MITRE
- `create_attack_techniques_and_subtechniques()`: Create Jira issues
- `generate_json_layer()`: Export Navigator JSON
- `set_up_jira_automated()`: Complete initialization workflow
- `main()`: CLI entry point

**Dependencies:**
- `attackcti`: MITRE ATT&CK data retrieval
- `lib.jirahandler`: Jira API operations
- `json`, `argparse`, `getpass`: Standard library

---

### lib/jirahandler.py

**Purpose**: Jira Cloud REST API client

**Key Classes:**
- `JiraHandler`: Jira API wrapper

**Key Methods:**

**Authentication:**
- `login()`: Authenticate to Jira Cloud

**Project Management:**
- `create_project()`: Create Jira Software project
- `get_project_id()`: Retrieve project ID

**Custom Fields:**
- `create_custom_fields()`: Create 6 ATT&CK custom fields
- `get_custom_fields()`: Retrieve field IDs
- `add_custom_field_options()`: Populate dropdown options
- `do_custom_fields_exist()`: Check if fields exist

**Issue Management:**
- `create_issue()`: Create Task or Sub-task
- `get_technique_maturity()`: Query issue maturity levels

**Screen Management:**
- `add_custom_fields_to_screen()`: Add fields to screens
- `hide_unwanted_fields()`: Configure field visibility
- `get_screen_ids()`, `get_screen_tab_ids()`: Navigate screen hierarchy

**ATT&CK Integration:**
- `get_attack_tactics()`: Fetch tactics
- `get_attack_datasources()`: Fetch data sources

**Dependencies:**
- `requests`: HTTP client for REST API calls
- `urllib3`: HTTP library (SSL warnings disabled)
- `attackcti`: ATT&CK data retrieval

---

## Data Flow

### Initialization Workflow

```
1. CLI Invocation
   └─> python3 attack2jira.py -url ... -u ... -a initialize

2. Argument Parsing
   └─> main() function parses command-line arguments

3. Authentication
   └─> getpass() prompts for API token securely
   └─> Attack2Jira.__init__() → JiraHandler.login()

4. Project Creation
   └─> JiraHandler.create_project()
       └─> POST /rest/simplified/latest/project

5. Custom Field Creation
   └─> JiraHandler.create_custom_fields()
       └─> POST /rest/api/3/field (6 times)

6. Field Option Population
   └─> JiraHandler.add_custom_field_options()
       ├─> get_attack_tactics() → attackcti API
       ├─> get_attack_datasources() → attackcti API
       └─> POST /rest/globalconfig/1/customfieldoptions/{field_id}

7. Screen Configuration
   └─> JiraHandler.add_custom_fields_to_screen()
       └─> POST /rest/api/3/screens/{id}/tabs/{id}/fields
   └─> JiraHandler.hide_unwanted_fields()
       └─> PUT /rest/issuedetailslayout/config/classic/screen

8. Technique Import
   └─> Attack2Jira.create_attack_techniques_and_subtechniques()
       ├─> attackcti.get_enterprise() → Fetch all techniques
       ├─> Sort by technique ID
       └─> For each technique:
           ├─> If parent: Create Task
           └─> If sub-technique: Create Sub-task
               └─> POST /rest/api/2/issue (600+ times)

9. Completion
   └─> Return to CLI
```

**Total API Calls**: ~650 (6 fields + 600 issues + 50 configuration)

---

### Export Workflow

```
1. CLI Invocation
   └─> python3 attack2jira.py -url ... -u ... -a export

2. Authentication
   └─> JiraHandler.login()

3. Query Issues
   └─> JiraHandler.get_technique_maturity()
       └─> GET /rest/api/3/search?jql=project=ATTACK&startAt={offset}
       └─> Pagination: 50 issues per request (~12 requests for 600 issues)

4. Build Maturity Map
   └─> {technique_id: maturity_value} dictionary

5. Generate JSON Layer
   └─> Attack2Jira.generate_json_layer()
       ├─> Map maturity values to colors
       ├─> Build Navigator JSON structure
       └─> Write to attack2jira.json

6. Completion
   └─> File written to disk
```

**Total API Calls**: ~15 (authentication + paginated queries)

---

## API Interactions

### Jira Cloud REST API

**Base URL**: `https://{site}.atlassian.net`

**Authentication**: HTTP Basic Auth
- Username: Email address
- Password: API token

**Key Endpoints Used:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/rest/api/2/issue/createmeta` | GET | Verify authentication |
| `/rest/simplified/latest/project` | POST | Create project |
| `/rest/api/3/field` | POST | Create custom field |
| `/rest/api/3/field` | GET | List all fields |
| `/rest/globalconfig/1/customfieldoptions/{id}` | POST | Add field options |
| `/rest/api/2/issue` | POST | Create issue |
| `/rest/api/3/search` | GET | Query issues (JQL) |
| `/rest/api/3/screens/{id}/tabs/{id}/fields` | POST | Add field to screen |
| `/rest/issuedetailslayout/config/classic/screen` | PUT | Configure field layout |
| `/rest/api/3/project/search` | GET | List projects |
| `/rest/api/2/screenscheme` | GET | Get screen scheme |

**Rate Limits**:
- Free/Standard: 50,000 requests/hour/IP
- Premium: 150,000 requests/hour/IP

---

### MITRE ATT&CK TAXII Server

**Library**: `attackcti` Python client

**Server**: `cti-taxii.mitre.org`

**Key Methods:**

```python
from attackcti import attack_client

client = attack_client()

# Get all enterprise data
enterprise = client.get_enterprise()

# Get techniques
techniques = client.get_techniques()

# Get tactics
tactics = client.get_tactics()

# Get data sources
datasources = client.get_data_sources()  # Note: Deprecated, uses workaround
```

**Data Format**: STIX 2.0 JSON objects

---

## Error Handling

### Current Implementation

**Philosophy**: Fail fast with explicit error messages

**Pattern**:
```python
try:
    # API call
    r = requests.post(...)

    if r.status_code == 200:
        # Success
        return result
    elif r.status_code == 401:
        print('[!] Unauthorized')
        sys.exit(1)
    else:
        print('[!] Error occurred')
        sys.exit(1)

except Exception as ex:
    print(f'[!] Exception: {ex}')
    traceback.print_exc(file=sys.stdout)
    sys.exit(1)
```

**Behavior**:
- Critical failures (authentication, project creation) → `sys.exit(1)`
- Issue creation failures → Print error, continue with next issue
- Network errors → Immediate exit (no retry)

---

### Recommended Enhancements

**1. Graceful Degradation**
```python
# Instead of sys.exit(), raise custom exceptions
class Attack2JiraException(Exception):
    pass

class AuthenticationError(Attack2JiraException):
    pass

class RateLimitError(Attack2JiraException):
    pass
```

**2. Retry Logic**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def create_issue_with_retry(self, issue_dict, id):
    # Will retry up to 3 times with exponential backoff
    return self.create_issue(issue_dict, id)
```

---

## Retry Logic

### Current Implementation

**No automatic retry** - Single attempt for all operations

**Impact**:
- Transient network failures cause complete abort
- Rate limiting not handled gracefully
- Large imports vulnerable to connection drops

---

### Recommended Implementation

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = backoff ** attempt
                    print(f"[!] Retry {attempt+1}/{max_retries} in {wait_time}s...")
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator

# Usage
@retry_on_failure(max_retries=3, backoff=2)
def create_issue(self, issue_dict, id):
    # Existing logic
    pass
```

---

## Logging & Monitoring

### Current Implementation

**Logging**: Basic print statements to stdout

**Example**:
```python
print("[*] Creating Jira issues for ATT&CK's techniques...")
print("\t[!] Successfully created Jira issue for " + id)
print("[!] Error creating Jira issue for " + id)
```

**No structured logging** - Difficult to parse, no log levels, no persistence

---

### Recommended Enhancement

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

# Usage
logger.info("Creating Jira issues for ATT&CK techniques")
logger.debug(f"Issue payload: {issue_dict}")
logger.warning("Rate limit approaching")
logger.error(f"Failed to create issue for {id}: {error}")
```

**Benefits**:
- Log levels for filtering
- Timestamps for troubleshooting
- Persistent logs for auditing
- Structured format for log aggregation

---

## Extensibility

### Design for Extension

attack2jira is designed for customization via:

**1. Custom Fields**
- Add new fields in `create_custom_fields()`
- Populate in `create_attack_techniques_and_subtechniques()`

**2. Maturity Models**
- Modify `add_custom_field_options()` for custom levels
- Update color mapping in `generate_json_layer()`

**3. ATT&CK Matrices**
- Modify `get_attack_techniques()` to use different matrices:
  ```python
  mobile = client.get_mobile()  # Mobile ATT&CK
  ics = client.get_ics()        # ICS ATT&CK
  ```

**4. Integration Points**
- After issue creation: Add webhooks, SIEM integration
- After export: Push to S3, send to Slack, trigger CI/CD

---

### Extension Example: Add NIST Mapping

**1. Add custom field:**
```python
# In lib/jirahandler.py, create_custom_fields()
custom_field7_dict = {
    "name": "NIST Control",
    "description": "NIST 800-53 Control Mapping",
    "type": "com.atlassian.jira.plugin.system.customfieldtypes:textfield"
}
custom_fields.append(custom_field7_dict)
```

**2. Populate field:**
```python
# In attack2jira.py, create_attack_techniques_and_subtechniques()
nist_mapping = map_technique_to_nist(technique_id)  # Your custom function

issue_dict["fields"][custom_fields['NIST Control']] = nist_mapping
```

---

## Design Decisions

### Why Jira Cloud Only?

**Decision**: Support only Jira Cloud (not Server/Data Center)

**Rationale**:
- Cloud API endpoints differ significantly (`/rest/simplified/latest/project`)
- Cloud-only features (simplified project creation, screen layout API)
- Atlassian moving toward cloud-first development
- Server/Data Center requires different authentication (PAT vs API token)

**Impact**: Limits audience to Jira Cloud customers

---

### Why No Configuration Files?

**Decision**: All configuration via CLI arguments, no config files

**Rationale**:
- Reduces attack surface (no credentials on disk)
- Simplifies deployment (no config file management)
- Explicit parameters improve security awareness
- Easy to integrate with secrets managers

**Impact**: Slightly more verbose CLI commands

---

### Why Flat File Export (JSON)?

**Decision**: Export to local JSON file instead of cloud storage

**Rationale**:
- No additional dependencies (cloud SDKs)
- User controls storage location
- Works offline
- Compatible with ATT&CK Navigator (local upload)

**Impact**: Requires manual file management for history tracking

---

### Why attackcti Library?

**Decision**: Use existing `attackcti` library instead of direct TAXII calls

**Rationale**:
- Battle-tested, maintained by community
- Handles STIX parsing complexity
- Simplifies ATT&CK version management
- Reduces code complexity

**Impact**: Dependency on external library

---

**Architecture documentation complete! Understand the system internals. 🏗️**
