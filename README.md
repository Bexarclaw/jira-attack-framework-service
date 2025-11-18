# JIRA Attack Framework Service (JAFRS)

**Automate MITRE ATT&CK coverage tracking in Jira Software Cloud**

---

## 🎯 Overview

The MITRE ATT&CK Framework is a powerful tool security teams can leverage to measure their organization's security posture against tactics and techniques used in the wild by real threat actors.

At the time of writing, ATT&CK covers 600+ techniques across 14 tactics. Manually tracking this posture's state over time can become tedious and challenging. Blue/Purple teams require proper tools that allow them to efficiently tackle this challenge and focus on what's important.

**JIRA Attack Framework Service (JAFRS)** automates the process of standing up a Jira environment that can be used to track and measure ATT&CK coverage. **No more spreadsheets!**

---

## ✨ Features

- **One-Command Setup**: Automatically creates Jira project with all ATT&CK techniques
- **Hierarchical Structure**: Sub-techniques created as Jira Sub-tasks for proper organization
- **Maturity Tracking**: Built-in 5-level maturity model (Not Tracked → Optimized)
- **Navigator Export**: Export coverage as ATT&CK Navigator JSON layers for visualization
- **Data Source Mapping**: Links techniques to required data sources
- **Tactic Organization**: Automatically organizes techniques by ATT&CK tactics
- **600+ Techniques**: Covers all Enterprise ATT&CK techniques and sub-techniques

---

## 📚 Documentation

**Complete documentation available in the [`docs/`](docs/) directory:**

- **[Getting Started](docs/GETTING_STARTED.md)** - Quick setup guide for new users
- **[Installation Guide](docs/INSTALLATION_GUIDE.md)** - Detailed installation for all platforms
- **[User Guide](docs/USER_GUIDE.md)** - Complete feature documentation
- **[Configuration Guide](docs/CONFIGURATION_GUIDE.md)** - Configuration reference
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Production deployment strategies
- **[API Reference](docs/API_REFERENCE.md)** - Python API documentation
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Workflows](docs/WORKFLOWS.md)** - Real-world workflow examples
- **[Architecture](docs/ARCHITECTURE.md)** - Technical architecture guide
- **[FAQ](docs/FAQ.md)** - Frequently asked questions

---

## 🚀 Quick Start

### System Requirements

- **Python 3.6+** (3.7+ recommended)
- **Jira Software Cloud** environment with admin access
- **Jira API token** for authentication
- Internet connectivity (HTTPS to Jira Cloud and MITRE ATT&CK API)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/jira-attack-framework-service.git
cd jira-attack-framework-service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip3 install -r requirements.txt
```

### Jira Software Cloud Setup

1. Sign up for [Jira Software Cloud](https://www.atlassian.com/software/jira/free) (free tier available for up to 10 users)
2. Ensure you have **admin access** to create projects and custom fields
3. Generate an API token at [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

---

## 💻 Usage

### Initialize: Create ATT&CK Project

Create the Jira ATTACK project with default settings:

```bash
python3 jira_attack_framework_service.py \
  -url https://yourcompany.atlassian.net \
  -u your-email@company.com \
  -a initialize
```

Create with custom project name and key:

```bash
python3 jira_attack_framework_service.py \
  -url https://yourcompany.atlassian.net \
  -u your-email@company.com \
  -a initialize \
  -p "Security Coverage Tracker" \
  -k SCT
```

**What this does:**
1. Creates Jira Software project
2. Creates 6 custom fields (Tactic, Maturity, URL, Datasources, Id, Sub-Technique of)
3. Configures screen layout
4. Creates 600+ technique issues (Tasks and Sub-tasks)

**Duration**: 5-10 minutes

---

### Export: Generate ATT&CK Navigator Layer

Export current coverage as ATT&CK Navigator JSON:

```bash
python3 jira_attack_framework_service.py \
  -url https://yourcompany.atlassian.net \
  -u your-email@company.com \
  -a export
```

Export with "Not Tracked" techniques hidden:

```bash
python3 jira_attack_framework_service.py \
  -url https://yourcompany.atlassian.net \
  -u your-email@company.com \
  -a export \
  -hide
```

**Output**: `coverage_layer.json` (upload to [ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/))

---

### Help Menu

```bash
python3 jira_attack_framework_service.py -h
```

---

## 📊 Maturity Model

JAFRS uses a 5-level maturity model to track detection/prevention capabilities:

| Level | Meaning | Description |
|-------|---------|-------------|
| **Not Tracked** | No coverage | No detection or prevention capability |
| **Initial** | Ad-hoc detection | Basic alerts exist but not tested; high false positives |
| **Defined** | Documented detection | Detection logic documented and tested; moderate false positives |
| **Resilient** | Validated detection | Regularly tested; low false positives; some prevention |
| **Optimized** | Automated prevention | Automated blocking; minimal false positives; continuous testing |

---

## 🎨 ATT&CK Navigator Integration

After exporting `coverage_layer.json`:

1. Visit [ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/)
2. Click **Open Existing Layer** → **Upload from local**
3. Select `coverage_layer.json`
4. Visualize your coverage with color-coded heatmap

**Color Scheme:**
- Gray: Not Tracked
- Light Green: Initial
- Green: Defined
- Dark Green: Resilient
- Darkest Green: Optimized

---

## 🏗️ Architecture

JAFRS uses a clean, service-oriented architecture:

```
┌─────────────────────────────────────┐
│  jira_attack_framework_service.py   │  ← Main orchestrator
└──────────────┬──────────────────────┘
               │
               ├───────────────┬─────────────────┐
               ▼               ▼                 ▼
         ┌──────────┐   ┌──────────┐    ┌──────────────┐
         │  Jira    │   │ MITRE    │    │   Navigator  │
         │  Handler │   │ ATT&CK   │    │    Export    │
         └──────────┘   └──────────┘    └──────────────┘
               │              │                 │
               ▼              ▼                 ▼
         Jira Cloud     ATT&CK API      coverage_layer.json
```

**Key Components:**
- **JiraAttackFrameworkService**: Main orchestration class
- **JiraHandler**: Jira API client (in `lib/jirahandler.py`)
- **attackcti**: MITRE ATT&CK data client

See [Architecture Documentation](docs/ARCHITECTURE.md) for details.

---

## 🔧 Customization

### Custom Maturity Levels

Edit `lib/jirahandler.py` to use your own maturity model:

```python
# Line 157 - Replace with your maturity levels
payload=[
    {"name":"Level 1 - Initial"},
    {"name":"Level 2 - Managed"},
    {"name":"Level 3 - Defined"},
    {"name":"Level 4 - Optimized"},
    {"name":"Level 5 - Innovating"}
]
```

### Additional Custom Fields

Add custom fields for SIEM rules, test dates, risk scores, etc.

See [API Reference](docs/API_REFERENCE.md) for extension examples.

---

## 🚀 Production Deployment

### VPS Deployment

Deploy on cloud VPS for scheduled exports and team collaboration:

```bash
# On VPS
cd /opt
git clone https://github.com/yourusername/jira-attack-framework-service.git
cd jira-attack-framework-service
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# Schedule weekly exports
crontab -e
# Add: 0 6 * * 1 /opt/jira-attack-framework-service/venv/bin/python3 /opt/jira-attack-framework-service/jira_attack_framework_service.py -url https://company.atlassian.net -u user@company.com -a export
```

See [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) for complete instructions.

### CI/CD Integration

Integrate with GitHub Actions, GitLab CI, or Jenkins for automated coverage tracking.

See [Deployment Guide - CI/CD Integration](docs/DEPLOYMENT_GUIDE.md#cicd-integration).

---

## 🤝 Contributing

Contributions are welcome! Whether it's bug fixes, new features, or documentation improvements.

**How to contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Ideas for contributions:**
- Docker support
- Jira Server/Data Center compatibility
- Mobile/ICS ATT&CK matrix support
- Enhanced error handling
- SIEM/SOAR integrations

---

## 📖 Resources

### Demo & Presentations

- **Live Demo Instance**: [https://attack.atlassian.net](https://attack.atlassian.net/jira/software/c/projects/ATTACK/issues/)
- **ATT&CKCon 2.0 Presentation**: [YouTube](https://www.youtube.com/watch?v=hrzR8TpnjAw&t=1198s)
- **Blog Post**: [Medium](https://medium.com/@mvelazco/tracking-and-measuring-att-ck-coverage-with-attack2jira-fe700e2a1654)

### Related Projects

- **MITRE ATT&CK Framework**: [https://attack.mitre.org](https://attack.mitre.org)
- **ATT&CK Navigator**: [https://mitre-attack.github.io/attack-navigator/](https://mitre-attack.github.io/attack-navigator/)
- **ATTACK-Python-Client**: [https://github.com/Cyb3rWard0g/ATTACK-Python-Client](https://github.com/Cyb3rWard0g/ATTACK-Python-Client)

---

## 📄 License

This project is licensed under the **BSD 3-Clause License** - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors & Acknowledgments

**Original Project (attack2jira):**
- Mauricio Velazco - [@mvelazco](https://twitter.com/mvelazco)
- Olindo Verrillo - [@olindoverrillo](https://twitter.com/olindoverrillo)

**JAFRS Rebrand:**
- Maintained as an independent fork

**Acknowledgments:**
- MITRE Corporation for the ATT&CK Framework
- Atlassian for Jira Software Cloud
- The security community for feedback and contributions

---

## 🆘 Support

- **Documentation**: [`docs/`](docs/) directory
- **Issues**: [GitHub Issues](https://github.com/yourusername/jira-attack-framework-service/issues)
- **FAQ**: [docs/FAQ.md](docs/FAQ.md)
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 🔗 Quick Links

| Task | Link |
|------|------|
| 📖 Read the docs | [docs/README.md](docs/README.md) |
| 🚀 Get started | [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) |
| 💻 Install | [docs/INSTALLATION_GUIDE.md](docs/INSTALLATION_GUIDE.md) |
| 🔧 Configure | [docs/CONFIGURATION_GUIDE.md](docs/CONFIGURATION_GUIDE.md) |
| 🐛 Troubleshoot | [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) |
| ❓ FAQ | [docs/FAQ.md](docs/FAQ.md) |

---

**Ready to automate your ATT&CK coverage tracking? Get started with the [Installation Guide](docs/INSTALLATION_GUIDE.md)!** 🎯
