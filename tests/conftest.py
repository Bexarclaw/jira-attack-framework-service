"""Shared pytest fixtures for all tests."""

import pytest
from unittest.mock import Mock, patch
from src.config import ConfigSettings
from src.jira.client import JiraClient


@pytest.fixture
def config():
    """Mock configuration."""
    return ConfigSettings(
        jira_url="https://test.atlassian.net",
        jira_username="test@example.com",
        jira_api_token="test-token",
        mitre_api_endpoint="https://test.com/attack.json",
        log_level="INFO",
        project_name="TEST",
        project_key="TEST",
    )


@pytest.fixture
def client(config):
    """Mock Jira client."""
    with patch('src.jira.client.httpx.Client'):
        return JiraClient(config)


@pytest.fixture
def mock_response():
    """Mock HTTP response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"success": True}
    return mock
