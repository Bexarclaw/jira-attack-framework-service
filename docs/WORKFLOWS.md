# attack2jira Workflows

Real-world workflow examples for operationalizing MITRE ATT&CK coverage tracking with attack2jira.

## Table of Contents

- [Overview](#overview)
- [Workflow 1: Basic Setup](#workflow-1-basic-setup)
- [Workflow 2: Hierarchical Assessment](#workflow-2-hierarchical-assessment)
- [Workflow 3: Recurring Syncs](#workflow-3-recurring-syncs)
- [Workflow 4: Integration with Security Tools](#workflow-4-integration-with-security-tools)
- [Workflow 5: Coverage Reporting](#workflow-5-coverage-reporting)
- [Workflow 6: Team Collaboration](#workflow-6-team-collaboration)
- [Best Practices](#best-practices)

---

## Overview

attack2jira enables various workflows depending on your organization's maturity and requirements. This guide provides step-by-step workflows for common use cases.

---

## Workflow 1: Basic Setup

**Use Case**: First-time setup for tracking ATT&CK coverage

**Duration**: 1-2 hours

**Prerequisites**:
- Jira Software Cloud account (admin access)
- Jira API token
- Python 3.6+ environment

---

### Step 1: Install attack2jira (15 minutes)

```bash
# Clone repository
cd /opt
git clone https://github.com/mvelazc0/attack2jira.git
cd attack2jira

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt
```

---

### Step 2: Initialize Jira Project (10 minutes)

```bash
# Run initialization
python3 attack2jira.py \
  -url https://yourcompany.atlassian.net \
  -u security@yourcompany.com \
  -a initialize \
  -p "ATT&CK Coverage Tracker" \
  -k ATTACK

# Wait 5-10 minutes for completion
```

**Expected Output:**
- Project "ATT&CK Coverage Tracker" created
- 6 custom fields created (Tactic, Maturity, URL, Datasources, Id, Sub-Technique of)
- ~600 technique issues created (Tasks and Sub-tasks)

---

### Step 3: Configure Jira Board (10 minutes)

1. Navigate to your Jira project
2. Create custom board:
   - **Board name**: "ATT&CK Coverage"
   - **Board type**: Kanban
   - **Columns**: Not Tracked → Initial → Defined → Resilient → Optimized

3. Configure board filter:
```sql
project = ATTACK ORDER BY Id ASC
```

4. Set swimlanes by **Tactic**:
   - **Project Settings** → **Board** → **Swimlanes**
   - **Group by**: Tactic custom field

---

### Step 4: Assign Techniques (30 minutes)

Distribute techniques across your team:

**Option A: By Tactic**
```
Assign all "initial-access" techniques to Alice
Assign all "execution" techniques to Bob
Assign all "persistence" techniques to Charlie
```

**Option B: By Data Source**
```
Assign all techniques requiring "Process Monitoring" to SOC Team
Assign all techniques requiring "Network Traffic" to Network Team
```

**Bulk Assignment:**
1. Filter: `project = ATTACK AND Tactic = "execution"`
2. Select all (Ctrl+A)
3. **Bulk Change** → **Edit Issues** → **Assignee** → Bob

---

### Step 5: Conduct Initial Assessment (Ongoing)

Each assigned team member:

1. Open assigned technique
2. Read ATT&CK description (click **URL** field)
3. Assess current detection capability
4. Update **Maturity** field
5. Document findings in comments

---

### Step 6: Export Initial Coverage (5 minutes)

```bash
python3 attack2jira.py \
  -url https://yourcompany.atlassian.net \
  -u security@yourcompany.com \
  -a export

# Upload attack2jira.json to ATT&CK Navigator
# Save screenshot for baseline reporting
```

---

## Workflow 2: Hierarchical Assessment

**Use Case**: Assess parent techniques before sub-techniques

**Duration**: Iterative (weeks/months)

---

### Sprint 1: Assess Parent Techniques

**Goal**: Determine coverage for all parent techniques (~200 techniques)

**JQL Filter:**
```sql
project = ATTACK AND issuetype = Task AND Maturity = "Not Tracked" ORDER BY Tactic
```

**Process:**
1. Assign 10-20 parent techniques per analyst
2. Analysts assess coverage and update Maturity
3. Document detection mechanisms in comments
4. Sprint review: Export Navigator layer, measure progress

**Metrics:**
- Techniques assessed: 200
- Average maturity level: Calculate
- High-priority gaps identified: List

---

### Sprint 2: Deep-Dive Sub-Techniques

**Goal**: Assess sub-techniques for techniques marked "Initial" or higher

**JQL Filter:**
```sql
project = ATTACK AND issuetype = Sub-task AND "Sub-Technique of" IN linkedIssues("Maturity IN ('Initial', 'Defined', 'Resilient', 'Optimized')")
```

**Process:**
1. Identify parent techniques with existing coverage
2. Assess how well sub-technique variants are detected
3. Identify detection gaps in sub-technique coverage
4. Update Maturity levels for sub-techniques

**Example:**
```
T1055 - Process Injection: Defined (we detect most variants)
  T1055.001 - DLL Injection: Defined (detected via Sysmon Event ID 7)
  T1055.002 - PE Injection: Initial (basic detection, high false positives)
  T1055.012 - Process Hollowing: Not Tracked (no detection)

Action: Prioritize T1055.012 for detection engineering
```

---

### Sprint 3: Untracked Techniques

**Goal**: Baseline all remaining "Not Tracked" techniques

**JQL Filter:**
```sql
project = ATTACK AND Maturity = "Not Tracked" ORDER BY Tactic
```

**Process:**
1. Identify why techniques are untracked (no data source, low priority, etc.)
2. Tag with custom labels: `no-datasource`, `low-risk`, `planned-q3`
3. Prioritize based on threat intelligence
4. Create remediation tasks for high-priority gaps

---

## Workflow 3: Recurring Syncs

**Use Case**: Automated weekly coverage exports for reporting

**Duration**: 5 minutes setup, then automated

---

### Setup: VPS Deployment

Follow [Deployment Guide - VPS Deployment](DEPLOYMENT_GUIDE.md#vps-deployment)

---

### Schedule Weekly Exports

**Crontab Configuration:**
```bash
crontab -e

# Export coverage every Monday at 6 AM UTC
0 6 * * 1 /home/attack2jira/attack2jira_wrapper.sh -a export > /home/attack2jira/logs/export_$(date +\%Y\%m\%d).log 2>&1

# Archive export with date
5 6 * * 1 cp /home/attack2jira/attack2jira/attack2jira.json /home/attack2jira/exports/coverage_$(date +\%Y\%m\%d).json
```

---

### Automated Reporting

**Create Reporting Script:**
```bash
cat > ~/generate_coverage_report.sh <<'EOF'
#!/bin/bash
set -e

# Export coverage
cd ~/attack2jira
source venv/bin/activate
python3 attack2jira.py -url $JIRA_URL -u $JIRA_USER -a export

# Parse JSON and generate summary
TOTAL=$(jq '.techniques | length' attack2jira.json)
TRACKED=$(jq '[.techniques[] | select(.enabled == true)] | length' attack2jira.json)
COVERAGE_PCT=$((TRACKED * 100 / TOTAL))

# Email report
echo "ATT&CK Coverage Report - $(date +%Y-%m-%d)

Total Techniques: $TOTAL
Tracked Techniques: $TRACKED
Coverage: $COVERAGE_PCT%

Navigator layer attached.
" | mail -s "Weekly ATT&CK Coverage Report" -A attack2jira.json security-team@company.com

EOF

chmod +x ~/generate_coverage_report.sh
```

**Schedule:**
```cron
0 7 * * 1 /home/attack2jira/generate_coverage_report.sh
```

---

## Workflow 4: Integration with Security Tools

**Use Case**: Link ATT&CK techniques to SIEM detection rules

---

### Step 1: Tag Techniques with SIEM Rules

**Add custom field for SIEM Rule ID** (requires code modification or use existing field)

**Manual Approach:**
1. Open technique in Jira (e.g., T1055 - Process Injection)
2. Add comment:
```
Detection Rules:
- Splunk: correlation_t1055_process_injection
- Elastic: siem.rules.process_injection
- Sigma: proc_creation_win_susp_proc_injection.yml
```

3. Add link to rule repository:
   - Click **Link** → **Web Link**
   - URL: `https://github.com/company/siem-rules/blob/main/t1055_process_injection.yml`
   - Title: "SIEM Detection Rule"

---

### Step 2: Correlate Coverage with Rule Testing

**JQL for Untested Rules:**
```sql
project = ATTACK AND Maturity = "Initial" AND labels = "has-siem-rule"
```

**Process:**
1. Identify techniques with rules but low maturity
2. Schedule rule testing (Atomic Red Team, Red Team exercise)
3. Document test results in comments
4. Update maturity based on test outcomes

---

### Step 3: Track Rule Lifecycle

**Create Jira Automation:**
1. **Trigger**: Maturity changed to "Optimized"
2. **Action**: Create linked issue in "Detection Engineering" project
3. **Summary**: "Maintain detection for [Technique Name]"
4. **Description**: "This technique has reached optimized maturity. Schedule annual validation."

---

## Workflow 5: Coverage Reporting

**Use Case**: Executive reporting and metrics tracking

---

### Monthly Executive Summary

**Metrics to Track:**

1. **Overall Coverage Percentage**
```python
total_techniques = len(maturity_map)
tracked = sum(1 for m in maturity_map.values() if m['value'] != "Not Tracked")
coverage_pct = (tracked / total_techniques) * 100
```

2. **Maturity Distribution**
```sql
-- Jira JQL queries for each maturity level
project = ATTACK AND Maturity = "Optimized"  # High confidence
project = ATTACK AND Maturity = "Resilient"   # Good coverage
project = ATTACK AND Maturity = "Defined"     # Basic coverage
project = ATTACK AND Maturity = "Initial"     # Needs improvement
project = ATTACK AND Maturity = "Not Tracked" # Gaps
```

3. **Coverage by Tactic**
```sql
project = ATTACK AND Tactic = "initial-access" AND Maturity != "Not Tracked"
-- Repeat for each tactic
```

4. **Improvement Over Time**
- Compare current export to previous month
- Calculate delta in "Tracked" techniques
- Identify techniques that improved maturity level

---

### Dashboard Creation

**Jira Dashboard Widgets:**

1. **Pie Chart: Maturity Distribution**
   - Filter: `project = ATTACK`
   - Stat: Count of issues by Maturity

2. **Bar Chart: Coverage by Tactic**
   - Filter: `project = ATTACK AND Maturity != "Not Tracked"`
   - Stat: Count by Tactic

3. **Two-Dimensional Filter: Assignee vs Maturity**
   - Shows team member contributions

4. **Created vs Resolved Chart**
   - Track assessment velocity

---

### Trend Analysis

**Version Control Navigator Exports:**
```bash
# Store in Git repository
mkdir -p coverage-history
cp attack2jira.json coverage-history/coverage_$(date +%Y%m%d).json

git add coverage-history/
git commit -m "Coverage snapshot - $(date +%Y-%m-%d)"
git push
```

**Compare Snapshots:**
```python
import json

# Load two snapshots
with open('coverage_20240101.json') as f:
    old_coverage = json.load(f)
with open('coverage_20240201.json') as f:
    new_coverage = json.load(f)

# Find improvements
old_techniques = {t['techniqueID']: t for t in old_coverage['techniques']}
new_techniques = {t['techniqueID']: t for t in new_coverage['techniques']}

improvements = []
for tech_id in new_techniques:
    if old_techniques[tech_id]['color'] != new_techniques[tech_id]['color']:
        # Color changed = maturity improved
        improvements.append(tech_id)

print(f"Improved techniques this month: {len(improvements)}")
print(improvements)
```

---

## Workflow 6: Team Collaboration

**Use Case**: Collaborative assessment across multiple teams

---

### Setup: Team Structure

**Teams:**
- **SOC Team**: Assess detection capabilities
- **Threat Intel Team**: Prioritize techniques by threat relevance
- **Purple Team**: Validate detections via testing
- **Incident Response**: Document techniques observed in incidents

---

### Collaboration Process

**1. Threat Intel Prioritization (Weekly)**

Threat intel team adds labels to techniques:
```
project = ATTACK AND Id = "T1078"
Add label: "apt29-ttp"
Add label: "priority-high"
Add comment: "APT29 uses this in recent campaigns per CISA alert AA24-..."
```

**2. SOC Assessment (Sprint-based)**

SOC team focuses on prioritized techniques:
```sql
project = ATTACK AND labels IN ("priority-high", "apt29-ttp") AND Maturity = "Not Tracked"
```

Process:
1. Assign techniques from filter
2. Assess current detection
3. Update maturity
4. Document detection logic

**3. Purple Team Validation (Monthly)**

Purple team tests techniques marked "Defined" or higher:
```sql
project = ATTACK AND Maturity IN ("Defined", "Resilient", "Optimized") AND labels = "pending-validation"
```

Process:
1. Execute technique via Atomic Red Team
2. Verify detection fires
3. Measure time-to-detect
4. Document results in comments
5. Update maturity if needed

**4. Incident Response Feedback (Ongoing)**

After incidents, IR team tags observed techniques:
```
Add label: "observed-incident-2024-03"
Add comment: "Observed in ransomware incident #2024-03. Our detection delayed (45 min). Upgrade to purple team for testing."
```

---

## Best Practices

### 1. Start Simple

- Begin with parent techniques only
- Expand to sub-techniques once process is established
- Don't aim for 100% coverage immediately

---

### 2. Prioritize by Threat Intelligence

Use threat intelligence to focus efforts:
```sql
-- High-priority techniques
project = ATTACK AND labels IN ("ransomware-ttp", "apt-observed", "cisa-alert")
```

---

### 3. Integrate with Change Management

When deploying new security controls:
1. Create Jira ticket in Change Management project
2. Link to relevant ATT&CK techniques
3. Update technique maturity after deployment
4. Export new coverage layer

---

### 4. Schedule Regular Reviews

**Quarterly ATT&CK Review Meetings:**
- Review maturity distribution
- Identify gaps in coverage
- Prioritize next quarter's assessments
- Celebrate improvements

---

### 5. Document Everything

Use Jira comments to document:
- Why a technique has a specific maturity level
- Detection logic and SIEM rules
- Testing results
- Known limitations
- Remediation plans

---

### 6. Leverage Jira Features

**Use Jira's built-in features:**
- **Watchers**: Subscribe to technique updates
- **Due dates**: Track assessment deadlines
- **Sprints**: Sprint-based assessment cycles
- **Dashboards**: Real-time metrics
- **Automation**: Auto-assign, notifications

---

**Workflows complete! Operationalize ATT&CK coverage tracking effectively. 📊**
