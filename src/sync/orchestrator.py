"""Main workflow orchestrator for ATT&CK to JIRA synchronization.

This module coordinates the entire sync process including:
- Project setup
- Custom field creation
- Technique import
- Screen configuration
"""

from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import ConfigSettings
from src.jira.client import JiraClient
from src.jira.custom_fields import CustomFieldManager
from src.jira.models import CustomFieldOption, JiraProject, MaturityLevel
from src.jira.project import ProjectManager
from src.jira.screen import ScreenManager
from src.logger import get_logger
from src.mitre.client import MitreClient
from src.sync.techniques import TechniqueSync

logger = get_logger(__name__)
console = Console()


class SyncOrchestrator:
    """Orchestrates the complete ATT&CK to JIRA synchronization workflow.

    This class coordinates all the components needed to set up a JIRA project
    and sync ATT&CK techniques.

    Attributes:
        config: Application configuration
        jira_client: JIRA API client
        mitre_client: MITRE ATT&CK client
        project_manager: JIRA project manager
        field_manager: Custom field manager
        screen_manager: Screen manager
        technique_sync: Technique synchronization manager
    """

    def __init__(self, config: ConfigSettings) -> None:
        """Initialize sync orchestrator.

        Args:
            config: Application configuration
        """
        self.config = config

        # Initialize clients
        self.jira_client = JiraClient(config)
        self.mitre_client = MitreClient(config)

        # Initialize managers (will be set after connection)
        self.project_manager: Optional[ProjectManager] = None
        self.field_manager: Optional[CustomFieldManager] = None
        self.screen_manager: Optional[ScreenManager] = None
        self.technique_sync: Optional[TechniqueSync] = None

        logger.info("sync_orchestrator_initialized")

    def connect(self) -> None:
        """Connect to JIRA and MITRE APIs.

        Raises:
            JiraAuthenticationError: If JIRA connection fails
            MitreConnectionError: If MITRE connection fails
        """
        logger.info("connecting_to_apis")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            progress.add_task("Connecting to JIRA...", total=None)
            self.jira_client.connect()

            progress.add_task("Connecting to MITRE ATT&CK...", total=None)
            self.mitre_client.connect()

        # Initialize managers
        self.project_manager = ProjectManager(self.jira_client)
        self.field_manager = CustomFieldManager(self.jira_client)
        self.screen_manager = ScreenManager(self.jira_client)
        self.technique_sync = TechniqueSync(
            self.jira_client,
            self.mitre_client,
            self.config,
        )

        console.print("[green]✓ Connected to JIRA and MITRE ATT&CK[/green]")
        logger.info("apis_connected")

    def setup_project(
        self,
        project_name: Optional[str] = None,
        project_key: Optional[str] = None,
    ) -> JiraProject:
        """Set up JIRA project with all required configurations.

        This performs the complete setup:
        1. Create project
        2. Create custom fields
        3. Add field options
        4. Configure screens
        5. Hide unwanted fields

        Args:
            project_name: Override project name from config
            project_key: Override project key from config

        Returns:
            Created JIRA project

        Raises:
            ValueError: If managers not initialized
            JiraAPIError: If setup fails
        """
        if not self.project_manager or not self.field_manager or not self.screen_manager:
            raise ValueError("Not connected. Call connect() first.")

        logger.info("starting_project_setup")
        console.print("\n[bold]Setting up JIRA project...[/bold]\n")

        # Use config values if not overridden
        name = project_name or self.config.jira_project_name
        key = project_key or self.config.jira_project_key

        # Step 1: Create project
        console.print("[cyan]1. Creating project...[/cyan]")
        project = JiraProject(key=key, name=name)
        project = self.project_manager.create_project(project)

        # Step 2: Create custom fields
        console.print("[cyan]2. Creating custom fields...[/cyan]")
        field_ids = self.field_manager.create_attack_custom_fields()

        # Step 3: Add field options
        console.print("[cyan]3. Adding field options...[/cyan]")
        self._add_field_options(field_ids)

        # Step 4: Get project ID for screen configuration
        project_id = self.project_manager.get_project_id(key)
        if not project_id:
            raise ValueError(f"Failed to get project ID for {key}")

        # Step 5: Add custom fields to screen
        console.print("[cyan]4. Configuring screens...[/cyan]")
        self.screen_manager.add_custom_fields_to_screen(project_id, field_ids)

        # Step 6: Hide unwanted fields
        console.print("[cyan]5. Hiding unwanted fields...[/cyan]")
        self.screen_manager.hide_unwanted_fields(key, field_ids)

        console.print("\n[green]✓ Project setup complete![/green]\n")
        logger.info("project_setup_complete", project_key=key)

        return project

    def _add_field_options(self, field_ids: dict[str, str]) -> None:
        """Add options to custom fields.

        Args:
            field_ids: Dictionary of field names to IDs
        """
        if not self.field_manager:
            raise ValueError("Field manager not initialized")

        # Add maturity levels
        if "Maturity" in field_ids:
            maturity_options = [
                CustomFieldOption(value=MaturityLevel.NOT_TRACKED.value),
                CustomFieldOption(value=MaturityLevel.INITIAL.value),
                CustomFieldOption(value=MaturityLevel.DEFINED.value),
                CustomFieldOption(value=MaturityLevel.RESILIENT.value),
                CustomFieldOption(value=MaturityLevel.OPTIMIZED.value),
            ]
            self.field_manager.add_field_options(field_ids["Maturity"], maturity_options)

        # Add tactic options
        if "Tactic" in field_ids:
            tactics = self.mitre_client.get_enterprise_tactics()
            tactic_options = [
                CustomFieldOption(value=tactic.x_mitre_shortname) for tactic in tactics
            ]
            self.field_manager.add_field_options(field_ids["Tactic"], tactic_options)

        # Add data source options
        if "Datasources" in field_ids:
            data_sources = self.mitre_client.get_data_sources()
            ds_options = [CustomFieldOption(value=ds.name) for ds in data_sources]
            self.field_manager.add_field_options(field_ids["Datasources"], ds_options)

    def sync_techniques(
        self,
        project_key: str,
        techniques_only: bool = False,
        force: bool = False,
    ) -> int:
        """Sync ATT&CK techniques to JIRA.

        Args:
            project_key: JIRA project key
            techniques_only: Only sync parent techniques (no sub-techniques)
            force: Force re-import of existing techniques

        Returns:
            Number of techniques created

        Raises:
            ValueError: If technique sync not initialized
            MitreDataError: If fetching techniques fails
            JiraAPIError: If creating issues fails
        """
        if not self.technique_sync:
            raise ValueError("Not connected. Call connect() first.")

        logger.info(
            "starting_technique_sync",
            project_key=project_key,
            techniques_only=techniques_only,
            force=force,
        )

        console.print("\n[bold]Synchronizing ATT&CK techniques...[/bold]\n")

        # Fetch techniques from MITRE
        console.print("[cyan]Fetching techniques from MITRE ATT&CK...[/cyan]")
        collection = self.mitre_client.get_all_data()

        # Sync to JIRA
        count = self.technique_sync.sync_all_techniques(
            project_key=project_key,
            collection=collection,
            include_subtechniques=not techniques_only,
            force_update=force,
        )

        console.print(f"\n[green]✓ Synced {count} techniques to JIRA![/green]\n")
        logger.info("technique_sync_complete", count=count)

        return count

    def run_full_setup(
        self,
        project_name: Optional[str] = None,
        project_key: Optional[str] = None,
    ) -> None:
        """Run complete setup: create project and import techniques.

        Args:
            project_name: Override project name from config
            project_key: Override project key from config
        """
        logger.info("starting_full_setup")

        try:
            # Connect
            self.connect()

            # Setup project
            project = self.setup_project(project_name, project_key)

            # Sync techniques
            self.sync_techniques(project.key)

            console.print("[bold green]✓ Full setup complete![/bold green]")
            logger.info("full_setup_complete")

        except Exception as e:
            logger.error("full_setup_failed", error=str(e))
            console.print(f"[red]Setup failed: {e}[/red]")
            raise

        finally:
            self.close()

    def close(self) -> None:
        """Close all connections."""
        if self.jira_client:
            self.jira_client.close()
        if self.mitre_client:
            self.mitre_client.close()

        logger.info("sync_orchestrator_closed")
