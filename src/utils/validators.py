"""Input validation functions.

This module provides validation functions for JIRA and ATT&CK data.
"""

import re
from typing import Optional
from urllib.parse import urlparse

from src.logger import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Exception raised when validation fails."""

    pass


def validate_jira_url(url: str) -> bool:
    """Validate JIRA URL format.

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise

    Raises:
        ValidationError: If URL is invalid
    """
    if not url:
        raise ValidationError("JIRA URL cannot be empty")

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValidationError(f"Invalid URL format: {e}") from e

    # Check scheme
    if parsed.scheme not in ("http", "https"):
        raise ValidationError("URL must use http or https scheme")

    # Check netloc (hostname)
    if not parsed.netloc:
        raise ValidationError("URL must include hostname")

    # Check for common JIRA patterns
    if not (
        ".atlassian.net" in parsed.netloc
        or "jira" in parsed.netloc.lower()
        or parsed.path.startswith("/jira")
    ):
        logger.warning("url_does_not_look_like_jira", url=url)

    logger.debug("jira_url_validated", url=url)
    return True


def validate_project_key(key: str) -> bool:
    """Validate JIRA project key format.

    JIRA project keys must be:
    - 2-10 characters
    - Uppercase letters only
    - Start with a letter

    Args:
        key: Project key to validate

    Returns:
        True if valid, False otherwise

    Raises:
        ValidationError: If project key is invalid
    """
    if not key:
        raise ValidationError("Project key cannot be empty")

    # Convert to uppercase for validation
    key = key.upper()

    # Check length
    if not (2 <= len(key) <= 10):
        raise ValidationError("Project key must be 2-10 characters long")

    # Check format (letters only)
    if not key.isalpha():
        raise ValidationError("Project key must contain only letters")

    # Check starts with letter
    if not key[0].isalpha():
        raise ValidationError("Project key must start with a letter")

    logger.debug("project_key_validated", key=key)
    return True


def validate_technique_id(technique_id: str) -> bool:
    """Validate ATT&CK technique ID format.

    Valid formats:
    - T1234 (technique)
    - T1234.001 (sub-technique)

    Args:
        technique_id: Technique ID to validate

    Returns:
        True if valid, False otherwise

    Raises:
        ValidationError: If technique ID is invalid
    """
    if not technique_id:
        raise ValidationError("Technique ID cannot be empty")

    # Pattern for technique IDs: T followed by digits, optionally .digits
    pattern = r"^T\d{4}(\.\d{3})?$"

    if not re.match(pattern, technique_id):
        raise ValidationError(
            f"Invalid technique ID format: {technique_id}. "
            "Expected format: T1234 or T1234.001"
        )

    logger.debug("technique_id_validated", technique_id=technique_id)
    return True


def validate_email(email: str) -> bool:
    """Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise

    Raises:
        ValidationError: If email is invalid
    """
    if not email:
        raise ValidationError("Email cannot be empty")

    # Basic email pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        raise ValidationError(f"Invalid email format: {email}")

    logger.debug("email_validated", email=email)
    return True


def validate_api_token(token: str) -> bool:
    """Validate API token format.

    Args:
        token: API token to validate

    Returns:
        True if valid, False otherwise

    Raises:
        ValidationError: If token is invalid
    """
    if not token:
        raise ValidationError("API token cannot be empty")

    # Check minimum length (Atlassian tokens are typically 24+ chars)
    if len(token) < 20:
        raise ValidationError("API token appears too short")

    # Check for placeholder values
    placeholders = ["your_token", "placeholder", "example", "token_here"]
    if any(placeholder in token.lower() for placeholder in placeholders):
        raise ValidationError("API token appears to be a placeholder value")

    logger.debug("api_token_validated")
    return True


def sanitize_jql(jql: str) -> str:
    """Sanitize JQL query string.

    Args:
        jql: JQL query to sanitize

    Returns:
        Sanitized JQL query
    """
    # Remove potential SQL injection attempts
    dangerous_patterns = [";", "--", "/*", "*/", "xp_", "sp_"]

    sanitized = jql
    for pattern in dangerous_patterns:
        sanitized = sanitized.replace(pattern, "")

    return sanitized.strip()


def validate_maturity_level(level: str) -> bool:
    """Validate maturity level value.

    Args:
        level: Maturity level to validate

    Returns:
        True if valid, False otherwise

    Raises:
        ValidationError: If maturity level is invalid
    """
    valid_levels = ["Not Tracked", "Initial", "Defined", "Resilient", "Optimized"]

    if level not in valid_levels:
        raise ValidationError(
            f"Invalid maturity level: {level}. "
            f"Must be one of: {', '.join(valid_levels)}"
        )

    logger.debug("maturity_level_validated", level=level)
    return True
