"""JIRA custom field management operations.

This module provides functionality for creating and managing
custom fields in JIRA.
"""

from typing import Optional

from rich.console import Console

from src.jira.client import JiraClient, JiraAPIError
from src.jira.models import CustomField, CustomFieldOption, CustomFieldType
from src.logger import get_logger

logger = get_logger(__name__)
console = Console()


class CustomFieldManager:
    """Manager for JIRA custom field operations.

    Attributes:
        client: JIRA API client
        field_cache: Cache of field ID to name mappings
    """

    def __init__(self, client: JiraClient) -> None:
        """Initialize custom field manager.

        Args:
            client: Authenticated JIRA client
        """
        self.client = client
        self.field_cache: dict[str, str] = {}
        logger.info("custom_field_manager_initialized")

    def create_custom_field(self, field: CustomField) -> CustomField:
        """Create a new custom field.

        Args:
            field: Custom field definition

        Returns:
            Created field with ID populated

        Raises:
            JiraAPIError: If field creation fails
        """
        logger.info("creating_custom_field", name=field.name, type=field.field_type)

        try:
            payload = {
                "name": field.name,
                "description": field.description,
                "type": field.field_type,
                "searcherKey": field.searcherKey,
            }

            response = self.client.post("/rest/api/3/field", data=payload)

            field.id = response.get("id")
            self.field_cache[field.name] = field.id

            logger.info("custom_field_created", name=field.name, id=field.id)
            console.print(f"[green]✓ Created custom field: {field.name}[/green]")

            return field

        except JiraAPIError as e:
            if e.status_code == 400:
                logger.warning("custom_field_already_exists", name=field.name)
                # Try to get existing field
                existing = self.get_custom_field_by_name(field.name)
                if existing:
                    return existing
            logger.error("custom_field_creation_failed", name=field.name, error=str(e))
            raise

    def get_all_custom_fields(self) -> dict[str, str]:
        """Get all custom fields and their IDs.

        Returns:
            Dictionary mapping field names to field IDs

        Raises:
            JiraAPIError: If retrieval fails
        """
        logger.info("getting_all_custom_fields")

        try:
            response = self.client.get("/rest/api/3/field")

            # Filter for custom fields only (start with customfield_)
            custom_fields = {}
            for field in response:
                if field.get("id", "").startswith("customfield_"):
                    custom_fields[field["name"]] = field["id"]

            self.field_cache = custom_fields
            logger.info("custom_fields_retrieved", count=len(custom_fields))

            return custom_fields

        except JiraAPIError as e:
            logger.error("custom_field_retrieval_failed", error=str(e))
            raise

    def get_custom_field_by_name(self, field_name: str) -> Optional[CustomField]:
        """Get custom field by name.

        Args:
            field_name: Name of the field

        Returns:
            CustomField if found, None otherwise
        """
        logger.info("getting_custom_field", name=field_name)

        # Check cache first
        if field_name in self.field_cache:
            field_id = self.field_cache[field_name]
            logger.info("custom_field_found_in_cache", name=field_name, id=field_id)
            return CustomField(
                id=field_id,
                name=field_name,
                description="",
                field_type=CustomFieldType.TEXT,
                searcherKey="",
            )

        # Refresh cache and check again
        all_fields = self.get_all_custom_fields()
        if field_name in all_fields:
            field_id = all_fields[field_name]
            logger.info("custom_field_found", name=field_name, id=field_id)
            return CustomField(
                id=field_id,
                name=field_name,
                description="",
                field_type=CustomFieldType.TEXT,
                searcherKey="",
            )

        logger.warning("custom_field_not_found", name=field_name)
        return None

    def get_custom_field_id(self, field_name: str) -> Optional[str]:
        """Get custom field ID by name.

        Args:
            field_name: Name of the field

        Returns:
            Field ID if found, None otherwise
        """
        field = self.get_custom_field_by_name(field_name)
        return field.id if field else None

    def add_field_options(
        self,
        field_id: str,
        options: list[CustomFieldOption],
    ) -> None:
        """Add options to a select/multiselect field.

        Args:
            field_id: Custom field ID
            options: List of options to add

        Raises:
            JiraAPIError: If adding options fails
        """
        logger.info("adding_field_options", field_id=field_id, count=len(options))

        try:
            # Convert to JIRA format
            payload = [{"name": opt.value} for opt in options]

            # Use the legacy endpoint that supports option creation
            self.client.post(
                f"/rest/globalconfig/1/customfieldoptions/{field_id}",
                data=payload,
            )

            logger.info("field_options_added", field_id=field_id, count=len(options))
            console.print(f"[green]✓ Added {len(options)} options to field[/green]")

        except JiraAPIError as e:
            logger.error("field_option_addition_failed", field_id=field_id, error=str(e))
            raise

    def create_attack_custom_fields(self) -> dict[str, str]:
        """Create all custom fields needed for ATT&CK.

        Returns:
            Dictionary mapping field names to field IDs

        Raises:
            JiraAPIError: If field creation fails
        """
        logger.info("creating_attack_custom_fields")

        fields_to_create = [
            CustomField(
                name="Tactic",
                description="Attack Tactic",
                field_type=CustomFieldType.SELECT,
                searcherKey="com.atlassian.jira.plugin.system.customfieldtypes:multiselectsearcher",
            ),
            CustomField(
                name="Maturity",
                description="Detection Maturity",
                field_type=CustomFieldType.SELECT,
                searcherKey="com.atlassian.jira.plugin.system.customfieldtypes:multiselectsearcher",
            ),
            CustomField(
                name="Url",
                description="Attack Technique Url",
                field_type=CustomFieldType.URL,
                searcherKey="com.atlassian.jira.plugin.system.customfieldtypes:exacttextsearcher",
            ),
            CustomField(
                name="Datasources",
                description="Data Sources",
                field_type=CustomFieldType.MULTISELECT,
                searcherKey="com.atlassian.jira.plugin.system.customfieldtypes:multiselectsearcher",
            ),
            CustomField(
                name="Id",
                description="Technique Id",
                field_type=CustomFieldType.TEXT,
                searcherKey="com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
            ),
            CustomField(
                name="Sub-Technique of",
                description="Parent Technique Id",
                field_type=CustomFieldType.TEXT,
                searcherKey="com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
            ),
        ]

        field_ids = {}
        for field in fields_to_create:
            try:
                created_field = self.create_custom_field(field)
                field_ids[field.name] = created_field.id
            except JiraAPIError as e:
                logger.warning("skipping_field_creation", name=field.name, error=str(e))
                # Try to get existing field
                existing = self.get_custom_field_by_name(field.name)
                if existing:
                    field_ids[field.name] = existing.id

        logger.info("attack_custom_fields_created", count=len(field_ids))
        return field_ids

    def custom_fields_exist(self) -> bool:
        """Check if ATT&CK custom fields already exist.

        Returns:
            True if all required fields exist, False otherwise
        """
        required_fields = [
            "Tactic",
            "Maturity",
            "Url",
            "Datasources",
            "Id",
            "Sub-Technique of",
        ]

        all_fields = self.get_all_custom_fields()

        for field_name in required_fields:
            if field_name not in all_fields:
                return False

        return True
