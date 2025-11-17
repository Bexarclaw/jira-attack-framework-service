"""JIRA screen and field layout management operations.

This module provides functionality for managing screen configurations
and field layouts in JIRA.
"""

from typing import Any

from rich.console import Console

from src.jira.client import JiraAPIError, JiraClient
from src.jira.models import FieldLayoutConfig
from src.logger import get_logger

logger = get_logger(__name__)
console = Console()


class ScreenManager:
    """Manager for JIRA screen operations.

    Attributes:
        client: JIRA API client
    """

    def __init__(self, client: JiraClient) -> None:
        """Initialize screen manager.

        Args:
            client: Authenticated JIRA client
        """
        self.client = client
        logger.info("screen_manager_initialized")

    def get_screens(self) -> list[dict[str, Any]]:
        """Get all screens.

        Returns:
            List of screen definitions

        Raises:
            JiraAPIError: If retrieval fails
        """
        logger.info("getting_screens")

        try:
            response = self.client.get("/rest/api/3/screens")
            screens = response.get("values", [])

            logger.info("screens_retrieved", count=len(screens))
            return screens

        except JiraAPIError as e:
            logger.error("screen_retrieval_failed", error=str(e))
            raise

    def get_project_screens(self, project_key: str) -> list[str]:
        """Get screen IDs for a project.

        Args:
            project_key: Project key

        Returns:
            List of screen IDs

        Raises:
            JiraAPIError: If retrieval fails
        """
        logger.info("getting_project_screens", project_key=project_key)

        try:
            screens = self.get_screens()

            # Filter screens for this project
            project_screens = [
                screen["id"]
                for screen in screens
                if project_key in screen.get("name", "")
                and "Default Issue Screen" in screen.get("name", "")
            ]

            logger.info("project_screens_found", count=len(project_screens))
            return project_screens

        except JiraAPIError as e:
            logger.error("project_screen_retrieval_failed", error=str(e))
            raise

    def get_screen_tabs(self, screen_id: str) -> list[dict[str, Any]]:
        """Get tabs for a screen.

        Args:
            screen_id: Screen ID

        Returns:
            List of tab definitions

        Raises:
            JiraAPIError: If retrieval fails
        """
        logger.info("getting_screen_tabs", screen_id=screen_id)

        try:
            response = self.client.get(f"/rest/api/3/screens/{screen_id}/tabs")
            logger.info("screen_tabs_retrieved", screen_id=screen_id, count=len(response))
            return response

        except JiraAPIError as e:
            logger.error("screen_tab_retrieval_failed", screen_id=screen_id, error=str(e))
            raise

    def add_field_to_screen(
        self,
        screen_id: str,
        tab_id: str,
        field_id: str,
    ) -> None:
        """Add custom field to screen tab.

        Args:
            screen_id: Screen ID
            tab_id: Tab ID
            field_id: Field ID to add

        Raises:
            JiraAPIError: If addition fails
        """
        logger.info("adding_field_to_screen", screen_id=screen_id, field_id=field_id)

        try:
            payload = {"fieldId": field_id}

            self.client.post(
                f"/rest/api/3/screens/{screen_id}/tabs/{tab_id}/fields",
                data=payload,
            )

            logger.info("field_added_to_screen", screen_id=screen_id, field_id=field_id)

        except JiraAPIError as e:
            if e.status_code == 400:
                logger.warning("field_already_on_screen", field_id=field_id)
            else:
                logger.error("field_addition_failed", field_id=field_id, error=str(e))
                raise

    def add_custom_fields_to_screen(
        self,
        project_id: str,
        field_ids: dict[str, str],
    ) -> None:
        """Add all custom fields to project screens.

        Args:
            project_id: Project ID
            field_ids: Dictionary of field names to field IDs

        Raises:
            JiraAPIError: If addition fails
        """
        logger.info("adding_custom_fields_to_screens", project_id=project_id)

        try:
            # Get screen IDs for project
            screen_ids = self.get_screen_ids(project_id)

            # Get tab IDs for each screen
            screen_tab_ids = self.get_screen_tab_ids(project_id)

            # Add each field to the first screen/tab
            if screen_ids and screen_tab_ids:
                for field_name, field_id in field_ids.items():
                    try:
                        self.add_field_to_screen(
                            screen_ids[0],
                            screen_tab_ids[0],
                            field_id,
                        )
                    except JiraAPIError as e:
                        logger.warning("skipping_field", field_name=field_name, error=str(e))

            console.print("[green]✓ Added custom fields to screen[/green]")

        except JiraAPIError as e:
            logger.error("custom_field_screen_addition_failed", error=str(e))
            raise

    def configure_field_layout(
        self,
        project_key: str,
        screen_id: str,
        layout: FieldLayoutConfig,
    ) -> None:
        """Configure field layout for issue view.

        Args:
            project_key: Project key
            screen_id: Screen ID
            layout: Field layout configuration

        Raises:
            JiraAPIError: If configuration fails
        """
        logger.info("configuring_field_layout", project_key=project_key, screen_id=screen_id)

        try:
            payload = layout.to_jira_format()

            self.client.put(
                f"/rest/issuedetailslayout/config/classic/screen"
                f"?projectIdOrKey={project_key}&screenId={screen_id}",
                data=payload,
            )

            logger.info("field_layout_configured", project_key=project_key)

        except JiraAPIError as e:
            logger.error("field_layout_configuration_failed", error=str(e))
            raise

    def hide_unwanted_fields(
        self,
        project_key: str,
        custom_field_ids: dict[str, str],
    ) -> None:
        """Hide unwanted fields from issue layout.

        Args:
            project_key: Project key
            custom_field_ids: Dictionary of custom field IDs

        Raises:
            JiraAPIError: If configuration fails
        """
        logger.info("hiding_unwanted_fields", project_key=project_key)

        try:
            # Get project ID
            from src.jira.project import ProjectManager

            project_mgr = ProjectManager(self.client)
            project_id = project_mgr.get_project_id(project_key)

            if not project_id:
                raise ValueError(f"Project {project_key} not found")

            # Get screen IDs
            screen_ids = self.get_screen_ids(project_id)

            # Create field layout configuration
            layout = FieldLayoutConfig(
                primary=[
                    {"id": "assignee", "type": "FIELD"},
                    {"id": "reporter", "type": "FIELD"},
                    {"id": "labels", "type": "FIELD"},
                    {"id": custom_field_ids.get("Maturity", ""), "type": "FIELD"},
                    {"id": custom_field_ids.get("Datasources", ""), "type": "FIELD"},
                ],
                secondary=[
                    {"id": "priority", "type": "FIELD"},
                ],
                visible=[
                    {"id": custom_field_ids.get("Tactic", ""), "type": "FIELD"},
                    {"id": custom_field_ids.get("Id", ""), "type": "FIELD"},
                    {"id": custom_field_ids.get("Url", ""), "type": "FIELD"},
                    {"id": custom_field_ids.get("Sub-Technique of", ""), "type": "FIELD"},
                    {"id": "description", "type": "FIELD"},
                ],
                always_hidden=[
                    {"id": "timeoriginalestimate", "type": "FIELD"},
                    {"id": "timetracking", "type": "FIELD"},
                    {"id": "components", "type": "FIELD"},
                    {"id": "fixVersions", "type": "FIELD"},
                    {"id": "duedate", "type": "FIELD"},
                    {"id": "devSummary", "type": "DEV_SUMMARY"},
                ],
            )

            # Apply layout to each screen
            for screen_id in screen_ids:
                self.configure_field_layout(project_key, screen_id, layout)

            console.print("[green]✓ Configured field layout[/green]")

        except Exception as e:
            logger.error("field_hiding_failed", error=str(e))
            raise

    def get_screen_ids(self, project_id: str) -> list[str]:
        """Get screen IDs for a project.

        Args:
            project_id: Project ID

        Returns:
            List of screen IDs
        """
        logger.info("getting_screen_ids", project_id=project_id)

        try:
            screen_scheme_ids = self.get_screen_scheme_ids(project_id)
            screen_ids = []

            for scheme_id in screen_scheme_ids:
                response = self.client.get(f"/rest/api/2/screenscheme?id={scheme_id}")
                values = response.get("values", [])
                if values:
                    screens = values[0].get("screens", {})
                    if screens:
                        screen_ids.append(list(screens.values())[0])

            logger.info("screen_ids_retrieved", count=len(screen_ids))
            return screen_ids

        except JiraAPIError as e:
            logger.error("screen_id_retrieval_failed", error=str(e))
            raise

    def get_screen_scheme_ids(self, project_id: str) -> list[str]:
        """Get screen scheme IDs for a project.

        Args:
            project_id: Project ID

        Returns:
            List of screen scheme IDs
        """
        logger.info("getting_screen_scheme_ids", project_id=project_id)

        try:
            issue_type_scheme_ids = self.get_issue_type_screen_scheme_ids(project_id)
            screen_scheme_ids = []

            for scheme_id in issue_type_scheme_ids:
                response = self.client.get(
                    f"/rest/api/2/issuetypescreenscheme/mapping"
                    f"?issueTypeScreenSchemeId={scheme_id}"
                )

                for item in response.get("values", []):
                    screen_scheme_ids.append(item["screenSchemeId"])

            logger.info("screen_scheme_ids_retrieved", count=len(screen_scheme_ids))
            return screen_scheme_ids

        except JiraAPIError as e:
            logger.error("screen_scheme_id_retrieval_failed", error=str(e))
            raise

    def get_issue_type_screen_scheme_ids(self, project_id: str) -> list[str]:
        """Get issue type screen scheme IDs for a project.

        Args:
            project_id: Project ID

        Returns:
            List of scheme IDs
        """
        logger.info("getting_issue_type_screen_scheme_ids", project_id=project_id)

        try:
            response = self.client.get(
                "/rest/api/3/issuetypescreenscheme/project/",
                params={"projectId": project_id},
            )

            scheme_ids = [
                item["issueTypeScreenScheme"]["id"] for item in response.get("values", [])
            ]

            logger.info("issue_type_screen_scheme_ids_retrieved", count=len(scheme_ids))
            return scheme_ids

        except JiraAPIError as e:
            logger.error("issue_type_screen_scheme_id_retrieval_failed", error=str(e))
            raise

    def get_screen_tab_ids(self, project_id: str) -> list[str]:
        """Get screen tab IDs for a project.

        Args:
            project_id: Project ID

        Returns:
            List of tab IDs
        """
        logger.info("getting_screen_tab_ids", project_id=project_id)

        try:
            screen_ids = self.get_screen_ids(project_id)
            tab_ids = []

            for screen_id in screen_ids:
                tabs = self.get_screen_tabs(screen_id)
                if tabs:
                    tab_ids.append(tabs[0]["id"])

            logger.info("screen_tab_ids_retrieved", count=len(tab_ids))
            return tab_ids

        except JiraAPIError as e:
            logger.error("screen_tab_id_retrieval_failed", error=str(e))
            raise
