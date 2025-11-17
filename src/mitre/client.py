"""MITRE ATT&CK API client for fetching framework data.

This module provides a client for interacting with the MITRE ATT&CK API
using the attackcti library.
"""

from typing import Optional

import httpx
from attackcti import attack_client
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import ConfigSettings
from src.logger import get_logger
from src.mitre.models import (
    DataSource,
    Tactic,
    Technique,
    TechniqueCollection,
)

logger = get_logger(__name__)


class MitreClientError(Exception):
    """Base exception for MITRE client errors."""

    pass


class MitreConnectionError(MitreClientError):
    """Exception raised when connection to MITRE API fails."""

    pass


class MitreDataError(MitreClientError):
    """Exception raised when MITRE data is invalid or missing."""

    pass


class MitreClient:
    """Client for fetching MITRE ATT&CK framework data.

    This client wraps the attackcti library and provides structured
    access to ATT&CK techniques, tactics, and data sources.

    Attributes:
        config: Application configuration
        client: attackcti client instance
    """

    def __init__(self, config: ConfigSettings) -> None:
        """Initialize MITRE ATT&CK client.

        Args:
            config: Application configuration settings
        """
        self.config = config
        self.client: Optional[attack_client] = None
        logger.info("mitre_client_initialized")

    def connect(self) -> None:
        """Establish connection to MITRE ATT&CK API.

        Raises:
            MitreConnectionError: If connection fails
        """
        try:
            logger.info("connecting_to_mitre_api")
            self.client = attack_client()
            logger.info("mitre_api_connected")
        except Exception as e:
            logger.error("mitre_connection_failed", error=str(e))
            raise MitreConnectionError(f"Failed to connect to MITRE API: {e}") from e

    def get_enterprise_techniques(self) -> list[Technique]:
        """Fetch all enterprise ATT&CK techniques.

        Returns:
            List of Technique objects

        Raises:
            MitreConnectionError: If not connected
            MitreDataError: If data fetching fails
        """
        if not self.client:
            raise MitreConnectionError("Not connected to MITRE API. Call connect() first.")

        try:
            logger.info("fetching_enterprise_techniques")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
            ) as progress:
                progress.add_task("Fetching ATT&CK techniques...", total=None)

                # Fetch all enterprise data
                all_enterprise = self.client.get_enterprise()

                # Parse techniques
                techniques = []
                for tech_obj in all_enterprise.get("techniques", []):
                    tech_dict = tech_obj.serialize() if hasattr(tech_obj, "serialize") else tech_obj

                    # Skip revoked techniques
                    if tech_dict.get("revoked", False):
                        continue

                    # Parse into Pydantic model
                    technique = Technique(**tech_dict)
                    techniques.append(technique)

            logger.info("techniques_fetched", count=len(techniques))
            return techniques

        except Exception as e:
            logger.error("technique_fetch_failed", error=str(e))
            raise MitreDataError(f"Failed to fetch techniques: {e}") from e

    def get_enterprise_tactics(self) -> list[Tactic]:
        """Fetch all enterprise ATT&CK tactics.

        Returns:
            List of Tactic objects

        Raises:
            MitreConnectionError: If not connected
            MitreDataError: If data fetching fails
        """
        if not self.client:
            raise MitreConnectionError("Not connected to MITRE API. Call connect() first.")

        try:
            logger.info("fetching_enterprise_tactics")
            all_enterprise = self.client.get_enterprise()

            tactics = []
            for tactic_obj in all_enterprise.get("tactics", []):
                tactic_dict = tactic_obj.serialize() if hasattr(tactic_obj, "serialize") else tactic_obj
                tactic = Tactic(**tactic_dict)
                tactics.append(tactic)

            logger.info("tactics_fetched", count=len(tactics))
            return tactics

        except Exception as e:
            logger.error("tactic_fetch_failed", error=str(e))
            raise MitreDataError(f"Failed to fetch tactics: {e}") from e

    def get_data_sources(self) -> list[DataSource]:
        """Extract unique data sources from techniques.

        Returns:
            List of DataSource objects

        Raises:
            MitreConnectionError: If not connected
            MitreDataError: If data extraction fails
        """
        if not self.client:
            raise MitreConnectionError("Not connected to MITRE API. Call connect() first.")

        try:
            logger.info("extracting_data_sources")

            # Get techniques to extract data sources
            techniques = self.get_enterprise_techniques()

            # Collect unique data sources
            data_source_names = set()
            for technique in techniques:
                for ds in technique.x_mitre_data_sources:
                    data_source_names.add(ds)

            # Create DataSource objects
            data_sources = [DataSource(name=ds) for ds in sorted(data_source_names)]

            logger.info("data_sources_extracted", count=len(data_sources))
            return data_sources

        except Exception as e:
            logger.error("data_source_extraction_failed", error=str(e))
            raise MitreDataError(f"Failed to extract data sources: {e}") from e

    def get_all_data(self) -> TechniqueCollection:
        """Fetch all ATT&CK data (techniques, tactics, data sources).

        Returns:
            TechniqueCollection with all data

        Raises:
            MitreConnectionError: If not connected
            MitreDataError: If data fetching fails
        """
        if not self.client:
            self.connect()

        logger.info("fetching_all_attack_data")

        try:
            techniques = self.get_enterprise_techniques()
            tactics = self.get_enterprise_tactics()
            data_sources = self.get_data_sources()

            collection = TechniqueCollection(
                techniques=techniques,
                tactics=tactics,
                data_sources=data_sources,
                version=None,  # TODO: Extract version from API if available
            )

            logger.info(
                "all_attack_data_fetched",
                techniques=len(techniques),
                tactics=len(tactics),
                data_sources=len(data_sources),
            )

            return collection

        except Exception as e:
            logger.error("all_data_fetch_failed", error=str(e))
            raise MitreDataError(f"Failed to fetch all ATT&CK data: {e}") from e

    def close(self) -> None:
        """Close connection to MITRE API."""
        self.client = None
        logger.info("mitre_client_closed")
