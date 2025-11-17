"""JIRA Cloud REST API client.

This module provides a base client for authenticating and making
requests to the JIRA Cloud REST API.
"""

from typing import Any

import httpx

from src.config import ConfigSettings
from src.logger import get_logger
from src.utils.retry import with_retry

logger = get_logger(__name__)


class JiraClientError(Exception):
    """Base exception for JIRA client errors."""

    pass


class JiraAuthenticationError(JiraClientError):
    """Exception raised when authentication fails."""

    pass


class JiraAPIError(JiraClientError):
    """Exception raised when API request fails."""

    def __init__(self, message: str, status_code: int | None = None, response: dict | None = None):
        """Initialize API error.

        Args:
            message: Error message
            status_code: HTTP status code
            response: API response body
        """
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class JiraClient:
    """Client for JIRA Cloud REST API.

    This client handles authentication, request management, and
    provides base functionality for JIRA operations.

    Attributes:
        config: Application configuration
        base_url: Base URL for JIRA instance
        auth: Authentication tuple (username, token)
        client: HTTP client instance
    """

    def __init__(self, config: ConfigSettings) -> None:
        """Initialize JIRA client.

        Args:
            config: Application configuration settings
        """
        self.config = config
        self.base_url = config.jira_url.rstrip("/")
        self.auth = (config.jira_username, config.jira_api_token)
        self.client: httpx.Client | None = None
        logger.info("jira_client_initialized", url=self.base_url)

    def connect(self) -> None:
        """Establish connection to JIRA API.

        Raises:
            JiraAuthenticationError: If authentication fails
        """
        try:
            logger.info("connecting_to_jira", url=self.base_url)

            # Create HTTP client
            self.client = httpx.Client(
                auth=self.auth,
                verify=self.config.ssl_verify,
                timeout=self.config.request_timeout,
                headers={"Content-Type": "application/json"},
            )

            # Test authentication
            response = self.client.get(f"{self.base_url}/rest/api/3/myself")

            if response.status_code == 200:
                user_info = response.json()
                logger.info("jira_authenticated", user=user_info.get("displayName"))
            elif response.status_code == 401:
                raise JiraAuthenticationError("Invalid credentials")
            else:
                raise JiraAuthenticationError(
                    f"Authentication failed: {response.status_code}"
                )

        except httpx.HTTPError as e:
            logger.error("jira_connection_failed", error=str(e))
            raise JiraAuthenticationError(f"Failed to connect to JIRA: {e}") from e

    @with_retry()
    def get(self, endpoint: str, params: dict | None = None) -> dict[str, Any]:
        """Make GET request to JIRA API.

        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            JiraClientError: If not connected
            JiraAPIError: If request fails
        """
        if not self.client:
            raise JiraClientError("Not connected. Call connect() first.")

        url = f"{self.base_url}{endpoint}"
        logger.debug("jira_get_request", url=url, params=params)

        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error("jira_get_failed", url=url, status=e.response.status_code)
            raise JiraAPIError(
                f"GET request failed: {e}",
                status_code=e.response.status_code,
                response=e.response.json() if e.response.content else None,
            ) from e

    @with_retry()
    def post(
        self,
        endpoint: str,
        data: dict | None = None,
        params: dict | None = None,
    ) -> dict[str, Any]:
        """Make POST request to JIRA API.

        Args:
            endpoint: API endpoint (without base URL)
            data: Request body
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            JiraClientError: If not connected
            JiraAPIError: If request fails
        """
        if not self.client:
            raise JiraClientError("Not connected. Call connect() first.")

        url = f"{self.base_url}{endpoint}"
        logger.debug("jira_post_request", url=url, params=params)

        try:
            response = self.client.post(url, json=data, params=params)
            response.raise_for_status()

            # Some endpoints return empty responses
            if response.content:
                return response.json()
            return {}

        except httpx.HTTPStatusError as e:
            logger.error("jira_post_failed", url=url, status=e.response.status_code)
            raise JiraAPIError(
                f"POST request failed: {e}",
                status_code=e.response.status_code,
                response=e.response.json() if e.response.content else None,
            ) from e

    @with_retry()
    def put(
        self,
        endpoint: str,
        data: dict | None = None,
        params: dict | None = None,
    ) -> dict[str, Any]:
        """Make PUT request to JIRA API.

        Args:
            endpoint: API endpoint (without base URL)
            data: Request body
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            JiraClientError: If not connected
            JiraAPIError: If request fails
        """
        if not self.client:
            raise JiraClientError("Not connected. Call connect() first.")

        url = f"{self.base_url}{endpoint}"
        logger.debug("jira_put_request", url=url, params=params)

        try:
            response = self.client.put(url, json=data, params=params)
            response.raise_for_status()

            # Some endpoints return empty responses
            if response.content:
                return response.json()
            return {}

        except httpx.HTTPStatusError as e:
            logger.error("jira_put_failed", url=url, status=e.response.status_code)
            raise JiraAPIError(
                f"PUT request failed: {e}",
                status_code=e.response.status_code,
                response=e.response.json() if e.response.content else None,
            ) from e

    @with_retry()
    def delete(self, endpoint: str, params: dict | None = None) -> None:
        """Make DELETE request to JIRA API.

        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters

        Raises:
            JiraClientError: If not connected
            JiraAPIError: If request fails
        """
        if not self.client:
            raise JiraClientError("Not connected. Call connect() first.")

        url = f"{self.base_url}{endpoint}"
        logger.debug("jira_delete_request", url=url, params=params)

        try:
            response = self.client.delete(url, params=params)
            response.raise_for_status()

        except httpx.HTTPStatusError as e:
            logger.error("jira_delete_failed", url=url, status=e.response.status_code)
            raise JiraAPIError(
                f"DELETE request failed: {e}",
                status_code=e.response.status_code,
                response=e.response.json() if e.response.content else None,
            ) from e

    def close(self) -> None:
        """Close HTTP client connection."""
        if self.client:
            self.client.close()
            self.client = None
            logger.info("jira_client_closed")

    def __enter__(self) -> "JiraClient":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
