"""ATT&CK Navigator layer export functionality.

This module generates MITRE ATT&CK Navigator JSON layers
from JIRA issue data.
"""

import json
from pathlib import Path
from typing import Any, Optional

from rich.console import Console

from src.jira.models import MaturityLevel
from src.logger import get_logger
from src.sync.techniques import TechniqueSync

logger = get_logger(__name__)
console = Console()


class NavigatorExporter:
    """Exports ATT&CK Navigator layers from JIRA data.

    Attributes:
        technique_sync: Technique synchronization manager
    """

    VERSION = "4.9"
    DOMAIN = "enterprise-attack"

    # Maturity level colors
    COLORS = {
        MaturityLevel.NOT_TRACKED: "#DCDCDC",  # Gray
        MaturityLevel.INITIAL: "#e1fce1",  # Lightest green
        MaturityLevel.DEFINED: "#81fc81",  # Lighter green
        MaturityLevel.RESILIENT: "#49fc49",  # Green
        MaturityLevel.OPTIMIZED: "#03ad03",  # Darker green
    }

    def __init__(self, technique_sync: TechniqueSync) -> None:
        """Initialize navigator exporter.

        Args:
            technique_sync: Technique sync manager
        """
        self.technique_sync = technique_sync
        logger.info("navigator_exporter_initialized")

    def export_layer(
        self,
        project_key: str,
        output_path: str = "attack2jira.json",
        hide_not_tracked: bool = False,
        layer_name: Optional[str] = None,
        layer_description: Optional[str] = None,
    ) -> Path:
        """Export ATT&CK Navigator layer from JIRA data.

        Args:
            project_key: JIRA project key
            output_path: Output file path
            hide_not_tracked: Hide techniques with 'Not Tracked' maturity
            layer_name: Custom layer name
            layer_description: Custom layer description

        Returns:
            Path to exported file
        """
        logger.info(
            "exporting_navigator_layer",
            project_key=project_key,
            output_path=output_path,
        )

        console.print(f"[cyan]Exporting ATT&CK Navigator layer...[/cyan]")

        # Get technique maturity levels from JIRA
        maturity_map = self.technique_sync.get_technique_maturity_levels(project_key)

        # Build layer
        layer = self._build_layer(
            maturity_map=maturity_map,
            hide_not_tracked=hide_not_tracked,
            layer_name=layer_name or "Attack2Jira Coverage",
            layer_description=layer_description
            or f"Defensive coverage from JIRA project {project_key}",
        )

        # Write to file
        output_file = Path(output_path)
        output_file.write_text(json.dumps(layer, indent=2, ensure_ascii=False))

        console.print(f"[green]✓ Exported layer to {output_path}[/green]")
        logger.info("navigator_layer_exported", path=output_path, techniques=len(layer["techniques"]))

        return output_file

    def _build_layer(
        self,
        maturity_map: dict[str, str],
        hide_not_tracked: bool,
        layer_name: str,
        layer_description: str,
    ) -> dict[str, Any]:
        """Build ATT&CK Navigator layer structure.

        Args:
            maturity_map: Mapping of technique IDs to maturity levels
            hide_not_tracked: Hide techniques with 'Not Tracked' maturity
            layer_name: Layer name
            layer_description: Layer description

        Returns:
            Navigator layer dictionary
        """
        techniques = []

        for technique_id, maturity_value in maturity_map.items():
            # Determine color based on maturity
            color = self.COLORS.get(
                MaturityLevel(maturity_value),
                self.COLORS[MaturityLevel.NOT_TRACKED],
            )

            # Determine if enabled
            enabled = True
            if maturity_value == MaturityLevel.NOT_TRACKED.value:
                enabled = not hide_not_tracked

            technique = {
                "techniqueID": technique_id,
                "enabled": enabled,
                "color": color,
                "comment": f"Maturity: {maturity_value}",
            }

            techniques.append(technique)

        # Build layer structure
        layer = {
            "name": layer_name,
            "versions": {
                "attack": "14",  # ATT&CK version
                "navigator": self.VERSION,
                "layer": "4.5",
            },
            "domain": self.DOMAIN,
            "description": layer_description,
            "filters": {
                "platforms": ["windows", "linux", "macos", "network", "cloud"]
            },
            "sorting": 0,
            "layout": {
                "layout": "side",
                "aggregateFunction": "average",
                "showID": False,
                "showName": True,
                "showAggregateScores": False,
                "countUnscored": False,
            },
            "hideDisabled": hide_not_tracked,
            "techniques": techniques,
            "gradient": {
                "colors": [
                    self.COLORS[MaturityLevel.NOT_TRACKED],
                    self.COLORS[MaturityLevel.OPTIMIZED],
                ],
                "minValue": 0,
                "maxValue": 100,
            },
            "legendItems": [
                {
                    "label": MaturityLevel.NOT_TRACKED.value,
                    "color": self.COLORS[MaturityLevel.NOT_TRACKED],
                },
                {
                    "label": MaturityLevel.INITIAL.value,
                    "color": self.COLORS[MaturityLevel.INITIAL],
                },
                {
                    "label": MaturityLevel.DEFINED.value,
                    "color": self.COLORS[MaturityLevel.DEFINED],
                },
                {
                    "label": MaturityLevel.RESILIENT.value,
                    "color": self.COLORS[MaturityLevel.RESILIENT],
                },
                {
                    "label": MaturityLevel.OPTIMIZED.value,
                    "color": self.COLORS[MaturityLevel.OPTIMIZED],
                },
            ],
            "metadata": [],
            "links": [],
            "showTacticRowBackground": True,
            "tacticRowBackground": "#dddddd",
            "selectTechniquesAcrossTactics": True,
            "selectSubtechniquesWithParent": False,
        }

        return layer

    def validate_layer(self, layer_path: str) -> bool:
        """Validate Navigator layer JSON structure.

        Args:
            layer_path: Path to layer file

        Returns:
            True if valid, False otherwise
        """
        logger.info("validating_layer", path=layer_path)

        try:
            layer_file = Path(layer_path)
            if not layer_file.exists():
                logger.error("layer_file_not_found", path=layer_path)
                return False

            layer = json.loads(layer_file.read_text())

            # Check required fields
            required_fields = ["name", "versions", "domain", "techniques"]
            for field in required_fields:
                if field not in layer:
                    logger.error("missing_required_field", field=field)
                    return False

            # Validate techniques
            if not isinstance(layer["techniques"], list):
                logger.error("techniques_not_list")
                return False

            for technique in layer["techniques"]:
                if "techniqueID" not in technique:
                    logger.error("technique_missing_id")
                    return False

            logger.info("layer_validated", path=layer_path)
            return True

        except json.JSONDecodeError as e:
            logger.error("layer_json_invalid", error=str(e))
            return False
        except Exception as e:
            logger.error("layer_validation_failed", error=str(e))
            return False
