"""Configuration management for JIRA Attack Framework Service.

This module provides configuration loading and validation using Pydantic.
Configuration values are loaded from environment variables or .env file.
"""

import sys
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console

console = Console()


class ConfigSettings(BaseSettings):
    """Application configuration settings.

    All settings are loaded from environment variables or .env file.
    See .env.example for a complete list of available settings.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # JIRA Configuration
    jira_url: str = Field(
        ...,
        description="Base URL of the JIRA instance (without trailing slash)",
        examples=["https://your-company.atlassian.net"],
    )

    jira_username: str = Field(
        ...,
        description="JIRA username (usually email address)",
        examples=["user@example.com"],
    )

    jira_api_token: str = Field(
        ...,
        description="JIRA API token for authentication",
    )

    jira_project_name: str = Field(
        default="Mitre Attack Framework",
        description="Name of the JIRA project to create/use",
    )

    jira_project_key: str = Field(
        default="ATTACK",
        description="JIRA project key (short identifier)",
    )

    # MITRE ATT&CK Configuration
    mitre_api_endpoint: str | None = Field(
        default=None,
        description="Custom MITRE ATT&CK API endpoint (optional)",
    )

    # Application Settings
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )

    log_format: Literal["json", "console"] = Field(
        default="console",
        description="Log output format",
    )

    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment",
    )

    ssl_verify: bool = Field(
        default=True,
        description="Enable SSL certificate verification",
    )

    hide_not_tracked: bool = Field(
        default=False,
        description="Hide techniques with 'Not Tracked' maturity in exports",
    )

    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retries for API calls",
    )

    request_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Request timeout in seconds",
    )

    @field_validator("jira_url")
    @classmethod
    def validate_jira_url(cls, v: str) -> str:
        """Validate and normalize JIRA URL."""
        if not v:
            raise ValueError("JIRA_URL is required")

        # Remove trailing slash
        v = v.rstrip("/")

        # Ensure it starts with http:// or https://
        if not v.startswith(("http://", "https://")):
            raise ValueError("JIRA_URL must start with http:// or https://")

        return v

    @field_validator("jira_project_key")
    @classmethod
    def validate_project_key(cls, v: str) -> str:
        """Validate JIRA project key format."""
        if not v:
            raise ValueError("JIRA_PROJECT_KEY is required")

        # Convert to uppercase
        v = v.upper()

        # JIRA project keys must be 2-10 characters, uppercase letters only
        if not v.isalpha():
            raise ValueError(
                "JIRA_PROJECT_KEY must contain only letters (will be converted to uppercase)"
            )

        if not (2 <= len(v) <= 10):
            raise ValueError("JIRA_PROJECT_KEY must be between 2 and 10 characters")

        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


def load_config() -> ConfigSettings:
    """Load and validate configuration settings.

    Returns:
        ConfigSettings: Validated configuration object

    Raises:
        SystemExit: If configuration is invalid or required settings are missing
    """
    try:
        config = ConfigSettings()

        # Display warning if SSL verification is disabled
        if not config.ssl_verify and config.is_production:
            console.print(
                "[bold yellow]WARNING:[/bold yellow] SSL verification is disabled in production!",
                style="yellow",
            )

        return config

    except Exception as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}", style="red")
        console.print("\n[yellow]Please check your .env file or environment variables.[/yellow]")
        console.print("[yellow]See .env.example for required settings.[/yellow]")
        sys.exit(1)


def validate_config_file_exists() -> bool:
    """Check if .env file exists.

    Returns:
        bool: True if .env exists, False otherwise
    """
    env_file = Path(".env")
    return env_file.exists()


def create_default_env_file() -> None:
    """Create a default .env file from .env.example if it doesn't exist."""
    env_file = Path(".env")
    example_file = Path(".env.example")

    if env_file.exists():
        console.print("[yellow].env file already exists[/yellow]")
        return

    if not example_file.exists():
        console.print("[red].env.example not found[/red]")
        return

    try:
        env_file.write_text(example_file.read_text())
        console.print("[green]Created .env file from .env.example[/green]")
        console.print("[yellow]Please edit .env with your actual configuration values[/yellow]")
    except Exception as e:
        console.print(f"[red]Failed to create .env file: {e}[/red]")


# Global configuration instance (lazy loaded)
_config: ConfigSettings | None = None


def get_config() -> ConfigSettings:
    """Get the global configuration instance.

    This provides a singleton configuration object that is loaded once
    and reused throughout the application.

    Returns:
        ConfigSettings: Global configuration instance
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


if __name__ == "__main__":
    # Test configuration loading
    console.print("[bold]Testing Configuration Loading...[/bold]\n")

    if not validate_config_file_exists():
        console.print("[yellow].env file not found[/yellow]")
        console.print("[yellow]Creating from .env.example...[/yellow]\n")
        create_default_env_file()

    try:
        config = load_config()
        console.print("[green]✓ Configuration loaded successfully![/green]\n")
        console.print("[bold]Configuration Summary:[/bold]")
        console.print(f"  JIRA URL: {config.jira_url}")
        console.print(f"  JIRA Username: {config.jira_username}")
        console.print(f"  Project Name: {config.jira_project_name}")
        console.print(f"  Project Key: {config.jira_project_key}")
        console.print(f"  Environment: {config.environment}")
        console.print(f"  Log Level: {config.log_level}")
        console.print(f"  SSL Verify: {config.ssl_verify}")
    except SystemExit:
        console.print("\n[red]✗ Configuration validation failed[/red]")
        sys.exit(1)
