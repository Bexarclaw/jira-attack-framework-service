# attack2jira Troubleshooting Guide

Comprehensive troubleshooting guide for common attack2jira issues and their solutions.

## Table of Contents

- [Authentication Errors](#authentication-errors)
- [API Rate Limiting](#api-rate-limiting)
- [Custom Field Errors](#custom-field-errors)
- [Issue Creation Failures](#issue-creation-failures)
- [Navigator Export Issues](#navigator-export-issues)
- [Performance Problems](#performance-problems)
- [Network Issues](#network-issues)
- [Debugging Techniques](#debugging-techniques)

---

## Authentication Errors

### Error: "401 Unauthorized"

**Full Error:**
```
[!] Wrong username or password :( .
```

**Causes:**
1. Invalid API token
2. Incorrect email address
3. Token has been revoked
4. Using password instead of API token

**Solutions:**

**1. Regenerate API Token:**
```bash
# Navigate to: https://id.atlassian.com/manage-profile/security/api-tokens
# Click "Create API token"
# Copy new token
# Retry with new token
```

**2. Verify Email Address:**
```bash
# Test authentication with curl
curl -u your-email@company.com:your-api-token \
  https://yourcompany.atlassian.net/rest/api/2/myself

# Should return JSON with your user details
```

**3. Check for Whitespace:**
```bash
# When pasting API token, ensure no trailing spaces
# Use quotes in scripts:
API_TOKEN="paste-token-here"
```

**4. Verify Account Access:**
- Log into Jira web interface with same email
- Ensure account is active (not suspended)
- Check if account has been migrated to different email

---

### Error: "Unauthorized. Probably not enough permissions"

**Full Error:**
```
[!] Unauthorized. Probably not enough permissions :(
```

**Cause**: User lacks Jira Administrator global permission

**Verification:**
1. Log into Jira Cloud
2. Navigate to **Jira Settings** → **System** → **Global permissions**
3. Check if your user is listed under **Jira Administrators**

**Solutions:**

**Option 1: Request Admin Access**
```
Contact your Jira administrator with this message:

"I need Jira Administrator permission to run attack2jira, which creates
custom fields for ATT&CK coverage tracking. This permission is required
to create custom fields via the REST API."
```

**Option 2: Use Admin Account**
```bash
# Have a Jira admin run initialization for you
python3 attack2jira.py -url https://company.atlassian.net -u admin@company.com -a initialize
```

**Option 3: Manual Field Creation**
- Have admin create custom fields manually via Jira UI
- Modify attack2jira to skip field creation step

---

## API Rate Limiting

### Error: "429 Too Many Requests"

**Symptoms:**
- Slow or failed issue creation
- Intermittent timeouts
- API calls failing mid-process

**Cause**: Jira Cloud API rate limits exceeded

**Jira Cloud Rate Limits:**
- **Free/Standard**: 50,000 requests per hour per IP
- **Premium**: 150,000 requests per hour per IP
- **Enterprise**: Custom limits

**Solutions:**

**1. Add Delays Between API Calls:**

Edit `lib/jirahandler.py` in `create_issue()` method:
```python
import time

def create_issue(self, issue_dict, id):
    # ... existing code ...

    # Add delay to avoid rate limiting
    time.sleep(0.5)  # 500ms delay between issues

    r = requests.post(...)
```

**2. Implement Exponential Backoff:**

```python
import time

def create_issue_with_retry(self, issue_dict, id, max_retries=3):
    for attempt in range(max_retries):
        try:
            r = requests.post(self.url + '/rest/api/2/issue', ...)
            if r.status_code == 201:
                return json.loads(r.text)
            elif r.status_code == 429:
                wait_time = (2 ** attempt)  # Exponential: 1s, 2s, 4s
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                break
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")

    # Original error handling
    print(f"[!] Error creating Jira issue for {id}")
    sys.exit()
```

**3. Run During Off-Peak Hours:**
```bash
# Schedule for low-traffic times
crontab -e
# Run at 2 AM UTC when usage is low
0 2 * * * /path/to/attack2jira_wrapper.sh -a initialize
```

**4. Monitor Rate Limit Headers:**
```python
r = requests.post(...)
print(f"Rate Limit Remaining: {r.headers.get('X-RateLimit-Remaining')}")
print(f"Rate Limit Reset: {r.headers.get('X-RateLimit-Reset')}")
```

---

## Custom Field Errors

### Error: "Error creating custom fields"

**Causes:**
1. Custom fields already exist
2. Insufficient permissions
3. Jira plan doesn't support custom fields (rare)

**Solution 1: Check Existing Fields**

```bash
# List all custom fields
curl -u user@company.com:api-token \
  https://company.atlassian.net/rest/api/3/field | jq '.[] | select(.custom==true) | {name: .name, id: .id}'

# Look for: Tactic, Maturity, Url, Datasources, Id, Sub-Technique of
```

**If fields exist:**
- attack2jira will detect and skip creation
- Ensure field types match (Select, URL, Multi-select, Text)
- Delete conflicting fields if needed

**Solution 2: Manual Field Deletion**

1. **Jira Settings** → **Issues** → **Custom Fields**
2. Search for "Tactic", "Maturity", etc.
3. Click **...** → **Delete**
4. Confirm deletion
5. Retry attack2jira

**Warning**: Deleting custom fields removes data from ALL projects using them.

---

### Error: "Error creating options for custom field"

**Full Error:**
```
[!] Error creating options for the maturity custom field.
```

**Cause**: API endpoint for adding field options failed

**Debug Steps:**

```bash
# Get custom field ID
curl -u user@company.com:api-token \
  https://company.atlassian.net/rest/api/3/field | grep -A2 "Maturity"

# Manually add options via API
curl -X POST \
  -u user@company.com:api-token \
  -H "Content-Type: application/json" \
  -d '[{"name":"Not Tracked"},{"name":"Initial"}]' \
  https://company.atlassian.net/rest/globalconfig/1/customfieldoptions/customfield_XXXXX
```

**Solution**: Update attackcti library
```bash
pip3 install --upgrade attackcti requests
```

---

## Issue Creation Failures

### Error: "Could not create ticket for T1234"

**Full Error:**
```
[*] Could not create ticket for T1055.001
{error details}
```

**Common Causes:**

**1. Parent Issue Not Created Yet**

For sub-techniques, parent must exist first.

**Solution**: attack2jira sorts by ID automatically, but verify:
```python
# In attack2jira.py line 98
sorted_techniques = sorted(techniques, key=lambda k: k['external_references'][0]['external_id'])
```

**2. Missing Required Fields**

**Debug**:
```bash
# Check issue creation payload
# Add print statement in attack2jira.py before line 162
print(json.dumps(issue_dict, indent=2))
```

**3. Invalid Custom Field ID**

**Verify custom fields exist:**
```python
custom_fields = handler.get_custom_fields()
print(custom_fields)
# Should have 6 fields
```

**Solution**: Re-run custom field creation
```bash
# Delete existing fields
# Re-run: python3 attack2jira.py -a initialize
```

---

### Error: "Sub-task issue type not found"

**Cause**: Jira project doesn't have Sub-task issue type enabled

**Solution**:

1. Go to **Project Settings** → **Issue types**
2. Ensure **Sub-task** is enabled
3. If missing, add it via **Jira Settings** → **Issues** → **Issue types**

---

## Navigator Export Issues

### Error: "attack2jira.json not found"

**Cause**: Export command failed silently or ran in wrong directory

**Solutions:**

**1. Check Current Directory:**
```bash
pwd  # Ensure you're in the right directory
ls -la attack2jira.json
```

**2. Verbose Debugging:**
```bash
# Add debug output
python3 attack2jira.py -url https://company.atlassian.net -u user@company.com -a export
echo "Exit code: $?"  # Should be 0 for success
```

**3. Check Permissions:**
```bash
# Ensure write permissions
ls -ld $(pwd)
# Should show 'w' permission
```

---

### Issue: Navigator Shows Wrong Colors

**Symptom**: Techniques have incorrect colors in ATT&CK Navigator

**Cause**: Maturity field values don't match color mapping

**Debug:**
```python
# Check maturity values in Jira
handler = JiraHandler(url, username, token)
maturity_map = handler.get_technique_maturity()

# Check for unexpected values
for tech_id, maturity in maturity_map.items():
    if maturity['value'] not in ["Not Tracked", "Initial", "Defined", "Resilient", "Optimized"]:
        print(f"Unexpected maturity for {tech_id}: {maturity['value']}")
```

**Solution**: Update color mapping in `generate_json_layer()` to match your custom maturity levels

---

## Performance Problems

### Issue: Initialization Takes Too Long (>15 minutes)

**Expected Time**: 5-10 minutes for ~600 techniques

**Causes:**
1. Network latency to Jira Cloud
2. Rate limiting (see [API Rate Limiting](#api-rate-limiting))
3. Large number of existing issues in project

**Solutions:**

**1. Check Network Latency:**
```bash
# Ping Jira instance
ping yourcompany.atlassian.net

# Measure API response time
time curl -u user@company.com:token https://yourcompany.atlassian.net/rest/api/2/myself
```

**2. Use VPS in Same Region:**
- If Jira is in US East, use AWS us-east-1
- Reduces latency from 200ms to <50ms

**3. Increase Pagination Size:**

Edit `lib/jirahandler.py` line 383:
```python
# Current: 50 issues per page
read_issues += 50
startAt += 50

# Faster: 100 issues per page
read_issues += 100
startAt += 100
```

---

### Issue: Export Takes Too Long

**Expected Time**: 30-60 seconds

**Causes:**
1. Large project (1000+ issues)
2. Complex JQL queries
3. Network latency

**Solution: Cache Results:**

```python
# Add caching to avoid repeated API calls
import pickle
import os

def get_technique_maturity_cached(self):
    cache_file = '/tmp/attack2jira_cache.pkl'

    if os.path.exists(cache_file) and (time.time() - os.path.getmtime(cache_file)) < 3600:
        # Use cache if less than 1 hour old
        with open(cache_file, 'rb') as f:
            return pickle.load(f)

    # Fetch fresh data
    data = self.get_technique_maturity()

    # Cache result
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)

    return data
```

---

## Network Issues

### Error: "Error connecting to Att&ck's API"

**Full Error:**
```
[!] Error connecting obtaining tactics from Att&ck's API !
```

**Causes:**
1. No internet connectivity
2. Firewall blocking HTTPS to `cti-taxii.mitre.org`
3. MITRE API downtime
4. Corporate proxy intercepting traffic

**Solutions:**

**1. Test Connectivity:**
```bash
# Test MITRE API
curl -I https://cti-taxii.mitre.org

# Test via Python
python3 -c "from attackcti import attack_client; client = attack_client(); print('OK')"
```

**2. Configure Proxy:**
```bash
export HTTPS_PROXY=http://proxy.company.com:8080
python3 attack2jira.py ...
```

**3. Use Alternative TAXII Server:**

Edit `lib/jirahandler.py`:
```python
# Line 399, 406, 431 - add mirror parameter
client = attack_client(server="https://your-taxii-mirror.com")
```

**4. Check DNS Resolution:**
```bash
nslookup cti-taxii.mitre.org
# Should resolve to valid IP
```

---

### Error: "SSL: CERTIFICATE_VERIFY_FAILED"

**Cause**: Corporate firewall/proxy with SSL inspection

**Solutions:**

**1. Update CA Certificates:**
```bash
sudo apt install ca-certificates
sudo update-ca-certificates
```

**2. Import Corporate Root CA:**
```bash
# Get corporate root CA certificate (corporate_root.crt)
sudo cp corporate_root.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

**3. Disable SSL Verification (NOT RECOMMENDED for production):**

Edit `lib/jirahandler.py`:
```python
# Already disabled by default (line 6)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# All requests use verify=False
r = requests.post(..., verify=False)
```

---

## Debugging Techniques

### Enable Verbose Logging

Add logging to attack2jira:

```python
import logging

# Add to attack2jira.py at top
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('attack2jira_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add logging statements
logger.debug(f"Creating issue: {issue_dict}")
logger.info(f"Successfully created {id}")
```

---

### Inspect API Requests

Use `requests` library debugging:

```python
# Add to lib/jirahandler.py
import logging
import http.client as http_client

http_client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
```

---

### Test Individual Components

```bash
# Test authentication only
python3 -c "
from lib.jirahandler import JiraHandler
handler = JiraHandler('https://company.atlassian.net', 'user@company.com', 'token')
print('Auth successful')
"

# Test ATT&CK API only
python3 -c "
from attackcti import attack_client
client = attack_client()
tactics = client.get_tactics()
print(f'Fetched {len(tactics)} tactics')
"
```

---

### Common Debugging Commands

```bash
# Check Python environment
which python3
python3 --version
pip3 list | grep -E "attackcti|requests"

# Check network connectivity
ping yourcompany.atlassian.net
curl -I https://yourcompany.atlassian.net
curl -I https://cti-taxii.mitre.org

# Check file permissions
ls -la attack2jira.py
ls -la lib/jirahandler.py

# Check disk space
df -h
```

---

### When All Else Fails

1. **Enable full debug logging** (see above)
2. **Run with minimal changes**: Use default project name/key
3. **Test on fresh Jira instance**: Create free trial to isolate issues
4. **Check GitHub Issues**: https://github.com/mvelazc0/attack2jira/issues
5. **File bug report** with:
   - Full error output
   - attack2jira version (`git rev-parse HEAD`)
   - Python version
   - Operating system
   - Debug logs (sanitize credentials)

---

**Troubleshooting complete! Most issues can be resolved with these solutions. 🔍**
