# attack2jira Documentation

Complete documentation for attack2jira v2.0.0 - Automate MITRE ATT&CK coverage tracking in Jira Software Cloud.

---

## 📚 Documentation Suite

### Quick Start
- **[Getting Started](GETTING_STARTED.md)** - New to attack2jira? Start here! Quick setup guide with first-time setup instructions.

### Installation & Configuration
- **[Installation Guide](INSTALLATION_GUIDE.md)** - Detailed installation instructions for all platforms (Linux, Windows, macOS, Docker, VPS).
- **[Configuration Guide](CONFIGURATION_GUIDE.md)** - Complete configuration reference including Jira setup, API tokens, and environment variables.
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Production deployment strategies including VPS, Docker, CI/CD integration, and automation.

### Usage & Operations
- **[User Guide](USER_GUIDE.md)** - Comprehensive guide to all features, commands, and customization options.
- **[Workflows](WORKFLOWS.md)** - Real-world workflow examples from basic setup to advanced team collaboration.

### Technical Documentation
- **[API Reference](API_REFERENCE.md)** - Python API documentation for developers and integrators.
- **[Architecture](ARCHITECTURE.md)** - Technical architecture, data flow, and design decisions.

### Support & Resources
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions with debugging techniques.
- **[FAQ](FAQ.md)** - Frequently asked questions and answers.

---

## 🚀 Quick Links

| I want to... | Go to... |
|-------------|----------|
| Install attack2jira for the first time | [Installation Guide](INSTALLATION_GUIDE.md) |
| Understand what attack2jira does | [Getting Started - What is attack2jira?](GETTING_STARTED.md#what-is-attack2jira) |
| Set up my first ATT&CK project | [Getting Started - Running Your First Sync](GETTING_STARTED.md#running-your-first-sync) |
| Learn all available commands | [User Guide - Command Reference](USER_GUIDE.md#command-reference) |
| Export coverage to ATT&CK Navigator | [User Guide - Exporting Navigator JSON](USER_GUIDE.md#exporting-navigator-json) |
| Deploy on a VPS or cloud server | [Deployment Guide - VPS Deployment](DEPLOYMENT_GUIDE.md#vps-deployment) |
| Set up automated weekly exports | [Workflows - Recurring Syncs](WORKFLOWS.md#workflow-3-recurring-syncs) |
| Integrate with my SIEM | [Workflows - Integration](WORKFLOWS.md#workflow-4-integration-with-security-tools) |
| Customize maturity levels | [FAQ - Can I use a different maturity model?](FAQ.md#can-i-use-a-different-maturity-model) |
| Fix "401 Unauthorized" error | [Troubleshooting - Authentication Errors](TROUBLESHOOTING.md#authentication-errors) |
| Understand the architecture | [Architecture](ARCHITECTURE.md) |
| Extend attack2jira with Python | [API Reference](API_REFERENCE.md) |

---

## 📖 Documentation by Role

### For Security Analysts
- Start: [Getting Started](GETTING_STARTED.md)
- Learn: [User Guide](USER_GUIDE.md)
- Apply: [Workflows - Basic Setup](WORKFLOWS.md#workflow-1-basic-setup)
- Master: [Workflows - Team Collaboration](WORKFLOWS.md#workflow-6-team-collaboration)

### For Administrators
- Install: [Installation Guide](INSTALLATION_GUIDE.md)
- Configure: [Configuration Guide](CONFIGURATION_GUIDE.md)
- Deploy: [Deployment Guide](DEPLOYMENT_GUIDE.md)
- Monitor: [Troubleshooting](TROUBLESHOOTING.md)

### For Developers
- Integrate: [API Reference](API_REFERENCE.md)
- Understand: [Architecture](ARCHITECTURE.md)
- Extend: [API Reference - Custom Extensions](API_REFERENCE.md#custom-extensions)
- Debug: [Troubleshooting - Debugging Techniques](TROUBLESHOOTING.md#debugging-techniques)

### For Managers
- Overview: [Getting Started - Why Use attack2jira?](GETTING_STARTED.md#why-use-attack2jira)
- Workflows: [Workflows - Coverage Reporting](WORKFLOWS.md#workflow-5-coverage-reporting)
- ROI: [FAQ - Why use attack2jira instead of spreadsheets?](FAQ.md#why-use-attack2jira-instead-of-spreadsheets)

---

## 🎯 Common Use Cases

### Use Case 1: First-Time Setup
```
1. Read: Getting Started
2. Follow: Installation Guide
3. Execute: User Guide - Initialize Command
4. Verify: Getting Started - Verifying Success
```

### Use Case 2: Regular Coverage Tracking
```
1. Setup: Workflows - Hierarchical Assessment
2. Assess: User Guide - Maturity Tracking
3. Export: User Guide - Exporting Navigator JSON
4. Report: Workflows - Coverage Reporting
```

### Use Case 3: Production Deployment
```
1. Plan: Deployment Guide - Overview
2. Deploy: Deployment Guide - VPS Deployment
3. Automate: Deployment Guide - CI/CD Integration
4. Monitor: Deployment Guide - Monitoring & Logging
```

### Use Case 4: Team Collaboration
```
1. Organize: Workflows - Team Collaboration
2. Assign: User Guide - Maturity Tracking
3. Integrate: Workflows - Integration with Security Tools
4. Review: Workflows - Coverage Reporting
```

---

## 📋 Documentation Structure

### Beginner Path (Day 1)
```
Getting Started → Installation Guide → User Guide (Basics)
```
**Time**: 2-3 hours
**Outcome**: Working attack2jira setup with basic knowledge

---

### Intermediate Path (Week 1)
```
Configuration Guide → Workflows → User Guide (Advanced)
```
**Time**: 4-6 hours
**Outcome**: Customized setup with team workflows

---

### Advanced Path (Month 1)
```
Deployment Guide → API Reference → Architecture
```
**Time**: 8-12 hours
**Outcome**: Production deployment with custom integrations

---

## 🔧 Technical Specifications

### System Requirements
- **Python**: 3.6+ (3.7+ recommended)
- **Jira**: Software Cloud (Admin access required)
- **Network**: HTTPS to Jira Cloud and MITRE ATT&CK API
- **Dependencies**: attackcti, requests, urllib3

### Supported Platforms
- ✅ Linux (Ubuntu, Debian, Kali, CentOS)
- ✅ Windows 10/11
- ✅ macOS 10.14+
- ✅ Docker (community contribution welcome)

### API Coverage
- **Jira Cloud REST API**: v2 and v3 endpoints
- **MITRE ATT&CK**: Enterprise matrix (v14+)
- **Export Format**: ATT&CK Navigator JSON Layer v2.2

---

## 📈 Documentation Metrics

| Document | Length | Target Audience | Read Time |
|----------|--------|----------------|-----------|
| Getting Started | 1,200+ words | Beginners | 10 min |
| User Guide | 2,000+ words | All users | 20 min |
| Installation Guide | 1,500+ words | Admins | 15 min |
| Configuration Guide | 1,200+ words | Admins | 12 min |
| Deployment Guide | 1,500+ words | DevOps | 15 min |
| API Reference | 1,200+ words | Developers | 12 min |
| Troubleshooting | 1,000+ words | Support | 10 min |
| Workflows | 1,200+ words | Analysts | 12 min |
| Architecture | 1,000+ words | Engineers | 10 min |
| FAQ | 800+ words | Everyone | 8 min |

**Total**: 13,600+ words | ~2 hours comprehensive read

---

## 🤝 Contributing to Documentation

Found a typo? Have a suggestion? Want to add examples?

1. Fork the repository
2. Edit documentation in `docs/` directory
3. Submit a pull request

**Documentation Guidelines:**
- Use clear, concise language
- Provide code examples for technical concepts
- Include troubleshooting tips
- Test all commands before documenting
- Follow existing markdown formatting

---

## 📝 Changelog

### v2.0.0 Documentation (2024)
- Complete documentation suite created
- 10 comprehensive guides
- 13,600+ words of content
- Real-world workflow examples
- API reference documentation
- Architecture documentation

### v1.0.0 (Original)
- Basic README.md
- Installation instructions
- Usage examples

---

## 🔗 External Resources

### MITRE ATT&CK
- **ATT&CK Website**: [https://attack.mitre.org](https://attack.mitre.org)
- **ATT&CK Navigator**: [https://mitre-attack.github.io/attack-navigator/](https://mitre-attack.github.io/attack-navigator/)
- **ATT&CK Python Client**: [https://github.com/Cyb3rWard0g/ATTACK-Python-Client](https://github.com/Cyb3rWard0g/ATTACK-Python-Client)

### Jira
- **Jira Cloud Documentation**: [https://support.atlassian.com/jira-software-cloud/](https://support.atlassian.com/jira-software-cloud/)
- **Jira REST API**: [https://developer.atlassian.com/cloud/jira/platform/rest/v3/](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- **API Token Management**: [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

### attack2jira
- **GitHub Repository**: [https://github.com/mvelazc0/attack2jira](https://github.com/mvelazc0/attack2jira)
- **Demo Instance**: [https://attack.atlassian.net](https://attack.atlassian.net/jira/software/c/projects/ATTACK/issues/)
- **ATT&CKCon Presentation**: [YouTube](https://www.youtube.com/watch?v=hrzR8TpnjAw&t=1198s)
- **Blog Post**: [Medium](https://medium.com/@mvelazco/tracking-and-measuring-att-ck-coverage-with-attack2jira-fe700e2a1654)

---

## 💡 Tips for Using This Documentation

### First Time?
Start with **[Getting Started](GETTING_STARTED.md)** - it will guide you through your first setup.

### Looking for Something Specific?
Use the **Quick Links** table above or your browser's search function (Ctrl+F / Cmd+F).

### Want to Learn Everything?
Follow the **Beginner → Intermediate → Advanced Path** outlined above.

### Need Help?
Check **[Troubleshooting](TROUBLESHOOTING.md)** first, then **[FAQ](FAQ.md)**. Still stuck? File an issue on GitHub.

### Want to Go Deeper?
Read **[Architecture](ARCHITECTURE.md)** to understand how attack2jira works internally.

---

## 📧 Support & Community

### Get Help
- **Documentation**: You're reading it!
- **GitHub Issues**: [Report bugs or request features](https://github.com/mvelazc0/attack2jira/issues)
- **Community**: Security forums and Slack channels

### Stay Updated
- **GitHub**: Watch the repository for updates
- **Twitter**: Follow [@mvelazco](https://twitter.com/mvelazco) and [@olindoverrillo](https://twitter.com/olindoverrillo)

---

## 📄 License

attack2jira is licensed under the **BSD 3-Clause License**.

See [LICENSE](../LICENSE) file for details.

---

**Ready to get started? → [Getting Started Guide](GETTING_STARTED.md)**

**Happy ATT&CK tracking! 🎯**
