# attack2jira Frequently Asked Questions

Common questions and answers about attack2jira.

## Table of Contents

- [General Questions](#general-questions)
- [Installation & Setup](#installation--setup)
- [Usage & Operations](#usage--operations)
- [Customization](#customization)
- [Performance & Scalability](#performance--scalability)
- [Integration](#integration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## General Questions

### What is attack2jira?

attack2jira is a Python tool that automates the creation of a Jira Software Cloud project populated with all MITRE ATT&CK techniques and sub-techniques. It enables security teams to track and measure their defensive coverage against real-world adversary tactics and techniques using Jira's project management features.

---

### Why use attack2jira instead of spreadsheets?

**Benefits over spreadsheets:**
- **Collaboration**: Multiple team members can work simultaneously
- **Audit trail**: Full history of changes and assessments
- **Automation**: Scheduled exports, notifications, integrations
- **Visualization**: Jira dashboards and ATT&CK Navigator integration
- **Workflow**: Assignments, comments, transitions, approvals
- **Scalability**: Handles 600+ techniques easily
- **Version control**: Track improvements over time

---

### What does attack2jira cost?

**attack2jira is free and open-source** (BSD 3-Clause License).

**Costs you may incur:**
- **Jira Software Cloud**: Free tier (up to 10 users) or paid plans ($7.75+/user/month)
- **Infrastructure**: If deploying on VPS/cloud (optional)

**Note**: Jira offers a free trial with full features for evaluation.

---

### Is attack2jira officially supported by MITRE?

No, attack2jira is a **community project** created by security practitioners. It uses MITRE's publicly available ATT&CK data via the attackcti library, but is not officially endorsed or supported by MITRE Corporation.

---

## Installation & Setup

### How long does initialization take?

**Typical duration**: 5-10 minutes

**Breakdown:**
- Authentication: 2-5 seconds
- Project creation: 5-10 seconds
- Custom field creation: 10-15 seconds
- Field option population: 15-30 seconds
- Screen configuration: 10-20 seconds
- Technique import: 3-8 minutes (~600 issues)

**Factors affecting duration:**
- Network latency to Jira Cloud
- Jira instance performance
- Rate limiting

---

### How often should I re-run initialization?

**Usually never.** Initialize once to create the project structure.

**Re-initialize only if:**
- You want a separate project (different key/name)
- You corrupted the existing project beyond repair
- You want to reset to default state

**For updates:** MITRE ATT&CK updates can be handled manually by creating new issues for new techniques, or by re-initializing into a new project and comparing.

---

### Can I use attack2jira with Jira Server or Data Center?

**No, not currently.** attack2jira is designed specifically for **Jira Cloud** and uses Cloud-specific API endpoints that don't exist in Jira Server or Data Center.

**Workarounds:**
- Migrate to Jira Cloud
- Contribute code to add Server/Data Center support (community contributions welcome)

---

## Usage & Operations

### How often should I export Navigator layers?

**Recommended frequency:**
- **Weekly**: For active assessment periods
- **Monthly**: For ongoing maintenance
- **Quarterly**: For executive reporting
- **After major updates**: When techniques change maturity levels

**Automation**: Set up scheduled exports via cron or CI/CD (see [Deployment Guide](DEPLOYMENT_GUIDE.md)).

---

### Can I modify the custom fields attack2jira creates?

**Yes, but with caution.**

**Safe modifications:**
- Add new custom fields
- Change field descriptions
- Add field options (maturity levels, tactics)

**Risky modifications:**
- Deleting fields (breaks export functionality)
- Changing field types (breaks issue creation)
- Renaming fields (breaks API references)

**Recommendation**: Add new fields instead of modifying existing ones.

---

### How do I update techniques when ATT&CK releases a new version?

**Option 1: Manual Updates** (Recommended)
1. Review ATT&CK changelog
2. Manually create issues for new techniques
3. Update existing techniques if descriptions changed
4. Deprecate revoked techniques

**Option 2: Re-Initialize** (Nuclear option)
1. Export current maturity levels
2. Create new project with updated ATT&CK version
3. Manually restore maturity levels from export

**Future Enhancement**: Planned feature for incremental updates.

---

### Can I track multiple ATT&CK matrices (Enterprise, Mobile, ICS)?

**Currently**: Only Enterprise ATT&CK is supported out-of-the-box.

**Workaround:**
1. Create separate projects for each matrix
   - Enterprise: `ATTACK-ENT`
   - Mobile: `ATTACK-MOB`
   - ICS: `ATTACK-ICS`
2. Modify code to use different ATT&CK matrices:
   ```python
   # In attack2jira.py, modify get_attack_techniques()
   mobile = client.get_mobile()  # For Mobile ATT&CK
   ics = client.get_ics()        # For ICS ATT&CK
   ```

---

## Customization

### Can I use a different maturity model?

**Yes!** Modify the maturity levels to match your framework.

**Edit `/lib/jirahandler.py` line 157:**
```python
# Original (5-level model)
payload=[
    {"name":"Not Tracked"},
    {"name":"Initial"},
    {"name":"Defined"},
    {"name":"Resilient"},
    {"name":"Optimized"}
]

# Example: CMMI-based
payload=[
    {"name":"Level 1 - Initial"},
    {"name":"Level 2 - Managed"},
    {"name":"Level 3 - Defined"},
    {"name":"Level 4 - Quantitatively Managed"},
    {"name":"Level 5 - Optimizing"}
]
```

**Important**: Also update color mappings in `generate_json_layer()`.

---

### Can I add more custom fields (e.g., SIEM Rule ID)?

**Yes!** Add custom fields via code modification.

**Edit `/lib/jirahandler.py` method `create_custom_fields()`:**
```python
custom_field7_dict = {
    "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
    "name": "SIEM Rule ID",
    "description": "Detection rule identifier",
    "type": "com.atlassian.jira.plugin.system.customfieldtypes:textfield"
}
custom_fields.append(custom_field7_dict)
```

See [API Reference](API_REFERENCE.md) for details.

---

## Performance & Scalability

### How many issues will attack2jira create?

**Approximately 600-700 issues** for Enterprise ATT&CK:
- ~200 parent techniques (Tasks)
- ~400-500 sub-techniques (Sub-tasks)

**Note**: ATT&CK framework grows over time. As of 2024, there are 600+ total techniques.

---

### Will attack2jira slow down my Jira instance?

**No.** 600 issues is a small project for Jira Cloud, which is designed to handle thousands of issues per project.

**Performance impact:**
- Negligible on Jira Cloud performance
- No impact on other projects
- Standard Jira queries and filters work normally

---

### Can I run attack2jira on a schedule (automated)?

**Yes!** See [Deployment Guide - Recurring Syncs](DEPLOYMENT_GUIDE.md#recurring-syncs).

**Methods:**
- **Cron**: Linux/Unix scheduled tasks
- **Systemd Timers**: Modern Linux systems
- **GitHub Actions**: CI/CD automation
- **AWS Lambda**: Serverless execution

**Note**: Requires code modification to accept API token via environment variable instead of interactive prompt.

---

## Integration

### Can I integrate attack2jira with my SIEM?

**Yes!** Several approaches:

**1. Manual Linking**
- Add SIEM rule IDs in issue comments
- Link to rule repositories in issue links

**2. Custom Fields**
- Add "SIEM Rule ID" custom field
- Populate during assessment

**3. API Integration**
- Query Jira for techniques
- Cross-reference with SIEM detection rules
- Auto-update maturity based on rule testing

See [Workflows - Integration](WORKFLOWS.md#workflow-4-integration-with-security-tools).

---

### Can I use attack2jira with threat intelligence platforms?

**Yes!** Integrate with TIPs via:

**1. Labels**
- Tag techniques with threat actor names
- Tag with campaign identifiers
- Prioritize based on threat intel

**2. API Integration**
- Query TIP for relevant techniques
- Auto-update Jira priorities
- Link to threat reports

**3. Comments**
- Add threat intel context to technique issues
- Document observed usage in campaigns

---

## Troubleshooting

### What if initialization fails halfway through?

**Don't panic!** attack2jira is idempotent for most operations.

**Steps:**
1. **Check what was created**:
   - Project exists?
   - Custom fields created?
   - How many issues created?

2. **Resume or cleanup**:
   - If project exists but incomplete: Delete project and retry
   - If custom fields exist: Initialization will skip field creation
   - If some issues created: Delete project to start fresh

3. **Review logs**: Check error messages for specific failure point

See [Troubleshooting Guide](TROUBLESHOOTING.md) for specific errors.

---

### Why are some techniques missing data sources?

**This is expected.** Some ATT&CK techniques don't have data sources defined in the MITRE ATT&CK framework.

**From the code** (`attack2jira.py` line 57):
```python
# some techniques dont have the field populated
if 'x_mitre_data_sources' in technique.keys():
    datasources = technique['x_mitre_data_sources']
else:
    datasources = []
```

**Impact**: "Datasources" field will be empty for these techniques.

---

### Can I run attack2jira offline?

**Partially.** Offline mode requirements:

**Not possible:**
- Initial ATT&CK data fetch (requires internet)
- Jira API calls (Jira Cloud is online-only)

**Possible:**
- Export JSON from cached data (if previously fetched)
- Code modifications to use local ATT&CK JSON files

**Recommendation**: Run in connected environment.

---

## Contributing

### Can I contribute improvements to attack2jira?

**Yes! Contributions are welcome.**

**Repository**: [https://github.com/mvelazc0/attack2jira](https://github.com/mvelazc0/attack2jira)

**How to contribute:**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

**Ideas for contributions:**
- Docker support
- Jira Server/Data Center compatibility
- Incremental ATT&CK updates
- Mobile/ICS matrix support
- Enhanced error handling and retry logic
- Additional integrations (SIEM, TIP, SOAR)

---

### Who maintains attack2jira?

**Original Authors:**
- Mauricio Velazco - [@mvelazco](https://twitter.com/mvelazco)
- Olindo Verrillo - [@olindoverrillo](https://twitter.com/olindoverrillo)

**License**: BSD 3-Clause

**Community**: Maintained as an open-source project with community contributions.

---

### Where can I get help?

**Resources:**
1. **Documentation**: This docs folder
2. **GitHub Issues**: [https://github.com/mvelazc0/attack2jira/issues](https://github.com/mvelazc0/attack2jira/issues)
3. **Community Forums**: Security community forums and Slack channels
4. **Twitter**: Contact authors via Twitter

---

### How do I uninstall attack2jira?

**Uninstall steps:**

**1. Remove Python environment:**
```bash
cd /opt/attack2jira
deactivate  # If virtual environment active
cd ..
rm -rf attack2jira
```

**2. Remove Jira project (optional):**
- Log into Jira
- Project Settings → Details → Move to trash

**3. Remove custom fields (optional, affects all projects):**
- Jira Settings → Issues → Custom Fields
- Delete: Tactic, Maturity, URL, Datasources, Id, Sub-Technique of

**Warning**: Deleting custom fields is permanent and affects ALL projects using them.

---

**Still have questions? Check [Troubleshooting Guide](TROUBLESHOOTING.md) or file an issue on GitHub. ❓**
