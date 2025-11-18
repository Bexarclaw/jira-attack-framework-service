#!/usr/bin/env python3
"""
Setup script for JIRA Attack Framework Service (JAFRS)
"""

from setuptools import setup, find_packages
import os

# Read the README for long description
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="jira-attack-framework-service",
    version="2.0.0",
    author="Original: Mauricio Velazco, Olindo Verrillo",
    author_email="",
    description="Automate MITRE ATT&CK coverage tracking in Jira Software Cloud",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jira-attack-framework-service",
    packages=find_packages(),
    py_modules=['jira_attack_framework_service'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'attackcti',
        'requests>=2.20.0',
        'urllib3',
    ],
    entry_points={
        'console_scripts': [
            'jafrs=jira_attack_framework_service:main',
        ],
    },
    keywords='mitre attack jira security cybersecurity threat-intelligence',
    project_urls={
        'Documentation': 'https://github.com/yourusername/jira-attack-framework-service/tree/main/docs',
        'Source': 'https://github.com/yourusername/jira-attack-framework-service',
        'Tracker': 'https://github.com/yourusername/jira-attack-framework-service/issues',
    },
    license='BSD-3-Clause',
    include_package_data=True,
    zip_safe=False,
)
