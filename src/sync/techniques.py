"""Technique synchronization logic for ATT&CK to JIRA.

This module handles the creation and updating of JIRA issues
for ATT&CK techniques and sub-techniques.
"""

from typing import Any

from rich.console import Console
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn

from src.config import ConfigSettings
from src.jira.client import JiraClient
from src.jira.custom_fields import CustomFieldManager
from src.jira.issues import IssueManager
from src.jira.models import IssueType, MaturityLevel
from src.logger import get_logger
from src.mitre.client import MitreClient
from src.mitre.models import Technique, TechniqueCollection

logger = get_logger(__name__)
console = Console()


class TechniqueSync:
    """Handles synchronization of ATT&CK techniques to JIRA issues.

    Attributes:
        jira_client: JIRA API client
        mitre_client: MITRE ATT&CK client
        config: Application configuration
        issue_manager: JIRA issue manager
        field_manager: Custom field manager
    """

    def __init__(
        self,
        jira_client: JiraClient,
        mitre_client: MitreClient,
        config: ConfigSettings,
    ) -> None:
        """Initialize technique sync.

        Args:
            jira_client: Authenticated JIRA client
            mitre_client: MITRE ATT&CK client
            config: Application configuration
        """
        self.jira_client = jira_client
        self.mitre_client = mitre_client
        self.config = config

        self.issue_manager = IssueManager(jira_client)
        self.field_manager = CustomFieldManager(jira_client)

        # Cache for parent issue IDs
        self.parent_issue_cache: dict[str, dict[str, str]] = {}

        logger.info("technique_sync_initialized")

    def sync_all_techniques(
        self,
        project_key: str,
        collection: TechniqueCollection,
        include_subtechniques: bool = True,
        force_update: bool = False,
    ) -> int:
        """Sync all techniques from collection to JIRA.

        Args:
            project_key: JIRA project key
            collection: Collection of ATT&CK techniques
            include_subtechniques: Whether to include sub-techniques
            force_update: Force update of existing issues

        Returns:
            Number of techniques created/updated
        """
        logger.info(
            "syncing_all_techniques",
            project_key=project_key,
            total=len(collection.active_techniques),
            include_subtechniques=include_subtechniques,
        )

        # Get custom field IDs
        field_ids = self.field_manager.get_all_custom_fields()

        # Sort techniques to ensure parents are created before sub-techniques
        sorted_techniques = sorted(
            collection.active_techniques,
            key=lambda t: t.technique_id,
        )

        created_count = 0

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        ) as progress:
            task = progress.add_task(
                "Creating JIRA issues...",
                total=len(sorted_techniques),
            )

            for technique in sorted_techniques:
                # Skip sub-techniques if not requested
                if technique.x_mitre_is_subtechnique and not include_subtechniques:
                    progress.advance(task)
                    continue

                try:
                    self.sync_technique(
                        project_key=project_key,
                        technique=technique,
                        field_ids=field_ids,
                        force_update=force_update,
                    )
                    created_count += 1

                except Exception as e:
                    logger.error(
                        "technique_sync_failed",
                        technique_id=technique.technique_id,
                        error=str(e),
                    )
                    console.print(
                        f"[red]✗ Failed to sync {technique.technique_id}: {e}[/red]"
                    )

                progress.advance(task)

        logger.info("all_techniques_synced", count=created_count)
        return created_count

    def sync_technique(
        self,
        project_key: str,
        technique: Technique,
        field_ids: dict[str, str],
        force_update: bool = False,
    ) -> dict[str, Any]:
        """Sync a single technique to JIRA.

        Args:
            project_key: JIRA project key
            technique: Technique to sync
            field_ids: Custom field IDs
            force_update: Force update if issue exists

        Returns:
            Created/updated issue response
        """
        logger.info("syncing_technique", technique_id=technique.technique_id)

        # Build issue payload
        issue_dict = self._build_issue_dict(
            project_key=project_key,
            technique=technique,
            field_ids=field_ids,
        )

        # Create issue
        try:
            response = self.issue_manager.create_issue_raw(issue_dict)

            # Cache parent issue for sub-techniques
            if not technique.x_mitre_is_subtechnique:
                self.parent_issue_cache[technique.technique_id] = response

            logger.info(
                "technique_synced",
                technique_id=technique.technique_id,
                issue_key=response.get("key"),
            )

            return response

        except Exception as e:
            logger.error(
                "technique_sync_error",
                technique_id=technique.technique_id,
                error=str(e),
            )
            raise

    def _build_issue_dict(
        self,
        project_key: str,
        technique: Technique,
        field_ids: dict[str, str],
    ) -> dict[str, Any]:
        """Build JIRA issue dictionary for a technique.

        Args:
            project_key: JIRA project key
            technique: Technique to convert
            field_ids: Custom field IDs

        Returns:
            Issue dictionary for JIRA API
        """
        # Base fields
        fields: dict[str, Any] = {
            "project": {"key": project_key},
            "summary": technique.name,
            "description": technique.description,
            "issuetype": {
                "name": IssueType.SUBTASK.value
                if technique.x_mitre_is_subtechnique
                else IssueType.TASK.value
            },
        }

        # Add custom fields
        if "Id" in field_ids:
            fields[field_ids["Id"]] = technique.technique_id

        if "Tactic" in field_ids and technique.primary_tactic:
            fields[field_ids["Tactic"]] = {"value": technique.primary_tactic}

        if "Maturity" in field_ids:
            fields[field_ids["Maturity"]] = {"value": MaturityLevel.NOT_TRACKED.value}

        if "Url" in field_ids:
            fields[field_ids["Url"]] = technique.url

        if "Datasources" in field_ids and technique.x_mitre_data_sources:
            fields[field_ids["Datasources"]] = [
                {"value": ds.title()} for ds in technique.x_mitre_data_sources
            ]

        # Add parent for sub-techniques
        if technique.x_mitre_is_subtechnique and technique.parent_id:
            parent_issue = self.parent_issue_cache.get(technique.parent_id)
            if parent_issue:
                fields["parent"] = {"id": parent_issue["id"]}

                # Add sub-technique link
                if "Sub-Technique of" in field_ids:
                    fields[field_ids["Sub-Technique of"]] = (
                        f"{self.jira_client.base_url}/browse/{parent_issue['key']}"
                    )

        return {"fields": fields}

    def get_technique_maturity_levels(self, project_key: str) -> dict[str, str]:
        """Get maturity levels for all techniques in project.

        Args:
            project_key: JIRA project key

        Returns:
            Dictionary mapping technique IDs to maturity levels
        """
        logger.info("getting_technique_maturity", project_key=project_key)

        try:
            # Get custom field IDs
            field_ids = self.field_manager.get_all_custom_fields()
            id_field = field_ids.get("Id")
            maturity_field = field_ids.get("Maturity")

            if not id_field or not maturity_field:
                raise ValueError("Required custom fields not found")

            # Search for all issues in project
            issues = self.issue_manager.get_all_issues_for_project(project_key)

            # Extract maturity levels
            maturity_map = {}
            for issue in issues:
                technique_id = issue["fields"].get(id_field)
                maturity = issue["fields"].get(maturity_field)

                if technique_id and maturity:
                    maturity_value = maturity.get("value") if isinstance(maturity, dict) else maturity
                    maturity_map[technique_id] = maturity_value

            logger.info("technique_maturity_retrieved", count=len(maturity_map))
            return maturity_map

        except Exception as e:
            logger.error("technique_maturity_retrieval_failed", error=str(e))
            raise

    def clear_cache(self) -> None:
        """Clear parent issue cache."""
        self.parent_issue_cache.clear()
        logger.info("cache_cleared")
