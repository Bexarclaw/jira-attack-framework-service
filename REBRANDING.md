# JAFRS Rebranding Guide

**From attack2jira to JIRA Attack Framework Service (JAFRS)**

---

## 🔄 Overview

This document explains the rebranding from **attack2jira** to **JIRA Attack Framework Service (JAFRS)** and how to use your newly rebranded fork.

---

## ✅ What Changed

### 1. **Project Name**
- **Old**: attack2jira
- **New**: JIRA Attack Framework Service (JAFRS)
- **Acronym**: JAFRS (pronounced "jeffers")

### 2. **Main Python File**
- **Old**: `attack2jira.py`
- **New**: `jira_attack_framework_service.py`

### 3. **Main Class**
- **Old**: `Attack2Jira`
- **New**: `JiraAttackFrameworkService`

### 4. **Export Filename**
- **Old**: `attack2jira.json`
- **New**: `coverage_layer.json`

### 5. **Navigator Layer Name**
- **Old**: "Attack2Jira"
- **New**: "JIRA Attack Framework Service"

---

## 📝 What Stayed the Same

### Unchanged Components

✅ **Backend library**: `lib/jirahandler.py` (no changes needed)
✅ **Dependencies**: Same requirements.txt
✅ **Jira integration**: All Jira API calls work identically
✅ **ATT&CK integration**: Uses same attackcti library
✅ **Custom fields**: Same 6 custom fields created
✅ **Maturity model**: Same 5-level maturity tracking
✅ **Functionality**: 100% compatible with original

---

## 🚀 Quick Start with JAFRS

### Using the New Command

**Old command:**
```bash
python3 attack2jira.py -url https://company.atlassian.net -u user@company.com -a initialize
```

**New command:**
```bash
python3 jira_attack_framework_service.py -url https://company.atlassian.net -u user@company.com -a initialize
```

### Export Changes

**Old export:**
- Command: `python3 attack2jira.py ... -a export`
- Output: `attack2jira.json`

**New export:**
- Command: `python3 jira_attack_framework_service.py ... -a export`
- Output: `coverage_layer.json`

---

## 🔧 Migration from Original attack2jira

If you were using the original attack2jira, here's how to migrate:

### Step 1: Keep Original File (Backward Compatibility)

The original `attack2jira.py` file is still present for backward compatibility. Your existing scripts will continue to work.

### Step 2: Update Your Scripts (Recommended)

Update any automation scripts to use the new filename:

**Before:**
```bash
#!/bin/bash
python3 /opt/attack2jira/attack2jira.py -url $URL -u $USER -a export
```

**After:**
```bash
#!/bin/bash
python3 /opt/jira-attack-framework-service/jira_attack_framework_service.py -url $URL -u $USER -a export
```

### Step 3: Update Export File References

If you have scripts that process `attack2jira.json`:

**Before:**
```bash
cp attack2jira.json /path/to/archive/coverage_$(date +%Y%m%d).json
```

**After:**
```bash
cp coverage_layer.json /path/to/archive/coverage_$(date +%Y%m%d).json
```

---

## 📂 File Structure Comparison

### Old Structure (attack2jira)
```
attack2jira/
├── attack2jira.py          ← Main file
├── lib/
│   └── jirahandler.py
├── requirements.txt
└── README.md
```

### New Structure (JAFRS)
```
jira-attack-framework-service/
├── jira_attack_framework_service.py  ← New main file
├── attack2jira.py                     ← Legacy (for compatibility)
├── lib/
│   └── jirahandler.py                ← Unchanged
├── requirements.txt                   ← Unchanged
├── README.md                          ← Rebranded
├── REBRANDING.md                      ← This file
├── setup.py                           ← New (Python package)
└── docs/                              ← Full documentation suite
    ├── README.md
    ├── GETTING_STARTED.md
    ├── USER_GUIDE.md
    ├── INSTALLATION_GUIDE.md
    ├── CONFIGURATION_GUIDE.md
    ├── DEPLOYMENT_GUIDE.md
    ├── API_REFERENCE.md
    ├── TROUBLESHOOTING.md
    ├── WORKFLOWS.md
    ├── ARCHITECTURE.md
    └── FAQ.md
```

---

## 🐍 Python API Changes

If you're using attack2jira programmatically:

### Old Code
```python
from attack2jira import Attack2Jira

a2j = Attack2Jira(url, username, password)
a2j.set_up_jira_automated("Project", "KEY")
a2j.generate_json_layer(False)
```

### New Code
```python
from jira_attack_framework_service import JiraAttackFrameworkService

jafrs = JiraAttackFrameworkService(url, username, password)
jafrs.set_up_jira_automated("Project", "KEY")
jafrs.generate_json_layer(False)
```

---

## 📚 Documentation

JAFRS includes comprehensive documentation in the `docs/` directory:

| Document | Purpose |
|----------|---------|
| **README.md** | Documentation overview and navigation |
| **GETTING_STARTED.md** | Quick setup guide for new users |
| **USER_GUIDE.md** | Complete feature documentation |
| **INSTALLATION_GUIDE.md** | Platform-specific installation |
| **CONFIGURATION_GUIDE.md** | Configuration reference |
| **DEPLOYMENT_GUIDE.md** | Production deployment strategies |
| **API_REFERENCE.md** | Python API documentation |
| **TROUBLESHOOTING.md** | Common issues and solutions |
| **WORKFLOWS.md** | Real-world workflow examples |
| **ARCHITECTURE.md** | Technical architecture guide |
| **FAQ.md** | Frequently asked questions |

**Total**: 13,600+ words of professional documentation

---

## 🔗 Repository Updates

### GitHub Repository Name

If you forked from `attack2jira`, your repository may still use the old name. To rename:

1. Go to your GitHub repository
2. Click **Settings**
3. Scroll to **Repository name**
4. Change to: `jira-attack-framework-service`
5. Click **Rename**

### Update Remote URL

After renaming your GitHub repository:

```bash
# Check current remote
git remote -v

# Update remote URL
git remote set-url origin https://github.com/yourusername/jira-attack-framework-service.git

# Verify
git remote -v
```

---

## 🎯 Branding Guidelines

When referring to this tool:

### Correct Usage
- ✅ "JIRA Attack Framework Service"
- ✅ "JAFRS"
- ✅ "jira-attack-framework-service" (repository name)
- ✅ "jira_attack_framework_service.py" (filename)

### Avoid
- ❌ "attack2jira" (except when referring to the original project)
- ❌ "JAFS" (missing 'R')
- ❌ "Jira-Attack" (incomplete)

---

## 🤔 Why Rebrand?

### Advantages of Independent Fork

1. **Clear Identity**: JAFRS is your own project
2. **Customization Freedom**: Make changes without upstream conflicts
3. **Professional Naming**: More descriptive and enterprise-friendly
4. **Documentation**: Complete documentation suite included
5. **Extensibility**: Clear path for adding features

### Maintaining Attribution

JAFRS maintains proper attribution to original authors:
- README includes "Original Project" section
- Code comments reference original work
- License preserved (BSD 3-Clause)

---

## 📋 Checklist for Complete Migration

Use this checklist to ensure complete migration:

### Repository Setup
- [ ] Fork renamed to `jira-attack-framework-service`
- [ ] Remote URL updated
- [ ] README.md reviewed and customized

### Code Updates
- [ ] Scripts updated to use `jira_attack_framework_service.py`
- [ ] Export file handling changed to `coverage_layer.json`
- [ ] Python imports updated (if using programmatically)

### Documentation
- [ ] Reviewed `docs/README.md` for navigation
- [ ] Read `docs/GETTING_STARTED.md` for quick setup
- [ ] Checked `docs/FAQ.md` for common questions

### Deployment
- [ ] VPS/server paths updated (if applicable)
- [ ] Cron jobs updated with new file paths
- [ ] CI/CD pipelines updated
- [ ] Team notified of new command

### Testing
- [ ] Tested initialize command with new file
- [ ] Tested export command and verified output file
- [ ] Confirmed Navigator layer imports correctly
- [ ] Verified all documentation links work

---

## 🆘 Support

### Questions About Rebranding?

- **Documentation**: Check [docs/README.md](docs/README.md)
- **FAQ**: See [docs/FAQ.md](docs/FAQ.md)
- **Issues**: File an issue on your GitHub repository

### Original attack2jira Support

For questions about the original attack2jira:
- **GitHub**: [https://github.com/mvelazc0/attack2jira](https://github.com/mvelazc0/attack2jira)
- **Issues**: [attack2jira Issues](https://github.com/mvelazc0/attack2jira/issues)

---

## 🎉 Welcome to JAFRS!

You now have a fully rebranded, professionally documented fork of attack2jira.

**Next steps:**
1. Read [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) to get started
2. Run your first initialization with the new command
3. Explore the comprehensive documentation
4. Customize for your organization's needs

**Happy ATT&CK tracking with JAFRS! 🚀**
