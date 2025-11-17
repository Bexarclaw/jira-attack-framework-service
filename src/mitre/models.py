"""Data models for MITRE ATT&CK framework entities.

This module defines Pydantic models for ATT&CK techniques, tactics,
sub-techniques, and data sources.
"""

from dataclasses import dataclass, field
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ExternalReference(BaseModel):
    """External reference for ATT&CK objects.

    Attributes:
        source_name: Name of the reference source
        external_id: External identifier (e.g., T1003)
        url: URL to the reference
        description: Optional description
    """

    source_name: str
    external_id: str
    url: HttpUrl
    description: Optional[str] = None


class KillChainPhase(BaseModel):
    """Kill chain phase (tactic) for a technique.

    Attributes:
        kill_chain_name: Name of the kill chain (typically 'mitre-attack')
        phase_name: Name of the phase/tactic
    """

    kill_chain_name: str
    phase_name: str


class Tactic(BaseModel):
    """MITRE ATT&CK Tactic.

    Attributes:
        id: ATT&CK object ID
        name: Display name of the tactic
        description: Detailed description
        external_references: List of external references
        x_mitre_shortname: Short name used in URLs
    """

    id: str
    name: str
    description: str
    external_references: list[ExternalReference]
    x_mitre_shortname: str

    @property
    def tactic_id(self) -> str:
        """Get the tactic ID (e.g., TA0001)."""
        for ref in self.external_references:
            if ref.source_name == "mitre-attack":
                return ref.external_id
        return ""

    @property
    def url(self) -> str:
        """Get the ATT&CK URL for this tactic."""
        for ref in self.external_references:
            if ref.source_name == "mitre-attack":
                return str(ref.url)
        return ""


class DataSource(BaseModel):
    """ATT&CK Data Source.

    Attributes:
        name: Name of the data source
        description: Optional description
    """

    name: str
    description: Optional[str] = None


class Technique(BaseModel):
    """MITRE ATT&CK Technique.

    Attributes:
        id: ATT&CK object ID
        name: Display name of the technique
        description: Detailed description
        external_references: List of external references
        kill_chain_phases: List of tactics this technique belongs to
        x_mitre_data_sources: List of data sources for detection
        x_mitre_is_subtechnique: Whether this is a sub-technique
        x_mitre_platforms: Platforms this technique applies to
        x_mitre_version: Version of the technique definition
        revoked: Whether this technique has been revoked
        deprecated: Whether this technique has been deprecated
    """

    id: str
    name: str
    description: str
    external_references: list[ExternalReference]
    kill_chain_phases: list[KillChainPhase] = Field(default_factory=list)
    x_mitre_data_sources: list[str] = Field(default_factory=list)
    x_mitre_is_subtechnique: bool = False
    x_mitre_platforms: list[str] = Field(default_factory=list)
    x_mitre_version: Optional[str] = None
    revoked: bool = False
    deprecated: bool = False

    @property
    def technique_id(self) -> str:
        """Get the technique ID (e.g., T1003, T1003.001)."""
        for ref in self.external_references:
            if ref.source_name == "mitre-attack":
                return ref.external_id
        return ""

    @property
    def url(self) -> str:
        """Get the ATT&CK URL for this technique."""
        for ref in self.external_references:
            if ref.source_name == "mitre-attack":
                return str(ref.url)
        return ""

    @property
    def parent_id(self) -> Optional[str]:
        """Get parent technique ID for sub-techniques (e.g., T1003 from T1003.001)."""
        if self.x_mitre_is_subtechnique:
            tech_id = self.technique_id
            if "." in tech_id:
                return tech_id.split(".")[0]
        return None

    @property
    def primary_tactic(self) -> str:
        """Get the primary (first) tactic for this technique."""
        if self.kill_chain_phases:
            return self.kill_chain_phases[0].phase_name
        return ""

    @property
    def is_active(self) -> bool:
        """Check if technique is active (not revoked or deprecated)."""
        return not (self.revoked or self.deprecated)


class SubTechnique(Technique):
    """MITRE ATT&CK Sub-Technique.

    This is a specialized version of Technique where x_mitre_is_subtechnique
    is always True.
    """

    x_mitre_is_subtechnique: bool = Field(default=True, frozen=True)


@dataclass
class TechniqueCollection:
    """Collection of techniques with metadata.

    Attributes:
        techniques: List of all techniques
        tactics: List of all tactics
        data_sources: List of all data sources
        version: ATT&CK version/release
    """

    techniques: list[Technique] = field(default_factory=list)
    tactics: list[Tactic] = field(default_factory=list)
    data_sources: list[DataSource] = field(default_factory=list)
    version: Optional[str] = None

    @property
    def parent_techniques(self) -> list[Technique]:
        """Get only parent techniques (not sub-techniques)."""
        return [t for t in self.techniques if not t.x_mitre_is_subtechnique]

    @property
    def sub_techniques(self) -> list[Technique]:
        """Get only sub-techniques."""
        return [t for t in self.techniques if t.x_mitre_is_subtechnique]

    @property
    def active_techniques(self) -> list[Technique]:
        """Get only active techniques (not revoked or deprecated)."""
        return [t for t in self.techniques if t.is_active]

    def get_technique_by_id(self, technique_id: str) -> Optional[Technique]:
        """Get a technique by its ID.

        Args:
            technique_id: The technique ID (e.g., T1003)

        Returns:
            Technique if found, None otherwise
        """
        for technique in self.techniques:
            if technique.technique_id == technique_id:
                return technique
        return None

    def get_subtechniques_for_parent(self, parent_id: str) -> list[Technique]:
        """Get all sub-techniques for a given parent technique.

        Args:
            parent_id: Parent technique ID (e.g., T1003)

        Returns:
            List of sub-techniques
        """
        return [t for t in self.sub_techniques if t.parent_id == parent_id]
