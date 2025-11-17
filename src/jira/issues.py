"""JIRA issue creation and management operations.

This module provides functionality for creating and managing
JIRA issues for ATT&CK techniques.
"""

from typing import Any

from rich.console import Console

from src.jira.client import JiraAPIError, JiraClient
from src.jira.models import JiraIssue, JiraIssueFields
from src.logger import get_logger

logger = get_logger(__name__)
console = Console()


class IssueManager:
    """Manager for JIRA issue operations.

    Attributes:
        client: JIRA API client
    """

    def __init__(self, client: JiraClient) -> None:
        """Initialize issue manager.

        Args:
            client: Authenticated JIRA client
        """
        self.client = client
        logger.info("issue_manager_initialized")

    def create_issue(self, issue: JiraIssue) -> JiraIssue:
        """Create a new JIRA issue.

        Args:
            issue: Issue definition

        Returns:
            Created issue with ID and key populated

        Raises:
            JiraAPIError: If issue creation fails
        """
        logger.info("creating_issue", summary=issue.fields.summary)

        try:
            # Convert to JIRA API format
            payload = {"fields": issue.fields.model_dump(by_alias=True, exclude_none=True)}

            response = self.client.post("/rest/api/2/issue", data=payload)

            issue.id = response.get("id")
            issue.key = response.get("key")
            issue.self_url = response.get("self")

            logger.info("issue_created", key=issue.key, id=issue.id)

            return issue

        except JiraAPIError as e:
            logger.error(
                "issue_creation_failed",
                summary=issue.fields.summary,
                error=str(e),
            )
            raise

    def create_issue_raw(self, issue_dict: dict[str, Any]) -> dict[str, Any]:
        """Create issue using raw dictionary payload.

        Args:
            issue_dict: Issue data as dictionary

        Returns:
            Created issue response

        Raises:
            JiraAPIError: If issue creation fails
        """
        logger.info("creating_issue_raw")

        try:
            response = self.client.post("/rest/api/2/issue", data=issue_dict)
            logger.info("issue_created_raw", key=response.get("key"))
            return response

        except JiraAPIError as e:
            logger.error("issue_creation_failed_raw", error=str(e))
            raise

    def get_issue(self, issue_key: str) -> JiraIssue | None:
        """Get issue by key.

        Args:
            issue_key: Issue key (e.g., ATTACK-123)

        Returns:
            Issue if found, None otherwise

        Raises:
            JiraAPIError: If API request fails
        """
        logger.info("getting_issue", key=issue_key)

        try:
            response = self.client.get(f"/rest/api/3/issue/{issue_key}")

            issue = JiraIssue(
                id=response["id"],
                key=response["key"],
                fields=JiraIssueFields(**response["fields"]),
                self_url=response.get("self"),
            )

            logger.info("issue_retrieved", key=issue_key)
            return issue

        except JiraAPIError as e:
            if e.status_code == 404:
                logger.warning("issue_not_found", key=issue_key)
                return None
            else:
                logger.error("issue_retrieval_failed", key=issue_key, error=str(e))
                raise

    def update_issue(self, issue_key: str, fields: dict[str, Any]) -> None:
        """Update issue fields.

        Args:
            issue_key: Issue key to update
            fields: Fields to update

        Raises:
            JiraAPIError: If update fails
        """
        logger.info("updating_issue", key=issue_key)

        try:
            payload = {"fields": fields}
            self.client.put(f"/rest/api/3/issue/{issue_key}", data=payload)

            logger.info("issue_updated", key=issue_key)

        except JiraAPIError as e:
            logger.error("issue_update_failed", key=issue_key, error=str(e))
            raise

    def delete_issue(self, issue_key: str) -> None:
        """Delete an issue.

        Args:
            issue_key: Issue key to delete

        Raises:
            JiraAPIError: If deletion fails
        """
        logger.info("deleting_issue", key=issue_key)

        try:
            self.client.delete(f"/rest/api/3/issue/{issue_key}")
            logger.info("issue_deleted", key=issue_key)

        except JiraAPIError as e:
            logger.error("issue_deletion_failed", key=issue_key, error=str(e))
            raise

    def search_issues(
        self,
        jql: str,
        fields: list[str] | None = None,
        max_results: int = 50,
        start_at: int = 0,
    ) -> list[dict[str, Any]]:
        """Search for issues using JQL.

        Args:
            jql: JQL query string
            fields: Fields to return (None = all)
            max_results: Maximum results per page
            start_at: Starting index for pagination

        Returns:
            List of issue dictionaries

        Raises:
            JiraAPIError: If search fails
        """
        logger.info("searching_issues", jql=jql, max_results=max_results)

        try:
            params = {
                "jql": jql,
                "maxResults": max_results,
                "startAt": start_at,
            }

            if fields:
                params["fields"] = ",".join(fields)

            response = self.client.get("/rest/api/3/search", params=params)

            issues = response.get("issues", [])
            logger.info("issues_found", count=len(issues), total=response.get("total"))

            return issues

        except JiraAPIError as e:
            logger.error("issue_search_failed", jql=jql, error=str(e))
            raise

    def get_all_issues_for_project(self, project_key: str) -> list[dict[str, Any]]:
        """Get all issues for a project.

        Args:
            project_key: Project key

        Returns:
            List of all issues in project

        Raises:
            JiraAPIError: If retrieval fails
        """
        logger.info("getting_all_project_issues", project_key=project_key)

        all_issues = []
        start_at = 0
        max_results = 50

        while True:
            jql = f"project = {project_key}"
            issues = self.search_issues(jql, max_results=max_results, start_at=start_at)

            if not issues:
                break

            all_issues.extend(issues)
            start_at += max_results

            if len(issues) < max_results:
                break

        logger.info("all_project_issues_retrieved", count=len(all_issues))
        return all_issues

    def issue_exists(self, issue_key: str) -> bool:
        """Check if issue exists.

        Args:
            issue_key: Issue key to check

        Returns:
            True if issue exists, False otherwise
        """
        try:
            issue = self.get_issue(issue_key)
            return issue is not None
        except JiraAPIError:
            return False
