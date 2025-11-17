"""Main CLI entry point for JIRA Attack Framework Service.

This module provides the command-line interface using Click for managing
MITRE ATT&CK techniques in JIRA.
"""

import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.config import create_default_env_file, get_config, validate_config_file_exists
from src.logger import get_logger, setup_logging

console = Console()
logger = get_logger(__name__)


@click.group()
@click.version_option(version="2.0.0", prog_name="attack2jira")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to .env configuration file",
)
@click.pass_context
def cli(ctx: click.Context, config: str | None) -> None:
    """JIRA Attack Framework Service - Import MITRE ATT&CK into JIRA.

    This tool helps security teams track their defensive coverage against
    MITRE ATT&CK techniques by importing them into JIRA for project management.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Check for .env file
    if not validate_config_file_exists() and config is None:
        console.print(
            Panel.fit(
                "[yellow]No .env file found.[/yellow]\n"
                "Run [bold]attack2jira init[/bold] to create one.",
                title="Configuration Missing",
                border_style="yellow",
            )
        )
        if not click.confirm("Would you like to create .env from template?"):
            console.print("[red]Exiting. Please configure .env file.[/red]")
            sys.exit(1)
        create_default_env_file()

    # Load configuration and setup logging
    try:
        app_config = get_config()
        setup_logging(app_config)
        ctx.obj["config"] = app_config
        logger.info("application_started", version="2.0.0")
    except Exception as e:
        console.print(f"[red]Failed to load configuration: {e}[/red]")
        sys.exit(1)


@cli.command()
def init() -> None:
    """Initialize configuration by creating .env file from template."""
    console.print(Panel.fit("Initializing JIRA Attack Framework Service", style="bold blue"))

    if validate_config_file_exists():
        console.print("[yellow].env file already exists[/yellow]")
        if not click.confirm("Overwrite existing .env file?", default=False):
            console.print("[yellow]Initialization cancelled[/yellow]")
            return

    create_default_env_file()
    console.print("\n[green]✓ Initialization complete![/green]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("1. Edit .env with your JIRA credentials")
    console.print("2. Run: [bold]attack2jira setup[/bold] to create JIRA project")
    console.print("3. Run: [bold]attack2jira sync[/bold] to import techniques")


@cli.command()
@click.option(
    "--project-name",
    "-p",
    help="JIRA project name (overrides .env)",
)
@click.option(
    "--project-key",
    "-k",
    help="JIRA project key (overrides .env)",
)
@click.pass_context
def setup(
    ctx: click.Context,
    project_name: str | None,
    project_key: str | None,
) -> None:
    """Set up JIRA project with custom fields and screens.

    This command will:
    - Create a new JIRA project
    - Add custom fields (Tactic, Maturity, Data Sources, etc.)
    - Configure field options
    - Set up screen layouts
    """
    config = ctx.obj["config"]
    logger.info("setup_started", project_name=project_name, project_key=project_key)

    console.print(Panel.fit("Setting up JIRA Project for ATT&CK", style="bold blue"))

    # TODO: Implementation in Phase 2
    console.print("[yellow]Setup command - Implementation pending[/yellow]")


@cli.command()
@click.option(
    "--techniques-only",
    is_flag=True,
    help="Import only parent techniques (no sub-techniques)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force re-import of existing techniques",
)
@click.pass_context
def sync(
    ctx: click.Context,
    techniques_only: bool,
    force: bool,
) -> None:
    """Synchronize MITRE ATT&CK techniques to JIRA.

    This command will:
    - Fetch latest ATT&CK techniques from MITRE
    - Create JIRA issues for each technique
    - Link sub-techniques to parent techniques
    - Update existing issues if --force is used
    """
    config = ctx.obj["config"]
    logger.info("sync_started", techniques_only=techniques_only, force=force)

    console.print(Panel.fit("Synchronizing ATT&CK Techniques to JIRA", style="bold blue"))

    # TODO: Implementation in Phase 2
    console.print("[yellow]Sync command - Implementation pending[/yellow]")


@cli.command()
@click.option(
    "--output",
    "-o",
    default="attack2jira.json",
    help="Output file path",
)
@click.option(
    "--hide-not-tracked",
    is_flag=True,
    help="Hide techniques with 'Not Tracked' maturity",
)
@click.pass_context
def export(
    ctx: click.Context,
    output: str,
    hide_not_tracked: bool,
) -> None:
    """Export ATT&CK Navigator layer from JIRA data.

    Creates a JSON file compatible with the MITRE ATT&CK Navigator
    showing your defensive coverage based on JIRA issue maturity levels.
    """
    config = ctx.obj["config"]
    logger.info("export_started", output=output, hide_not_tracked=hide_not_tracked)

    console.print(Panel.fit("Exporting ATT&CK Navigator Layer", style="bold blue"))

    # TODO: Implementation in Phase 2
    console.print("[yellow]Export command - Implementation pending[/yellow]")


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show current configuration and JIRA connection status."""
    config = ctx.obj["config"]

    table = Table(title="Configuration Status", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("JIRA URL", config.jira_url)
    table.add_row("JIRA Username", config.jira_username)
    table.add_row("Project Name", config.jira_project_name)
    table.add_row("Project Key", config.jira_project_key)
    table.add_row("Environment", config.environment)
    table.add_row("Log Level", config.log_level)
    table.add_row("SSL Verify", str(config.ssl_verify))

    console.print(table)

    # TODO: Test JIRA connection
    console.print("\n[yellow]Connection test - Implementation pending[/yellow]")


@cli.command()
def version() -> None:
    """Show version information."""
    console.print(Panel.fit(
        "[bold]JIRA Attack Framework Service[/bold]\n"
        "Version: 2.0.0\n"
        "Python: 3.11+",
        title="Version Info",
        border_style="blue",
    ))


def main() -> None:
    """Main entry point for the CLI application."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        logger.error("application_error", error=str(e), exc_info=True)
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
