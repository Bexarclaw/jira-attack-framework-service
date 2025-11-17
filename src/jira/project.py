"""JIRA project management operations.

This module provides functionality for creating and managing
JIRA projects.
"""

from typing import Optional

from rich.console import Console

from src.jira.client import JiraClient, JiraAPIError
from src.jira.models import JiraProject
from src.logger import get_logger

logger = get_logger(__name__)
console = Console()


class ProjectManager:
    """Manager for JIRA project operations.

    Attributes:
        client: JIRA API client
    """

    def __init__(self, client: JiraClient) -> None:
        """Initialize project manager.

        Args:
            client: Authenticated JIRA client
        """
        self.client = client
        logger.info("project_manager_initialized")

    def create_project(self, project: JiraProject) -> JiraProject:
        """Create a new JIRA project.

        Args:
            project: Project configuration

        Returns:
            Created project with ID populated

        Raises:
            JiraAPIError: If project creation fails
        """
        logger.info("creating_project", key=project.key, name=project.name)

        try:
            # Use simplified project creation endpoint
            payload = {
                "key": project.key,
                "name": project.name,
                "templateKey": project.templateKey,
            }

            response = self.client.post(
                "/rest/simplified/latest/project",
                data=payload,
            )

            logger.info("project_created", key=project.key, id=response.get("id"))
            console.print(f"[green]✓ Created project: {project.name} ({project.key})[/green]")

            # Update project with response data
            project.id = response.get("id")
            return project

        except JiraAPIError as e:
            if e.status_code == 409:
                logger.warning("project_already_exists", key=project.key)
                console.print(f"[yellow]Project {project.key} already exists[/yellow]")
                # Try to get existing project
                return self.get_project(project.key) or project
            else:
                logger.error("project_creation_failed", key=project.key, error=str(e))
                raise

    def get_project(self, project_key: str) -> Optional[JiraProject]:
        """Get project by key.

        Args:
            project_key: Project key

        Returns:
            Project if found, None otherwise

        Raises:
            JiraAPIError: If API request fails
        """
        logger.info("getting_project", key=project_key)

        try:
            response = self.client.get(f"/rest/api/3/project/{project_key}")

            project = JiraProject(
                id=response["id"],
                key=response["key"],
                name=response["name"],
                description=response.get("description"),
            )

            logger.info("project_retrieved", key=project_key, id=project.id)
            return project

        except JiraAPIError as e:
            if e.status_code == 404:
                logger.warning("project_not_found", key=project_key)
                return None
            else:
                logger.error("project_retrieval_failed", key=project_key, error=str(e))
                raise

    def get_project_id(self, project_key: str) -> Optional[str]:
        """Get project ID from project key.

        Args:
            project_key: Project key

        Returns:
            Project ID if found, None otherwise
        """
        logger.info("getting_project_id", key=project_key)

        try:
            response = self.client.get("/rest/api/3/project/search")

            for project in response.get("values", []):
                if project["key"] == project_key:
                    project_id = project["id"]
                    logger.info("project_id_found", key=project_key, id=project_id)
                    return project_id

            logger.warning("project_id_not_found", key=project_key)
            return None

        except JiraAPIError as e:
            logger.error("project_id_retrieval_failed", key=project_key, error=str(e))
            raise

    def delete_project(self, project_key: str) -> None:
        """Delete a project.

        Args:
            project_key: Project key to delete

        Raises:
            JiraAPIError: If deletion fails
        """
        logger.info("deleting_project", key=project_key)

        try:
            self.client.delete(f"/rest/api/3/project/{project_key}")
            logger.info("project_deleted", key=project_key)
            console.print(f"[green]✓ Deleted project: {project_key}[/green]")

        except JiraAPIError as e:
            logger.error("project_deletion_failed", key=project_key, error=str(e))
            raise

    def project_exists(self, project_key: str) -> bool:
        """Check if project exists.

        Args:
            project_key: Project key to check

        Returns:
            True if project exists, False otherwise
        """
        try:
            project = self.get_project(project_key)
            return project is not None
        except JiraAPIError:
            return False
